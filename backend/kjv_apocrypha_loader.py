#!/usr/bin/env python3
"""
KJV with Apocrypha Bible Data Loader

This script parses the complete KJV with Apocrypha text file and loads it into MongoDB
to replace the incomplete "Yah Scriptures" data with a complete Bible version.

File format: {chapter:verse} text content
Books are separated by headers like "Page X   BookName" or "The X Book of Y, called Z"
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

class KJVApocryphaLoader:
    def __init__(self, text_file_path: str):
        self.text_file_path = text_file_path
        self.verses_processed = 0
        self.books_processed = 0
        
        # Bible book order and testament mapping
        self.book_order_testament = {
            # Old Testament (1-39)
            "Genesis": {"order": 1, "testament": "old"},
            "Exodus": {"order": 2, "testament": "old"},
            "Leviticus": {"order": 3, "testament": "old"},
            "Numbers": {"order": 4, "testament": "old"},
            "Deuteronomy": {"order": 5, "testament": "old"},
            "Joshua": {"order": 6, "testament": "old"},
            "Judges": {"order": 7, "testament": "old"},
            "Ruth": {"order": 8, "testament": "old"},
            "1 Samuel": {"order": 9, "testament": "old"},
            "2 Samuel": {"order": 10, "testament": "old"},
            "1 Kings": {"order": 11, "testament": "old"},
            "2 Kings": {"order": 12, "testament": "old"},
            "1 Chronicles": {"order": 13, "testament": "old"},
            "2 Chronicles": {"order": 14, "testament": "old"},
            "Ezra": {"order": 15, "testament": "old"},
            "Nehemiah": {"order": 16, "testament": "old"},
            "Esther": {"order": 17, "testament": "old"},
            "Job": {"order": 18, "testament": "old"},
            "Psalms": {"order": 19, "testament": "old"},
            "Proverbs": {"order": 20, "testament": "old"},
            "Ecclesiastes": {"order": 21, "testament": "old"},
            "Song of Songs": {"order": 22, "testament": "old"},
            "Isaiah": {"order": 23, "testament": "old"},
            "Jeremiah": {"order": 24, "testament": "old"},
            "Lamentations": {"order": 25, "testament": "old"},
            "Ezekiel": {"order": 26, "testament": "old"},
            "Daniel": {"order": 27, "testament": "old"},
            "Hosea": {"order": 28, "testament": "old"},
            "Joel": {"order": 29, "testament": "old"},
            "Amos": {"order": 30, "testament": "old"},
            "Obadiah": {"order": 31, "testament": "old"},
            "Jonah": {"order": 32, "testament": "old"},
            "Micah": {"order": 33, "testament": "old"},
            "Nahum": {"order": 34, "testament": "old"},
            "Habakkuk": {"order": 35, "testament": "old"},
            "Zephaniah": {"order": 36, "testament": "old"},
            "Haggai": {"order": 37, "testament": "old"},
            "Zechariah": {"order": 38, "testament": "old"},
            "Malachi": {"order": 39, "testament": "old"},
            
            # New Testament (40-65) 
            "Matthew": {"order": 40, "testament": "new"},
            "Mark": {"order": 41, "testament": "new"},
            "Luke": {"order": 42, "testament": "new"},
            "John": {"order": 43, "testament": "new"},
            "Acts": {"order": 44, "testament": "new"},
            "Romans": {"order": 45, "testament": "new"},
            "1 Corinthians": {"order": 46, "testament": "new"},
            "2 Corinthians": {"order": 47, "testament": "new"},
            "Galatians": {"order": 48, "testament": "new"},
            "Ephesians": {"order": 49, "testament": "new"},
            "Philippians": {"order": 50, "testament": "new"},
            "Colossians": {"order": 51, "testament": "new"},
            "1 Thessalonians": {"order": 52, "testament": "new"},
            "2 Thessalonians": {"order": 53, "testament": "new"},
            "1 Timothy": {"order": 54, "testament": "new"},
            "2 Timothy": {"order": 55, "testament": "new"},
            "Titus": {"order": 56, "testament": "new"},
            "Philemon": {"order": 57, "testament": "new"},
            "Hebrews": {"order": 58, "testament": "new"},
            "James": {"order": 59, "testament": "new"},
            "1 Peter": {"order": 60, "testament": "new"},
            "2 Peter": {"order": 61, "testament": "new"},
            "1 John": {"order": 62, "testament": "new"},
            "2 John": {"order": 63, "testament": "new"},
            "3 John": {"order": 64, "testament": "new"},
            "Jude": {"order": 65, "testament": "new"},
            "Revelation": {"order": 66, "testament": "new"},
            
            # Apocrypha (67-80+)
            "1 Esdras": {"order": 67, "testament": "apocrypha"},
            "2 Esdras": {"order": 68, "testament": "apocrypha"},
            "Tobit": {"order": 69, "testament": "apocrypha"},
            "Judith": {"order": 70, "testament": "apocrypha"},
            "Esther (Greek)": {"order": 71, "testament": "apocrypha"},
            "Wisdom": {"order": 72, "testament": "apocrypha"},
            "Sirach": {"order": 73, "testament": "apocrypha"},
            "Ecclesiasticus": {"order": 73, "testament": "apocrypha"},  # Same as Sirach
            "Baruch": {"order": 74, "testament": "apocrypha"},
            "Letter of Jeremiah": {"order": 75, "testament": "apocrypha"},
            "Prayer of Azariah": {"order": 76, "testament": "apocrypha"},
            "Song of the Three": {"order": 76, "testament": "apocrypha"},
            "Susanna": {"order": 77, "testament": "apocrypha"},
            "Bel and the Dragon": {"order": 78, "testament": "apocrypha"},
            "1 Maccabees": {"order": 79, "testament": "apocrypha"},
            "2 Maccabees": {"order": 80, "testament": "apocrypha"},
            "Prayer of Manasseh": {"order": 81, "testament": "apocrypha"},
        }
    
    def normalize_book_name(self, raw_name: str) -> str:
        """Normalize book names found in the text to standard names"""
        raw_name = raw_name.strip()
        
        # Handle common variations
        mappings = {
            "The First Book of Moses, called Genesis": "Genesis",
            "The Second Book of Moses, Called Exodus": "Exodus", 
            "The Third Book of Moses, called Leviticus": "Leviticus",
            "The Fourth Book of Moses, called Numbers": "Numbers",
            "The Fifth Book of Moses, called Deuteronomy": "Deuteronomy",
            "The Book of Joshua": "Joshua",
            "The Book of Judges": "Judges",
            "The Book of Ruth": "Ruth",
            "The First Book of Samuel": "1 Samuel",
            "The Second Book of Samuel": "2 Samuel",
            "The First Book of the Kings": "1 Kings",
            "The Second Book of the Kings": "2 Kings",
            "The First Book of the Chronicles": "1 Chronicles",
            "The Second Book of the Chronicles": "2 Chronicles",
            "Ezra": "Ezra",
            "The Book of Nehemiah": "Nehemiah",
            "The Book of Esther": "Esther",
            "The Book of Job": "Job",
            "The Book of Psalms": "Psalms",
            "The Proverbs": "Proverbs",
            "Ecclesiastes": "Ecclesiastes",
            "The Song of Songs": "Song of Songs",
            "The Book of the Prophet Isaiah": "Isaiah",
            "The Book of the Prophet Jeremiah": "Jeremiah",
            "The Lamentations of Jeremiah": "Lamentations",
            "The Book of the Prophet Ezekiel": "Ezekiel",
            "The Book of Daniel": "Daniel",
            "Hosea": "Hosea",
            "Joel": "Joel",
            "Amos": "Amos",
            "Obadiah": "Obadiah",
            "Jonah": "Jonah",
            "Micah": "Micah",
            "Nahum": "Nahum",
            "Habakkuk": "Habakkuk",
            "Zephaniah": "Zephaniah",
            "Haggai": "Haggai",
            "Zechariah": "Zechariah",
            "Malachi": "Malachi"
        }
        
        return mappings.get(raw_name, raw_name)
    
    def extract_book_name_from_line(self, line: str) -> str:
        """Extract book name from header lines"""
        line = line.strip()
        
        # Pattern 1: "Page X    BookName"
        page_match = re.search(r'Page \d+\s+(.+)', line)
        if page_match:
            return page_match.group(1).strip()
            
        # Pattern 2: "The X Book of Y, called Z" or similar
        book_patterns = [
            r'The (.+?) Book of (.+?)(?:,|$)',
            r'The Book of (.+?)(?:,|$)', 
            r'(.+?)(?:,|$)'
        ]
        
        for pattern in book_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0).strip().rstrip(',')
        
        return line
    
    async def parse_text_file(self) -> Dict[str, List[Dict]]:
        """Parse the KJV text file and extract all verses by book"""
        logger.info(f"Starting to parse {self.text_file_path}")
        
        books_data = {}
        current_book = None
        current_chapter = 1
        
        with open(self.text_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split into lines for processing
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for book headers
            if (re.match(r'Page \d+.*?(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|Esdras|Tobit|Judith|Wisdom|Sirach|Ecclesiasticus|Baruch|Maccabees)', line, re.IGNORECASE) or
                'Book of Moses' in line or 'Book of' in line):
                
                book_name = self.extract_book_name_from_line(line)
                normalized_name = self.normalize_book_name(book_name)
                
                if normalized_name in self.book_order_testament:
                    current_book = normalized_name
                    current_chapter = 1
                    books_data[current_book] = []
                    logger.info(f"Found book: {current_book}")
                    continue
            
            # Look for verse patterns: {chapter:verse} text
            if current_book:
                verse_matches = re.finditer(r'\{(\d+):(\d+)\}\s*([^{]*?)(?=\s*\{\d+:\d+\}|$)', line)
                
                for match in verse_matches:
                    chapter = int(match.group(1))
                    verse_num = int(match.group(2))
                    verse_text = match.group(3).strip()
                    
                    if verse_text:  # Only add non-empty verses
                        books_data[current_book].append({
                            'chapter': chapter,
                            'verse': verse_num, 
                            'text': verse_text
                        })
                        self.verses_processed += 1
        
        logger.info(f"Parsing complete. Found {len(books_data)} books, {self.verses_processed} verses")
        return books_data
    
    async def clear_existing_kjv_data(self):
        """Clear existing KJV 1611 data"""
        logger.info("Clearing existing KJV 1611 data...")
        
        await bible_verses_collection.delete_many({"version": "kjv1611_divine"})
        await bible_books_collection.delete_many({"version": "kjv1611_divine"})
        
        logger.info("Existing KJV 1611 data cleared")
    
    async def load_books_to_db(self, books_data: Dict[str, List[Dict]]):
        """Load book metadata to database"""
        logger.info("Loading books metadata...")
        
        books_to_insert = []
        
        for book_name, verses in books_data.items():
            if book_name in self.book_order_testament:
                book_info = self.book_order_testament[book_name]
                
                # Calculate chapters
                chapters = max([v['chapter'] for v in verses]) if verses else 0
                verse_count = len(verses)
                
                book_doc = {
                    'id': str(uuid.uuid4()),
                    'version': 'kjv1611_divine',
                    'name': book_name,
                    'testament': book_info['testament'],
                    'order': book_info['order'],
                    'chapters': chapters,
                    'verses': verse_count
                }
                
                books_to_insert.append(book_doc)
                logger.info(f"Prepared book: {book_name} ({verse_count} verses, {chapters} chapters)")
        
        if books_to_insert:
            await bible_books_collection.insert_many(books_to_insert)
            logger.info(f"Inserted {len(books_to_insert)} books")
            self.books_processed = len(books_to_insert)
    
    async def load_verses_to_db(self, books_data: Dict[str, List[Dict]]):
        """Load verses to database in batches"""
        logger.info("Loading verses...")
        
        batch_size = 1000
        verses_to_insert = []
        
        for book_name, verses in books_data.items():
            if book_name in self.book_order_testament:
                book_info = self.book_order_testament[book_name]
                
                for verse_data in verses:
                    verse_doc = {
                        'id': str(uuid.uuid4()),
                        'version': 'kjv1611_divine',
                        'book': book_name,
                        'chapter': verse_data['chapter'],
                        'verse': verse_data['verse'],
                        'text': verse_data['text'],
                        'testament': book_info['testament'],
                        'has_precept': False  # Default, can be updated later
                    }
                    
                    verses_to_insert.append(verse_doc)
                    
                    # Insert in batches
                    if len(verses_to_insert) >= batch_size:
                        await bible_verses_collection.insert_many(verses_to_insert)
                        logger.info(f"Inserted batch of {len(verses_to_insert)} verses")
                        verses_to_insert = []
        
        # Insert remaining verses
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
            logger.info(f"Inserted final batch of {len(verses_to_insert)} verses")
    
    async def create_indexes(self):
        """Create database indexes for efficient querying"""
        logger.info("Creating database indexes...")
        
        # Indexes for bible_verses_collection
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_verses_collection.create_index([("version", 1), ("book", 1)])
        await bible_verses_collection.create_index([("text", "text")])  # Text search index
        
        # Indexes for bible_books_collection
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
        await bible_books_collection.create_index([("version", 1), ("testament", 1)])
        
        logger.info("Database indexes created")
    
    async def run(self):
        """Main execution method"""
        try:
            logger.info("=== Starting KJV with Apocrypha Loading ===")
            
            # Parse the text file
            books_data = await self.parse_text_file()
            
            if not books_data:
                logger.error("No books found in text file")
                return
            
            # Clear existing data
            await self.clear_existing_kjv_data()
            
            # Load to database
            await self.load_books_to_db(books_data)
            await self.load_verses_to_db(books_data)
            await self.create_indexes()
            
            logger.info("=== KJV Loading Complete ===")
            logger.info(f"Books processed: {self.books_processed}")
            logger.info(f"Verses processed: {self.verses_processed}")
            
        except Exception as e:
            logger.error(f"Error during loading: {e}")
            raise
        finally:
            client.close()

async def main():
    """Main function"""
    text_file_path = "/app/kjv_with_apocrypha.txt"
    
    if not os.path.exists(text_file_path):
        logger.error(f"Text file not found: {text_file_path}")
        return
    
    loader = KJVApocryphaLoader(text_file_path)
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())