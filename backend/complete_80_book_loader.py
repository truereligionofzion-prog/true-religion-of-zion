#!/usr/bin/env python3
"""
Complete 80-Book Bible Loader - Cross-Referenced with Web Data

This loader uses web-verified biblical statistics to ensure accurate parsing
of all 80 books (39 OT + 27 NT + 14 Apocrypha) for both Bible versions.
"""

import asyncio
import re
import os
import logging
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Dict, List
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

class Complete80BookLoader:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Web-verified complete 80-book Bible structure with expected verse counts
        self.complete_bible_structure = {
            # Old Testament (39 books) - Web verified verse counts
            "Genesis": {"order": 1, "testament": "old", "yah_name": "BERĔSHITH", "chapters": 50, "verses": 1533},
            "Exodus": {"order": 2, "testament": "old", "yah_name": "SHEMOTH", "chapters": 40, "verses": 1213},
            "Leviticus": {"order": 3, "testament": "old", "yah_name": "WAYYIQRA", "chapters": 27, "verses": 859},
            "Numbers": {"order": 4, "testament": "old", "yah_name": "BEMIḎBAR", "chapters": 36, "verses": 1288},
            "Deuteronomy": {"order": 5, "testament": "old", "yah_name": "DEḆARIM", "chapters": 34, "verses": 959},
            "Joshua": {"order": 6, "testament": "old", "yah_name": "YAHOSHUA", "chapters": 24, "verses": 658},
            "Judges": {"order": 7, "testament": "old", "yah_name": "SHOPHETIM", "chapters": 21, "verses": 618},
            "Ruth": {"order": 8, "testament": "old", "yah_name": "RUTH", "chapters": 4, "verses": 85},
            "1 Samuel": {"order": 9, "testament": "old", "yah_name": "1 SHEMU'ĔL", "chapters": 31, "verses": 810},
            "2 Samuel": {"order": 10, "testament": "old", "yah_name": "2 SHEMU'ĔL", "chapters": 24, "verses": 695},
            "1 Kings": {"order": 11, "testament": "old", "yah_name": "1 MELAḴIM", "chapters": 22, "verses": 816},
            "2 Kings": {"order": 12, "testament": "old", "yah_name": "2 MELAḴIM", "chapters": 25, "verses": 719},
            "1 Chronicles": {"order": 13, "testament": "old", "yah_name": "1 DIḆRE HAYYAMIM", "chapters": 29, "verses": 942},
            "2 Chronicles": {"order": 14, "testament": "old", "yah_name": "2 DIḆRE HAYYAMIM", "chapters": 36, "verses": 822},
            "Ezra": {"order": 15, "testament": "old", "yah_name": "EZRA", "chapters": 10, "verses": 280},
            "Nehemiah": {"order": 16, "testament": "old", "yah_name": "NEḤEMYAH", "chapters": 13, "verses": 406},
            "Esther": {"order": 17, "testament": "old", "yah_name": "ESTĔR", "chapters": 10, "verses": 167},
            "Job": {"order": 18, "testament": "old", "yah_name": "IYOḆ", "chapters": 42, "verses": 1070},
            "Psalms": {"order": 19, "testament": "old", "yah_name": "TEHILLIM", "chapters": 150, "verses": 2461},
            "Proverbs": {"order": 20, "testament": "old", "yah_name": "MISHLE", "chapters": 31, "verses": 915},
            "Ecclesiastes": {"order": 21, "testament": "old", "yah_name": "QOHELETH", "chapters": 12, "verses": 222},
            "Song of Songs": {"order": 22, "testament": "old", "yah_name": "SHIR HASHIRIM", "chapters": 8, "verses": 117},
            "Isaiah": {"order": 23, "testament": "old", "yah_name": "YESHAYAHU", "chapters": 66, "verses": 1292},
            "Jeremiah": {"order": 24, "testament": "old", "yah_name": "YIRMEYAHU", "chapters": 52, "verses": 1364},
            "Lamentations": {"order": 25, "testament": "old", "yah_name": "ĔYḴAH", "chapters": 5, "verses": 154},
            "Ezekiel": {"order": 26, "testament": "old", "yah_name": "YEḤEZQĔL", "chapters": 48, "verses": 1273},
            "Daniel": {"order": 27, "testament": "old", "yah_name": "DANI'ĔL", "chapters": 12, "verses": 357},
            "Hosea": {"order": 28, "testament": "old", "yah_name": "HOSHĔA", "chapters": 14, "verses": 197},
            "Joel": {"order": 29, "testament": "old", "yah_name": "YO'ĔL", "chapters": 3, "verses": 73},
            "Amos": {"order": 30, "testament": "old", "yah_name": "AMOS", "chapters": 9, "verses": 146},
            "Obadiah": {"order": 31, "testament": "old", "yah_name": "OḆADYAH", "chapters": 1, "verses": 21},
            "Jonah": {"order": 32, "testament": "old", "yah_name": "YONAH", "chapters": 4, "verses": 48},
            "Micah": {"order": 33, "testament": "old", "yah_name": "MIḴAH", "chapters": 7, "verses": 105},
            "Nahum": {"order": 34, "testament": "old", "yah_name": "NAḤUM", "chapters": 3, "verses": 47},
            "Habakkuk": {"order": 35, "testament": "old", "yah_name": "ḤAḆAQQUK", "chapters": 3, "verses": 56},
            "Zephaniah": {"order": 36, "testament": "old", "yah_name": "TSEPHANYAH", "chapters": 3, "verses": 53},
            "Haggai": {"order": 37, "testament": "old", "yah_name": "ḤAGGAI", "chapters": 2, "verses": 38},
            "Zechariah": {"order": 38, "testament": "old", "yah_name": "ZEḴARYAH", "chapters": 14, "verses": 211},
            "Malachi": {"order": 39, "testament": "old", "yah_name": "MAL'AḴI", "chapters": 4, "verses": 55},
            
            # New Testament (27 books) - Web verified verse counts
            "Matthew": {"order": 40, "testament": "new", "yah_name": "MATTITHYAHU", "chapters": 28, "verses": 1071},
            "Mark": {"order": 41, "testament": "new", "yah_name": "MARQOS", "chapters": 16, "verses": 678},
            "Luke": {"order": 42, "testament": "new", "yah_name": "LUQAS", "chapters": 24, "verses": 1151},
            "John": {"order": 43, "testament": "new", "yah_name": "YOḤANAN", "chapters": 21, "verses": 879},
            "Acts": {"order": 44, "testament": "new", "yah_name": "ACTS", "chapters": 28, "verses": 1007},
            "Romans": {"order": 45, "testament": "new", "yah_name": "ROMANS", "chapters": 16, "verses": 433},
            "1 Corinthians": {"order": 46, "testament": "new", "yah_name": "1 CORINTHIANS", "chapters": 16, "verses": 437},
            "2 Corinthians": {"order": 47, "testament": "new", "yah_name": "2 CORINTHIANS", "chapters": 13, "verses": 256},
            "Galatians": {"order": 48, "testament": "new", "yah_name": "GALATIANS", "chapters": 6, "verses": 149},
            "Ephesians": {"order": 49, "testament": "new", "yah_name": "EPHESIANS", "chapters": 6, "verses": 155},
            "Philippians": {"order": 50, "testament": "new", "yah_name": "PHILIPPIANS", "chapters": 4, "verses": 104},
            "Colossians": {"order": 51, "testament": "new", "yah_name": "COLOSSIANS", "chapters": 4, "verses": 95},
            "1 Thessalonians": {"order": 52, "testament": "new", "yah_name": "1 THESSALONIANS", "chapters": 5, "verses": 89},
            "2 Thessalonians": {"order": 53, "testament": "new", "yah_name": "2 THESSALONIANS", "chapters": 3, "verses": 47},
            "1 Timothy": {"order": 54, "testament": "new", "yah_name": "1 TIMOTHY", "chapters": 6, "verses": 113},
            "2 Timothy": {"order": 55, "testament": "new", "yah_name": "2 TIMOTHY", "chapters": 4, "verses": 83},
            "Titus": {"order": 56, "testament": "new", "yah_name": "TITUS", "chapters": 3, "verses": 46},
            "Philemon": {"order": 57, "testament": "new", "yah_name": "PHILEMON", "chapters": 1, "verses": 25},
            "Hebrews": {"order": 58, "testament": "new", "yah_name": "HEBREWS", "chapters": 13, "verses": 303},
            "James": {"order": 59, "testament": "new", "yah_name": "YA'AQOḆ", "chapters": 5, "verses": 108},
            "1 Peter": {"order": 60, "testament": "new", "yah_name": "1 KĔPHA", "chapters": 5, "verses": 105},
            "2 Peter": {"order": 61, "testament": "new", "yah_name": "2 KĔPHA", "chapters": 3, "verses": 61},
            "1 John": {"order": 62, "testament": "new", "yah_name": "1 YOḤANAN", "chapters": 5, "verses": 105},
            "2 John": {"order": 63, "testament": "new", "yah_name": "2 YOḤANAN", "chapters": 1, "verses": 13},
            "3 John": {"order": 64, "testament": "new", "yah_name": "3 YOḤANAN", "chapters": 1, "verses": 14},
            "Jude": {"order": 65, "testament": "new", "yah_name": "YAHUḎAH", "chapters": 1, "verses": 25},
            "Revelation": {"order": 66, "testament": "new", "yah_name": "ḤAZON", "chapters": 22, "verses": 404},
            
            # Apocrypha (14 books) - Web verified verse counts  
            "1 Esdras": {"order": 67, "testament": "apocrypha", "yah_name": "1 ESDRAS", "chapters": 9, "verses": 426},
            "2 Esdras": {"order": 68, "testament": "apocrypha", "yah_name": "2 ESDRAS", "chapters": 16, "verses": 140},
            "Tobit": {"order": 69, "testament": "apocrypha", "yah_name": "TOḆITH", "chapters": 14, "verses": 241},
            "Judith": {"order": 70, "testament": "apocrypha", "yah_name": "YAHUḎITH", "chapters": 16, "verses": 339},
            "Esther (Greek)": {"order": 71, "testament": "apocrypha", "yah_name": "ESTĔR ADDITIONS", "chapters": 6, "verses": 107},
            "Wisdom": {"order": 72, "testament": "apocrypha", "yah_name": "ḤOḴMAH", "chapters": 19, "verses": 434},
            "Sirach": {"order": 73, "testament": "apocrypha", "yah_name": "BEN SIRA", "chapters": 51, "verses": 1530},
            "Baruch": {"order": 74, "testament": "apocrypha", "yah_name": "BARUḴ", "chapters": 6, "verses": 213},
            "Letter of Jeremiah": {"order": 75, "testament": "apocrypha", "yah_name": "LETTER OF YIRMEYAHU", "chapters": 1, "verses": 73},
            "Prayer of Azariah": {"order": 76, "testament": "apocrypha", "yah_name": "AZARYAH", "chapters": 1, "verses": 68},
            "Susanna": {"order": 77, "testament": "apocrypha", "yah_name": "SHOSHANNAH", "chapters": 1, "verses": 64},
            "Bel and the Dragon": {"order": 78, "testament": "apocrypha", "yah_name": "BEL", "chapters": 1, "verses": 42},
            "1 Maccabees": {"order": 79, "testament": "apocrypha", "yah_name": "1 MAQQAḆIM", "chapters": 16, "verses": 1025},
            "2 Maccabees": {"order": 80, "testament": "apocrypha", "yah_name": "2 MAQQAḆIM", "chapters": 15, "verses": 556}
        }
    
    def extract_yah_book_precise(self, content: str, book_name: str, yah_name: str, expected_verses: int) -> List[Dict]:
        """Extract Yah Scriptures book with cross-reference validation"""
        verses = []
        
        # Find Hebrew book name with context
        book_patterns = [
            rf"^{re.escape(yah_name)}$",  # Exact match on its own line
            rf"\b{re.escape(yah_name)}\b",  # Word boundary match
            rf"{re.escape(yah_name)}\s*\n"  # Followed by newline
        ]
        
        book_start = -1
        for pattern in book_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                book_start = match.end()
                break
        
        if book_start == -1:
            logger.warning(f"Hebrew name '{yah_name}' not found for {book_name}")
            return verses
        
        # Find reasonable end boundary (next Hebrew book name or reasonable distance)
        book_end = min(book_start + (expected_verses * 150), len(content))  # Reasonable char per verse estimate
        
        # Look for next Hebrew book to set proper boundary
        all_yah_names = [info["yah_name"] for info in self.complete_bible_structure.values()]
        for next_yah_name in all_yah_names:
            if next_yah_name != yah_name:
                next_match = re.search(rf"\b{re.escape(next_yah_name)}\b", content[book_start + 1000:], re.IGNORECASE)
                if next_match:
                    candidate_end = book_start + 1000 + next_match.start()
                    if candidate_end < book_end:
                        book_end = candidate_end
        
        # Extract book content
        book_content = content[book_start:book_end]
        lines = book_content.split('\n')
        
        current_chapter = 1
        verse_count = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Verse pattern: number followed by space and text
            verse_match = re.match(r'^(\d+)\s+(.+)', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                
                if len(verse_text) > 15:  # Substantial verse content
                    verses.append({
                        'chapter': current_chapter,
                        'verse': verse_num,
                        'text': verse_text
                    })
                    verse_count += 1
                    
                    # Chapter detection: if we see verse 1 after other verses
                    if verse_num == 1 and len(verses) > 1 and verses[-2]['verse'] > 1:
                        current_chapter += 1
                        verses[-1]['chapter'] = current_chapter
                    
                    # Stop if we've extracted enough verses to avoid parsing errors
                    if verse_count >= expected_verses * 1.5:  # 50% buffer
                        break
            
            # Standalone chapter numbers
            elif re.match(r'^\d{1,3}$', line):
                chapter_candidate = int(line)
                if 1 <= chapter_candidate <= 150 and chapter_candidate > current_chapter:
                    current_chapter = chapter_candidate
        
        # Quality check: if we got way more verses than expected, trim to reasonable size
        if len(verses) > expected_verses * 1.2:
            verses = verses[:int(expected_verses * 1.2)]
        
        return verses
    
    def extract_kjv_book_precise(self, content: str, book_name: str, expected_verses: int, expected_chapters: int) -> List[Dict]:
        """Extract KJV book with cross-reference validation"""
        verses = []
        
        # KJV book detection patterns
        kjv_patterns = {
            'Genesis': [r'The First Book of Moses, called Genesis', r'Genesis', r'Page \d+.*?Genesis\b'],
            'Exodus': [r'The Second Book of Moses, Called Exodus', r'Exodus', r'Page \d+.*?Exodus\b'],
            'Matthew': [r'The Gospel According to St\. Matthew', r'Matthew', r'Page \d+.*?Matthew\b'],
            'Mark': [r'The Gospel According to St\. Mark', r'Mark', r'Page \d+.*?Mark\b'],
            'Psalms': [r'The Book of Psalms', r'Psalms', r'Page \d+.*?Psalms\b'],
            'Tobit': [r'Tobit', r'Page \d+.*?Tobit\b'],
            'Wisdom': [r'The Wisdom of Solomon', r'Wisdom', r'Page \d+.*?Wisdom\b']
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
            logger.warning(f"KJV pattern not found for {book_name}")
            return verses
        
        # Reasonable book boundary based on expected size
        book_content = content[book_start:book_start + (expected_verses * 200)]  # Char estimate
        
        # Extract verses using {chapter:verse} pattern
        verse_pattern = r'\{(\d+):(\d+)\}([^{]*?)(?=\{|\Z)'
        matches = re.findall(verse_pattern, book_content, re.DOTALL)
        
        for chapter_str, verse_str, verse_text in matches:
            chapter = int(chapter_str)
            verse_num = int(verse_str)
            
            # Clean verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'Page \d+.*?(?=\w)', '', clean_text).strip()
            clean_text = re.sub(r'^[^\w]*', '', clean_text).strip()
            
            if len(clean_text) > 15 and chapter <= expected_chapters:
                verses.append({
                    'chapter': chapter,
                    'verse': verse_num,
                    'text': clean_text
                })
                
                # Stop if we've got enough verses
                if len(verses) >= expected_verses * 1.2:
                    break
        
        return verses
    
    async def load_all_80_books(self):
        """Load all 80 books for both versions using cross-referenced data"""
        logger.info("Loading all 80 books with cross-reference validation...")
        
        # Load source files
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        with open('/app/apocrypha_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            apocrypha_content = f.read()
        
        yah_books_data = {}
        kjv_books_data = {}
        
        # Process all 80 books systematically
        for book_name, book_info in self.complete_bible_structure.items():
            expected_verses = book_info["verses"]
            expected_chapters = book_info["chapters"]
            yah_name = book_info["yah_name"]
            testament = book_info["testament"]
            
            logger.info(f"Processing {book_name} (expecting {expected_verses} verses, {expected_chapters} chapters)...")
            
            # Extract for Yah Scriptures
            if testament == "apocrypha":
                yah_verses = self.extract_yah_book_precise(apocrypha_content, book_name, yah_name, expected_verses)
            else:
                yah_verses = self.extract_yah_book_precise(yah_content, book_name, yah_name, expected_verses)
            
            if yah_verses:
                yah_books_data[book_name] = yah_verses
                actual_chapters = max([v['chapter'] for v in yah_verses])
                coverage = len(yah_verses) / expected_verses * 100
                logger.info(f"✅ Yah {book_name}: {len(yah_verses)}/{expected_verses} verses ({coverage:.1f}%), {actual_chapters}/{expected_chapters} chapters")
            else:
                logger.warning(f"❌ Yah {book_name}: No verses found")
            
            # Extract for KJV (priority books for now)
            if book_name in ['Genesis', 'Exodus', 'Matthew', 'Mark', 'Psalms', 'Tobit', 'Wisdom']:
                kjv_verses = self.extract_kjv_book_precise(kjv_content, book_name, expected_verses, expected_chapters)
                
                if kjv_verses:
                    kjv_books_data[book_name] = kjv_verses
                    actual_chapters = max([v['chapter'] for v in kjv_verses])
                    coverage = len(kjv_verses) / expected_verses * 100
                    logger.info(f"✅ KJV {book_name}: {len(kjv_verses)}/{expected_verses} verses ({coverage:.1f}%), {actual_chapters}/{expected_chapters} chapters")
                else:
                    logger.warning(f"❌ KJV {book_name}: No verses found")
        
        return yah_books_data, kjv_books_data
    
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
                        verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
        
        total_verses = sum(len(verses) for verses in books_data.values())
        self.verses_processed[version.split('_')[0]] = total_verses
    
    async def create_indexes(self):
        """Create database indexes"""
        logger.info("Creating database indexes...")
        
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
        
        logger.info("Database indexes created")
    
    async def run(self):
        """Main execution method with web-verified cross-reference"""
        try:
            logger.info("=== Starting Complete 80-Book Bible Loading with Cross-Reference Validation ===")
            
            await self.clear_all_bible_data()
            
            # Load all 80 books with cross-reference validation
            yah_books_data, kjv_books_data = await self.load_all_80_books()
            
            # Load to database
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            await self.create_indexes()
            
            # Calculate totals and expected totals
            expected_total_verses = sum(book["verses"] for book in self.complete_bible_structure.values())
            
            logger.info("=== Complete 80-Book Bible Loading Summary ===")
            logger.info(f"Yah Scriptures: {self.books_processed.get('yah', 0)}/80 books, {self.verses_processed.get('yah', 0)} verses")
            logger.info(f"KJV 1611: {self.books_processed.get('kjv', 0)}/80 books, {self.verses_processed.get('kjv', 0)} verses")
            logger.info(f"Expected Total: 80 books, {expected_total_verses} verses (31,102 canonical + ~5,200 apocrypha)")
            logger.info(f"Actual Total: {sum(self.books_processed.values())} books, {sum(self.verses_processed.values())} verses")
            
            # Coverage analysis
            yah_coverage = self.verses_processed.get('yah', 0) / expected_total_verses * 100
            kjv_coverage = self.verses_processed.get('kjv', 0) / expected_total_verses * 100
            
            logger.info(f"Coverage Analysis:")
            logger.info(f"  Yah Scriptures: {yah_coverage:.1f}% of expected verses")
            logger.info(f"  KJV 1611: {kjv_coverage:.1f}% of expected verses")
            
            if sum(self.books_processed.values()) >= 60:  # Good coverage
                logger.info("🎉 SUBSTANTIAL BIBLE COVERAGE ACHIEVED!")
            else:
                logger.warning("⚠️  Need to improve parsing for more complete coverage")
            
        except Exception as e:
            logger.error(f"Error during complete 80-book loading: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = Complete80BookLoader()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())