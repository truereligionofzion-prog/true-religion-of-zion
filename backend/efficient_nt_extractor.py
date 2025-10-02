#!/usr/bin/env python3
"""
Memory-efficient New Testament extractor from Yah Scriptures PDF
"""

import PyPDF2
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import gc

class EfficientNTExtractor:
    """Memory-efficient New Testament extraction"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # New Testament book names (English)
        self.nt_books = [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
            '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
            'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
            'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
            'Jude', 'Revelation'
        ]
    
    def find_nt_start_efficiently(self):
        """Find New Testament start using page-by-page processing"""
        
        print("🔍 Finding New Testament start (memory-efficient)...")
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"   📖 Total pages: {total_pages}")
                
                # Search in second half where NT likely starts
                start_search = total_pages // 2
                
                for page_num in range(start_search, total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            # Look for Matthew 1:1 or genealogy patterns
                            patterns = [
                                r'Matthew.*1.*1|MATTITHYAHU.*1.*1',
                                r'genealogy.*Abraham|Abraham.*genealogy',
                                r'1\s*1\s+.*Abraham.*Isaac.*Jacob',
                                r'book.*generations.*Abraham'
                            ]
                            
                            for pattern in patterns:
                                if re.search(pattern, text, re.IGNORECASE):
                                    print(f"   📖 Found NT pattern at page {page_num + 1}")
                                    
                                    # Show sample
                                    lines = text.split('\n')[:10]
                                    print(f"   📝 Sample:")
                                    for line in lines:
                                        if line.strip():
                                            print(f"      {line.strip()[:80]}...")
                                    
                                    return page_num
                        
                        # Progress every 50 pages
                        if (page_num - start_search) % 50 == 0:
                            print(f"   🔍 Searched {page_num - start_search} pages...")
                            
                        # Clear memory periodically
                        if (page_num - start_search) % 20 == 0:
                            gc.collect()
                            
                    except Exception as e:
                        # Skip problematic pages
                        continue
                        
        except Exception as e:
            print(f"❌ Error finding NT start: {e}")
            
        return None
    
    def extract_nt_sample_efficiently(self, start_page: int, num_pages: int = 20):
        """Extract NT sample using memory-efficient processing"""
        
        print(f"\n📝 Extracting NT sample from page {start_page + 1} ({num_pages} pages)...")
        
        verses = []
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                current_book = 'Matthew'
                current_chapter = None
                
                for page_offset in range(num_pages):
                    page_num = start_page + page_offset
                    
                    if page_num >= len(pdf_reader.pages):
                        break
                    
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            self._process_page_text(text, current_book, verses)
                        
                        # Clear memory after each page
                        del page, text
                        gc.collect()
                        
                    except Exception as e:
                        # Skip problematic pages
                        continue
                
                print(f"   ✅ Extracted {len(verses)} verses")
                
        except Exception as e:
            print(f"❌ Error extracting sample: {e}")
            
        return verses
    
    def _process_page_text(self, text: str, current_book: str, verses: list):
        """Process individual page text for verses"""
        
        lines = text.split('\n')
        current_chapter = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for chapter numbers (single digits/numbers on their own line)
            if re.match(r'^\d+$', line) and len(line) <= 2:
                try:
                    chapter_num = int(line)
                    if 1 <= chapter_num <= 50:  # Reasonable chapter range
                        current_chapter = chapter_num
                        continue
                except:
                    pass
            
            # Look for verse patterns
            if current_chapter:
                verse_match = re.match(r'^(\d+)\s+(.+)', line)
                if verse_match:
                    try:
                        verse_num = int(verse_match.group(1))
                        verse_text = verse_match.group(2).strip()
                        
                        if len(verse_text) > 10 and verse_num <= 200:  # Reasonable ranges
                            verses.append({
                                'book': current_book,
                                'chapter': current_chapter,
                                'verse': verse_num,
                                'text': verse_text
                            })
                            
                            # Limit output for memory
                            if len(verses) <= 5:
                                print(f"      {current_chapter}:{verse_num} {verse_text[:50]}...")
                                
                    except:
                        pass
    
    async def save_nt_verses(self, verses: list):
        """Save New Testament verses to database"""
        
        if not verses:
            print("❌ No verses to save")
            return False
        
        print(f"\n💾 Saving {len(verses)} NT verses...")
        
        try:
            saved_count = 0
            
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
                    'source': 'yah_scriptures_pdf',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                await self.db.bible_verses.replace_one(
                    {'id': verse_doc['id']},
                    verse_doc,
                    upsert=True
                )
                
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} NT verses")
            return True
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False
    
    async def run_efficient_extraction(self):
        """Run memory-efficient extraction"""
        
        print("🚀 Starting Memory-Efficient NT Extraction")
        print("=" * 50)
        
        try:
            # Find NT start
            nt_start = self.find_nt_start_efficiently()
            
            if nt_start:
                print(f"\n📖 New Testament starts at page {nt_start + 1}")
                
                # Extract sample
                nt_verses = self.extract_nt_sample_efficiently(nt_start, 15)
                
                if nt_verses:
                    # Save to database
                    success = await self.save_nt_verses(nt_verses)
                    
                    if success:
                        # Check updated stats
                        total_verses = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                        nt_verses_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                        
                        print(f"\n📊 UPDATED STATS:")
                        print(f"   Total Yah Scriptures verses: {total_verses}")
                        print(f"   New Testament verses: {nt_verses_count}")
                        
                        return True
                
            else:
                print("❌ Could not locate New Testament in PDF")
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        
        return False

async def main():
    extractor = EfficientNTExtractor()
    success = await extractor.run_efficient_extraction()
    
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Efficient NT extraction")

if __name__ == "__main__":
    asyncio.run(main())