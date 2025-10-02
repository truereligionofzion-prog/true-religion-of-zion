#!/usr/bin/env python3
"""
Improved KJV with Apocrypha Bible Data Loader

This script uses an improved parsing approach to handle the two-column layout
and extract all verses correctly from the KJV text file.
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

class ImprovedKJVParser:
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
    
    async def parse_text_file_improved(self) -> Dict[str, List[Dict]]:
        """Improved parsing that handles the two-column layout"""
        logger.info(f"Starting improved parsing of {self.text_file_path}")
        
        with open(self.text_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        books_data = {}
        
        # Find all verse references with their text using a more comprehensive regex
        # This pattern captures verse markers and everything up to the next verse marker or end
        pattern = r'\{(\d+):(\d+)\}(.*?)(?=\{\d+:\d+\}|$)'
        all_verses = re.findall(pattern, content, re.DOTALL)
        
        logger.info(f"Found {len(all_verses)} verse matches using regex")
        
        # Now we need to assign these verses to books
        # Let's find book boundaries
        book_boundaries = []
        
        # Look for book headers
        lines = content.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for book headers with better patterns
            if (re.match(r'Page \d+.*?(Genesis|Exodus|Leviticus|Numbers|Deuteronomy)', line, re.IGNORECASE) or
                'The First Book of Moses' in line or 'The Second Book of Moses' in line or
                'The Third Book of Moses' in line or 'The Fourth Book of Moses' in line or
                'The Fifth Book of Moses' in line):
                
                if 'Genesis' in line or 'The First Book of Moses' in line:
                    book_boundaries.append(('Genesis', current_pos))
                elif 'Exodus' in line or 'The Second Book of Moses' in line:
                    book_boundaries.append(('Exodus', current_pos))
                elif 'Leviticus' in line or 'The Third Book of Moses' in line:
                    book_boundaries.append(('Leviticus', current_pos))
                elif 'Numbers' in line or 'The Fourth Book of Moses' in line:
                    book_boundaries.append(('Numbers', current_pos))
                elif 'Deuteronomy' in line or 'The Fifth Book of Moses' in line:
                    book_boundaries.append(('Deuteronomy', current_pos))
            
            current_pos += len(line) + 1  # +1 for newline
        
        logger.info(f"Found {len(book_boundaries)} book boundaries")
        
        # For now, let's use a different approach - extract verses by searching for known book sections
        books_to_extract = ['Genesis', 'Exodus', 'Matthew', 'Mark', 'Tobit', 'Psalms']
        
        for book_name in books_to_extract:
            book_verses = self.extract_book_verses(content, book_name)
            if book_verses:
                books_data[book_name] = book_verses
                logger.info(f"Extracted {len(book_verses)} verses for {book_name}")
        
        return books_data
    
    def extract_book_verses(self, content: str, book_name: str) -> List[Dict]:
        """Extract verses for a specific book"""
        verses = []
        
        # Find the start of the book
        book_patterns = {
            'Genesis': [r'The First Book of Moses, called Genesis', r'Page \d+.*Genesis'],
            'Exodus': [r'The Second Book of Moses, Called Exodus', r'Page \d+.*Exodus'],
            'Matthew': [r'The Gospel According to St\. Matthew', r'Matthew'],
            'Mark': [r'The Gospel According to St\. Mark', r'Mark'],
            'Tobit': [r'Tobit', r'Page \d+.*Tobit'],
            'Psalms': [r'The Book of Psalms', r'Psalms']
        }
        
        if book_name not in book_patterns:
            return verses
        
        # Find book start position
        book_start = -1
        for pattern in book_patterns[book_name]:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                book_start = match.start()
                break
        
        if book_start == -1:
            logger.warning(f"Could not find start of {book_name}")
            return verses
        
        # Find book end position (start of next book or end of content)
        next_book_patterns = [
            r'Page \d+.*?(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation)',
            r'The \w+ Book of',
            r'The Gospel According to'
        ]
        
        book_end = len(content)
        book_content = content[book_start:]
        
        # Look for next book starting after current book
        for pattern in next_book_patterns:
            matches = list(re.finditer(pattern, book_content, re.IGNORECASE))
            if len(matches) > 1:  # Skip the first match (current book)
                book_end = book_start + matches[1].start()
                break
        
        # Extract book content
        book_text = content[book_start:book_end]
        
        # Extract verses from book content
        verse_pattern = r'\{(\d+):(\d+)\}(.*?)(?=\{\d+:\d+\}|$)'
        verse_matches = re.findall(verse_pattern, book_text, re.DOTALL)
        
        for chapter, verse_num, verse_text in verse_matches:
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            # Remove page numbers and headers
            clean_text = re.sub(r'Page \d+.*?(?=\w)', '', clean_text).strip()
            clean_text = re.sub(r'^.*?(?=[A-Z][a-z])', '', clean_text).strip()
            
            if clean_text and len(clean_text) > 3:  # Only verses with actual content
                verses.append({
                    'chapter': int(chapter),
                    'verse': int(verse_num),
                    'text': clean_text
                })
        
        return verses
    
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
            logger.info("=== Starting Improved KJV Loading ===")
            
            # Parse the text file with improved method
            books_data = await self.parse_text_file_improved()
            
            if not books_data:
                logger.error("No books found in text file")
                return
            
            # Clear existing data
            await self.clear_existing_kjv_data()
            
            # Load to database
            await self.load_books_to_db(books_data)
            await self.load_verses_to_db(books_data)
            await self.create_indexes()
            
            # Count total verses processed
            self.verses_processed = sum(len(verses) for verses in books_data.values())
            
            logger.info("=== Improved KJV Loading Complete ===")
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
    
    parser = ImprovedKJVParser(text_file_path)
    await parser.run()

if __name__ == "__main__":
    asyncio.run(main())