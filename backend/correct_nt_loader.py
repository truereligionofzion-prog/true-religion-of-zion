#!/usr/bin/env python3
"""
Load correct New Testament from the provided text file
"""

import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class CorrectNTLoader:
    """Load correctly formatted NT from text file"""
    
    def __init__(self):
        self.text_file = '/app/yah_scriptures_correct.txt'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # NT book mappings
        self.nt_books = {
            'MATTHEW': 'Matthew',
            'MARK': 'Mark',
            'LUKE': 'Luke', 
            'JOHN': 'John',
            'ACTS': 'Acts',
            'ROMANS': 'Romans',
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
            'JAMES': 'James',
            '1 PETER': '1 Peter',
            '2 PETER': '2 Peter',
            '1 JOHN': '1 John',
            '2 JOHN': '2 John',
            '3 JOHN': '3 John',
            'JUDE': 'Jude',
            'REVELATION': 'Revelation'
        }
    
    def find_nt_start(self):
        """Find where New Testament starts in the text file"""
        
        print("🔍 Finding New Testament start in text file...")
        
        try:
            with open(self.text_file, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # Look for MATTHEW (the start of NT)
                    if line == 'MATTHEW':
                        # Check next few lines to confirm this is the NT section
                        file.seek(0)  # Reset file pointer
                        lines = file.readlines()
                        
                        # Look ahead to see if this is the right Matthew
                        for i in range(line_num, min(line_num + 10, len(lines))):
                            ahead_line = lines[i].strip()
                            if ahead_line.startswith('1 ') and 'genealogy' in ahead_line:
                                print(f"   📖 Found NT starting at line {line_num}")
                                return line_num
                        
        except Exception as e:
            print(f"❌ Error finding NT start: {e}")
        
        return None
    
    def extract_nt_from_text(self, start_line: int):
        """Extract NT verses from text file starting from given line"""
        
        print(f"📝 Extracting NT from line {start_line}...")
        
        verses = []
        current_book = None
        current_chapter = 1
        verse_buffer = []
        current_verse_num = None
        
        try:
            with open(self.text_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
                # Start from the NT beginning
                for i in range(start_line - 1, len(lines)):
                    line = lines[i].strip()
                    
                    if not line:
                        continue
                    
                    # Check for book headers
                    if line in self.nt_books:
                        # Save pending verse before switching books
                        if current_verse_num and verse_buffer and current_book:
                            verse_text = ' '.join(verse_buffer).strip()
                            if len(verse_text) > 5:
                                verses.append({
                                    'book': current_book,
                                    'chapter': current_chapter,
                                    'verse': current_verse_num,
                                    'text': self._clean_verse_text(verse_text)
                                })
                        
                        current_book = self.nt_books[line]
                        current_chapter = 1
                        current_verse_num = None
                        verse_buffer = []
                        print(f"   📖 Found book: {current_book}")
                        continue
                    
                    # Skip Hebrew names, page numbers, etc.
                    if (re.match(r'^\d{4}$', line) or  # Page numbers like 2168
                        line in ['MATTIHYAHU', 'MARQOS', 'LUQAS', 'YOḤANAN'] or  # Hebrew names
                        re.match(r'^[^\w\s]+\s*\w+$', line)):  # Hebrew text patterns
                        continue
                    
                    # Process lines only if we're in a book
                    if current_book:
                        # Check for verse numbers at start of line
                        verse_match = re.match(r'^(\d+)\s+(.+)', line)
                        if verse_match:
                            # Save previous verse
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
                            verse_num = int(verse_match.group(1))
                            verse_text = verse_match.group(2).strip()
                            
                            # Check for chapter transitions
                            if verse_num == 1 and current_verse_num and current_verse_num > 5:
                                current_chapter += 1
                            
                            current_verse_num = verse_num
                            verse_buffer = [verse_text] if verse_text else []
                            continue
                        
                        # Add continuation text to current verse
                        if current_verse_num and line:
                            # Skip obvious headers and single words
                            if (len(line.split()) > 1 and 
                                not re.match(r'^[A-Z\s]+$', line)):
                                verse_buffer.append(line)
                
                # Save final verse
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
        
        print(f"\n📊 Extracted {len(verses)} NT verses")
        
        # Show book summary
        book_counts = {}
        for verse in verses:
            book = verse['book']
            book_counts[book] = book_counts.get(book, 0) + 1
        
        for book_name in self.nt_books.values():
            count = book_counts.get(book_name, 0)
            if count > 0:
                print(f"   📖 {book_name}: {count} verses")
        
        return verses
    
    def _clean_verse_text(self, text: str) -> str:
        """Clean verse text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Divine name standardization
        text = re.sub(r'\{vWHY\}|\{HWHY\}|hWhY', 'YHWH', text)
        text = re.sub(r'ha\'YHWH', 'YHWH', text)
        
        return text
    
    async def save_correct_nt(self, verses: list):
        """Save correct NT verses to database"""
        
        if not verses:
            print("❌ No verses to save")
            return False
        
        print(f"\n💾 Saving correct NT ({len(verses)} verses)...")
        
        try:
            # Clear existing NT verses
            deleted_count = await self.db.bible_verses.delete_many({'version': 'yah_scriptures', 'testament': 'new'})
            print(f"   🗑️ Cleared {deleted_count.deleted_count} existing incorrect NT verses")
            
            # Insert correct verses
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
                    'source': 'yah_scriptures_correct_text_file',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                await self.db.bible_verses.insert_one(verse_doc)
                books_created.add(verse['book'])
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} correct verses from {len(books_created)} NT books")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving: {e}")
            return False
    
    async def run_correct_loading(self):
        """Run correct NT loading"""
        
        print("🚀 LOADING CORRECT NEW TESTAMENT")
        print("=" * 60)
        
        try:
            # Find NT start
            nt_start = self.find_nt_start()
            
            if nt_start:
                # Extract correct verses
                verses = self.extract_nt_from_text(nt_start)
                
                if verses:
                    # Save to database
                    success = await self.save_correct_nt(verses)
                    
                    if success:
                        # Final statistics
                        total_yah = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                        nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                        old_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'old'})
                        apo_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'apocrypha'})
                        
                        print(f"\n🎉 CORRECTED YAH SCRIPTURES RESULTS:")
                        print(f"   📖 Old Testament: {old_count} verses")
                        print(f"   📖 New Testament: {nt_count} verses (CORRECTED)")
                        print(f"   📖 Apocrypha: {apo_count} verses")
                        print(f"   📖 TOTAL: {total_yah} verses")
                        
                        return True
                        
                else:
                    print("❌ No verses extracted")
                    
            else:
                print("❌ Could not find NT start")
                
        except Exception as e:
            print(f"❌ Correct loading failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        
        return False

async def main():
    loader = CorrectNTLoader()
    success = await loader.run_correct_loading()
    
    if success:
        print("\n✅ Correct New Testament loading successful!")
        print("🎉 Yah Scriptures now has correct verse numbering!")
    else:
        print("\n❌ Correct New Testament loading failed")

if __name__ == "__main__":
    asyncio.run(main())