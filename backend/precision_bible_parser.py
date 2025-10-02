#!/usr/bin/env python3
"""
Precision Bible Parser - Web-Validated Content Integrity

This parser uses web-verified specifications to ensure each book has correct content:
- Genesis: 50 chapters, 1,533 verses, starts "In the beginning God created"
- Matthew: 28 chapters, 1,071 verses, starts "The book of the generation of Jesus Christ"

NO cross-contamination between books allowed.
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

class PrecisionBibleParser:
    def __init__(self):
        self.verses_processed = {"kjv": 0, "yah": 0}
        self.books_processed = {"kjv": 0, "yah": 0}
        
        # Web-verified book specifications with validation patterns
        self.book_specifications = {
            # Old Testament (web-verified)
            "Genesis": {
                "order": 1, "testament": "old", "chapters": 50, "verses": 1533,
                "yah_names": ["BERĔSHITH", "BERESHITH"],
                "kjv_patterns": [r"The First Book of Moses, called Genesis", r"Genesis"],
                "first_verse_pattern": r"In the beginning.*?created",
                "content_validators": ["heaven", "earth", "Adam", "Eve", "flood", "Noah"]
            },
            "Exodus": {
                "order": 2, "testament": "old", "chapters": 40, "verses": 1213,
                "yah_names": ["SHEMOTH", "SHEMOT"],
                "kjv_patterns": [r"The Second Book of Moses.*?Exodus", r"Exodus"],
                "first_verse_pattern": r"Now these.*?names.*?children.*?Israel",
                "content_validators": ["Egypt", "Moses", "Pharaoh", "plague", "commandments"]
            },
            "Psalms": {
                "order": 19, "testament": "old", "chapters": 150, "verses": 2461,
                "yah_names": ["TEHILLIM"],
                "kjv_patterns": [r"The Book of Psalms", r"Psalms"],
                "first_verse_pattern": r"Blessed.*?man.*?walketh.*?ungodly",
                "content_validators": ["LORD", "praise", "blessed", "righteous", "David"]
            },
            
            # New Testament (web-verified)
            "Matthew": {
                "order": 40, "testament": "new", "chapters": 28, "verses": 1071,
                "yah_names": ["MATTITHYAHU"],
                "kjv_patterns": [r"The Gospel According to St\. Matthew", r"Matthew"],
                "first_verse_pattern": r"The book.*?generation.*?Jesus Christ.*?son.*?David",
                "content_validators": ["Jesus", "Christ", "disciples", "kingdom", "heaven"]
            },
            "Mark": {
                "order": 41, "testament": "new", "chapters": 16, "verses": 678,
                "yah_names": ["MARQOS"],
                "kjv_patterns": [r"The Gospel According to St\. Mark", r"Mark"],
                "first_verse_pattern": r"The beginning.*?gospel.*?Jesus Christ",
                "content_validators": ["Jesus", "gospel", "disciples", "miracle"]
            },
            "Luke": {
                "order": 42, "testament": "new", "chapters": 24, "verses": 1151,
                "yah_names": ["LUQAS"],
                "kjv_patterns": [r"The Gospel According to St\. Luke", r"Luke"],
                "first_verse_pattern": r"Forasmuch.*?taken.*?hand.*?declaration",
                "content_validators": ["Jesus", "Theophilus", "Mary", "birth"]
            },
            "John": {
                "order": 43, "testament": "new", "chapters": 21, "verses": 879,
                "yah_names": ["YOḤANAN", "YOCHANAN"],
                "kjv_patterns": [r"The Gospel According to St\. John", r"John"],
                "first_verse_pattern": r"In the beginning was the Word",
                "content_validators": ["Word", "light", "life", "believe", "eternal"]
            },
            
            # Key Apocrypha
            "Tobit": {
                "order": 69, "testament": "apocrypha", "chapters": 14, "verses": 241,
                "yah_names": ["TOḆITH", "TOVIT"],
                "kjv_patterns": [r"Tobit"],
                "first_verse_pattern": r"book.*?words.*?Tobit",
                "content_validators": ["Tobit", "Tobias", "angel", "fish"]
            },
            "Wisdom": {
                "order": 72, "testament": "apocrypha", "chapters": 19, "verses": 434,
                "yah_names": ["ḤOḴMAH", "CHOCHMAH"],
                "kjv_patterns": [r"The Wisdom of Solomon", r"Wisdom"],
                "first_verse_pattern": r"Love.*?righteousness.*?think.*?Lord",
                "content_validators": ["wisdom", "Solomon", "righteous", "understanding"]
            }
        }
    
    def validate_book_content(self, book_name: str, verses: List[Dict]) -> bool:
        """Validate that book content is correct using web-verified patterns"""
        if book_name not in self.book_specifications:
            return False
            
        spec = self.book_specifications[book_name]
        
        if not verses:
            return False
        
        # Check first verse matches expected pattern
        first_verse_text = verses[0]['text'].lower()
        first_pattern = spec['first_verse_pattern'].lower()
        
        if not re.search(first_pattern, first_verse_text):
            logger.warning(f"❌ {book_name}: First verse doesn't match pattern. Got: {first_verse_text[:100]}...")
            return False
        
        # Check for expected content validators
        all_text = ' '.join([v['text'].lower() for v in verses[:50]]).lower()  # Check first 50 verses
        validators = spec['content_validators']
        
        found_validators = sum(1 for validator in validators if validator.lower() in all_text)
        if found_validators < len(validators) / 2:  # At least half should be present
            logger.warning(f"❌ {book_name}: Content validation failed. Found {found_validators}/{len(validators)} validators")
            return False
        
        # Check chapter count is reasonable
        max_chapter = max(v['chapter'] for v in verses)
        expected_chapters = spec['chapters']
        
        if max_chapter > expected_chapters * 1.5 or max_chapter < expected_chapters * 0.5:
            logger.warning(f"❌ {book_name}: Chapter count suspicious. Got {max_chapter}, expected {expected_chapters}")
            return False
        
        logger.info(f"✅ {book_name}: Content validation PASSED")
        return True
    
    def extract_book_with_strict_boundaries(self, content: str, book_name: str, is_yah: bool) -> List[Dict]:
        """Extract book with strict boundary detection to prevent cross-contamination"""
        spec = self.book_specifications[book_name]
        verses = []
        
        # Find book start
        if is_yah:
            patterns = spec['yah_names']
        else:
            patterns = spec['kjv_patterns']
        
        book_start = -1
        matched_pattern = None
        
        for pattern in patterns:
            if is_yah:
                # For Yah, look for exact Hebrew name matches
                regex = rf"^{re.escape(pattern)}$"
            else:
                # For KJV, use title patterns
                regex = pattern
                
            match = re.search(regex, content, re.MULTILINE | re.IGNORECASE)
            if match:
                book_start = match.end()
                matched_pattern = pattern
                break
        
        if book_start == -1:
            logger.warning(f"❌ {book_name}: Could not find start pattern")
            return verses
        
        logger.info(f"📍 {book_name}: Found start at position {book_start} using pattern '{matched_pattern}'")
        
        # Determine book end using strict boundary detection
        book_end = self.find_book_end_boundary(content, book_start, book_name, is_yah)
        
        # Extract book content
        book_content = content[book_start:book_end]
        logger.info(f"📏 {book_name}: Extracted {len(book_content)} characters ({book_end - book_start})")
        
        # Parse verses based on format
        if is_yah:
            verses = self.parse_yah_verses(book_content, book_name)
        else:
            verses = self.parse_kjv_verses(book_content, book_name)
        
        # Validate content integrity
        if not self.validate_book_content(book_name, verses):
            logger.error(f"💥 {book_name}: CONTENT VALIDATION FAILED - discarding results")
            return []
        
        # Trim to expected size to prevent contamination
        expected_verses = spec['verses']
        if len(verses) > expected_verses * 1.3:
            logger.warning(f"⚠️ {book_name}: Trimming from {len(verses)} to {int(expected_verses * 1.2)} verses")
            verses = verses[:int(expected_verses * 1.2)]
        
        return verses
    
    def find_book_end_boundary(self, content: str, book_start: int, current_book: str, is_yah: bool) -> int:
        """Find the end boundary of a book to prevent content mixing"""
        
        # Look for next book patterns
        search_content = content[book_start + 1000:]  # Skip ahead to avoid current book
        min_end = len(content)
        
        # Get all other book patterns
        for other_book, spec in self.book_specifications.items():
            if other_book == current_book:
                continue
                
            if is_yah:
                patterns = spec['yah_names']
            else:
                patterns = spec['kjv_patterns']
            
            for pattern in patterns:
                if is_yah:
                    regex = rf"^{re.escape(pattern)}$"
                else:
                    regex = pattern
                    
                match = re.search(regex, search_content, re.MULTILINE | re.IGNORECASE)
                if match:
                    candidate_end = book_start + 1000 + match.start()
                    if candidate_end < min_end:
                        min_end = candidate_end
                        logger.info(f"🔍 {current_book}: Found boundary at {candidate_end} (next: {other_book})")
        
        # Also look for clear structural breaks
        structural_patterns = [
            r'^[A-Z][A-Z\s]{10,}$',  # All caps headers
            r'^THE [A-Z]',  # "THE BOOK OF", "THE GOSPEL", etc
            r'^\d+\s*$',  # Standalone numbers (page numbers)
        ]
        
        for pattern in structural_patterns:
            for match in re.finditer(pattern, search_content, re.MULTILINE):
                candidate_end = book_start + 1000 + match.start()
                if candidate_end < min_end:
                    min_end = candidate_end
        
        # If no boundary found, use reasonable size limit
        if min_end == len(content):
            expected_verses = self.book_specifications[current_book]['verses']
            reasonable_limit = book_start + (expected_verses * 200)  # 200 chars per verse estimate
            min_end = min(reasonable_limit, len(content))
        
        return min_end
    
    def parse_yah_verses(self, book_content: str, book_name: str) -> List[Dict]:
        """Parse Yah Scriptures verses with strict formatting"""
        verses = []
        lines = book_content.split('\n')
        current_chapter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verse pattern: number + space + text
            verse_match = re.match(r'^(\d+)\s+(.+)', line)
            if verse_match:
                verse_num = int(verse_match.group(1))
                verse_text = verse_match.group(2).strip()
                
                # Quality check
                if len(verse_text) < 10 or len(verse_text) > 500:  # Reasonable verse length
                    continue
                
                # Contamination check - ensure this looks like biblical text
                if self.is_contaminated_text(verse_text, book_name):
                    continue
                
                verses.append({
                    'chapter': current_chapter,
                    'verse': verse_num,
                    'text': verse_text
                })
                
                # Chapter detection
                if verse_num == 1 and len(verses) > 1 and verses[-2]['verse'] > 1:
                    current_chapter += 1
                    verses[-1]['chapter'] = current_chapter
            
            # Standalone chapter markers
            elif re.match(r'^\d{1,3}$', line):
                chapter_candidate = int(line)
                expected_chapters = self.book_specifications[book_name]['chapters']
                if 1 <= chapter_candidate <= expected_chapters * 1.2:
                    current_chapter = chapter_candidate
        
        return verses
    
    def parse_kjv_verses(self, book_content: str, book_name: str) -> List[Dict]:
        """Parse KJV verses using {chapter:verse} format"""
        verses = []
        
        # Extract using {chapter:verse} pattern
        verse_pattern = r'\{(\d+):(\d+)\}([^{]*?)(?=\{|\Z)'
        matches = re.findall(verse_pattern, book_content, re.DOTALL)
        
        for chapter_str, verse_str, verse_text in matches:
            chapter = int(chapter_str)
            verse_num = int(verse_str)
            
            # Clean verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'Page \d+.*?(?=\w)', '', clean_text).strip()
            clean_text = re.sub(r'^[^\w]*', '', clean_text).strip()
            
            # Quality and contamination checks
            if len(clean_text) < 10 or len(clean_text) > 500:
                continue
                
            if self.is_contaminated_text(clean_text, book_name):
                continue
            
            # Chapter bounds check
            expected_chapters = self.book_specifications[book_name]['chapters']
            if chapter > expected_chapters * 1.2:
                continue
            
            verses.append({
                'chapter': chapter,
                'verse': verse_num,
                'text': clean_text
            })
        
        return verses
    
    def is_contaminated_text(self, text: str, book_name: str) -> bool:
        """Check if text contains content that shouldn't be in this book"""
        text_lower = text.lower()
        
        # Check for wrong testament content
        spec = self.book_specifications[book_name]
        testament = spec['testament']
        
        if testament == 'old':
            # Old Testament shouldn't have NT-specific terms
            nt_terms = ['jesus', 'christ', 'gospel', 'apostle', 'corinthians', 'thessalonians', 'timothy', 'ephesians']
            if any(term in text_lower for term in nt_terms):
                logger.warning(f"⚠️ {book_name}: Found NT contamination: {text[:100]}...")
                return True
        
        elif testament == 'new':
            # New Testament shouldn't have OT-specific terms in wrong context
            ot_terms = ['genesis', 'exodus', 'leviticus', 'deuteronomy']
            if any(term in text_lower for term in ot_terms):
                logger.warning(f"⚠️ {book_name}: Found OT contamination: {text[:100]}...")
                return True
        
        # Check for obvious formatting artifacts
        artifacts = ['page', 'chapter', 'book of', 'testament']
        if any(artifact in text_lower for artifact in artifacts):
            if len(text) < 50:  # Short text with artifacts is suspicious
                return True
        
        return False
    
    async def load_precision_books(self):
        """Load books with precision parsing and validation"""
        logger.info("🎯 Loading books with precision parsing...")
        
        # Load source files
        with open('/app/yah_scriptures_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            yah_content = f.read()
        
        with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
            kjv_content = f.read()
        
        with open('/app/apocrypha_complete.txt', 'r', encoding='utf-8', errors='ignore') as f:
            apocrypha_content = f.read()
        
        yah_books_data = {}
        kjv_books_data = {}
        
        # Process each book with precision
        for book_name, spec in self.book_specifications.items():
            expected_verses = spec['verses']
            expected_chapters = spec['chapters']
            testament = spec['testament']
            
            logger.info(f"🔍 Processing {book_name} (expecting {expected_chapters} chapters, {expected_verses} verses)...")
            
            # Extract for Yah Scriptures
            if testament == "apocrypha":
                source_content = apocrypha_content
            else:
                source_content = yah_content
            
            yah_verses = self.extract_book_with_strict_boundaries(source_content, book_name, is_yah=True)
            
            if yah_verses:
                yah_books_data[book_name] = yah_verses
                actual_chapters = max(v['chapter'] for v in yah_verses)
                coverage = len(yah_verses) / expected_verses * 100
                logger.info(f"✅ Yah {book_name}: {len(yah_verses)}/{expected_verses} verses ({coverage:.1f}%), {actual_chapters}/{expected_chapters} chapters")
            else:
                logger.error(f"❌ Yah {book_name}: FAILED precision extraction")
            
            # Extract for KJV
            if testament == "apocrypha":
                source_content = apocrypha_content
            else:
                source_content = kjv_content
                
            kjv_verses = self.extract_book_with_strict_boundaries(source_content, book_name, is_yah=False)
            
            if kjv_verses:
                kjv_books_data[book_name] = kjv_verses
                actual_chapters = max(v['chapter'] for v in kjv_verses)
                coverage = len(kjv_verses) / expected_verses * 100
                logger.info(f"✅ KJV {book_name}: {len(kjv_verses)}/{expected_verses} verses ({coverage:.1f}%), {actual_chapters}/{expected_chapters} chapters")
            else:
                logger.error(f"❌ KJV {book_name}: FAILED precision extraction")
        
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
            if book_name in self.book_specifications:
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
        
        batch_size = 500  # Smaller batches for precision
        verses_to_insert = []
        
        for book_name, verses in books_data.items():
            if book_name in self.book_specifications:
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
        """Main execution - precision parsing with validation"""
        try:
            logger.info("🎯 === Starting Precision Bible Parsing with Web Validation ===")
            
            await self.clear_all_bible_data()
            
            # Load books with precision parsing
            yah_books_data, kjv_books_data = await self.load_precision_books()
            
            # Load to database
            await self.load_books_to_db(yah_books_data, "yah_scriptures")
            await self.load_verses_to_db(yah_books_data, "yah_scriptures")
            
            await self.load_books_to_db(kjv_books_data, "kjv1611_divine")
            await self.load_verses_to_db(kjv_books_data, "kjv1611_divine")
            
            await self.create_indexes()
            
            logger.info("🎯 === Precision Bible Parsing Complete ===")
            logger.info(f"Yah Scriptures: {self.books_processed.get('yah', 0)} books, {self.verses_processed.get('yah', 0)} verses")
            logger.info(f"KJV 1611: {self.books_processed.get('kjv', 0)} books, {self.verses_processed.get('kjv', 0)} verses")
            logger.info(f"Total: {sum(self.books_processed.values())} books, {sum(self.verses_processed.values())} verses")
            
            # Quality assessment
            success_books = sum(self.books_processed.values())
            target_books = len(self.book_specifications) * 2  # Both versions
            
            if success_books >= target_books * 0.8:
                logger.info("🎉 EXCELLENT: High-quality precision parsing achieved!")
            elif success_books >= target_books * 0.6:
                logger.info("✅ GOOD: Substantial precision parsing achieved!")
            else:
                logger.warning("⚠️ PARTIAL: Some books need additional parsing work")
            
        except Exception as e:
            logger.error(f"💥 Error during precision parsing: {e}")
            raise
        finally:
            client.close()

async def main():
    parser = PrecisionBibleParser()
    await parser.run()

if __name__ == "__main__":
    asyncio.run(main())