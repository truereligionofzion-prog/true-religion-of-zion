#!/usr/bin/env python3
"""
Final New Testament extractor with accurate chapter/verse detection
"""

import pdfplumber
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class FinalNTExtractor:
    """Extract New Testament with careful chapter/verse detection"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Expected verse counts per chapter for Matthew (for validation)
        self.matthew_chapters = {
            1: 25, 2: 23, 3: 17, 4: 25, 5: 48, 6: 34, 7: 29, 8: 34,
            9: 38, 10: 42, 11: 30, 12: 50, 13: 58, 14: 36, 15: 39,
            16: 28, 17: 27, 18: 35, 19: 30, 20: 34, 21: 46, 22: 46,
            23: 39, 24: 51, 25: 46, 26: 75, 27: 66, 28: 20
        }
    
    def extract_nt_carefully(self, start_page: int = 2169, num_pages: int = 100):
        """Extract NT with careful attention to structure"""
        
        print(f"📝 Carefully extracting NT from page {start_page} ({num_pages} pages)...")
        
        verses = []
        current_book = None
        current_chapter = None
        in_verse_mode = False
        verse_text_buffer = []
        current_verse_num = None
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_offset in range(num_pages):
                    page_num = start_page - 1 + page_offset
                    
                    if page_num >= len(pdf.pages):
                        break
                    
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        lines = text.split('\n')
                        
                        for i, line in enumerate(lines):
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Print debug for first few pages to understand structure
                            if page_offset < 3 and len(verses) < 20:
                                print(f"Debug: '{line}' -> ", end="")
                            
                            # Check for book headers
                            if line.upper() == 'MATTHEW' and current_book != 'Matthew':
                                # Save any pending verse
                                if current_verse_num and verse_text_buffer:
                                    verse_text = ' '.join(verse_text_buffer).strip()
                                    if len(verse_text) > 5:
                                        verses.append({
                                            'book': current_book,
                                            'chapter': current_chapter,
                                            'verse': current_verse_num,
                                            'text': self._clean_verse_text(verse_text)
                                        })
                                
                                current_book = 'Matthew'
                                current_chapter = 1  # Start with chapter 1
                                current_verse_num = None
                                verse_text_buffer = []
                                in_verse_mode = True
                                
                                if page_offset < 3:
                                    print("BOOK HEADER")
                                continue
                            
                            # Skip Hebrew headers and other non-content lines
                            if (line.upper() in ['MATTITHYAHU'] or
                                re.match(r'^[^\w\s]+\s*\w+$', line) or  # Hebrew-like text
                                line.isdigit() and len(line) == 4):  # Page numbers
                                if page_offset < 3:
                                    print("SKIP")
                                continue
                            
                            # In Matthew, look for verse numbers and text
                            if current_book == 'Matthew' and in_verse_mode:
                                
                                # Check if this line is just a number (potential verse)
                                if re.match(r'^\d+$', line):
                                    num = int(line)
                                    
                                    # Heuristic: if it's 1-3 and we've seen some verses, might be new chapter
                                    if (num in [1, 2, 3] and 
                                        current_verse_num and current_verse_num > 10 and
                                        current_chapter < 28):  # Matthew has 28 chapters
                                        
                                        # Save current verse
                                        if verse_text_buffer:
                                            verse_text = ' '.join(verse_text_buffer).strip()
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse_num,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        # Move to next chapter
                                        current_chapter += 1
                                        current_verse_num = num
                                        verse_text_buffer = []
                                        
                                        if page_offset < 3:
                                            print(f"NEW CHAPTER {current_chapter}, VERSE {num}")
                                        continue
                                    
                                    # Regular verse number
                                    if 1 <= num <= 100:  # Reasonable verse range
                                        # Save previous verse
                                        if current_verse_num and verse_text_buffer:
                                            verse_text = ' '.join(verse_text_buffer).strip()
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse_num,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        # Start new verse
                                        current_verse_num = num
                                        verse_text_buffer = []
                                        
                                        if page_offset < 3:
                                            print(f"VERSE {num}")
                                        continue
                                
                                # Collect verse text
                                if current_verse_num:
                                    # Skip obvious non-content
                                    if (not re.match(r'^[A-Z\s]+$', line) and  # Skip all caps
                                        len(line) > 1 and
                                        not line.isdigit()):
                                        verse_text_buffer.append(line)
                                        if page_offset < 3:
                                            print(f"TEXT for v{current_verse_num}")
                                    else:
                                        if page_offset < 3:
                                            print("SKIP TEXT")
                                else:
                                    if page_offset < 3:
                                        print("NO VERSE YET")
                            else:
                                if page_offset < 3:
                                    print("NOT IN VERSE MODE")
                
                # Save final verse
                if current_verse_num and verse_text_buffer:
                    verse_text = ' '.join(verse_text_buffer).strip()
                    if len(verse_text) > 5:
                        verses.append({
                            'book': current_book,
                            'chapter': current_chapter,
                            'verse': current_verse_num,
                            'text': self._clean_verse_text(verse_text)
                        })
        
        except Exception as e:
            print(f"❌ Error extracting: {e}")
        
        print(f"\n📊 Extracted {len(verses)} verses")
        
        # Validate extraction by checking chapter structure
        self._validate_extraction(verses)
        
        return verses
    
    def _validate_extraction(self, verses: list):
        """Validate extraction against known Matthew structure"""
        
        print("\n📋 EXTRACTION VALIDATION:")
        
        # Group by chapter
        chapters = {}
        for verse in verses:
            if verse['book'] == 'Matthew':
                ch = verse['chapter']
                if ch not in chapters:
                    chapters[ch] = []
                chapters[ch].append(verse['verse'])
        
        # Check each chapter
        for ch_num in sorted(chapters.keys()):
            verse_nums = sorted(chapters[ch_num])
            expected_count = self.matthew_chapters.get(ch_num, 0)
            actual_count = len(verse_nums)
            
            if expected_count > 0:
                completeness = (actual_count / expected_count) * 100
                status = "✅" if completeness > 80 else "⚠️" if completeness > 50 else "❌"
                print(f"   {status} Chapter {ch_num}: {actual_count}/{expected_count} verses ({completeness:.1f}%)")
                
                # Show verse range
                if verse_nums:
                    print(f"      Verses: {verse_nums[0]}-{verse_nums[-1]}")
                    
                    # Show first verse sample
                    first_verse = next((v for v in verses if v['chapter'] == ch_num and v['verse'] == verse_nums[0]), None)
                    if first_verse:
                        print(f"      Sample: {first_verse['text'][:60]}...")
            else:
                print(f"   ❓ Chapter {ch_num}: {actual_count} verses (unknown expected count)")
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean verse text"""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\d+$', '', text).strip()  # Remove trailing numbers
        
        # Divine name standardization
        text = re.sub(r'\{vWHY\}|\{HWHY\}|hWhY', 'YHWH', text)
        text = re.sub(r'ha\'YHWH', 'YHWH', text)
        
        return text
    
    async def save_nt_verses_final(self, verses: list):
        """Save final NT verses"""
        
        if not verses:
            print("❌ No verses to save")
            return False
        
        print(f"\n💾 Saving {len(verses)} final NT verses...")
        
        try:
            # Clear any existing NT verses first
            await self.db.bible_verses.delete_many({'version': 'yah_scriptures', 'testament': 'new'})
            
            saved_count = 0
            books_created = set()
            
            for verse in verses:
                verse_doc = {
                    'id': f"{verse['book'].lower().replace(' ', '_')}_{verse['chapter']}_{verse['verse']}_yah_scriptures",
                    'book': verse['book'],
                    'chapter': verse['chapter'],
                    'verse': verse['verse'],
                    'text': verse['text'],
                    'version': 'yah_scriptures',
                    'testament': 'new',
                    'has_precept': False,
                    'source': 'yah_scriptures_pdf_final',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                await self.db.bible_verses.insert_one(verse_doc)
                books_created.add(verse['book'])
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} verses from {len(books_created)} books")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False
    
    async def run_careful_extraction(self):
        """Run careful extraction"""
        
        print("🚀 Starting Final Careful New Testament Extraction")
        print("=" * 70)
        
        try:
            # Extract with more pages to get more of Matthew
            verses = self.extract_nt_carefully()
            
            if verses:
                success = await self.save_nt_verses_final(verses)
                
                if success:
                    # Final stats
                    total_yah = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                    nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                    
                    print(f"\n📊 FINAL RESULTS:")
                    print(f"   📖 Total Yah Scriptures verses: {total_yah}")
                    print(f"   📖 New Testament verses: {nt_count}")
                    
                    return True
                    
        except Exception as e:
            print(f"❌ Final extraction failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        
        return False

async def main():
    extractor = FinalNTExtractor()
    success = await extractor.run_careful_extraction()
    
    if success:
        print("\n🎉 Final careful extraction completed!")
    else:
        print("\n❌ Final careful extraction failed")

if __name__ == "__main__":
    asyncio.run(main())