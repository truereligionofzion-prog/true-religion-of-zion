#!/usr/bin/env python3
"""
Corrected New Testament extractor with proper verse parsing
"""

import pdfplumber
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class CorrectedNTExtractor:
    """Extract New Testament with correct understanding of PDF structure"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Book mappings and their chapter counts
        self.nt_books = {
            'MATTHEW': {'name': 'Matthew', 'chapters': 28},
            'MATTITHYAHU': {'name': 'Matthew', 'chapters': 28},
            'MARK': {'name': 'Mark', 'chapters': 16},
            'MARQOS': {'name': 'Mark', 'chapters': 16},
            'LUKE': {'name': 'Luke', 'chapters': 24},
            'LUQAS': {'name': 'Luke', 'chapters': 24},
            'JOHN': {'name': 'John', 'chapters': 21},
            'YOḤANAN': {'name': 'John', 'chapters': 21},
            'ACTS': {'name': 'Acts', 'chapters': 28},
            'MA\'ASEH': {'name': 'Acts', 'chapters': 28},
            'ROMANS': {'name': 'Romans', 'chapters': 16},
            'ROMIYIM': {'name': 'Romans', 'chapters': 16},
            '1 CORINTHIANS': {'name': '1 Corinthians', 'chapters': 16},
            '2 CORINTHIANS': {'name': '2 Corinthians', 'chapters': 13},
            'GALATIANS': {'name': 'Galatians', 'chapters': 6},
            'EPHESIANS': {'name': 'Ephesians', 'chapters': 6},
            'PHILIPPIANS': {'name': 'Philippians', 'chapters': 4},
            'COLOSSIANS': {'name': 'Colossians', 'chapters': 4},
            '1 THESSALONIANS': {'name': '1 Thessalonians', 'chapters': 5},
            '2 THESSALONIANS': {'name': '2 Thessalonians', 'chapters': 3},
            '1 TIMOTHY': {'name': '1 Timothy', 'chapters': 6},
            '2 TIMOTHY': {'name': '2 Timothy', 'chapters': 4},
            'TITUS': {'name': 'Titus', 'chapters': 3},
            'PHILEMON': {'name': 'Philemon', 'chapters': 1},
            'HEBREWS': {'name': 'Hebrews', 'chapters': 13},
            'IḆRIM': {'name': 'Hebrews', 'chapters': 13},
            'JAMES': {'name': 'James', 'chapters': 5},
            'YA\'AQOḆ': {'name': 'James', 'chapters': 5},
            '1 PETER': {'name': '1 Peter', 'chapters': 5},
            '2 PETER': {'name': '2 Peter', 'chapters': 3},
            'KĔPHA ALEPH': {'name': '1 Peter', 'chapters': 5},
            'KĔPHA BETH': {'name': '2 Peter', 'chapters': 3},
            '1 JOHN': {'name': '1 John', 'chapters': 5},
            '2 JOHN': {'name': '2 John', 'chapters': 1},
            '3 JOHN': {'name': '3 John', 'chapters': 1},
            'JUDE': {'name': 'Jude', 'chapters': 1},
            'YAHUDAH': {'name': 'Jude', 'chapters': 1},
            'REVELATION': {'name': 'Revelation', 'chapters': 22},
            'ḤAZON': {'name': 'Revelation', 'chapters': 22}
        }
    
    def extract_nt_verses(self, start_page: int = 2169, num_pages: int = 50):
        """Extract NT verses with corrected logic"""
        
        print(f"📝 Extracting NT verses from page {start_page} ({num_pages} pages)...")
        
        verses = []
        current_book = None
        current_chapter = 1  # Start with chapter 1
        verse_buffer = []
        current_verse_num = None
        expecting_new_chapter = False
        
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
                            
                            # Check for book headers
                            book_found = False
                            line_upper = line.upper()
                            for header_name, book_info in self.nt_books.items():
                                if line_upper == header_name:
                                    # Save any pending verse
                                    if current_verse_num and verse_buffer and current_book:
                                        verse_text = ' '.join(verse_buffer).strip()
                                        if len(verse_text) > 5:
                                            verses.append({
                                                'book': current_book,
                                                'chapter': current_chapter,
                                                'verse': current_verse_num,
                                                'text': self._clean_verse_text(verse_text)
                                            })
                                    
                                    current_book = book_info['name']
                                    current_chapter = 1  # Always start with chapter 1
                                    current_verse_num = None
                                    verse_buffer = []
                                    expecting_new_chapter = False
                                    print(f"   📖 Found book: {current_book}")
                                    book_found = True
                                    break
                            
                            if book_found:
                                continue
                            
                            # Skip Hebrew book names and other headers
                            if (re.match(r'^[A-Z\s]+$', line_upper) and 
                                len(line) > 1 and 
                                line_upper not in self.nt_books):
                                continue
                            
                            # Check for chapter markers (look for isolated numbers that might be chapters)
                            if (current_book and 
                                re.match(r'^\d+$', line) and 
                                len(line) <= 2):
                                num = int(line)
                                
                                # Determine if this is a chapter or verse number
                                book_info = None
                                for header_name, info in self.nt_books.items():
                                    if info['name'] == current_book:
                                        book_info = info
                                        break
                                
                                if book_info:
                                    # If we're expecting a new chapter and this number is reasonable
                                    if (expecting_new_chapter and 
                                        1 <= num <= book_info['chapters']):
                                        # Save pending verse
                                        if current_verse_num and verse_buffer:
                                            verse_text = ' '.join(verse_buffer).strip()
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse_num,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        current_chapter = num
                                        current_verse_num = None
                                        verse_buffer = []
                                        expecting_new_chapter = False
                                        print(f"      📄 Chapter {current_chapter}")
                                        continue
                                    
                                    # Otherwise treat as verse number
                                    if 1 <= num <= 200:  # Reasonable verse range
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
                                        current_verse_num = num
                                        verse_buffer = []
                                        
                                        # Check if this might be the start of a new chapter
                                        if num == 1 and current_verse_num != 1:
                                            expecting_new_chapter = True
                                        
                                        continue
                            
                            # Collect verse text
                            if current_verse_num and current_book:
                                # Skip obvious non-text lines
                                if (not line.isdigit() and
                                    len(line) > 1 and
                                    not re.match(r'^[A-Z\s]+$', line) and
                                    not re.match(r'^\d{4}$', line)):  # Skip page numbers
                                    verse_buffer.append(line)
                
                # Save final verse if exists
                if current_verse_num and verse_buffer and current_book:
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
        
        # Show sample verses by book/chapter
        book_stats = {}
        for verse in verses:
            key = f"{verse['book']} {verse['chapter']}"
            if key not in book_stats:
                book_stats[key] = []
            book_stats[key].append(verse['verse'])
        
        for book_chapter in sorted(book_stats.keys())[:10]:
            verse_nums = sorted(book_stats[book_chapter])
            print(f"   📖 {book_chapter}: verses {verse_nums[0]}-{verse_nums[-1]} ({len(verse_nums)} verses)")
        
        return verses
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean and standardize verse text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove page numbers at end
        text = re.sub(r'\d+$', '', text).strip()
        
        # Apply divine name standardization
        text = re.sub(r'\{vWHY\}|\{HWHY\}|hWhY', 'YHWH', text)
        text = re.sub(r'ha\'YHWH', 'YHWH', text)
        
        return text
    
    async def save_nt_verses(self, verses: list):
        """Save NT verses to database"""
        
        if not verses:
            print("❌ No verses to save")
            return False
        
        print(f"\n💾 Saving {len(verses)} NT verses...")
        
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
                    'source': 'yah_scriptures_pdf_corrected',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                # Save verse (replace existing)
                await self.db.bible_verses.replace_one(
                    {'id': verse_doc['id']},
                    verse_doc,
                    upsert=True
                )
                
                books_created.add(verse['book'])
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} verses from {len(books_created)} books")
            print(f"   📚 Books: {', '.join(sorted(books_created))}")
            
            # Create book records
            await self._create_book_records(books_created)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving verses: {e}")
            return False
    
    async def _create_book_records(self, book_names: set):
        """Create book records for NT books"""
        
        print(f"\n📚 Creating book records...")
        
        nt_book_order = [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
            '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
            'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
            'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
            'Jude', 'Revelation'
        ]
        
        created_count = 0
        
        for book_name in book_names:
            # Get verse statistics for this book
            book_stats = await self.db.bible_verses.aggregate([
                {'$match': {'version': 'yah_scriptures', 'book': book_name}},
                {'$group': {
                    '_id': None,
                    'verse_count': {'$sum': 1},
                    'max_chapter': {'$max': '$chapter'}
                }}
            ]).to_list(length=1)
            
            if book_stats:
                stats = book_stats[0]
                order = nt_book_order.index(book_name) + 40 if book_name in nt_book_order else 999
                
                book_doc = {
                    'id': f"{book_name.lower().replace(' ', '_')}_book_yah_scriptures",
                    'name': book_name,
                    'testament': 'new',
                    'version': 'yah_scriptures',
                    'order': order,
                    'chapter_count': stats['max_chapter'],
                    'verse_count': stats['verse_count'],
                    'source': 'yah_scriptures_pdf_corrected',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                await self.db.bible_books.replace_one(
                    {'id': book_doc['id']},
                    book_doc,
                    upsert=True
                )
                
                created_count += 1
                print(f"   📖 {book_name}: {stats['verse_count']} verses, {stats['max_chapter']} chapters")
        
        print(f"   ✅ Created {created_count} book records")
    
    async def run_sample_extraction(self):
        """Run sample extraction to test the corrected logic"""
        
        print("🚀 Starting Corrected Sample New Testament Extraction")
        print("=" * 70)
        
        try:
            # Extract sample verses from 50 pages
            sample_verses = self.extract_nt_verses()
            
            if sample_verses:
                # Save to database
                success = await self.save_nt_verses(sample_verses)
                
                if success:
                    # Check results
                    total_yah = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                    nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                    
                    print(f"\n📊 FINAL RESULTS:")
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
    extractor = CorrectedNTExtractor()
    success = await extractor.run_sample_extraction()
    
    if success:
        print("\n🎉 Corrected sample extraction completed successfully!")
    else:
        print("\n❌ Corrected sample extraction failed")

if __name__ == "__main__":
    asyncio.run(main())