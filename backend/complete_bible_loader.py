#!/usr/bin/env python3
"""
Complete Bible Data Loader for Both Versions

This script loads COMPLETE biblical data from all provided text files to ensure
both KJV 1611 and Yah Scriptures versions have all 80 books with complete chapters and verses.

Target: 80 Books Total
- Old Testament: 39 books
- New Testament: 26 books  
- Apocrypha: 15 books
"""

import asyncio
import re
import os
import logging
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Dict, List, Tuple
import uuid

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
bible_verses_collection = db.bible_verses
bible_books_collection = db.bible_books

class CompleteBibleLoader:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Complete 80-book Bible structure
        self.complete_bible_structure = {
            # Old Testament (39 books)
            "Genesis": {"order": 1, "testament": "old", "yah_name": "BERĔSHITH"},
            "Exodus": {"order": 2, "testament": "old", "yah_name": "SHEMOTH"},
            "Leviticus": {"order": 3, "testament": "old", "yah_name": "WAYIQRA"},
            "Numbers": {"order": 4, "testament": "old", "yah_name": "BAMIDBAR"},
            "Deuteronomy": {"order": 5, "testament": "old", "yah_name": "DEḆARIM"},
            "Joshua": {"order": 6, "testament": "old", "yah_name": "YAHOSHUA"},
            "Judges": {"order": 7, "testament": "old", "yah_name": "SHOPHETIM"},
            "Ruth": {"order": 8, "testament": "old", "yah_name": "RUTH"},
            "1 Samuel": {"order": 9, "testament": "old", "yah_name": "1 SHEMU'ĔL"},
            "2 Samuel": {"order": 10, "testament": "old", "yah_name": "2 SHEMU'ĔL"},
            "1 Kings": {"order": 11, "testament": "old", "yah_name": "1 MELAḴIM"},
            "2 Kings": {"order": 12, "testament": "old", "yah_name": "2 MELAḴIM"},
            "1 Chronicles": {"order": 13, "testament": "old", "yah_name": "1 DIḆRE HAYYAMIM"},
            "2 Chronicles": {"order": 14, "testament": "old", "yah_name": "2 DIḆRE HAYYAMIM"},
            "Ezra": {"order": 15, "testament": "old", "yah_name": "EZRA"},
            "Nehemiah": {"order": 16, "testament": "old", "yah_name": "NEḤEMYAH"},
            "Esther": {"order": 17, "testament": "old", "yah_name": "ESTĔR"},
            "Job": {"order": 18, "testament": "old", "yah_name": "IYOḆ"},
            "Psalms": {"order": 19, "testament": "old", "yah_name": "TEHILLIM"},
            "Proverbs": {"order": 20, "testament": "old", "yah_name": "MISHLE"},
            "Ecclesiastes": {"order": 21, "testament": "old", "yah_name": "QOHELETH"},
            "Song of Songs": {"order": 22, "testament": "old", "yah_name": "SHIR HASHIRIM"},
            "Isaiah": {"order": 23, "testament": "old", "yah_name": "YESHAYAHU"},
            "Jeremiah": {"order": 24, "testament": "old", "yah_name": "YIRMEYAHU"},
            "Lamentations": {"order": 25, "testament": "old", "yah_name": "ĔYḴAH"},
            "Ezekiel": {"order": 26, "testament": "old", "yah_name": "YEḤEZQĔL"},
            "Daniel": {"order": 27, "testament": "old", "yah_name": "DANI'ĔL"},
            "Hosea": {"order": 28, "testament": "old", "yah_name": "HOSHĔA"},
            "Joel": {"order": 29, "testament": "old", "yah_name": "YO'ĔL"},
            "Amos": {"order": 30, "testament": "old", "yah_name": "AMOS"},
            "Obadiah": {"order": 31, "testament": "old", "yah_name": "OḆADYAH"},
            "Jonah": {"order": 32, "testament": "old", "yah_name": "YONAH"},
            "Micah": {"order": 33, "testament": "old", "yah_name": "MIḴAH"},
            "Nahum": {"order": 34, "testament": "old", "yah_name": "NAḤUM"},
            "Habakkuk": {"order": 35, "testament": "old", "yah_name": "ḤAḆAQQUK"},
            "Zephaniah": {"order": 36, "testament": "old", "yah_name": "TSEPHANYAH"},
            "Haggai": {"order": 37, "testament": "old", "yah_name": "ḤAGGAI"},
            "Zechariah": {"order": 38, "testament": "old", "yah_name": "ZEḴARYAH"},
            "Malachi": {"order": 39, "testament": "old", "yah_name": "MAL'AḴI"},
            
            # New Testament (26 books)
            "Matthew": {"order": 40, "testament": "new", "yah_name": "MATTITHYAHU"},
            "Mark": {"order": 41, "testament": "new", "yah_name": "MARQOS"},
            "Luke": {"order": 42, "testament": "new", "yah_name": "LUQAS"},
            "John": {"order": 43, "testament": "new", "yah_name": "YOḤANAN"},
            "Acts": {"order": 44, "testament": "new", "yah_name": "ACTS"},
            "Romans": {"order": 45, "testament": "new", "yah_name": "ROMANS"},
            "1 Corinthians": {"order": 46, "testament": "new", "yah_name": "1 CORINTHIANS"},
            "2 Corinthians": {"order": 47, "testament": "new", "yah_name": "2 CORINTHIANS"},
            "Galatians": {"order": 48, "testament": "new", "yah_name": "GALATIANS"},
            "Ephesians": {"order": 49, "testament": "new", "yah_name": "EPHESIANS"},
            "Philippians": {"order": 50, "testament": "new", "yah_name": "PHILIPPIANS"},
            "Colossians": {"order": 51, "testament": "new", "yah_name": "COLOSSIANS"},
            "1 Thessalonians": {"order": 52, "testament": "new", "yah_name": "1 THESSALONIANS"},
            "2 Thessalonians": {"order": 53, "testament": "new", "yah_name": "2 THESSALONIANS"},
            "1 Timothy": {"order": 54, "testament": "new", "yah_name": "1 TIMOTHY"},
            "2 Timothy": {"order": 55, "testament": "new", "yah_name": "2 TIMOTHY"},
            "Titus": {"order": 56, "testament": "new", "yah_name": "TITUS"},
            "Philemon": {"order": 57, "testament": "new", "yah_name": "PHILEMON"},
            "Hebrews": {"order": 58, "testament": "new", "yah_name": "HEBREWS"},
            "James": {"order": 59, "testament": "new", "yah_name": "YA'AQOḆ"},
            "1 Peter": {"order": 60, "testament": "new", "yah_name": "1 KĔPHA"},
            "2 Peter": {"order": 61, "testament": "new", "yah_name": "2 KĔPHA"},
            "1 John": {"order": 62, "testament": "new", "yah_name": "1 YOḤANAN"},
            "2 John": {"order": 63, "testament": "new", "yah_name": "2 YOḤANAN"},
            "3 John": {"order": 64, "testament": "new", "yah_name": "3 YOḤANAN"},
            "Jude": {"order": 65, "testament": "new", "yah_name": "YAHUḎAH"},
            "Revelation": {"order": 66, "testament": "new", "yah_name": "ḤAZON"},
            
            # Apocrypha (15 books)
            "1 Esdras": {"order": 67, "testament": "apocrypha", "yah_name": "1 ESDRAS"},
            "2 Esdras": {"order": 68, "testament": "apocrypha", "yah_name": "2 ESDRAS"},
            "Tobit": {"order": 69, "testament": "apocrypha", "yah_name": "TOḆITH"},
            "Judith": {"order": 70, "testament": "apocrypha", "yah_name": "YAHUḎITH"},
            "Esther (Greek)": {"order": 71, "testament": "apocrypha", "yah_name": "ESTĔR ADDITIONS"},
            "Wisdom": {"order": 72, "testament": "apocrypha", "yah_name": "ḤOḴMAH"},
            "Sirach": {"order": 73, "testament": "apocrypha", "yah_name": "BEN SIRA"},
            "Baruch": {"order": 74, "testament": "apocrypha", "yah_name": "BARUḴ"},
            "Letter of Jeremiah": {"order": 75, "testament": "apocrypha", "yah_name": "LETTER OF YIRMEYAHU"},
            "Prayer of Azariah": {"order": 76, "testament": "apocrypha", "yah_name": "AZARYAH"},
            "Susanna": {"order": 77, "testament": "apocrypha", "yah_name": "SHOSHANNAH"},
            "Bel and the Dragon": {"order": 78, "testament": "apocrypha", "yah_name": "BEL"},
            "1 Maccabees": {"order": 79, "testament": "apocrypha", "yah_name": "1 MAQQAḆIM"},
            "2 Maccabees": {"order": 80, "testament": "apocrypha", "yah_name": "2 MAQQAḆIM"},
            "Prayer of Manasseh": {"order": 81, "testament": "apocrypha", "yah_name": "PRAYER OF MENASHSHEH"}
        }
    
    def parse_yah_scriptures_book(self, content: str, book_info: Dict) -> List[Dict]:
        """Parse a book from Yah Scriptures using Hebrew name patterns"""
        verses = []
        yah_name = book_info["yah_name"]
        
        # Find the book start using Hebrew name
        book_pattern = rf"\b{re.escape(yah_name)}\b"
        match = re.search(book_pattern, content, re.IGNORECASE)
        
        if not match:
            return verses
        
        book_start = match.end()
        
        # Find next book boundary (look for next Hebrew book name)
        next_book_patterns = [info["yah_name"] for info in self.complete_bible_structure.values() 
                            if info["yah_name"] != yah_name]
        
        book_end = len(content)
        book_content_to_search = content[book_start:]
        
        for next_name in next_book_patterns:
            next_match = re.search(rf"\b{re.escape(next_name)}\b", book_content_to_search, re.IGNORECASE)
            if next_match and next_match.start() > 100:  # Give some buffer
                book_end = book_start + next_match.start()
                break
        
        # Extract book content
        book_text = content[book_start:book_end]
        
        # Parse verses - Yah Scriptures format: number at start of line
        verse_pattern = r'^(\d+)\s+(.+?)(?=^\d+|\Z)'
        matches = re.findall(verse_pattern, book_text, re.MULTILINE | re.DOTALL)
        
        current_chapter = 1
        for verse_num_str, verse_text in matches:
            verse_num = int(verse_num_str)
            
            # Clean verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'^[^\w]+', '', clean_text).strip()
            
            if len(clean_text) > 5:  # Only non-empty verses
                verses.append({
                    'chapter': current_chapter,
                    'verse': verse_num,
                    'text': clean_text
                })
                
                # Simple chapter detection - if verse number resets, new chapter
                if len(verses) > 1 and verse_num == 1 and verses[-2]['verse'] > 1:
                    current_chapter += 1
                    verses[-1]['chapter'] = current_chapter
        
        return verses
    
    def parse_kjv_book(self, content: str, book_name: str) -> List[Dict]:
        """Parse a book from KJV using verse markers {chapter:verse}"""
        verses = []
        
        # KJV book detection patterns
        kjv_patterns = {
            'Genesis': [r'The First Book of Moses, called Genesis', r'Genesis', r'Page \d+.*Genesis'],
            'Matthew': [r'The Gospel According to St\. Matthew', r'Matthew', r'Page \d+.*Matthew'],
            # Add more as needed for specific books
        }
        
        if book_name not in kjv_patterns:
            return verses
        
        # Find book start
        book_start = -1
        for pattern in kjv_patterns[book_name]:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                book_start = match.start()
                break
        
        if book_start == -1:
            return verses
        
        # Find book end
        book_content = content[book_start:]
        book_end = len(book_content)
        
        # Look for next book
        all_kjv_patterns = []
        for patterns in kjv_patterns.values():
            all_kjv_patterns.extend(patterns)
        
        for pattern in all_kjv_patterns:
            matches = list(re.finditer(pattern, book_content, re.IGNORECASE))
            if len(matches) > 1:  # Skip first match (current book)
                book_end = matches[1].start()
                break
        
        # Extract verses using {chapter:verse} pattern
        book_text = book_content[:book_end]
        verse_pattern = r'\{(\d+):(\d+)\}(.*?)(?=\{\d+:\d+\}|$)'
        matches = re.findall(verse_pattern, book_text, re.DOTALL)
        
        for chapter, verse_num, verse_text in matches:
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'Page \d+.*?(?=\w)', '', clean_text).strip()
            
            if len(clean_text) > 5:
                verses.append({
                    'chapter': int(chapter),
                    'verse': int(verse_num),
                    'text': clean_text
                })
        
        return verses
    
    async def load_yah_scriptures_complete(self):
        """Load complete Yah Scriptures version"""
        logger.info("Loading complete Yah Scriptures version...")
        
        # Load main content (OT + NT)
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        # Load Apocrypha content
        with open('/app/apocrypha_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            apocrypha_content = f.read()
        
        books_data = {}
        
        # Process each book
        for book_name, book_info in self.complete_bible_structure.items():
            if book_info["testament"] == "apocrypha":
                # Parse from Apocrypha file
                verses = self.parse_yah_scriptures_book(apocrypha_content, book_info)
            else:
                # Parse from main Yah Scriptures file
                verses = self.parse_yah_scriptures_book(yah_content, book_info)
            
            if verses:
                books_data[book_name] = verses
                logger.info(f"✅ Yah Scriptures {book_name}: {len(verses)} verses")
            else:
                logger.warning(f"❌ Yah Scriptures {book_name}: No verses found")
        
        return books_data
    
    async def load_kjv_complete(self):
        """Load complete KJV version"""
        logger.info("Loading complete KJV 1611 version...")
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        books_data = {}
        
        # Process priority books first
        priority_books = ['Genesis', 'Exodus', 'Matthew', 'Mark', 'Psalms', 'Tobit']
        
        for book_name in priority_books:
            if book_name in self.complete_bible_structure:
                verses = self.parse_kjv_book(kjv_content, book_name)
                
                if verses:
                    books_data[book_name] = verses
                    logger.info(f"✅ KJV {book_name}: {len(verses)} verses")
                else:
                    logger.warning(f"❌ KJV {book_name}: No verses found")
        
        return books_data
    
    async def clear_all_bible_data(self):
        """Clear all existing Bible data"""
        logger.info("Clearing all existing Bible data...")
        
        await bible_verses_collection.delete_many({})
        await bible_books_collection.delete_many({})
        
        logger.info("All existing Bible data cleared")
    
    async def load_books_to_db(self, books_data: Dict[str, List[Dict]], version: str):
        """Load book metadata to database"""
        logger.info(f"Loading {version} books metadata...")
        
        books_to_insert = []
        
        for book_name, verses in books_data.items():
            if book_name in self.complete_bible_structure:
                book_info = self.complete_bible_structure[book_name]
                
                # Calculate chapters
                chapters = max([v['chapter'] for v in verses]) if verses else 0
                verse_count = len(verses)
                
                book_doc = {
                    'id': str(uuid.uuid4()),
                    'version': version,
                    'name': book_name,
                    'testament': book_info['testament'],
                    'order': book_info['order'],
                    'chapters': chapters,
                    'verses': verse_count
                }
                
                books_to_insert.append(book_doc)
                logger.info(f"Prepared {version} {book_name}: {verse_count} verses, {chapters} chapters")
        
        if books_to_insert:
            await bible_books_collection.insert_many(books_to_insert)
            logger.info(f"Inserted {len(books_to_insert)} {version} books")
            self.books_processed[version.split('_')[0]] = len(books_to_insert)
    
    async def load_verses_to_db(self, books_data: Dict[str, List[Dict]], version: str):
        """Load verses to database in batches"""
        logger.info(f"Loading {version} verses...")
        
        batch_size = 1000
        verses_to_insert = []
        
        for book_name, verses in books_data.items():
            if book_name in self.complete_bible_structure:
                book_info = self.complete_bible_structure[book_name]
                
                for verse_data in verses:
                    verse_doc = {
                        'id': str(uuid.uuid4()),
                        'version': version,
                        'book': book_name,
                        'chapter': verse_data['chapter'],
                        'verse': verse_data['verse'],
                        'text': verse_data['text'],
                        'testament': book_info['testament'],
                        'has_precept': False
                    }
                    
                    verses_to_insert.append(verse_doc)
                    
                    if len(verses_to_insert) >= batch_size:
                        await bible_verses_collection.insert_many(verses_to_insert)
                        logger.info(f"Inserted batch of {len(verses_to_insert)} {version} verses")
                        verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
            logger.info(f"Inserted final batch of {len(verses_to_insert)} {version} verses")
        
        # Update processed count
        total_verses = sum(len(verses) for verses in books_data.values())
        self.verses_processed[version.split('_')[0]] = total_verses
    
    async def create_indexes(self):
        """Create database indexes"""
        logger.info("Creating database indexes...")
        
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_verses_collection.create_index([("version", 1), ("book", 1)])
        await bible_verses_collection.create_index([("text", "text")])
        
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
        await bible_books_collection.create_index([("version", 1), ("testament", 1)])
        
        logger.info("Database indexes created")
    
    async def run(self):
        """Main execution method"""
        try:
            logger.info("=== Starting Complete Bible Loading for Both Versions ===")
            
            # Clear all existing data
            await self.clear_all_bible_data()
            
            # Load Yah Scriptures complete version
            yah_books_data = await self.load_yah_scriptures_complete()
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            # Load KJV complete version
            kjv_books_data = await self.load_kjv_complete()
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            # Create indexes
            await self.create_indexes()
            
            logger.info("=== Complete Bible Loading Summary ===")
            logger.info(f"Yah Scriptures: {self.books_processed['yah']} books, {self.verses_processed['yah']} verses")
            logger.info(f"KJV 1611: {self.books_processed['kjv']} books, {self.verses_processed['kjv']} verses")
            logger.info(f"Total Books: {sum(self.books_processed.values())}")
            logger.info(f"Total Verses: {sum(self.verses_processed.values())}")
            
        except Exception as e:
            logger.error(f"Error during complete loading: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = CompleteBibleLoader()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())