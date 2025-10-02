#!/usr/bin/env python3
"""
Complete 80 Books Final Loader

Systematically loads ALL 80 books for both Bible versions using enhanced parsing
and web-verified book structure. Focuses on completing the full biblical canon.
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

class Complete80BooksFinal:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Complete 80-book structure with alternative names and patterns
        self.all_80_books = {
            # Old Testament (39 books)
            "Genesis": {"order": 1, "testament": "old", "yah_names": ["BERĔSHITH", "BERESHITH", "Genesis"], "verses": 1533},
            "Exodus": {"order": 2, "testament": "old", "yah_names": ["SHEMOTH", "SHEMOT", "Exodus"], "verses": 1213},
            "Leviticus": {"order": 3, "testament": "old", "yah_names": ["WAYYIQRA", "VAYIQRA", "Leviticus"], "verses": 859},
            "Numbers": {"order": 4, "testament": "old", "yah_names": ["BEMIḎBAR", "BEMIDBAR", "Numbers"], "verses": 1288},
            "Deuteronomy": {"order": 5, "testament": "old", "yah_names": ["DEḆARIM", "DEVARIM", "Deuteronomy"], "verses": 959},
            "Joshua": {"order": 6, "testament": "old", "yah_names": ["YAHOSHUA", "YEHOSHUA", "Joshua"], "verses": 658},
            "Judges": {"order": 7, "testament": "old", "yah_names": ["SHOPHETIM", "SHOFTIM", "Judges"], "verses": 618},
            "Ruth": {"order": 8, "testament": "old", "yah_names": ["RUTH", "Ruth"], "verses": 85},
            "1 Samuel": {"order": 9, "testament": "old", "yah_names": ["SHEMU'ĔL", "SAMUEL", "1 Samuel"], "verses": 810},
            "2 Samuel": {"order": 10, "testament": "old", "yah_names": ["SHEMU'ĔL", "SAMUEL", "2 Samuel"], "verses": 695},
            "1 Kings": {"order": 11, "testament": "old", "yah_names": ["MELAḴIM", "MELACHIM", "1 Kings"], "verses": 816},
            "2 Kings": {"order": 12, "testament": "old", "yah_names": ["MELAḴIM", "MELACHIM", "2 Kings"], "verses": 719},
            "1 Chronicles": {"order": 13, "testament": "old", "yah_names": ["DIḆRE HAYYAMIM", "DIVREI HAYAMIM", "Chronicles"], "verses": 942},
            "2 Chronicles": {"order": 14, "testament": "old", "yah_names": ["DIḆRE HAYYAMIM", "DIVREI HAYAMIM", "Chronicles"], "verses": 822},
            "Ezra": {"order": 15, "testament": "old", "yah_names": ["EZRA", "Ezra"], "verses": 280},
            "Nehemiah": {"order": 16, "testament": "old", "yah_names": ["NEḤEMYAH", "NEHEMIAH", "Nehemiah"], "verses": 406},
            "Esther": {"order": 17, "testament": "old", "yah_names": ["ESTĔR", "ESTHER", "Esther"], "verses": 167},
            "Job": {"order": 18, "testament": "old", "yah_names": ["IYOḆ", "IYOV", "Job"], "verses": 1070},
            "Psalms": {"order": 19, "testament": "old", "yah_names": ["TEHILLIM", "Psalms"], "verses": 2461},
            "Proverbs": {"order": 20, "testament": "old", "yah_names": ["MISHLE", "Proverbs"], "verses": 915},
            "Ecclesiastes": {"order": 21, "testament": "old", "yah_names": ["QOHELETH", "Ecclesiastes"], "verses": 222},
            "Song of Songs": {"order": 22, "testament": "old", "yah_names": ["SHIR HASHIRIM", "Song of Songs"], "verses": 117},
            "Isaiah": {"order": 23, "testament": "old", "yah_names": ["YESHAYAHU", "Isaiah"], "verses": 1292},
            "Jeremiah": {"order": 24, "testament": "old", "yah_names": ["YIRMEYAHU", "Jeremiah"], "verses": 1364},
            "Lamentations": {"order": 25, "testament": "old", "yah_names": ["ĔYḴAH", "EICHAH", "Lamentations"], "verses": 154},
            "Ezekiel": {"order": 26, "testament": "old", "yah_names": ["YEḤEZQĔL", "YECHEZKEL", "Ezekiel"], "verses": 1273},
            "Daniel": {"order": 27, "testament": "old", "yah_names": ["DANI'ĔL", "DANIEL", "Daniel"], "verses": 357},
            "Hosea": {"order": 28, "testament": "old", "yah_names": ["HOSHĔA", "Hosea"], "verses": 197},
            "Joel": {"order": 29, "testament": "old", "yah_names": ["YO'ĔL", "YOEL", "Joel"], "verses": 73},
            "Amos": {"order": 30, "testament": "old", "yah_names": ["AMOS", "Amos"], "verses": 146},
            "Obadiah": {"order": 31, "testament": "old", "yah_names": ["OḆADYAH", "OVADIAH", "Obadiah"], "verses": 21},
            "Jonah": {"order": 32, "testament": "old", "yah_names": ["YONAH", "Jonah"], "verses": 48},
            "Micah": {"order": 33, "testament": "old", "yah_names": ["MIḴAH", "MICAH", "Micah"], "verses": 105},
            "Nahum": {"order": 34, "testament": "old", "yah_names": ["NAḤUM", "NACHUM", "Nahum"], "verses": 47},
            "Habakkuk": {"order": 35, "testament": "old", "yah_names": ["ḤAḆAQQUK", "CHAVAKUK", "Habakkuk"], "verses": 56},
            "Zephaniah": {"order": 36, "testament": "old", "yah_names": ["TSEPHANYAH", "ZEPHANIAH", "Zephaniah"], "verses": 53},
            "Haggai": {"order": 37, "testament": "old", "yah_names": ["ḤAGGAI", "CHAGGAI", "Haggai"], "verses": 38},
            "Zechariah": {"order": 38, "testament": "old", "yah_names": ["ZEḴARYAH", "ZECHARYAH", "Zechariah"], "verses": 211},
            "Malachi": {"order": 39, "testament": "old", "yah_names": ["MAL'AḴI", "MALACHI", "Malachi"], "verses": 55},
            
            # New Testament (27 books)
            "Matthew": {"order": 40, "testament": "new", "yah_names": ["MATTITHYAHU", "Matthew"], "verses": 1071},
            "Mark": {"order": 41, "testament": "new", "yah_names": ["MARQOS", "Mark"], "verses": 678},
            "Luke": {"order": 42, "testament": "new", "yah_names": ["LUQAS", "Luke"], "verses": 1151},
            "John": {"order": 43, "testament": "new", "yah_names": ["YOḤANAN", "YOCHANAN", "John"], "verses": 879},
            "Acts": {"order": 44, "testament": "new", "yah_names": ["ACTS", "Acts"], "verses": 1007},
            "Romans": {"order": 45, "testament": "new", "yah_names": ["ROMANS", "Romans"], "verses": 433},
            "1 Corinthians": {"order": 46, "testament": "new", "yah_names": ["CORINTHIANS", "1 Corinthians"], "verses": 437},
            "2 Corinthians": {"order": 47, "testament": "new", "yah_names": ["CORINTHIANS", "2 Corinthians"], "verses": 256},
            "Galatians": {"order": 48, "testament": "new", "yah_names": ["GALATIANS", "Galatians"], "verses": 149},
            "Ephesians": {"order": 49, "testament": "new", "yah_names": ["EPHESIANS", "Ephesians"], "verses": 155},
            "Philippians": {"order": 50, "testament": "new", "yah_names": ["PHILIPPIANS", "Philippians"], "verses": 104},
            "Colossians": {"order": 51, "testament": "new", "yah_names": ["COLOSSIANS", "Colossians"], "verses": 95},
            "1 Thessalonians": {"order": 52, "testament": "new", "yah_names": ["THESSALONIANS", "1 Thessalonians"], "verses": 89},
            "2 Thessalonians": {"order": 53, "testament": "new", "yah_names": ["THESSALONIANS", "2 Thessalonians"], "verses": 47},
            "1 Timothy": {"order": 54, "testament": "new", "yah_names": ["TIMOTHY", "1 Timothy"], "verses": 113},
            "2 Timothy": {"order": 55, "testament": "new", "yah_names": ["TIMOTHY", "2 Timothy"], "verses": 83},
            "Titus": {"order": 56, "testament": "new", "yah_names": ["TITUS", "Titus"], "verses": 46},
            "Philemon": {"order": 57, "testament": "new", "yah_names": ["PHILEMON", "Philemon"], "verses": 25},
            "Hebrews": {"order": 58, "testament": "new", "yah_names": ["HEBREWS", "Hebrews"], "verses": 303},
            "James": {"order": 59, "testament": "new", "yah_names": ["YA'AQOḆ", "YAAQOV", "James"], "verses": 108},
            "1 Peter": {"order": 60, "testament": "new", "yah_names": ["KĔPHA", "KEFA", "Peter"], "verses": 105},
            "2 Peter": {"order": 61, "testament": "new", "yah_names": ["KĔPHA", "KEFA", "Peter"], "verses": 61},
            "1 John": {"order": 62, "testament": "new", "yah_names": ["YOḤANAN", "YOCHANAN", "John"], "verses": 105},
            "2 John": {"order": 63, "testament": "new", "yah_names": ["YOḤANAN", "YOCHANAN", "John"], "verses": 13},
            "3 John": {"order": 64, "testament": "new", "yah_names": ["YOḤANAN", "YOCHANAN", "John"], "verses": 14},
            "Jude": {"order": 65, "testament": "new", "yah_names": ["YAHUḎAH", "YAHUDAH", "Jude"], "verses": 25},
            "Revelation": {"order": 66, "testament": "new", "yah_names": ["ḤAZON", "CHAZON", "Revelation"], "verses": 404},
            
            # Apocrypha (14 books)
            "1 Esdras": {"order": 67, "testament": "apocrypha", "yah_names": ["ESDRAS", "1 Esdras"], "verses": 426},
            "2 Esdras": {"order": 68, "testament": "apocrypha", "yah_names": ["ESDRAS", "2 Esdras"], "verses": 140},
            "Tobit": {"order": 69, "testament": "apocrypha", "yah_names": ["TOḆITH", "TOVIT", "Tobit"], "verses": 241},
            "Judith": {"order": 70, "testament": "apocrypha", "yah_names": ["YAHUḎITH", "YEHUDIT", "Judith"], "verses": 339},
            "Esther (Greek)": {"order": 71, "testament": "apocrypha", "yah_names": ["ESTĔR ADDITIONS", "Esther Additions"], "verses": 107},
            "Wisdom": {"order": 72, "testament": "apocrypha", "yah_names": ["ḤOḴMAH", "CHOCHMAH", "Wisdom"], "verses": 434},
            "Sirach": {"order": 73, "testament": "apocrypha", "yah_names": ["BEN SIRA", "SIRACH", "Ecclesiasticus"], "verses": 1530},
            "Baruch": {"order": 74, "testament": "apocrypha", "yah_names": ["BARUḴ", "BARUCH", "Baruch"], "verses": 213},
            "Letter of Jeremiah": {"order": 75, "testament": "apocrypha", "yah_names": ["LETTER OF YIRMEYAHU", "Letter of Jeremiah"], "verses": 73},
            "Prayer of Azariah": {"order": 76, "testament": "apocrypha", "yah_names": ["AZARYAH", "Prayer of Azariah"], "verses": 68},
            "Susanna": {"order": 77, "testament": "apocrypha", "yah_names": ["SHOSHANNAH", "Susanna"], "verses": 64},
            "Bel and the Dragon": {"order": 78, "testament": "apocrypha", "yah_names": ["BEL", "Bel and the Dragon"], "verses": 42},
            "1 Maccabees": {"order": 79, "testament": "apocrypha", "yah_names": ["MAQQAḆIM", "MACCABEES", "1 Maccabees"], "verses": 1025},
            "2 Maccabees": {"order": 80, "testament": "apocrypha", "yah_names": ["MAQQAḆIM", "MACCABEES", "2 Maccabees"], "verses": 556}
        }
    
    def find_book_content_advanced(self, content: str, book_name: str, yah_names: List[str]) -> tuple:
        """Advanced book boundary detection using multiple strategies"""
        
        # Strategy 1: Look for exact Hebrew names
        for yah_name in yah_names:
            # Try different patterns
            patterns = [
                rf"^{re.escape(yah_name)}$",  # Exact match on own line
                rf"\b{re.escape(yah_name)}\b",  # Word boundary
                rf"{re.escape(yah_name)}\s*\n",  # Followed by newline
                rf"^{re.escape(yah_name)}\s*",  # Start of line with optional space
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))
                if matches:
                    return matches[0].end(), yah_name
        
        # Strategy 2: Fuzzy matching - remove special characters
        for yah_name in yah_names:
            clean_name = re.sub(r'[^\w]', '', yah_name)
            if len(clean_name) > 3:  # Avoid matching very short names
                pattern = rf"\b{re.escape(clean_name)}\b"
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                if matches:
                    return matches[0].end(), yah_name
        
        # Strategy 3: Partial matching for compound names
        for yah_name in yah_names:
            if len(yah_name.split()) > 1:  # Multi-word names
                first_word = yah_name.split()[0]
                if len(first_word) > 4:  # Substantial first word
                    pattern = rf"\b{re.escape(first_word)}\b"
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        return matches[0].end(), first_word
        
        return -1, None
    
    def extract_book_verses_advanced(self, content: str, book_start: int, expected_verses: int) -> List[Dict]:
        """Advanced verse extraction with multiple parsing strategies"""
        verses = []
        
        # Get reasonable amount of content
        book_content = content[book_start:book_start + (expected_verses * 200)]
        lines = book_content.split('\n')
        
        current_chapter = 1
        verse_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Strategy 1: Standard verse pattern (number + space + text)
            verse_match = re.match(r'^(\d+)\s+(.+)', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                
                if len(verse_text) > 10:  # Substantial content
                    verses.append({
                        'chapter': current_chapter,
                        'verse': verse_num,
                        'text': verse_text
                    })
                    verse_count += 1
                    
                    # Chapter detection
                    if verse_num == 1 and len(verses) > 1 and verses[-2]['verse'] > 1:
                        current_chapter += 1
                        verses[-1]['chapter'] = current_chapter
                    
                    if verse_count >= expected_verses * 1.3:  # Reasonable limit
                        break
            
            # Strategy 2: Standalone chapter markers
            elif re.match(r'^\d{1,3}$', line):
                chapter_candidate = int(line)
                if 1 <= chapter_candidate <= 150 and chapter_candidate > current_chapter:
                    current_chapter = chapter_candidate
            
            # Strategy 3: Alternative verse formats (verse:text)
            alt_verse_match = re.match(r'^(\d+):(.+)', line)
            if alt_verse_match and not verse_match:  # Don't double-process
                verse_num = int(alt_verse_match.group(1))
                verse_text = alt_verse_match.group(2).strip()
                
                if len(verse_text) > 10:
                    verses.append({
                        'chapter': current_chapter,
                        'verse': verse_num,
                        'text': verse_text
                    })
                    verse_count += 1
                    
                    if verse_count >= expected_verses * 1.3:
                        break
        
        return verses
    
    def extract_kjv_book_advanced(self, content: str, book_name: str, expected_verses: int) -> List[Dict]:
        """Advanced KJV extraction with comprehensive patterns"""
        verses = []
        
        # Comprehensive KJV patterns including all books
        kjv_patterns = [
            rf"The.*?Book.*?{re.escape(book_name)}",
            rf"The Gospel.*?{re.escape(book_name)}",
            rf"The.*?Epistle.*?{re.escape(book_name)}",
            rf"The.*?{re.escape(book_name)}",
            rf"Page \d+.*?{re.escape(book_name)}\b",
            rf"\b{re.escape(book_name)}\b.*?Page",
            rf"^{re.escape(book_name)}$",
            rf"\b{re.escape(book_name)}\b"
        ]
        
        book_start = -1
        for pattern in kjv_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
            if matches:
                book_start = matches[0].start()
                break
        
        if book_start == -1:
            return verses
        
        # Extract content
        book_content = content[book_start:book_start + (expected_verses * 250)]
        
        # Use {chapter:verse} pattern for KJV
        verse_pattern = r'\{(\d+):(\d+)\}([^{]*?)(?=\{|\Z)'
        matches = re.findall(verse_pattern, book_content, re.DOTALL)
        
        for chapter_str, verse_str, verse_text in matches:
            chapter = int(chapter_str)
            verse_num = int(verse_str)
            
            # Clean verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'Page \d+.*?(?=\w)', '', clean_text).strip()
            clean_text = re.sub(r'^[^\w]*', '', clean_text).strip()
            
            if len(clean_text) > 10:
                verses.append({
                    'chapter': chapter,
                    'verse': verse_num,
                    'text': clean_text
                })
                
                if len(verses) >= expected_verses * 1.4:  # Reasonable limit
                    break
        
        return verses
    
    async def load_all_80_books_systematically(self):
        """Systematically load all 80 books for both versions"""
        logger.info("Loading all 80 books systematically...")
        
        # Load source files
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        with open('/app/apocrypha_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            apocrypha_content = f.read()
        
        yah_books_data = {}
        kjv_books_data = {}
        
        # Process all 80 books in order
        for book_name, book_info in self.all_80_books.items():
            expected_verses = book_info["verses"]
            yah_names = book_info["yah_names"]
            testament = book_info["testament"]
            
            logger.info(f"Processing {book_name} (expecting {expected_verses} verses)...")
            
            # Extract for Yah Scriptures
            if testament == "apocrypha":
                source_content = apocrypha_content
            else:
                source_content = yah_content
            
            book_start, found_name = self.find_book_content_advanced(source_content, book_name, yah_names)
            
            if book_start != -1:
                yah_verses = self.extract_book_verses_advanced(source_content, book_start, expected_verses)
                if yah_verses:
                    yah_books_data[book_name] = yah_verses
                    coverage = len(yah_verses) / expected_verses * 100
                    logger.info(f"✅ Yah {book_name}: {len(yah_verses)}/{expected_verses} verses ({coverage:.1f}%) [found: {found_name}]")
                else:
                    logger.warning(f"❌ Yah {book_name}: Found location but no verses extracted")
            else:
                logger.warning(f"❌ Yah {book_name}: Book location not found")
            
            # Extract for KJV
            kjv_verses = self.extract_kjv_book_advanced(kjv_content, book_name, expected_verses)
            if kjv_verses:
                kjv_books_data[book_name] = kjv_verses
                coverage = len(kjv_verses) / expected_verses * 100
                logger.info(f"✅ KJV {book_name}: {len(kjv_verses)}/{expected_verses} verses ({coverage:.1f}%)")
            else:
                # Try Apocrypha source for KJV Apocrypha books
                if testament == "apocrypha":
                    kjv_verses = self.extract_kjv_book_advanced(apocrypha_content, book_name, expected_verses)
                    if kjv_verses:
                        kjv_books_data[book_name] = kjv_verses
                        coverage = len(kjv_verses) / expected_verses * 100
                        logger.info(f"✅ KJV {book_name}: {len(kjv_verses)}/{expected_verses} verses ({coverage:.1f}%) [apocrypha source]")
                    else:
                        logger.warning(f"❌ KJV {book_name}: No verses found")
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
            if book_name in self.all_80_books:
                book_info = self.all_80_books[book_name]
                
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
            if book_name in self.all_80_books:
                book_info = self.all_80_books[book_name]
                
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
        """Main execution method - complete 80 books"""
        try:
            logger.info("=== Starting Complete 80 Books Final Loading ===")
            
            await self.clear_all_bible_data()
            
            # Load all 80 books systematically
            yah_books_data, kjv_books_data = await self.load_all_80_books_systematically()
            
            # Load to database
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            await self.create_indexes()
            
            # Calculate totals
            expected_total_verses = sum(book["verses"] for book in self.all_80_books.values())
            
            logger.info("=== Complete 80 Books Final Loading Summary ===")
            logger.info(f"Expected: 80 books each, {expected_total_verses} total verses")
            logger.info(f"Yah Scriptures: {self.books_processed.get('yah', 0)}/80 books, {self.verses_processed.get('yah', 0)} verses")
            logger.info(f"KJV 1611: {self.books_processed.get('kjv', 0)}/80 books, {self.verses_processed.get('kjv', 0)} verses")
            logger.info(f"Total Achievement: {sum(self.books_processed.values())} books, {sum(self.verses_processed.values())} verses")
            
            # Coverage analysis
            yah_book_coverage = self.books_processed.get('yah', 0) / 80 * 100
            kjv_book_coverage = self.books_processed.get('kjv', 0) / 80 * 100
            
            logger.info(f"Coverage Analysis:")
            logger.info(f"  Yah Scriptures: {yah_book_coverage:.1f}% of 80 books")
            logger.info(f"  KJV 1611: {kjv_book_coverage:.1f}% of 80 books")
            
            if self.books_processed.get('yah', 0) >= 70 and self.books_processed.get('kjv', 0) >= 70:
                logger.info("🎉 EXCELLENT: Both versions have substantial coverage (70+ books each)!")
            elif sum(self.books_processed.values()) >= 120:
                logger.info("✅ GREAT: Combined substantial coverage achieved!")
            else:
                logger.info("📈 PROGRESS: Significant improvement made, continuing to target 80 books each")
            
        except Exception as e:
            logger.error(f"Error during complete 80-book loading: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = Complete80BooksFinal()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())