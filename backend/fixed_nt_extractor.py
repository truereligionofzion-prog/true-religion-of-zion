#!/usr/bin/env python3
"""
Fixed New Testament extractor based on actual PDF structure analysis
"""

import pdfplumber
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class FixedNTExtractor:
    """Extract New Testament with correct parsing logic"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Book mappings based on PDF analysis
        self.book_mappings = {
            'MATTHEW': 'Matthew',
            'MATTITHYAHU': 'Matthew',
            'MARK': 'Mark',
            'MARQOS': 'Mark',  
            'LUKE': 'Luke',
            'LUQAS': 'Luke',
            'JOHN': 'John', 
            'YOḤANAN': 'John',
            'ACTS': 'Acts',
            'MA\'ASEH': 'Acts',
            'ROMANS': 'Romans',
            'ROMIYIM': 'Romans',
            '1 CORINTHIANS': '1 Corinthians',
            '2 CORINTHIANS': '2 Corinthians', 
            'GALATIANS': 'Galatians',
            'EPHESIANS': 'Ephesians',
            'PHILIPPIANS': 'Philippians',
            'COLOSSIANS': 'Colossians',
            '1 THESSALONIANS': '1 Thessalonians',
            '2 THESSALONIANS': '2 Thessalonians',
            '1 TIMOTHY': '1 Timothy',
            '2 TIMOTHY': '2 Timothy',
            'TITUS': 'Titus',
            'PHILEMON': 'Philemon',
            'HEBREWS': 'Hebrews',
            'IḆRIM': 'Hebrews',
            'JAMES': 'James',
            'YA\'AQOḆ': 'James',
            '1 PETER': '1 Peter',
            '2 PETER': '2 Peter',
            'KĔPHA ALEPH': '1 Peter',
            'KĔPHA BETH': '2 Peter', 
            '1 JOHN': '1 John',
            '2 JOHN': '2 John',
            '3 JOHN': '3 John',
            'JUDE': 'Jude',
            'YAHUDAH': 'Jude',
            'REVELATION': 'Revelation',
            'ḤAZON': 'Revelation'
        }
    
    def extract_nt_sample(self, start_page: int = 2169, num_pages: int = 10):
        """Extract sample NT verses to test logic"""
        
        print(f"📝 Extracting sample NT verses from page {start_page} ({num_pages} pages)...")
        
        verses = []
        current_book = None
        current_chapter = None
        verse_buffer = []  # Buffer to collect verse text across multiple lines
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
                            
                            # Check for book headers (exact match)
                            book_found = False
                            line_upper = line.upper()
                            for pdf_name, standard_name in self.book_mappings.items():
                                if line_upper == pdf_name:
                                    # Save any pending verse before switching books
                                    if current_verse_num and verse_buffer and current_book and current_chapter:
                                        verse_text = ' '.join(verse_buffer).strip()
                                        if len(verse_text) > 5:
                                            verses.append({
                                                'book': current_book,
                                                'chapter': current_chapter,
                                                'verse': current_verse_num,
                                                'text': self._clean_verse_text(verse_text)
                                            })
                                    
                                    current_book = standard_name
                                    current_chapter = None
                                    current_verse_num = None
                                    verse_buffer = []
                                    print(f"   📖 Found book: {standard_name}")
                                    book_found = True
                                    break
                            
                            if book_found:
                                continue
                            
                            # Check for chapter numbers (single digit/double digit on its own line)
                            if current_book and re.match(r'^\d+$', line) and len(line) <= 2:
                                try:
                                    chapter_num = int(line)
                                    if 1 <= chapter_num <= 50:  # Reasonable chapter range
                                        # Save any pending verse before switching chapters
                                        if current_verse_num and verse_buffer and current_chapter:
                                            verse_text = ' '.join(verse_buffer).strip()
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse_num,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        current_chapter = chapter_num
                                        current_verse_num = None
                                        verse_buffer = []
                                        print(f"      📄 Chapter {current_chapter}")
                                        continue
                                except:
                                    pass
                            
                            # Check for verse numbers (when we're in a book and chapter)  
                            if (current_book and current_chapter and 
                                re.match(r'^\d+$', line) and len(line) <= 3):
                                try:
                                    verse_num = int(line)
                                    if 1 <= verse_num <= 200:  # Reasonable verse range
                                        # Save previous verse if exists
                                        if current_verse_num and verse_buffer:
                                            verse_text = ' '.join(verse_buffer).strip() 
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse_num,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        # Start new verse
                                        current_verse_num = verse_num
                                        verse_buffer = []
                                        continue
                                except:
                                    pass
                            
                            # Collect verse text (when we have a current verse)
                            if current_verse_num and current_book and current_chapter:
                                # Skip obvious headers and page numbers
                                if (not re.match(r'^[A-Z\s]+$', line) and  # Skip all caps headers
                                    not line.isdigit() and  # Skip pure numbers
                                    len(line) > 1):  # Skip very short lines
                                    verse_buffer.append(line)
                
                # Save final verse if exists
                if current_verse_num and verse_buffer and current_book and current_chapter:
                    verse_text = ' '.join(verse_buffer).strip()
                    if len(verse_text) > 5:
                        verses.append({
                            'book': current_book,
                            'chapter': current_chapter,
                            'verse': current_verse_num,
                            'text': self._clean_verse_text(verse_text)
                        })
        
        except Exception as e:
            print(f"❌ Error extracting verses: {e}")
        
        print(f"\n📊 Extracted {len(verses)} verses")
        
        # Show first few verses
        for i, verse in enumerate(verses[:10]):
            print(f"   {i+1}. {verse['book']} {verse['chapter']}:{verse['verse']} - {verse['text'][:80]}...")
        
        return verses
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean and standardize verse text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove page numbers at end
        text = re.sub(r'\d+$', '', text).strip()
        
        # Apply divine name standardization (YHWH/YHUH)
        # Replace various divine name forms with YHWH
        text = re.sub(r'\{vWHY\}|\{HWHY\}|hWhY', 'YHWH', text)
        text = re.sub(r'ha\'YHWH', 'YHWH', text)
        
        return text
    
    async def save_nt_sample(self, verses: list):
        """Save sample NT verses to database"""
        
        if not verses:
            print("❌ No verses to save")
            return False
        
        print(f"\n💾 Saving {len(verses)} sample NT verses...")
        
        try:
            saved_count = 0
            books_created = set()
            
            for verse in verses:
                # Create verse document
                verse_doc = {
                    'id': f"{verse['book'].lower().replace(' ', '_')}_{verse['chapter']}_{verse['verse']}_yah_scriptures",
                    'book': verse['book'],
                    'chapter': verse['chapter'],
                    'verse': verse['verse'],
                    'text': verse['text'],
                    'version': 'yah_scriptures',
                    'testament': 'new',
                    'has_precept': False,
                    'source': 'yah_scriptures_pdf_fixed',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                # Save verse (replace existing if any)
                await self.db.bible_verses.replace_one(
                    {'id': verse_doc['id']},
                    verse_doc,
                    upsert=True
                )
                
                books_created.add(verse['book'])
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} verses from {len(books_created)} books")
            print(f"   📚 Books: {', '.join(sorted(books_created))}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving verses: {e}")
            return False
    
    async def run_sample_extraction(self):
        """Run sample extraction to test the logic"""
        
        print("🚀 Starting Sample New Testament Extraction")
        print("=" * 60)
        
        try:
            # Extract sample verses from first 10 pages
            sample_verses = self.extract_nt_sample()
            
            if sample_verses:
                # Save to database
                success = await self.save_nt_sample(sample_verses)
                
                if success:
                    # Check results
                    total_yah = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                    nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                    
                    print(f"\n📊 RESULTS:")
                    print(f"   📖 Total Yah Scriptures verses: {total_yah}")
                    print(f"   📖 New Testament verses: {nt_count}")
                    
                    return True
                    
            else:
                print("❌ No verses extracted")
                
        except Exception as e:
            print(f"❌ Sample extraction failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        
        return False

async def main():
    extractor = FixedNTExtractor()
    success = await extractor.run_sample_extraction()
    
    if success:
        print("\n✅ Sample extraction completed successfully!")
    else:
        print("\n❌ Sample extraction failed")

if __name__ == "__main__":
    asyncio.run(main())