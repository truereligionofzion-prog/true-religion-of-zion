#!/usr/bin/env python3
"""
Efficient Bible Loader - Prioritizes Speed and Results

Based on web cross-reference data, focuses on getting maximum coverage quickly.
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

class EfficientBibleLoader:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Priority books for efficient loading (web-verified counts)
        self.priority_books = {
            # Old Testament essentials
            "Genesis": {"order": 1, "testament": "old", "yah_name": "BERĔSHITH", "verses": 1533, "chapters": 50},
            "Exodus": {"order": 2, "testament": "old", "yah_name": "SHEMOTH", "verses": 1213, "chapters": 40},
            "Psalms": {"order": 19, "testament": "old", "yah_name": "TEHILLIM", "verses": 2461, "chapters": 150},
            "Isaiah": {"order": 23, "testament": "old", "yah_name": "YESHAYAHU", "verses": 1292, "chapters": 66},
            "Jeremiah": {"order": 24, "testament": "old", "yah_name": "YIRMEYAHU", "verses": 1364, "chapters": 52},
            
            # New Testament complete
            "Matthew": {"order": 40, "testament": "new", "yah_name": "MATTITHYAHU", "verses": 1071, "chapters": 28},
            "Mark": {"order": 41, "testament": "new", "yah_name": "MARQOS", "verses": 678, "chapters": 16},
            "Luke": {"order": 42, "testament": "new", "yah_name": "LUQAS", "verses": 1151, "chapters": 24},
            "John": {"order": 43, "testament": "new", "yah_name": "YOḤANAN", "verses": 879, "chapters": 21},
            "Acts": {"order": 44, "testament": "new", "yah_name": "ACTS", "verses": 1007, "chapters": 28},
            "Romans": {"order": 45, "testament": "new", "yah_name": "ROMANS", "verses": 433, "chapters": 16},
            "1 Corinthians": {"order": 46, "testament": "new", "yah_name": "1 CORINTHIANS", "verses": 437, "chapters": 16},
            "Ephesians": {"order": 49, "testament": "new", "yah_name": "EPHESIANS", "verses": 155, "chapters": 6},
            "Philippians": {"order": 50, "testament": "new", "yah_name": "PHILIPPIANS", "verses": 104, "chapters": 4},
            "Hebrews": {"order": 58, "testament": "new", "yah_name": "HEBREWS", "verses": 303, "chapters": 13},
            "James": {"order": 59, "testament": "new", "yah_name": "YA'AQOḆ", "verses": 108, "chapters": 5},
            "1 Peter": {"order": 60, "testament": "new", "yah_name": "1 KĔPHA", "verses": 105, "chapters": 5},
            "Revelation": {"order": 66, "testament": "new", "yah_name": "ḤAZON", "verses": 404, "chapters": 22},
            
            # Key Apocrypha
            "Tobit": {"order": 69, "testament": "apocrypha", "yah_name": "TOḆITH", "verses": 241, "chapters": 14},
            "Wisdom": {"order": 72, "testament": "apocrypha", "yah_name": "ḤOḴMAH", "verses": 434, "chapters": 19},
            "Sirach": {"order": 73, "testament": "apocrypha", "yah_name": "BEN SIRA", "verses": 1530, "chapters": 51},
            "1 Maccabees": {"order": 79, "testament": "apocrypha", "yah_name": "1 MAQQAḆIM", "verses": 1025, "chapters": 16}
        }
    
    def extract_kjv_book_efficient(self, content: str, book_name: str) -> List[Dict]:
        """Efficient KJV book extraction using proven patterns"""
        verses = []
        
        # Proven KJV patterns from earlier success
        kjv_patterns = {
            'Genesis': [r'Page \d+.*?Genesis\b'],
            'Exodus': [r'Page \d+.*?Exodus\b'], 
            'Psalms': [r'Page \d+.*?Psalms\b'],
            'Matthew': [r'Page \d+.*?Matthew\b'],
            'Mark': [r'Page \d+.*?Mark\b'],
            'Luke': [r'Page \d+.*?Luke\b'],
            'John': [r'Page \d+.*?John\b'],
            'Acts': [r'Page \d+.*?Acts\b'],
            'Romans': [r'Page \d+.*?Romans\b'],
            'Hebrews': [r'Page \d+.*?Hebrews\b'],
            'Revelation': [r'Page \d+.*?Revelation\b'],
            'Tobit': [r'Page \d+.*?Tobit\b'],
            'Wisdom': [r'Page \d+.*?Wisdom\b']
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
        
        # Extract reasonable amount of content for the book
        expected_verses = self.priority_books[book_name]["verses"]
        book_content = content[book_start:book_start + (expected_verses * 200)]
        
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
            
            if len(clean_text) > 10:
                verses.append({
                    'chapter': chapter,
                    'verse': verse_num,
                    'text': clean_text
                })
                
                # Stop at reasonable limit to avoid parsing errors
                if len(verses) >= expected_verses * 1.5:
                    break
        
        return verses
    
    def extract_yah_book_efficient(self, content: str, book_name: str, yah_name: str) -> List[Dict]:
        """Efficient Yah Scriptures extraction using flexible patterns"""
        verses = []
        
        # Multiple patterns to find Hebrew book names
        search_patterns = [
            yah_name,  # Exact name
            yah_name.upper(),  # Uppercase
            yah_name.lower(),  # Lowercase
            re.sub(r'[^\w]', '', yah_name),  # Remove special characters
            re.sub(r'[^\w]', ' ', yah_name).strip(),  # Replace with spaces
        ]
        
        book_start = -1
        for pattern in search_patterns:
            matches = list(re.finditer(rf'\b{re.escape(pattern)}\b', content, re.IGNORECASE))
            if matches:
                book_start = matches[0].end()
                break
        
        if book_start == -1:
            return verses
        
        # Extract content with reasonable boundaries
        expected_verses = self.priority_books[book_name]["verses"]
        book_content = content[book_start:book_start + (expected_verses * 150)]
        
        # Parse verses using number-at-start pattern
        lines = book_content.split('\n')
        current_chapter = 1
        
        for line in lines:
            line = line.strip()
            
            # Verse pattern: number followed by space and text
            verse_match = re.match(r'^(\d+)\s+(.+)', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                
                if len(verse_text) > 15:
                    verses.append({
                        'chapter': current_chapter,
                        'verse': verse_num,
                        'text': verse_text
                    })
                    
                    # Chapter detection
                    if verse_num == 1 and len(verses) > 1 and verses[-2]['verse'] > 1:
                        current_chapter += 1
                        verses[-1]['chapter'] = current_chapter
                    
                    # Stop at reasonable limit
                    if len(verses) >= expected_verses * 1.2:
                        break
            
            # Standalone chapter numbers
            elif re.match(r'^\d{1,3}$', line):
                chapter_candidate = int(line)
                if 1 <= chapter_candidate <= 150 and chapter_candidate > current_chapter:
                    current_chapter = chapter_candidate
        
        return verses
    
    async def load_priority_books_efficiently(self):
        """Load priority books efficiently for both versions"""
        logger.info("Loading priority books efficiently...")
        
        # Load source files
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        with open('/app/apocrypha_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            apocrypha_content = f.read()
        
        yah_books_data = {}
        kjv_books_data = {}
        
        # Process each priority book
        for book_name, book_info in self.priority_books.items():
            expected_verses = book_info["verses"]
            expected_chapters = book_info["chapters"]
            yah_name = book_info["yah_name"]
            testament = book_info["testament"]
            
            logger.info(f"Processing {book_name} (expecting {expected_verses} verses)...")
            
            # Extract for Yah Scriptures
            if testament == "apocrypha":
                yah_verses = self.extract_yah_book_efficient(apocrypha_content, book_name, yah_name)
            else:
                yah_verses = self.extract_yah_book_efficient(yah_content, book_name, yah_name)
            
            if yah_verses:
                yah_books_data[book_name] = yah_verses
                coverage = len(yah_verses) / expected_verses * 100
                logger.info(f"✅ Yah {book_name}: {len(yah_verses)}/{expected_verses} verses ({coverage:.1f}%)")
            else:
                logger.warning(f"❌ Yah {book_name}: No verses found")
            
            # Extract for KJV
            kjv_verses = self.extract_kjv_book_efficient(kjv_content, book_name)
            
            if kjv_verses:
                kjv_books_data[book_name] = kjv_verses
                coverage = len(kjv_verses) / expected_verses * 100
                logger.info(f"✅ KJV {book_name}: {len(kjv_verses)}/{expected_verses} verses ({coverage:.1f}%)")
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
            if book_name in self.priority_books:
                book_info = self.priority_books[book_name]
                
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
            if book_name in self.priority_books:
                book_info = self.priority_books[book_name]
                
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
        """Main execution method - efficient approach"""
        try:
            logger.info("=== Starting Efficient Bible Loading ===")
            
            await self.clear_all_bible_data()
            
            # Load priority books efficiently
            yah_books_data, kjv_books_data = await self.load_priority_books_efficiently()
            
            # Load to database
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            await self.create_indexes()
            
            # Calculate expected totals for priority books
            expected_total = sum(book["verses"] for book in self.priority_books.values())
            
            logger.info("=== Efficient Bible Loading Complete ===")
            logger.info(f"Yah Scriptures: {self.books_processed.get('yah', 0)}/{len(self.priority_books)} books, {self.verses_processed.get('yah', 0)} verses")
            logger.info(f"KJV 1611: {self.books_processed.get('kjv', 0)}/{len(self.priority_books)} books, {self.verses_processed.get('kjv', 0)} verses")
            logger.info(f"Expected Total for Priority Books: {expected_total} verses")
            logger.info(f"Actual Total: {sum(self.verses_processed.values())} verses")
            
            # Coverage analysis
            total_coverage = sum(self.verses_processed.values()) / expected_total * 100
            logger.info(f"Priority Books Coverage: {total_coverage:.1f}%")
            
            if sum(self.books_processed.values()) >= 25:  # Good coverage for priority books
                logger.info("🎉 EXCELLENT PRIORITY BOOK COVERAGE ACHIEVED!")
            elif sum(self.books_processed.values()) >= 15:
                logger.info("✅ GOOD PRIORITY BOOK COVERAGE ACHIEVED!")
            else:
                logger.warning("⚠️  Limited coverage - may need parsing improvements")
            
        except Exception as e:
            logger.error(f"Error during efficient loading: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = EfficientBibleLoader()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())