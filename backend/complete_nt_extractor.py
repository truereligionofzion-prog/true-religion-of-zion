#!/usr/bin/env python3
"""
Complete New Testament extractor for all books
"""

import pdfplumber
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class CompleteNTExtractor:
    """Extract complete New Testament from Yah Scriptures PDF"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # NT book order and expected chapters
        self.nt_books_info = {
            'Matthew': {'chapters': 28, 'order': 40},
            'Mark': {'chapters': 16, 'order': 41},
            'Luke': {'chapters': 24, 'order': 42},
            'John': {'chapters': 21, 'order': 43},
            'Acts': {'chapters': 28, 'order': 44},
            'Romans': {'chapters': 16, 'order': 45},
            '1 Corinthians': {'chapters': 16, 'order': 46},
            '2 Corinthians': {'chapters': 13, 'order': 47},
            'Galatians': {'chapters': 6, 'order': 48},
            'Ephesians': {'chapters': 6, 'order': 49},
            'Philippians': {'chapters': 4, 'order': 50},
            'Colossians': {'chapters': 4, 'order': 51},
            '1 Thessalonians': {'chapters': 5, 'order': 52},
            '2 Thessalonians': {'chapters': 3, 'order': 53},
            '1 Timothy': {'chapters': 6, 'order': 54},
            '2 Timothy': {'chapters': 4, 'order': 55},
            'Titus': {'chapters': 3, 'order': 56},
            'Philemon': {'chapters': 1, 'order': 57},
            'Hebrews': {'chapters': 13, 'order': 58},
            'James': {'chapters': 5, 'order': 59},
            '1 Peter': {'chapters': 5, 'order': 60},
            '2 Peter': {'chapters': 3, 'order': 61},
            '1 John': {'chapters': 5, 'order': 62},
            '2 John': {'chapters': 1, 'order': 63},
            '3 John': {'chapters': 1, 'order': 64},
            'Jude': {'chapters': 1, 'order': 65},
            'Revelation': {'chapters': 22, 'order': 66}
        }
        
        # Book header mappings from PDF
        self.book_headers = {
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
            'QORINTIYIM ALEPH': '1 Corinthians',
            '2 CORINTHIANS': '2 Corinthians',
            'QORINTIYIM BETH': '2 Corinthians',
            'GALATIANS': 'Galatians',
            'GALATIYIM': 'Galatians',
            'EPHESIANS': 'Ephesians',
            'EPHESIYIM': 'Ephesians',
            'PHILIPPIANS': 'Philippians',
            'PHILIPPIYIM': 'Philippians',
            'COLOSSIANS': 'Colossians',
            'QOLASIYIM': 'Colossians',
            '1 THESSALONIANS': '1 Thessalonians',
            'THESSALONIQIM ALEPH': '1 Thessalonians',
            '2 THESSALONIANS': '2 Thessalonians',
            'THESSALONIQIM BETH': '2 Thessalonians',
            '1 TIMOTHY': '1 Timothy',
            'TIMOTHEOS ALEPH': '1 Timothy',
            '2 TIMOTHY': '2 Timothy',
            'TIMOTHEOS BETH': '2 Timothy',
            'TITUS': 'Titus',
            'TITOS': 'Titus',
            'PHILEMON': 'Philemon',
            'PHILEMON': 'Philemon',
            'HEBREWS': 'Hebrews',
            'IḆRIM': 'Hebrews',
            'JAMES': 'James',
            'YA\'AQOḆ': 'James',
            '1 PETER': '1 Peter',
            'KĔPHA ALEPH': '1 Peter',
            '2 PETER': '2 Peter',
            'KĔPHA BETH': '2 Peter',
            '1 JOHN': '1 John',
            'YOḤANAN ALEPH': '1 John',
            '2 JOHN': '2 John',
            'YOḤANAN BETH': '2 John',
            '3 JOHN': '3 John',
            'YOḤANAN GIMEL': '3 John',
            'JUDE': 'Jude',
            'YAHUDAH': 'Jude',
            'REVELATION': 'Revelation',
            'ḤAZON': 'Revelation'
        }
    
    def extract_complete_nt(self, start_page: int = 2169, end_page: int = 2847):
        """Extract complete New Testament"""
        
        print(f"📖 Extracting complete NT from pages {start_page} to {end_page}...")
        
        verses = []
        current_book = None
        current_chapter = 1
        current_verse = None
        verse_text_buffer = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num in range(start_page - 1, min(end_page, len(pdf.pages))):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        lines = text.split('\n')
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Check for book headers
                            line_upper = line.upper()
                            if line_upper in self.book_headers:
                                book_name = self.book_headers[line_upper]
                                
                                # Only process if this is a new book
                                if current_book != book_name:
                                    # Save any pending verse
                                    if current_verse and verse_text_buffer and current_book:
                                        verse_text = ' '.join(verse_text_buffer).strip()
                                        if len(verse_text) > 5:
                                            verses.append({
                                                'book': current_book,
                                                'chapter': current_chapter,
                                                'verse': current_verse,
                                                'text': self._clean_verse_text(verse_text)
                                            })
                                    
                                    current_book = book_name
                                    current_chapter = 1
                                    current_verse = None
                                    verse_text_buffer = []
                                    print(f"   📖 Found: {book_name}")
                                continue
                            
                            # Skip Hebrew names, page numbers, etc.
                            if (re.match(r'^\d{4}$', line) or  # Page numbers
                                len(line) < 2):
                                continue
                            
                            # Process verses only if we're in a book
                            if current_book:
                                # Check if this is a number (verse or chapter)
                                if re.match(r'^\d+$', line):
                                    num = int(line)
                                    
                                    # Determine if it's a chapter or verse
                                    max_chapters = self.nt_books_info.get(current_book, {}).get('chapters', 50)
                                    
                                    # Chapter detection heuristics
                                    if (num == 1 and current_verse and current_verse > 10) or \
                                       (num == 2 and current_chapter == 1 and current_verse and current_verse > 15) or \
                                       (num <= max_chapters and current_verse and current_verse > 20):
                                        
                                        # Save pending verse before new chapter
                                        if current_verse and verse_text_buffer:
                                            verse_text = ' '.join(verse_text_buffer).strip()
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        current_chapter = num
                                        current_verse = None
                                        verse_text_buffer = []
                                        continue
                                    
                                    # Otherwise treat as verse
                                    if 1 <= num <= 200:
                                        # Save previous verse
                                        if current_verse and verse_text_buffer:
                                            verse_text = ' '.join(verse_text_buffer).strip()
                                            if len(verse_text) > 5:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': current_verse,
                                                    'text': self._clean_verse_text(verse_text)
                                                })
                                        
                                        current_verse = num
                                        verse_text_buffer = []
                                        continue
                                
                                # Collect verse text
                                if current_verse:
                                    # Skip all-caps headers and single words
                                    if (not re.match(r'^[A-Z\s]+$', line) and
                                        len(line.split()) > 1):
                                        verse_text_buffer.append(line)
                    
                    # Progress indicator
                    if (page_num - start_page + 2) % 50 == 0:
                        progress = page_num - start_page + 2
                        total = end_page - start_page + 1
                        print(f"   📊 Progress: {progress}/{total} pages, {len(verses)} verses")
                
                # Save final verse
                if current_verse and verse_text_buffer and current_book:
                    verse_text = ' '.join(verse_text_buffer).strip()
                    if len(verse_text) > 5:
                        verses.append({
                            'book': current_book,
                            'chapter': current_chapter,
                            'verse': current_verse,
                            'text': self._clean_verse_text(verse_text)
                        })
        
        except Exception as e:
            print(f"❌ Error extracting: {e}")
        
        print(f"\n📊 Extracted {len(verses)} total NT verses")
        
        # Show book summary
        book_counts = {}
        for verse in verses:
            book = verse['book']
            book_counts[book] = book_counts.get(book, 0) + 1
        
        for book in self.nt_books_info.keys():
            count = book_counts.get(book, 0)
            if count > 0:
                print(f"   📖 {book}: {count} verses")
        
        return verses
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean verse text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove page numbers at end
        text = re.sub(r'\d+$', '', text).strip()
        
        # Divine name standardization - convert various forms to YHWH
        text = re.sub(r'\{vWHY\}|\{HWHY\}|hWhY', 'YHWH', text)
        text = re.sub(r'ha\'YHWH', 'YHWH', text)
        
        return text
    
    async def save_complete_nt(self, verses: list):
        """Save complete NT to database"""
        
        if not verses:
            print("❌ No verses to save")
            return False
        
        print(f"\n💾 Saving complete NT ({len(verses)} verses)...")
        
        try:
            # Clear existing NT verses
            deleted_count = await self.db.bible_verses.delete_many({'version': 'yah_scriptures', 'testament': 'new'})
            print(f"   🗑️ Cleared {deleted_count.deleted_count} existing NT verses")
            
            # Insert new verses
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
                    'source': 'yah_scriptures_pdf_complete',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                await self.db.bible_verses.insert_one(verse_doc)
                books_created.add(verse['book'])
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} verses from {len(books_created)} NT books")
            
            # Create book records
            await self._create_nt_book_records(books_created)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False
    
    async def _create_nt_book_records(self, book_names: set):
        """Create book records for NT books"""
        
        print(f"\n📚 Creating NT book records...")
        
        for book_name in book_names:
            # Get book statistics
            stats_pipeline = [
                {'$match': {'version': 'yah_scriptures', 'book': book_name}},
                {'$group': {
                    '_id': None,
                    'verse_count': {'$sum': 1},
                    'max_chapter': {'$max': '$chapter'}
                }}
            ]
            
            stats_result = await self.db.bible_verses.aggregate(stats_pipeline).to_list(1)
            
            if stats_result:
                stats = stats_result[0]
                book_info = self.nt_books_info.get(book_name, {})
                
                book_doc = {
                    'id': f"{book_name.lower().replace(' ', '_')}_book_yah_scriptures",
                    'name': book_name,
                    'testament': 'new',
                    'version': 'yah_scriptures',
                    'order': book_info.get('order', 999),
                    'chapter_count': stats['max_chapter'],
                    'verse_count': stats['verse_count'],
                    'source': 'yah_scriptures_pdf_complete',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                await self.db.bible_books.replace_one(
                    {'id': book_doc['id']},
                    book_doc,
                    upsert=True
                )
                
                print(f"   📖 {book_name}: {stats['verse_count']} verses, {stats['max_chapter']} chapters")
    
    async def run_complete_extraction(self):
        """Run complete NT extraction"""
        
        print("🚀 STARTING COMPLETE NEW TESTAMENT EXTRACTION")
        print("=" * 80)
        
        try:
            # Extract all NT books
            all_verses = self.extract_complete_nt()
            
            if all_verses:
                # Save to database
                success = await self.save_complete_nt(all_verses)
                
                if success:
                    # Final statistics
                    total_yah = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                    nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                    old_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'old'})
                    apo_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'apocrypha'})
                    
                    print(f"\n🎉 COMPLETE YAH SCRIPTURES EXTRACTION RESULTS:")
                    print(f"   📖 Old Testament: {old_count} verses")
                    print(f"   📖 New Testament: {nt_count} verses")  
                    print(f"   📖 Apocrypha: {apo_count} verses")
                    print(f"   📖 TOTAL: {total_yah} verses")
                    
                    return True
                    
            else:
                print("❌ No verses extracted")
                
        except Exception as e:
            print(f"❌ Complete extraction failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        
        return False

async def main():
    extractor = CompleteNTExtractor()
    success = await extractor.run_complete_extraction()
    
    if success:
        print("\n✅ Complete New Testament extraction successful!")
        print("🎉 Yah Scriptures version is now complete!")
    else:
        print("\n❌ Complete New Testament extraction failed")

if __name__ == "__main__":
    asyncio.run(main())