#!/usr/bin/env python3
"""
Optimized KJV Complete Loader - processes books in batches for efficiency
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

class OptimizedKJVLoader:
    def __init__(self, text_file_path: str):
        self.text_file_path = text_file_path
        self.verses_processed = 0
        self.books_processed = 0
        
        # Key books to focus on for complete Bible
        self.priority_books = [
            # Old Testament essentials
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', 
            '1 Kings', '2 Kings', 'Psalms', 'Proverbs', 'Isaiah',
            
            # New Testament complete
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
            '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
            'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
            'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
            'Jude', 'Revelation',
            
            # Apocrypha key books
            'Tobit', 'Judith', 'Wisdom', 'Sirach', '1 Maccabees', '2 Maccabees'
        ]
        
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
            
            # Apocrypha 
            "1 Esdras": {"order": 67, "testament": "apocrypha"},
            "2 Esdras": {"order": 68, "testament": "apocrypha"},
            "Tobit": {"order": 69, "testament": "apocrypha"},
            "Judith": {"order": 70, "testament": "apocrypha"},
            "Esther (Greek)": {"order": 71, "testament": "apocrypha"},
            "Wisdom": {"order": 72, "testament": "apocrypha"},
            "Sirach": {"order": 73, "testament": "apocrypha"},
            "Baruch": {"order": 74, "testament": "apocrypha"},
            "Letter of Jeremiah": {"order": 75, "testament": "apocrypha"},
            "Prayer of Azariah": {"order": 76, "testament": "apocrypha"},
            "Susanna": {"order": 77, "testament": "apocrypha"},
            "Bel and the Dragon": {"order": 78, "testament": "apocrypha"},
            "1 Maccabees": {"order": 79, "testament": "apocrypha"},
            "2 Maccabees": {"order": 80, "testament": "apocrypha"},
            "Prayer of Manasseh": {"order": 81, "testament": "apocrypha"},
        }
    
    async def parse_books_efficiently(self) -> Dict[str, List[Dict]]:
        """Parse books more efficiently using regex on entire file"""
        logger.info("Loading KJV text file...")
        
        with open(self.text_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        logger.info("Extracting all verses at once...")
        
        # Extract ALL verses at once with their position
        verse_pattern = r'\{(\d+):(\d+)\}([^{}]*?)(?=\{|\Z)'
        all_verses = []
        
        for match in re.finditer(verse_pattern, content, re.DOTALL):
            chapter = int(match.group(1))
            verse_num = int(match.group(2))
            verse_text = match.group(3).strip()
            position = match.start()
            
            if verse_text and len(verse_text) > 5:
                # Clean verse text
                clean_text = re.sub(r'\s+', ' ', verse_text)
                clean_text = re.sub(r'Page \d+.*?(?=\w|$)', '', clean_text).strip()
                
                if len(clean_text) > 5:
                    all_verses.append({
                        'chapter': chapter,
                        'verse': verse_num,
                        'text': clean_text,
                        'position': position
                    })
        
        logger.info(f"Found {len(all_verses)} total verses")
        
        # Now assign verses to books based on position
        books_data = {}
        
        for book_name in self.priority_books:
            logger.info(f"Processing {book_name}...")
            book_verses = self.get_verses_for_book(content, all_verses, book_name)
            
            if book_verses:
                books_data[book_name] = book_verses
                logger.info(f"✅ {book_name}: {len(book_verses)} verses")
            else:
                logger.warning(f"❌ {book_name}: No verses found")
        
        return books_data
    
    def get_verses_for_book(self, content: str, all_verses: List[Dict], book_name: str) -> List[Dict]:
        """Get verses for a specific book based on content position"""
        
        # Define book boundary patterns
        book_start_patterns = {
            'Genesis': [r'The First Book of Moses, called Genesis', r'Page \d+.*Genesis'],
            'Exodus': [r'The Second Book of Moses, Called Exodus'],
            'Matthew': [r'Page \d+.*Matthew'],
            'Mark': [r'Page \d+.*Mark'],
            'Luke': [r'Page \d+.*Luke'],
            'John': [r'Page \d+.*John'],
            'Acts': [r'Page \d+.*Acts'],
            'Romans': [r'Page \d+.*Romans'],
            'Psalms': [r'Page \d+.*Psalms'],
            'Tobit': [r'Page \d+.*Tobit'],
            'Wisdom': [r'Page \d+.*Wisdom'],
            # Add more as needed
        }
        
        if book_name not in book_start_patterns:
            return []
        
        # Find book start
        book_start = -1
        for pattern in book_start_patterns[book_name]:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                book_start = match.start()
                break
        
        if book_start == -1:
            return []
        
        # Find book end (start of next book or reasonable distance)
        book_end = book_start + 200000  # Reasonable book size limit
        
        # Look for next book boundary
        for other_book in self.priority_books:
            if other_book == book_name:
                continue
            if other_book in book_start_patterns:
                for pattern in book_start_patterns[other_book]:
                    match = re.search(pattern, content[book_start + 1000:], re.IGNORECASE)
                    if match:
                        next_start = book_start + 1000 + match.start()
                        if next_start < book_end:
                            book_end = next_start
        
        # Get verses within this book's boundaries
        book_verses = []
        for verse in all_verses:
            if book_start <= verse['position'] < book_end:
                book_verses.append({
                    'chapter': verse['chapter'],
                    'verse': verse['verse'],
                    'text': verse['text']
                })
        
        return book_verses
    
    async def clear_existing_kjv_data(self):
        """Clear existing KJV data"""
        logger.info("Clearing existing KJV 1611 data...")
        await bible_verses_collection.delete_many({"version": "kjv1611_divine"})
        await bible_books_collection.delete_many({"version": "kjv1611_divine"})
        logger.info("Existing data cleared")
    
    async def load_books_to_db(self, books_data: Dict[str, List[Dict]]):
        """Load book metadata"""
        logger.info("Loading books metadata...")
        
        books_to_insert = []
        for book_name, verses in books_data.items():
            if book_name in self.book_order_testament:
                book_info = self.book_order_testament[book_name]
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
                logger.info(f"Prepared: {book_name} ({verse_count} verses)")
        
        if books_to_insert:
            await bible_books_collection.insert_many(books_to_insert)
            self.books_processed = len(books_to_insert)
    
    async def load_verses_to_db(self, books_data: Dict[str, List[Dict]]):
        """Load verses in batches"""
        logger.info("Loading verses to database...")
        
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
                        'has_precept': False
                    }
                    
                    verses_to_insert.append(verse_doc)
                    
                    if len(verses_to_insert) >= batch_size:
                        await bible_verses_collection.insert_many(verses_to_insert)
                        logger.info(f"Inserted batch of {len(verses_to_insert)} verses")
                        verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
            logger.info(f"Inserted final batch of {len(verses_to_insert)} verses")
    
    async def create_indexes(self):
        """Create database indexes"""
        logger.info("Creating indexes...")
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
        logger.info("Indexes created")
    
    async def run(self):
        """Main execution"""
        try:
            logger.info("=== Starting Optimized KJV Loading ===")
            
            books_data = await self.parse_books_efficiently()
            
            if not books_data:
                logger.error("No books parsed")
                return
            
            await self.clear_existing_kjv_data()
            await self.load_books_to_db(books_data)
            await self.load_verses_to_db(books_data)
            await self.create_indexes()
            
            self.verses_processed = sum(len(verses) for verses in books_data.values())
            
            logger.info("=== Optimized KJV Loading Complete ===")
            logger.info(f"Books processed: {self.books_processed}")
            logger.info(f"Verses processed: {self.verses_processed}")
            
            # Testament summary
            ot_count = sum(1 for b in books_data.keys() if self.book_order_testament.get(b, {}).get('testament') == 'old')
            nt_count = sum(1 for b in books_data.keys() if self.book_order_testament.get(b, {}).get('testament') == 'new')
            ap_count = sum(1 for b in books_data.keys() if self.book_order_testament.get(b, {}).get('testament') == 'apocrypha')
            
            logger.info(f"Testament Distribution:")
            logger.info(f"  Old Testament: {ot_count} books")
            logger.info(f"  New Testament: {nt_count} books")
            logger.info(f"  Apocrypha: {ap_count} books")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            client.close()

async def main():
    text_file_path = "/app/kjv_with_apocrypha.txt"
    
    if not os.path.exists(text_file_path):
        logger.error(f"Text file not found: {text_file_path}")
        return
    
    loader = OptimizedKJVLoader(text_file_path)
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())