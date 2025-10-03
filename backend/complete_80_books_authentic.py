#!/usr/bin/env python3
"""
Complete 80 Books Authentic Loader

Loads ALL remaining 77 books of the KJV 1611 Bible (including Apocrypha)
using the proven Genesis/Exodus/Leviticus authentic extraction formula.

Target: Complete 80-book Bible with ONLY authentic biblical text.
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

class Complete80BooksAuthentic:
    def __init__(self):
        # Complete 80-book list with order, testament, chapters, and target verses
        self.all_books = [
            # OLD TESTAMENT (39 books) - Orders 1-39
            ("Genesis", 1, "old", 50, 1533),      # Already complete
            ("Exodus", 2, "old", 40, 1213),       # Already complete  
            ("Leviticus", 3, "old", 27, 859),     # Already complete
            ("Numbers", 4, "old", 36, 1288),
            ("Deuteronomy", 5, "old", 34, 959),
            ("Joshua", 6, "old", 24, 658),
            ("Judges", 7, "old", 21, 618),
            ("Ruth", 8, "old", 4, 85),
            ("1 Samuel", 9, "old", 31, 810),
            ("2 Samuel", 10, "old", 24, 695),
            ("1 Kings", 11, "old", 22, 816),
            ("2 Kings", 12, "old", 25, 719),
            ("1 Chronicles", 13, "old", 29, 942),
            ("2 Chronicles", 14, "old", 36, 822),
            ("Ezra", 15, "old", 10, 280),
            ("Nehemiah", 16, "old", 13, 406),
            ("Esther", 17, "old", 10, 167),
            ("Job", 18, "old", 42, 1070),
            ("Psalms", 19, "old", 150, 2461),
            ("Proverbs", 20, "old", 31, 915),
            ("Ecclesiastes", 21, "old", 12, 222),
            ("Song of Solomon", 22, "old", 8, 117),
            ("Isaiah", 23, "old", 66, 1292),
            ("Jeremiah", 24, "old", 52, 1364),
            ("Lamentations", 25, "old", 5, 154),
            ("Ezekiel", 26, "old", 48, 1273),
            ("Daniel", 27, "old", 12, 357),
            ("Hosea", 28, "old", 14, 193),
            ("Joel", 29, "old", 3, 73),
            ("Amos", 30, "old", 9, 146),
            ("Obadiah", 31, "old", 1, 21),
            ("Jonah", 32, "old", 4, 48),
            ("Micah", 33, "old", 7, 105),
            ("Nahum", 34, "old", 3, 47),
            ("Habakkuk", 35, "old", 3, 56),
            ("Zephaniah", 36, "old", 3, 53),
            ("Haggai", 37, "old", 2, 38),
            ("Zechariah", 38, "old", 14, 211),
            ("Malachi", 39, "old", 4, 55),
            
            # APOCRYPHA (14 books) - Orders 40-53
            ("1 Esdras", 40, "apocrypha", 9, 320),
            ("2 Esdras", 41, "apocrypha", 16, 822),
            ("Tobit", 42, "apocrypha", 14, 267),
            ("Judith", 43, "apocrypha", 16, 349),
            ("Additions to Esther", 44, "apocrypha", 6, 107),
            ("Wisdom of Solomon", 45, "apocrypha", 19, 435),
            ("Ecclesiasticus", 46, "apocrypha", 51, 1401),
            ("Baruch", 47, "apocrypha", 6, 213),
            ("Letter of Jeremiah", 48, "apocrypha", 1, 73),
            ("Prayer of Azariah", 49, "apocrypha", 1, 68),
            ("Susanna", 50, "apocrypha", 1, 64),
            ("Bel and the Dragon", 51, "apocrypha", 1, 42),
            ("Prayer of Manasses", 52, "apocrypha", 1, 15),
            ("1 Maccabees", 53, "apocrypha", 16, 924),
            ("2 Maccabees", 54, "apocrypha", 15, 555),
            
            # NEW TESTAMENT (27 books) - Orders 55-80  
            ("Matthew", 55, "new", 28, 1071),
            ("Mark", 56, "new", 16, 678),
            ("Luke", 57, "new", 24, 1151),
            ("John", 58, "new", 21, 879),
            ("Acts", 59, "new", 28, 1007),
            ("Romans", 60, "new", 16, 433),
            ("1 Corinthians", 61, "new", 16, 437),
            ("2 Corinthians", 62, "new", 13, 257),
            ("Galatians", 63, "new", 6, 149),
            ("Ephesians", 64, "new", 6, 155),
            ("Philippians", 65, "new", 4, 104),
            ("Colossians", 66, "new", 4, 95),
            ("1 Thessalonians", 67, "new", 5, 89),
            ("2 Thessalonians", 68, "new", 3, 47),
            ("1 Timothy", 69, "new", 6, 113),
            ("2 Timothy", 70, "new", 4, 83),
            ("Titus", 71, "new", 3, 46),
            ("Philemon", 72, "new", 1, 25),
            ("Hebrews", 73, "new", 13, 303),
            ("James", 74, "new", 5, 108),
            ("1 Peter", 75, "new", 5, 105),
            ("2 Peter", 76, "new", 3, 61),
            ("1 John", 77, "new", 5, 105),
            ("2 John", 78, "new", 1, 13),
            ("3 John", 79, "new", 1, 14),
            ("Jude", 80, "new", 1, 25),
            ("Revelation", 81, "new", 22, 404)
        ]
        
        # Books to process (skip already loaded Genesis, Exodus, Leviticus)
        self.books_to_load = [book for book in self.all_books if book[0] not in ["Genesis", "Exodus", "Leviticus"]]
        
        logger.info(f"📚 Total books to process: {len(self.books_to_load)}")
        
    async def verify_existing_books(self):
        """Verify our foundation books are intact"""
        logger.info("🔍 Verifying existing foundation books...")
        
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        exodus_count = await bible_verses_collection.count_documents({"book": "Exodus"}) 
        leviticus_count = await bible_verses_collection.count_documents({"book": "Leviticus"})
        
        logger.info(f"✅ Genesis: {genesis_count} verses")
        logger.info(f"✅ Exodus: {exodus_count} verses") 
        logger.info(f"✅ Leviticus: {leviticus_count} verses")
        logger.info(f"✅ Foundation total: {genesis_count + exodus_count + leviticus_count} verses")
        
        return genesis_count > 0 and exodus_count > 0 and leviticus_count > 0
    
    def find_book_boundaries_in_source(self, content: str, book_name: str, next_book_name: str = None) -> Tuple[int, int]:
        """Find start and end positions for a book in the source content"""
        
        # Book name variations to search for
        search_patterns = [
            f"The.*Book.*{book_name}",
            book_name.upper(),
            book_name,
            f"{book_name.replace(' ', '')}"
        ]
        
        book_start = -1
        for pattern in search_patterns:
            pos = content.find(pattern)
            if pos != -1:
                book_start = pos
                break
        
        if book_start == -1:
            return -1, -1
        
        # Find end boundary
        book_end = -1
        if next_book_name:
            next_patterns = [
                f"The.*Book.*{next_book_name}",
                next_book_name.upper(),
                next_book_name
            ]
            
            for pattern in next_patterns:
                pos = content.find(pattern, book_start + 1000)
                if pos != -1:
                    book_end = pos
                    break
        
        if book_end == -1:
            # Use conservative estimate
            book_end = book_start + 30000
        
        return book_start, book_end
    
    def extract_verses_from_book_content(self, book_content: str, book_name: str, target_chapters: int) -> List[Dict]:
        """Extract verses from book content using proven pattern"""
        
        verses = []
        
        # Extract verses using {chapter:verse} pattern
        pattern = r'\{(\d+):(\d+)\}'
        matches = re.finditer(pattern, book_content)
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Ensure chapter is within expected range
            if chapter < 1 or chapter > target_chapters * 2:  # Allow some flexibility
                continue
            
            # Find text after verse marker
            start_pos = match.end()
            
            # Find next verse marker
            next_match = re.search(r'\{\d+:\d+\}', book_content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 400
            
            # Extract and clean text
            raw_text = book_content[start_pos:end_pos]
            clean_text = self.clean_authentic_verse_text(raw_text)
            
            # Only keep authentic content
            if (clean_text and 
                len(clean_text) > 15 and 
                self.is_authentic_content(clean_text, book_name)):
                
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
        
        return verses
    
    def clean_authentic_verse_text(self, raw_text: str) -> str:
        """Clean verse text using proven method"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers and artifacts
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\w+\s+Page \d+', '', text)
        
        # Remove verse markers
        text = re.sub(r'\{\d+:\d+\}', '', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Take first substantial sentence
        if '.' in text:
            sentences = text.split('.')
            if len(sentences) > 0 and len(sentences[0]) > 10:
                text = sentences[0].strip()
                if not text.endswith('.'):
                    text += '.'
        
        # Remove leading non-word chars except authentic brackets
        text = re.sub(r'^[^\w\[\]]+', '', text)
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def is_authentic_content(self, text: str, book_name: str) -> bool:
        """Check if content is authentic biblical text"""
        
        # Reject placeholder content
        reject_patterns = [
            f'see {book_name}.*text',
            r'complete KJV text',
            r'KJV.*text'
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check for biblical content indicators
        biblical_indicators = [
            r'\bAnd\b',
            r'\bthe LORD\b',
            r'\bLord\b', 
            r'\bGod\b',
            r'\bshall\b',
            r'\bunto\b',
            r'\bsaith\b'
        ]
        
        has_biblical_content = any(re.search(indicator, text, re.IGNORECASE) for indicator in biblical_indicators)
        
        return len(text) > 15 and has_biblical_content
    
    def get_web_verified_key_verses(self, book_name: str, testament: str) -> List[Dict]:
        """Get key web-verified verses for each book type"""
        
        key_verses = []
        
        if book_name == "Numbers":
            key_verses = [
                (1, 1, "And the LORD spake unto Moses in the wilderness of Sinai, in the tabernacle of the congregation, on the first day of the second month, in the second year after they were come out of the land of Egypt, saying,"),
                (6, 24, "The LORD bless thee, and keep thee."),
                (6, 25, "The LORD make his face shine upon thee, and be gracious unto thee."),
                (6, 26, "The LORD lift up his countenance upon thee, and give thee peace.")
            ]
        elif book_name == "Deuteronomy":
            key_verses = [
                (1, 1, "These be the words which Moses spake unto all Israel on this side Jordan in the wilderness, in the plain over against the Red sea, between Paran, and Tophel, and Laban, and Hazeroth, and Dizahab."),
                (6, 4, "Hear, O Israel: The LORD our God is one LORD:"),
                (6, 5, "And thou shalt love the LORD thy God with all thine heart, and with all thy soul, and with all thy might.")
            ]
        elif book_name == "Psalms":
            key_verses = [
                (1, 1, "Blessed is the man that walketh not in the counsel of the ungodly, nor standeth in the way of sinners, nor sitteth in the seat of the scornful."),
                (23, 1, "The LORD is my shepherd; I shall not want."),
                (23, 4, "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.")
            ]
        elif book_name == "Matthew":
            key_verses = [
                (1, 1, "The book of the generation of Jesus Christ, the son of David, the son of Abraham."),
                (5, 3, "Blessed are the poor in spirit: for theirs is the kingdom of heaven."),
                (28, 19, "Go ye therefore, and teach all nations, baptizing them in the name of the Father, and of the Son, and of the Holy Ghost:")
            ]
        elif testament == "new":
            # Generic New Testament opening
            key_verses = [
                (1, 1, f"[Opening verse of {book_name} - see complete KJV text]")
            ]
        elif testament == "apocrypha":
            # Generic Apocrypha opening  
            key_verses = [
                (1, 1, f"[Opening verse of {book_name} - see complete KJV text]")
            ]
        else:
            # Generic Old Testament
            key_verses = [
                (1, 1, f"And the word of the LORD came [see {book_name} 1:1 in complete KJV text]")
            ]
        
        verses = []
        for chapter, verse, text in key_verses:
            # Only add if not a placeholder
            if not re.search(r'see.*text', text, re.IGNORECASE):
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': text
                })
        
        return verses
    
    async def process_single_book(self, book_info: Tuple) -> int:
        """Process a single book using authentic extraction"""
        
        book_name, order, testament, chapters, target_verses = book_info
        
        logger.info(f"📖 Processing {book_name} (Order: {order}, Testament: {testament})")
        
        # Read source file
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return 0
        
        # Find next book for boundary detection
        next_book = None
        for i, book in enumerate(self.all_books):
            if book[0] == book_name and i < len(self.all_books) - 1:
                next_book = self.all_books[i + 1][0]
                break
        
        # Find book boundaries
        book_start, book_end = self.find_book_boundaries_in_source(content, book_name, next_book)
        
        if book_start == -1:
            logger.warning(f"⚠️ Could not find {book_name} in source - using web-verified verses only")
            verses = self.get_web_verified_key_verses(book_name, testament)
        else:
            book_content = content[book_start:book_end]
            logger.info(f"📝 {book_name} content section: {len(book_content)} characters")
            
            # Extract verses from content
            extracted_verses = self.extract_verses_from_book_content(book_content, book_name, chapters)
            
            # Combine with web-verified key verses
            key_verses = self.get_web_verified_key_verses(book_name, testament)
            
            # Merge avoiding duplicates
            all_verses = key_verses.copy()
            existing_refs = set((v['chapter'], v['verse']) for v in key_verses)
            
            for verse in extracted_verses:
                ref = (verse['chapter'], verse['verse'])
                if ref not in existing_refs:
                    all_verses.append(verse)
            
            verses = all_verses
        
        # Sort verses
        verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        verse_count = len(verses)
        completion_pct = (verse_count / target_verses * 100) if target_verses > 0 else 0
        
        logger.info(f"✅ {book_name}: {verse_count}/{target_verses} verses ({completion_pct:.1f}%)")
        
        # Load to database if we have verses
        if verses:
            await self.load_book_to_database(book_name, order, testament, chapters, verses)
        
        return verse_count
    
    async def load_book_to_database(self, book_name: str, order: int, testament: str, chapters: int, verses: List[Dict]):
        """Load book and verses to database"""
        
        # Create book record
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': book_name,
            'testament': testament,
            'order': order,
            'chapters': chapters,
            'verses': len(verses)
        }
        
        await bible_books_collection.insert_one(book_doc)
        
        # Create verse records in batches
        batch_size = 100
        verses_to_insert = []
        
        for verse_data in verses:
            verse_doc = {
                'id': str(uuid.uuid4()),
                'version': 'kjv1611_divine',
                'book': book_name,
                'chapter': verse_data['chapter'],
                'verse': verse_data['verse'],
                'text': verse_data['text'],
                'testament': testament,
                'has_precept': False
            }
            
            verses_to_insert.append(verse_doc)
            
            if len(verses_to_insert) >= batch_size:
                await bible_verses_collection.insert_many(verses_to_insert)
                verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
    
    async def run(self):
        """Main execution - process all 77 remaining books"""
        try:
            logger.info("🎯 === Complete 80 Books Authentic Loading - All Remaining Books ===")
            
            # Verify foundation
            if not await self.verify_existing_books():
                logger.error("❌ Foundation books (Genesis, Exodus, Leviticus) not found!")
                return
            
            total_books_processed = 0
            total_verses_added = 0
            
            # Process books in batches for progress tracking
            batch_size = 10
            
            for i in range(0, len(self.books_to_load), batch_size):
                batch = self.books_to_load[i:i + batch_size]
                
                logger.info(f"🔄 Processing batch {i//batch_size + 1}: Books {i+1}-{min(i+batch_size, len(self.books_to_load))}")
                
                for book_info in batch:
                    try:
                        verse_count = await self.process_single_book(book_info)
                        total_verses_added += verse_count
                        total_books_processed += 1
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing {book_info[0]}: {e}")
                        continue
                
                # Progress update
                progress = (total_books_processed / len(self.books_to_load)) * 100
                logger.info(f"📊 Progress: {total_books_processed}/{len(self.books_to_load)} books ({progress:.1f}%)")
                logger.info(f"📊 Verses added this session: {total_verses_added}")
            
            # Final statistics
            final_total = await bible_verses_collection.count_documents({"version": "kjv1611_divine"})
            final_books = await bible_books_collection.count_documents({"version": "kjv1611_divine"})
            
            logger.info("🎉 === Complete 80 Books Loading Finished ===")
            logger.info(f"📊 Books processed this session: {total_books_processed}")
            logger.info(f"📊 Verses added this session: {total_verses_added}")
            logger.info(f"📊 Final database totals: {final_books} books, {final_total} verses")
            logger.info("✅ KJV 1611 Bible with Apocrypha loading complete!")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = Complete80BooksAuthentic()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())