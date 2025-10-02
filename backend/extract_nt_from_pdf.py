#!/usr/bin/env python3
"""
Extract New Testament from pages 2200-2847 of Yah Scriptures PDF
"""

import PyPDF2
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class YahScripturesNTExtractor:
    """Extract NT from known page range"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Book name mappings found in the PDF
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
    
    def extract_nt_verses(self, start_page=2200, end_page=2847):
        """Extract NT verses from specified page range"""
        
        print(f"📖 Extracting NT verses from pages {start_page}-{end_page}...")
        
        verses = []
        current_book = None
        current_chapter = None
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(start_page - 1, min(end_page, len(pdf_reader.pages))):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            lines = text.split('\n')
                            
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Check for book headers
                                book_found = False
                                for pdf_name, standard_name in self.book_mappings.items():
                                    if line.upper() == pdf_name.upper():
                                        current_book = standard_name
                                        current_chapter = None
                                        print(f"   📖 Found: {standard_name}")
                                        book_found = True
                                        break
                                
                                if book_found:
                                    continue
                                
                                # Check for chapter numbers (digits only on their own line)
                                if current_book and re.match(r'^\d+$', line) and len(line) <= 2:
                                    try:
                                        chapter_num = int(line)
                                        if 1 <= chapter_num <= 150:  # Reasonable range
                                            current_chapter = chapter_num
                                            continue
                                    except:
                                        pass
                                
                                # Extract verses (number + text)
                                if current_book and current_chapter:
                                    verse_match = re.match(r'^(\d+)\s+(.+)', line)
                                    if verse_match:
                                        try:
                                            verse_num = int(verse_match.group(1))
                                            verse_text = verse_match.group(2).strip()
                                            
                                            # Clean up the text
                                            verse_text = self._clean_verse_text(verse_text)
                                            
                                            if len(verse_text) > 5 and verse_num <= 200:
                                                verses.append({
                                                    'book': current_book,
                                                    'chapter': current_chapter,
                                                    'verse': verse_num,
                                                    'text': verse_text
                                                })
                                                
                                                # Show progress for first few verses
                                                if len(verses) <= 20:
                                                    print(f"      {current_book} {current_chapter}:{verse_num} {verse_text[:60]}...")
                                        
                                        except:
                                            pass
                        
                        # Progress indicator
                        if (page_num - start_page + 2) % 50 == 0:
                            progress = page_num - start_page + 2
                            total = end_page - start_page + 1
                            print(f"   📊 Progress: {progress}/{total} pages, {len(verses)} verses found")
                    
                    except Exception as e:
                        # Skip problematic pages
                        continue
        
        except Exception as e:
            print(f"❌ Error extracting verses: {e}")
        
        return verses
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean verse text"""
        # Remove extra spaces and clean formatting
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove page numbers and artifacts
        text = re.sub(r'\d+$', '', text).strip()
        
        return text
    
    async def save_nt_verses(self, verses: list):
        """Save NT verses to database"""
        
        if not verses:
            print("❌ No NT verses to save")
            return False
        
        print(f"\n💾 Saving {len(verses)} NT verses to database...")
        
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
                    'source': 'yah_scriptures_pdf',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                # Save verse
                await self.db.bible_verses.replace_one(
                    {'id': verse_doc['id']},
                    verse_doc,
                    upsert=True
                )
                
                books_created.add(verse['book'])
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} verses from {len(books_created)} books")
            print(f"   📚 NT Books: {', '.join(sorted(books_created))}")
            
            # Create book records for NT books
            await self._create_nt_book_records(books_created)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving verses: {e}")
            return False
    
    async def _create_nt_book_records(self, book_names: set):
        """Create book records for NT books"""
        
        print(f"\n📚 Creating book records for {len(book_names)} NT books...")
        
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
                    'source': 'yah_scriptures_pdf',
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
    
    async def run_nt_extraction(self):
        """Run complete NT extraction"""
        
        print("🚀 Starting Yah Scriptures New Testament Extraction")
        print("=" * 60)
        
        try:
            # Extract verses
            nt_verses = self.extract_nt_verses()
            
            if nt_verses:
                # Save to database
                success = await self.save_nt_verses(nt_verses)
                
                if success:
                    # Check final stats
                    total_verses = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                    nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                    nt_books = await self.db.bible_books.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                    
                    print(f"\n📊 FINAL RESULTS:")
                    print(f"   📖 Total Yah Scriptures verses: {total_verses}")
                    print(f"   📖 New Testament books: {nt_books}")
                    print(f"   📖 New Testament verses: {nt_count}")
                    
                    return True
            
            else:
                print("❌ No NT verses extracted")
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        
        return False

async def main():
    extractor = YahScripturesNTExtractor()
    success = await extractor.run_nt_extraction()
    
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: New Testament extraction")

if __name__ == "__main__":
    asyncio.run(main())