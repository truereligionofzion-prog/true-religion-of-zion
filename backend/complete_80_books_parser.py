#!/usr/bin/env python3
"""
Correct Structure Parser - Based on Actual File Analysis

Now I understand the correct structure:
1. Yah Scriptures: English name (GENESIS), Hebrew name (BERĔSHITH), then numbered verses (1, 2, 3...)
2. KJV: Traditional headers with {chapter:verse} markers

This parser uses the CORRECT structure patterns identified through analysis.
"""

import asyncio
import re
import os
import logging
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Dict, List, Tuple, Optional
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

class CorrectStructureParser:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Book specifications with CORRECT patterns based on file analysis
        self.book_specifications = {
            "Genesis": {
                "order": 1, "testament": "old", "chapters": 50, "verses": 1533,
                "yah_english": "GENESIS", "yah_hebrew": "BERĔSHITH",
                "kjv_patterns": [r"The First Book of Moses, called Genesis", r"Page \d+.*Genesis"],
                "validation_words": ["beginning", "created", "heaven", "earth"]
            },
            "Exodus": {
                "order": 2, "testament": "old", "chapters": 40, "verses": 1213,
                "yah_english": "EXODUS", "yah_hebrew": "SHEMOTH", 
                "kjv_patterns": [r"The Second Book of Moses.*Exodus", r"Page \d+.*Exodus"],
                "validation_words": ["names", "children", "Israel", "Egypt"]
            },
            "Psalms": {
                "order": 19, "testament": "old", "chapters": 150, "verses": 2461,
                "yah_english": "TEHILLIM", "yah_hebrew": "TEHILLIM",
                "kjv_patterns": [r"The Book of Psalms", r"Page \d+.*Psalms"],
                "validation_words": ["blessed", "man", "walketh", "LORD"]
            },
            "Matthew": {
                "order": 40, "testament": "new", "chapters": 28, "verses": 1071,
                "yah_english": "MATTITHYAHU", "yah_hebrew": "MATTITHYAHU",
                "kjv_patterns": [r"The Gospel According to St\. Matthew", r"Page \d+.*Matthew"],
                "validation_words": ["book", "generation", "Jesus", "Christ"]
            },
            "Mark": {
                "order": 41, "testament": "new", "chapters": 16, "verses": 678,
                "yah_english": "MARQOS", "yah_hebrew": "MARQOS",
                "kjv_patterns": [r"The Gospel According to St\. Mark", r"Page \d+.*Mark"],
                "validation_words": ["beginning", "gospel", "Jesus", "Christ"]
            },
            "Tobit": {
                "order": 69, "testament": "apocrypha", "chapters": 14, "verses": 241,
                "yah_english": "TOBIT", "yah_hebrew": "TOḆITH",
                "kjv_patterns": [r"Tobit"],
                "validation_words": ["book", "words", "Tobit"]
            },
        }
    
    def find_yah_book_boundaries(self, content: str, book_name: str) -> Tuple[int, int]:
        """Find exact boundaries for Yah Scriptures books using correct structure"""
        spec = self.book_specifications[book_name]
        english_name = spec["yah_english"]
        hebrew_name = spec["yah_hebrew"]
        
        # Look for the pattern: English name on its own line, followed by Hebrew name
        # Pattern: \n{ENGLISH_NAME}\n\n{HEBREW_NAME}\n
        pattern = rf"^{re.escape(english_name)}$\s*\n[^\n]*\n\s*{re.escape(hebrew_name)}"
        
        match = re.search(pattern, content, re.MULTILINE)
        if not match:
            # Try simpler pattern - just English name
            pattern = rf"^{re.escape(english_name)}$"
            match = re.search(pattern, content, re.MULTILINE)
        
        if not match:
            logger.error(f"❌ {book_name}: Could not find start pattern for '{english_name}'")
            return -1, -1
        
        book_start = match.end()
        logger.info(f"📍 {book_name}: Found start at {book_start}")
        
        # Find end by looking for next book's English name
        next_book_names = []
        for other_book, other_spec in self.book_specifications.items():
            if other_book != book_name and other_spec["order"] > spec["order"]:
                next_book_names.append(other_spec["yah_english"])
        
        book_end = len(content)
        search_content = content[book_start:]
        
        for next_name in next_book_names:
            pattern = rf"^{re.escape(next_name)}$"
            next_match = re.search(pattern, search_content, re.MULTILINE)
            if next_match:
                candidate_end = book_start + next_match.start()
                if candidate_end < book_end:
                    book_end = candidate_end
                    logger.info(f"🔍 {book_name}: Found end boundary at {candidate_end} (next: {next_name})")
        
        # If no next book found, use reasonable estimate
        if book_end == len(content):
            expected_verses = spec["verses"]
            reasonable_size = expected_verses * 100  # 100 chars per verse estimate
            book_end = min(book_start + reasonable_size, len(content))
        
        return book_start, book_end
    
    def find_kjv_book_boundaries(self, content: str, book_name: str) -> Tuple[int, int]:
        """Find KJV book boundaries using title patterns"""
        spec = self.book_specifications[book_name]
        patterns = spec["kjv_patterns"]
        
        book_start = -1
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                book_start = match.start()
                logger.info(f"📍 {book_name}: Found KJV start at {book_start}")
                break
        
        if book_start == -1:
            return -1, -1
        
        # Find end using next book patterns
        search_content = content[book_start + 1000:]  # Skip current book header
        book_end = len(content)
        
        for other_book, other_spec in self.book_specifications.items():
            if other_book != book_name:
                for pattern in other_spec["kjv_patterns"]:
                    next_match = re.search(pattern, search_content, re.IGNORECASE)
                    if next_match:
                        candidate_end = book_start + 1000 + next_match.start()
                        if candidate_end < book_end:
                            book_end = candidate_end
        
        # Use reasonable size if no next book found
        if book_end == len(content):
            expected_verses = spec["verses"]
            reasonable_size = expected_verses * 150
            book_end = min(book_start + reasonable_size, len(content))
        
        return book_start, book_end
    
    def parse_yah_book_content(self, content: str, book_start: int, book_end: int, book_name: str) -> List[Dict]:
        """Parse Yah Scriptures book content using correct verse numbering"""
        verses = []
        book_content = content[book_start:book_end]
        lines = book_content.split('\n')
        
        current_chapter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for verse pattern: number followed by text
            verse_match = re.match(r'^(\d+)\s+(.+)', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                
                # Quality checks
                if len(verse_text) < 10:  # Too short
                    continue
                if len(verse_text) > 1000:  # Suspiciously long
                    continue
                
                # Add verse
                verses.append({
                    'chapter': current_chapter,
                    'verse': verse_num,
                    'text': verse_text
                })
                
                # Chapter detection: if we see verse 1 after other verses
                if verse_num == 1 and len(verses) > 1:
                    prev_verse = verses[-2]['verse'] if len(verses) >= 2 else 0
                    if prev_verse > 1:  # Previous verse was not 1, so this is a new chapter
                        current_chapter += 1
                        verses[-1]['chapter'] = current_chapter
        
        return verses
    
    def parse_kjv_book_content(self, content: str, book_start: int, book_end: int, book_name: str) -> List[Dict]:
        """Parse KJV book content using {chapter:verse} format"""
        verses = []
        book_content = content[book_start:book_end]
        
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
            
            # Quality checks
            if len(clean_text) < 10:
                continue
            if len(clean_text) > 1000:
                continue
            
            verses.append({
                'chapter': chapter,
                'verse': verse_num,
                'text': clean_text
            })
        
        return verses
    
    def validate_book_content(self, book_name: str, verses: List[Dict]) -> bool:
        """Validate book content using expected words"""
        if not verses:
            return False
        
        spec = self.book_specifications[book_name]
        validation_words = spec["validation_words"]
        
        # Check first few verses for validation words
        first_verses_text = ' '.join([v['text'].lower() for v in verses[:5]])
        
        found_words = sum(1 for word in validation_words if word.lower() in first_verses_text)
        
        if found_words < len(validation_words) / 2:
            logger.warning(f"⚠️ {book_name}: Content validation failed. Found {found_words}/{len(validation_words)} validation words")
            return False
        
        logger.info(f"✅ {book_name}: Content validation passed ({found_words}/{len(validation_words)} words found)")
        return True
    
    async def extract_book(self, content: str, apocrypha_content: str, book_name: str, version: str) -> List[Dict]:
        """Extract a book with proper boundary detection and validation"""
        spec = self.book_specifications[book_name]
        testament = spec["testament"]
        
        # Choose source content
        if testament == "apocrypha":
            source_content = apocrypha_content
        else:
            source_content = content
        
        # Find boundaries
        if version == "yah":
            book_start, book_end = self.find_yah_book_boundaries(source_content, book_name)
        else:
            book_start, book_end = self.find_kjv_book_boundaries(source_content, book_name)
        
        if book_start == -1:
            logger.error(f"❌ {version.upper()} {book_name}: Could not find boundaries")
            return []
        
        # Parse content
        if version == "yah":
            verses = self.parse_yah_book_content(source_content, book_start, book_end, book_name)
        else:
            verses = self.parse_kjv_book_content(source_content, book_start, book_end, book_name)
        
        # Validate content
        if not self.validate_book_content(book_name, verses):
            logger.error(f"💥 {version.upper()} {book_name}: Content validation failed")
            return []
        
        # Check verse count reasonableness
        expected_verses = spec["verses"]
        if len(verses) < expected_verses * 0.5:
            logger.warning(f"⚠️ {version.upper()} {book_name}: Low verse count {len(verses)} vs expected {expected_verses}")
        elif len(verses) > expected_verses * 1.5:
            logger.warning(f"⚠️ {version.upper()} {book_name}: High verse count {len(verses)} vs expected {expected_verses} - trimming")
            verses = verses[:int(expected_verses * 1.2)]
        
        logger.info(f"✅ {version.upper()} {book_name}: Successfully extracted {len(verses)} verses")
        return verses
    
    async def load_corrected_books(self):
        """Load books using corrected structure understanding"""
        logger.info("🎯 Loading books with corrected structure parsing...")
        
        # Load source files
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        with open('/app/apocrypha_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            apocrypha_content = f.read()
        
        yah_books_data = {}
        kjv_books_data = {}
        
        # Process each book
        for book_name in self.book_specifications.keys():
            logger.info(f"🔍 Processing {book_name}...")
            
            # Extract for Yah Scriptures
            yah_verses = await self.extract_book(yah_content, apocrypha_content, book_name, "yah")
            if yah_verses:
                yah_books_data[book_name] = yah_verses
            
            # Extract for KJV
            kjv_verses = await self.extract_book(kjv_content, apocrypha_content, book_name, "kjv")
            if kjv_verses:
                kjv_books_data[book_name] = kjv_verses
        
        return yah_books_data, kjv_books_data
    
    async def clear_all_bible_data(self):
        """Clear all existing Bible data"""
        logger.info("🧹 Clearing all existing Bible data...")
        await bible_verses_collection.delete_many({})
        await bible_books_collection.delete_many({})
        logger.info("✅ All existing Bible data cleared")
    
    async def load_books_to_db(self, books_data: Dict[str, List[Dict]], version: str):
        """Load book metadata to database"""
        logger.info(f"📚 Loading {version} books metadata...")
        
        books_to_insert = []
        for book_name, verses in books_data.items():
            spec = self.book_specifications[book_name]
            
            chapters = max([v['chapter'] for v in verses]) if verses else 0
            verse_count = len(verses)
            
            book_doc = {
                'id': str(uuid.uuid4()),
                'version': version,
                'name': book_name,
                'testament': spec['testament'],
                'order': spec['order'],
                'chapters': chapters,
                'verses': verse_count
            }
            
            books_to_insert.append(book_doc)
        
        if books_to_insert:
            await bible_books_collection.insert_many(books_to_insert)
            logger.info(f"✅ Inserted {len(books_to_insert)} {version} books")
            self.books_processed[version.split('_')[0]] = len(books_to_insert)
    
    async def load_verses_to_db(self, books_data: Dict[str, List[Dict]], version: str):
        """Load verses to database in batches"""
        logger.info(f"📝 Loading {version} verses...")
        
        batch_size = 500
        verses_to_insert = []
        
        for book_name, verses in books_data.items():
            spec = self.book_specifications[book_name]
            
            for verse_data in verses:
                verse_doc = {
                    'id': str(uuid.uuid4()),
                    'version': version,
                    'book': book_name,
                    'chapter': verse_data['chapter'],
                    'verse': verse_data['verse'],
                    'text': verse_data['text'],
                    'testament': spec['testament'],
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
        logger.info("📊 Creating database indexes...")
        
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
        
        logger.info("✅ Database indexes created")
    
    async def run(self):
        """Main execution"""
        try:
            logger.info("🎯 === Starting Corrected Structure Bible Parsing ===")
            
            await self.clear_all_bible_data()
            
            # Load books with corrected understanding
            yah_books_data, kjv_books_data = await self.load_corrected_books()
            
            # Load to database
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            await self.create_indexes()
            
            logger.info("🎯 === Corrected Structure Parsing Complete ===")
            logger.info(f"Yah Scriptures: {self.books_processed.get('yah', 0)} books, {self.verses_processed.get('yah', 0)} verses")
            logger.info(f"KJV 1611: {self.books_processed.get('kjv', 0)} books, {self.verses_processed.get('kjv', 0)} verses")
            logger.info(f"Total: {sum(self.books_processed.values())} books, {sum(self.verses_processed.values())} verses")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    parser = CorrectStructureParser()
    await parser.run()

if __name__ == "__main__":
    asyncio.run(main())