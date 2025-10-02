#!/usr/bin/env python3
"""
Complete KJV with Apocrypha Bible Data Loader

This script loads ALL books from the KJV with Apocrypha text file
to create a complete Bible dataset in the database.
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

class CompleteKJVLoader:
    def __init__(self, text_file_path: str):
        self.text_file_path = text_file_path
        self.verses_processed = 0
        self.books_processed = 0
        
        # Complete Bible book order and testament mapping
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
            
            # Apocrypha (67-81)
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
        
        # Book name patterns for identification
        self.book_patterns = {
            'Genesis': [r'The First Book of Moses, called Genesis', r'Genesis', r'Page \d+.*Genesis'],
            'Exodus': [r'The Second Book of Moses, Called Exodus', r'Exodus', r'Page \d+.*Exodus'],
            'Leviticus': [r'The Third Book of Moses, called Leviticus', r'Leviticus', r'Page \d+.*Leviticus'],
            'Numbers': [r'The Fourth Book of Moses, called Numbers', r'Numbers', r'Page \d+.*Numbers'],
            'Deuteronomy': [r'The Fifth Book of Moses, called Deuteronomy', r'Deuteronomy', r'Page \d+.*Deuteronomy'],
            'Joshua': [r'The Book of Joshua', r'Joshua', r'Page \d+.*Joshua'],
            'Judges': [r'The Book of Judges', r'Judges', r'Page \d+.*Judges'],
            'Ruth': [r'The Book of Ruth', r'Ruth', r'Page \d+.*Ruth'],
            '1 Samuel': [r'The First Book of Samuel', r'1 Samuel', r'Page \d+.*Samuel'],
            '2 Samuel': [r'The Second Book of Samuel', r'2 Samuel'],
            '1 Kings': [r'The First Book of the Kings', r'1 Kings', r'Page \d+.*Kings'],
            '2 Kings': [r'The Second Book of the Kings', r'2 Kings'],
            '1 Chronicles': [r'The First Book of the Chronicles', r'1 Chronicles', r'Page \d+.*Chronicles'],
            '2 Chronicles': [r'The Second Book of the Chronicles', r'2 Chronicles'],
            'Ezra': [r'Ezra', r'Page \d+.*Ezra'],
            'Nehemiah': [r'The Book of Nehemiah', r'Nehemiah', r'Page \d+.*Nehemiah'],
            'Esther': [r'The Book of Esther', r'Esther', r'Page \d+.*Esther'],
            'Job': [r'The Book of Job', r'Job', r'Page \d+.*Job'],
            'Psalms': [r'The Book of Psalms', r'Psalms', r'Page \d+.*Psalms'],
            'Proverbs': [r'The Proverbs', r'Proverbs', r'Page \d+.*Proverbs'],
            'Ecclesiastes': [r'Ecclesiastes', r'Page \d+.*Ecclesiastes'],
            'Song of Songs': [r'The Song of Songs', r'Song of Songs', r'Page \d+.*Song'],
            'Isaiah': [r'The Book of the Prophet Isaiah', r'Isaiah', r'Page \d+.*Isaiah'],
            'Jeremiah': [r'The Book of the Prophet Jeremiah', r'Jeremiah', r'Page \d+.*Jeremiah'],
            'Lamentations': [r'The Lamentations of Jeremiah', r'Lamentations', r'Page \d+.*Lamentations'],
            'Ezekiel': [r'The Book of the Prophet Ezekiel', r'Ezekiel', r'Page \d+.*Ezekiel'],
            'Daniel': [r'The Book of Daniel', r'Daniel', r'Page \d+.*Daniel'],
            'Hosea': [r'Hosea', r'Page \d+.*Hosea'],
            'Joel': [r'Joel', r'Page \d+.*Joel'],
            'Amos': [r'Amos', r'Page \d+.*Amos'],
            'Obadiah': [r'Obadiah', r'Page \d+.*Obadiah'],
            'Jonah': [r'Jonah', r'Page \d+.*Jonah'],
            'Micah': [r'Micah', r'Page \d+.*Micah'],
            'Nahum': [r'Nahum', r'Page \d+.*Nahum'],
            'Habakkuk': [r'Habakkuk', r'Page \d+.*Habakkuk'],
            'Zephaniah': [r'Zephaniah', r'Page \d+.*Zephaniah'],
            'Haggai': [r'Haggai', r'Page \d+.*Haggai'],
            'Zechariah': [r'Zechariah', r'Page \d+.*Zechariah'],
            'Malachi': [r'Malachi', r'Page \d+.*Malachi'],
            
            # New Testament
            'Matthew': [r'The Gospel According to St\. Matthew', r'Matthew', r'Page \d+.*Matthew'],
            'Mark': [r'The Gospel According to St\. Mark', r'Mark', r'Page \d+.*Mark'],
            'Luke': [r'The Gospel According to St\. Luke', r'Luke', r'Page \d+.*Luke'],
            'John': [r'The Gospel According to St\. John', r'John', r'Page \d+.*John'],
            'Acts': [r'The Acts of the Apostles', r'Acts', r'Page \d+.*Acts'],
            'Romans': [r'The Epistle of Paul the Apostle to the Romans', r'Romans', r'Page \d+.*Romans'],
            '1 Corinthians': [r'The First Epistle of Paul the Apostle to the Corinthians', r'1 Corinthians', r'Page \d+.*Corinthians'],
            '2 Corinthians': [r'The Second Epistle of Paul the Apostle to the Corinthians', r'2 Corinthians'],
            'Galatians': [r'The Epistle of Paul the Apostle to the Galatians', r'Galatians', r'Page \d+.*Galatians'],
            'Ephesians': [r'The Epistle of Paul the Apostle to the Ephesians', r'Ephesians', r'Page \d+.*Ephesians'],
            'Philippians': [r'The Epistle of Paul the Apostle to the Philippians', r'Philippians', r'Page \d+.*Philippians'],
            'Colossians': [r'The Epistle of Paul the Apostle to the Colossians', r'Colossians', r'Page \d+.*Colossians'],
            '1 Thessalonians': [r'The First Epistle of Paul the Apostle to the Thessalonians', r'1 Thessalonians', r'Page \d+.*Thessalonians'],
            '2 Thessalonians': [r'The Second Epistle of Paul the Apostle to the Thessalonians', r'2 Thessalonians'],
            '1 Timothy': [r'The First Epistle of Paul the Apostle to Timothy', r'1 Timothy', r'Page \d+.*Timothy'],
            '2 Timothy': [r'The Second Epistle of Paul the Apostle to Timothy', r'2 Timothy'],
            'Titus': [r'The Epistle of Paul to Titus', r'Titus', r'Page \d+.*Titus'],
            'Philemon': [r'The Epistle of Paul to Philemon', r'Philemon', r'Page \d+.*Philemon'],
            'Hebrews': [r'The Epistle of Paul the Apostle to the Hebrews', r'Hebrews', r'Page \d+.*Hebrews'],
            'James': [r'The General Epistle of James', r'James', r'Page \d+.*James'],
            '1 Peter': [r'The First Epistle General of Peter', r'1 Peter', r'Page \d+.*Peter'],
            '2 Peter': [r'The Second Epistle General of Peter', r'2 Peter'],
            '1 John': [r'The First Epistle General of John', r'1 John', r'Page \d+.*John'],
            '2 John': [r'The Second Epistle of John', r'2 John'],
            '3 John': [r'The Third Epistle of John', r'3 John'],
            'Jude': [r'The General Epistle of Jude', r'Jude', r'Page \d+.*Jude'],
            'Revelation': [r'The Revelation of St\. John the Divine', r'Revelation', r'Page \d+.*Revelation'],
            
            # Apocrypha
            'Tobit': [r'Tobit', r'Page \d+.*Tobit'],
            'Judith': [r'Judith', r'Page \d+.*Judith'],
            'Esther (Greek)': [r'Esther \(Greek\)', r'Page \d+.*Esther.*Greek'],
            'Wisdom': [r'The Wisdom of Solomon', r'Wisdom', r'Page \d+.*Wisdom'],
            'Sirach': [r'The Wisdom of Jesus the Son of Sirach', r'Sirach', r'Ecclesiasticus', r'Page \d+.*Sirach'],
            'Baruch': [r'Baruch', r'Page \d+.*Baruch'],
            'Letter of Jeremiah': [r'The Letter of Jeremiah', r'Letter of Jeremiah'],
            'Prayer of Azariah': [r'Prayer of Azariah', r'Song of the Three'],
            'Susanna': [r'Susanna', r'Page \d+.*Susanna'],
            'Bel and the Dragon': [r'Bel and the Dragon', r'Page \d+.*Bel'],
            '1 Maccabees': [r'The First Book of the Maccabees', r'1 Maccabees', r'Page \d+.*Maccabees'],
            '2 Maccabees': [r'The Second Book of the Maccabees', r'2 Maccabees'],
            '1 Esdras': [r'The First Book of Esdras', r'1 Esdras', r'Page \d+.*Esdras'],
            '2 Esdras': [r'The Second Book of Esdras', r'2 Esdras'],
            'Prayer of Manasseh': [r'The Prayer of Manasses', r'Prayer of Manasseh']
        }
    
    def extract_book_verses(self, content: str, book_name: str) -> List[Dict]:
        """Extract verses for a specific book with improved logic"""
        verses = []
        
        if book_name not in self.book_patterns:
            return verses
        
        # Find the start of the book
        book_start = -1
        for pattern in self.book_patterns[book_name]:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                book_start = match.start()
                break
        
        if book_start == -1:
            logger.warning(f"Could not find start of {book_name}")
            return verses
        
        # Find book end position (start of next book)
        book_content = content[book_start:]
        
        # Look for the next book boundary
        next_book_start = len(book_content)
        
        # Get all book names ordered by their position in the file
        all_patterns = []
        for bname, patterns in self.book_patterns.items():
            if bname != book_name:
                all_patterns.extend(patterns)
        
        # Find the closest next book
        for pattern in all_patterns:
            matches = list(re.finditer(pattern, book_content, re.IGNORECASE))
            if matches:
                next_start = matches[0].start()
                if next_start > 100:  # Give some buffer to avoid finding current book
                    next_book_start = min(next_book_start, next_start)
        
        # Extract book content
        book_text = book_content[:next_book_start]
        
        # Extract verses from book content
        verse_pattern = r'\{(\d+):(\d+)\}(.*?)(?=\{\d+:\d+\}|$)'
        verse_matches = re.findall(verse_pattern, book_text, re.DOTALL)
        
        for chapter, verse_num, verse_text in verse_matches:
            # Clean the verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            # Remove page numbers and headers that might be mixed in
            clean_text = re.sub(r'Page \d+.*?(?=\w)', '', clean_text).strip()
            clean_text = re.sub(r'^.*?(?=[A-Z][a-z])', '', clean_text).strip()
            
            if clean_text and len(clean_text) > 3:  # Only verses with actual content
                verses.append({
                    'chapter': int(chapter),
                    'verse': int(verse_num),
                    'text': clean_text
                })
        
        return verses
    
    async def parse_all_books(self) -> Dict[str, List[Dict]]:
        """Parse all books from the KJV text file"""
        logger.info("Starting to parse ALL books from KJV file...")
        
        with open(self.text_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        books_data = {}
        
        # Process all books in order
        for book_name in self.book_order_testament.keys():
            if book_name == 'Ecclesiasticus':  # Skip duplicate (same as Sirach)
                continue
                
            logger.info(f"Processing {book_name}...")
            book_verses = self.extract_book_verses(content, book_name)
            
            if book_verses:
                books_data[book_name] = book_verses
                logger.info(f"✅ {book_name}: {len(book_verses)} verses")
            else:
                logger.warning(f"❌ {book_name}: No verses found")
        
        total_verses = sum(len(verses) for verses in books_data.values())
        logger.info(f"Parsing complete. Found {len(books_data)} books, {total_verses} total verses")
        
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
                logger.info(f"Prepared: {book_name} ({verse_count} verses, {chapters} chapters)")
        
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
            logger.info("=== Starting COMPLETE KJV Loading ===")
            
            # Parse ALL books from the text file
            books_data = await self.parse_all_books()
            
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
            
            logger.info("=== COMPLETE KJV Loading Complete ===")
            logger.info(f"Books processed: {self.books_processed}")
            logger.info(f"Verses processed: {self.verses_processed}")
            
            # Print summary by testament
            ot_books = [b for b in books_data.keys() if self.book_order_testament.get(b, {}).get('testament') == 'old']
            nt_books = [b for b in books_data.keys() if self.book_order_testament.get(b, {}).get('testament') == 'new']
            ap_books = [b for b in books_data.keys() if self.book_order_testament.get(b, {}).get('testament') == 'apocrypha']
            
            ot_verses = sum(len(books_data[b]) for b in ot_books)
            nt_verses = sum(len(books_data[b]) for b in nt_books)
            ap_verses = sum(len(books_data[b]) for b in ap_books)
            
            logger.info(f"Testament Summary:")
            logger.info(f"  Old Testament: {len(ot_books)} books, {ot_verses} verses")
            logger.info(f"  New Testament: {len(nt_books)} books, {nt_verses} verses")
            logger.info(f"  Apocrypha: {len(ap_books)} books, {ap_verses} verses")
            
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
    
    loader = CompleteKJVLoader(text_file_path)
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())