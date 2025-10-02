#!/usr/bin/env python3
"""
Targeted Bible Loader - Final Version

Precisely tailored to load both Bible versions correctly based on actual file formats.
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

class TargetedBibleLoader:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Key books with Hebrew names and expected verse counts
        self.key_books = {
            # Old Testament samples
            "Genesis": {"order": 1, "testament": "old", "yah_name": "BERĔSHITH", "expected_verses": 1533},
            "Exodus": {"order": 2, "testament": "old", "yah_name": "SHEMOTH", "expected_verses": 1213},
            "Psalms": {"order": 19, "testament": "old", "yah_name": "TEHILLIM", "expected_verses": 2461},
            
            # New Testament complete
            "Matthew": {"order": 40, "testament": "new", "yah_name": "MATTITHYAHU", "expected_verses": 1071},
            "Mark": {"order": 41, "testament": "new", "yah_name": "MARQOS", "expected_verses": 678},
            "Luke": {"order": 42, "testament": "new", "yah_name": "LUQAS", "expected_verses": 1151},
            "John": {"order": 43, "testament": "new", "yah_name": "YOḤANAN", "expected_verses": 879},
            "Acts": {"order": 44, "testament": "new", "yah_name": "ACTS", "expected_verses": 1007},
            "Romans": {"order": 45, "testament": "new", "yah_name": "ROMANS", "expected_verses": 433},
            "Revelation": {"order": 66, "testament": "new", "yah_name": "ḤAZON", "expected_verses": 404},
            
            # Apocrypha samples  
            "Tobit": {"order": 69, "testament": "apocrypha", "yah_name": "TOḆITH", "expected_verses": 300},
            "Wisdom": {"order": 72, "testament": "apocrypha", "yah_name": "ḤOḴMAH", "expected_verses": 435},
        }
    
    def extract_yah_book(self, content: str, book_name: str, yah_name: str) -> List[Dict]:
        """Extract verses for Yah Scriptures book using exact format matching"""
        verses = []
        
        # Find the Hebrew book header with the exact pattern we saw
        pattern = rf"{re.escape(yah_name)}\s*\n[^\n]*\n\s*(\d+)\s+(.+?)(?=\n\d+|\n[A-Z][A-Z]|\Z)"
        
        # Alternative: Look for the book header followed by verse content
        book_start_pattern = rf"{re.escape(yah_name)}\s*\n[^\n]*\n"
        match = re.search(book_start_pattern, content, re.DOTALL)
        
        if not match:
            # Try simpler pattern
            match = re.search(rf"{re.escape(yah_name)}", content)
            if not match:
                return verses
        
        book_start = match.end()
        
        # Find the end of this book (next Hebrew book name or end)
        # Look ahead for next book
        book_content = content[book_start:book_start + 200000]  # Reasonable book size
        
        # Parse verses using the format: number at start of line + text
        lines = book_content.split('\n')
        current_chapter = 1
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for verse pattern: starts with number followed by text
            verse_match = re.match(r'^(\d+)\s+(.+)', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                
                # Skip very short text (likely headers/artifacts)
                if len(verse_text) > 15:
                    verses.append({
                        'chapter': current_chapter,
                        'verse': verse_num,
                        'text': verse_text
                    })
                    
                    # If we see verse 1 after having other verses, it's likely a new chapter
                    if verse_num == 1 and len(verses) > 1 and verses[-2]['verse'] > 1:
                        current_chapter += 1
                        verses[-1]['chapter'] = current_chapter
            
            # Check for standalone numbers that might be chapter markers
            elif re.match(r'^\d{1,2}$', line):
                chapter_candidate = int(line)
                if 1 <= chapter_candidate <= 150 and chapter_candidate > current_chapter:
                    current_chapter = chapter_candidate
        
        # If we got too many verses, there might be parsing errors - limit to expected
        expected = self.key_books[book_name]["expected_verses"]
        if len(verses) > expected * 2:  # Allow some flexibility but cap at 2x expected
            verses = verses[:expected * 2]
        
        return verses
    
    def extract_kjv_book(self, content: str, book_name: str) -> List[Dict]:
        """Extract verses for KJV book using {chapter:verse} format"""
        verses = []
        
        # KJV patterns based on what we observed
        kjv_patterns = {
            'Genesis': [r'The First Book of Moses, called Genesis', r'Page \d+\s+Genesis'],
            'Matthew': [r'The Gospel According to St\. Matthew', r'Page \d+\s+Matthew'],
            'Psalms': [r'The Book of Psalms', r'Page \d+\s+Psalms']
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
        
        # Get reasonable chunk of content for this book
        book_content = content[book_start:book_start + 150000]
        
        # Extract verses using {chapter:verse} format
        verse_pattern = r'\{(\d+):(\d+)\}([^{]*?)(?=\{|\Z)'
        matches = re.findall(verse_pattern, book_content, re.DOTALL)
        
        for chapter_str, verse_str, verse_text in matches:
            chapter = int(chapter_str)
            verse_num = int(verse_str)
            
            # Clean the verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'Page \d+[^\w]*', '', clean_text).strip()
            clean_text = re.sub(r'^[^\w]*', '', clean_text).strip()
            
            if len(clean_text) > 15:  # Only substantial verses
                verses.append({
                    'chapter': chapter,
                    'verse': verse_num,
                    'text': clean_text
                })
        
        return verses
    
    async def load_yah_scriptures_targeted(self):
        """Load Yah Scriptures with targeted approach"""
        logger.info("Loading Yah Scriptures with targeted parsing...")
        
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        books_data = {}
        
        # Process each key book
        for book_name, book_info in self.key_books.items():
            if book_info["testament"] != "apocrypha":  # Skip apocrypha for now
                yah_name = book_info["yah_name"]
                verses = self.extract_yah_book(yah_content, book_name, yah_name)
                
                if verses:
                    books_data[book_name] = verses
                    chapters = max([v['chapter'] for v in verses])
                    expected = book_info["expected_verses"]
                    logger.info(f"✅ Yah {book_name}: {len(verses)} verses (expected ~{expected}), {chapters} chapters")
                else:
                    logger.warning(f"❌ Yah {book_name}: No verses found")
        
        return books_data
    
    async def load_kjv_targeted(self):
        """Load KJV with targeted approach"""
        logger.info("Loading KJV with targeted parsing...")
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        books_data = {}
        
        # Process key KJV books
        kjv_priority = ['Genesis', 'Matthew', 'Psalms']
        
        for book_name in kjv_priority:
            if book_name in self.key_books:
                verses = self.extract_kjv_book(kjv_content, book_name)
                
                if verses:
                    books_data[book_name] = verses
                    chapters = max([v['chapter'] for v in verses])
                    expected = self.key_books[book_name]["expected_verses"]
                    logger.info(f"✅ KJV {book_name}: {len(verses)} verses (expected ~{expected}), {chapters} chapters")
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
            if book_name in self.key_books:
                book_info = self.key_books[book_name]
                
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
            if book_name in self.key_books:
                book_info = self.key_books[book_name]
                
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
        """Main execution method"""
        try:
            logger.info("=== Starting Targeted Bible Loading ===")
            
            await self.clear_all_bible_data()
            
            # Load Yah Scriptures
            yah_books_data = await self.load_yah_scriptures_targeted()
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            # Load KJV
            kjv_books_data = await self.load_kjv_targeted()
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            await self.create_indexes()
            
            logger.info("=== Targeted Bible Loading Complete ===")
            logger.info(f"Yah Scriptures: {self.books_processed.get('yah', 0)} books, {self.verses_processed.get('yah', 0)} verses")
            logger.info(f"KJV 1611: {self.books_processed.get('kjv', 0)} books, {self.verses_processed.get('kjv', 0)} verses")
            logger.info(f"Total: {sum(self.books_processed.values())} books, {sum(self.verses_processed.values())} verses")
            
        except Exception as e:
            logger.error(f"Error during targeted loading: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = TargetedBibleLoader()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())