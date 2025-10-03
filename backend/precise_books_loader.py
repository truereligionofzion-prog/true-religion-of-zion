#!/usr/bin/env python3
"""
Precise Books Loader

Loads biblical books one-by-one using improved boundary detection.
Focus on accuracy over speed, following the proven Genesis/Exodus/Leviticus pattern.
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

class PreciseBooksLoader:
    def __init__(self):
        # Next few books to process in order
        self.priority_books = [
            ("Numbers", 4, "old", 36, 1288),
            ("Deuteronomy", 5, "old", 34, 959),
            ("Joshua", 6, "old", 24, 658),
            ("Judges", 7, "old", 21, 618),
            ("Ruth", 8, "old", 4, 85)
        ]
        
    async def clear_contaminated_books(self):
        """Clear any contaminated book data from failed run"""
        logger.info("🧹 Clearing any contaminated book data...")
        
        # Get books to clear (avoid clearing our good foundation)
        books_to_clear = ["Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings"]
        
        for book_name in books_to_clear:
            verses_deleted = await bible_verses_collection.delete_many({"book": book_name})
            books_deleted = await bible_books_collection.delete_many({"name": book_name})
            if verses_deleted.deleted_count > 0:
                logger.info(f"✅ Cleared {book_name}: {verses_deleted.deleted_count} verses")
        
        # Verify foundation is intact
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        exodus_count = await bible_verses_collection.count_documents({"book": "Exodus"})
        leviticus_count = await bible_verses_collection.count_documents({"book": "Leviticus"})
        
        logger.info(f"✅ Foundation preserved: Genesis={genesis_count}, Exodus={exodus_count}, Leviticus={leviticus_count}")
    
    def find_precise_book_boundaries(self, content: str, book_name: str) -> Tuple[int, int]:
        """Find precise boundaries for a book"""
        
        logger.info(f"🔍 Finding boundaries for {book_name}...")
        
        # Precise search patterns for each book
        if book_name == "Numbers":
            patterns = ["The Fourth Book of Moses, called Numbers", "NUMBERS"]
            next_patterns = ["The Fifth Book of Moses", "DEUTERONOMY"]
        elif book_name == "Deuteronomy":
            patterns = ["The Fifth Book of Moses, called Deuteronomy", "DEUTERONOMY"]
            next_patterns = ["Joshua", "JOSHUA"]
        elif book_name == "Joshua":
            patterns = ["Joshua", "JOSHUA"]
            next_patterns = ["Judges", "JUDGES"]
        elif book_name == "Judges":
            patterns = ["Judges", "JUDGES"]
            next_patterns = ["Ruth", "RUTH"]
        elif book_name == "Ruth":
            patterns = ["Ruth", "RUTH"]
            next_patterns = ["The First Book of Samuel", "1 Samuel", "I Samuel"]
        else:
            patterns = [book_name]
            next_patterns = []
        
        # Find start
        start_pos = -1
        for pattern in patterns:
            pos = content.find(pattern)
            if pos != -1:
                start_pos = pos
                logger.info(f"📍 Found {book_name} at position {pos} with pattern: {pattern}")
                break
        
        if start_pos == -1:
            logger.warning(f"⚠️ Could not find start of {book_name}")
            return -1, -1
        
        # Find end
        end_pos = -1
        if next_patterns:
            for pattern in next_patterns:
                pos = content.find(pattern, start_pos + 5000)  # Look after reasonable offset
                if pos != -1:
                    end_pos = pos
                    logger.info(f"📍 Found {book_name} end at position {pos} with pattern: {pattern}")
                    break
        
        if end_pos == -1:
            # Conservative estimate
            end_pos = start_pos + 25000
            logger.info(f"📍 Using conservative end for {book_name}: {end_pos}")
        
        return start_pos, end_pos
    
    def extract_verses_precisely(self, book_content: str, book_name: str, target_chapters: int) -> List[Dict]:
        """Extract verses with strict controls to prevent cross-contamination"""
        
        logger.info(f"📖 Extracting verses from {book_name} content ({len(book_content)} chars)...")
        
        verses = []
        
        # Extract verses using {chapter:verse} pattern
        pattern = r'\{(\d+):(\d+)\}'
        matches = list(re.finditer(pattern, book_content))
        
        logger.info(f"🔍 Found {len(matches)} potential verse markers")
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Strict chapter bounds (prevent cross-contamination)
            if chapter < 1 or chapter > target_chapters + 5:  # Allow small buffer
                continue
            
            # Find text after verse marker
            start_pos = match.end()
            
            # Find next verse marker with conservative limit
            next_match = re.search(r'\{\d+:\d+\}', book_content[start_pos:start_pos+300])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 200  # Conservative limit
            
            # Extract and clean text
            raw_text = book_content[start_pos:end_pos]
            clean_text = self.clean_verse_precisely(raw_text)
            
            # Strict content validation
            if (clean_text and 
                len(clean_text) > 20 and 
                len(clean_text) < 500 and  # Prevent overly long contaminated verses
                self.is_valid_biblical_text(clean_text)):
                
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
        
        # Sort and remove duplicates
        unique_verses = {}
        for verse in verses:
            key = (verse['chapter'], verse['verse'])
            if key not in unique_verses:
                unique_verses[key] = verse
        
        result = list(unique_verses.values())
        result.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Extracted {len(result)} clean verses for {book_name}")
        return result
    
    def clean_verse_precisely(self, raw_text: str) -> str:
        """Clean verse text with precision"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers and artifacts
        text = re.sub(r'Page \d+.*?(?=\w)', '', text)
        text = re.sub(r'\w+\s+Page \d+', '', text)
        
        # Remove verse markers
        text = re.sub(r'\{\d+:\d+\}', '', text)
        
        # Remove common artifacts
        text = re.sub(r'^\s*\w+\s*$', '', text)  # Single word artifacts
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Take first meaningful sentence only
        if '.' in text:
            sentences = text.split('.')
            if len(sentences) > 0 and len(sentences[0]) > 15:
                text = sentences[0].strip()
                if not text.endswith('.'):
                    text += '.'
        
        # Remove leading/trailing artifacts
        text = re.sub(r'^[^\w\[\]]+', '', text)
        text = re.sub(r'[^\w\[\]\.!?;:]+$', '', text)
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def is_valid_biblical_text(self, text: str) -> bool:
        """Validate text is proper biblical content"""
        
        # Reject obvious artifacts
        reject_patterns = [
            r'^Page \d+',
            r'^\d+$',
            r'^[A-Z]+$',  # All caps single words
            r'see.*text',
            r'complete.*text'
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Must have biblical indicators
        biblical_words = [
            r'\bAnd\b', r'\bthe LORD\b', r'\bLord\b', r'\bGod\b',
            r'\bshall\b', r'\bunto\b', r'\bsaith\b', r'\bspake\b'
        ]
        
        has_biblical_content = any(re.search(word, text, re.IGNORECASE) for word in biblical_words)
        
        # Must be reasonable length
        return len(text) > 15 and len(text) < 400 and has_biblical_content
    
    def get_verified_foundation_verses(self, book_name: str) -> List[Dict]:
        """Get web-verified foundation verses for specific books"""
        
        if book_name == "Numbers":
            return [
                (1, 1, "And the LORD spake unto Moses in the wilderness of Sinai, in the tabernacle of the congregation, on the first day of the second month, in the second year after they were come out of the land of Egypt, saying,"),
                (6, 24, "The LORD bless thee, and keep thee."),
                (6, 25, "The LORD make his face shine upon thee, and be gracious unto thee."),
                (6, 26, "The LORD lift up his countenance upon thee, and give thee peace.")
            ]
        elif book_name == "Deuteronomy":
            return [
                (1, 1, "These be the words which Moses spake unto all Israel on this side Jordan in the wilderness, in the plain over against the Red sea, between Paran, and Tophel, and Laban, and Hazeroth, and Dizahab."),
                (6, 4, "Hear, O Israel: The LORD our God is one LORD:"),
                (6, 5, "And thou shalt love the LORD thy God with all thine heart, and with all thy soul, and with all thy might.")
            ]
        elif book_name == "Joshua":
            return [
                (1, 1, "Now after the death of Moses the servant of the LORD it came to pass, that the LORD spake unto Joshua the son of Nun, Moses' minister, saying,"),
                (1, 8, "This book of the law shall not depart out of thy mouth; but thou shalt meditate therein day and night, that thou mayest observe to do according to all that is written therein: for then thou shalt make thy way prosperous, and then thou shalt have good success.")
            ]
        elif book_name == "Judges":
            return [
                (1, 1, "Now after the death of Joshua it came to pass, that the children of Israel asked the LORD, saying, Who shall go up for us against the Canaanites first, to fight against them?")
            ]
        elif book_name == "Ruth":
            return [
                (1, 1, "Now it came to pass in the days when the judges ruled, that there was a famine in the land. And a certain man of Bethlehemjudah went to sojourn in the country of Moab, he, and his wife, and his two sons."),
                (1, 16, "And Ruth said, Intreat me not to leave thee, or to return from following after thee: for whither thou goest, I will go; and where thou lodgest, I will lodge: thy people shall be my people, and thy God my God:")
            ]
        
        return []
    
    async def process_one_book_carefully(self, book_info: Tuple) -> int:
        """Process one book with maximum care"""
        
        book_name, order, testament, chapters, target_verses = book_info
        
        logger.info(f"🎯 === Processing {book_name} (Order: {order}) ===")
        
        # Read source file
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return 0
        
        # Find precise boundaries
        start_pos, end_pos = self.find_precise_book_boundaries(content, book_name)
        
        if start_pos == -1:
            logger.warning(f"⚠️ Could not find {book_name} - using foundation verses only")
            verses = []
        else:
            # Extract book content
            book_content = content[start_pos:end_pos]
            
            # Extract verses precisely
            verses = self.extract_verses_precisely(book_content, book_name, chapters)
        
        # Add web-verified foundation
        foundation_verses = self.get_verified_foundation_verses(book_name)
        foundation_formatted = [
            {'chapter': ch, 'verse': v, 'text': text} 
            for ch, v, text in foundation_verses
        ]
        
        # Merge avoiding duplicates
        existing_refs = set((v['chapter'], v['verse']) for v in verses)
        for fv in foundation_formatted:
            ref = (fv['chapter'], fv['verse'])
            if ref not in existing_refs:
                verses.append(fv)
        
        # Sort final verses
        verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        verse_count = len(verses)
        completion_pct = (verse_count / target_verses * 100) if target_verses > 0 else 0
        
        logger.info(f"📊 {book_name}: {verse_count}/{target_verses} verses ({completion_pct:.1f}%)")
        
        # Load to database
        if verses:
            await self.load_book_carefully(book_name, order, testament, chapters, verses)
        
        return verse_count
    
    async def load_book_carefully(self, book_name: str, order: int, testament: str, chapters: int, verses: List[Dict]):
        """Load book to database with care"""
        
        # Book record
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
        
        # Verse records
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
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
        
        logger.info(f"✅ {book_name} loaded to database: {len(verses)} verses")
    
    async def run(self):
        """Process priority books carefully"""
        try:
            logger.info("🎯 === Precise Books Loader - Next 5 Books ===")
            
            # Clear any contamination first
            await self.clear_contaminated_books()
            
            total_added = 0
            
            # Process each priority book
            for book_info in self.priority_books:
                book_name = book_info[0]
                
                # Check if already exists
                existing = await bible_books_collection.find_one({
                    "version": "kjv1611_divine",
                    "name": book_name
                })
                
                if existing:
                    logger.info(f"⏭️ {book_name} already exists, skipping...")
                    continue
                
                # Process the book
                verse_count = await self.process_one_book_carefully(book_info)
                total_added += verse_count
                
                logger.info(f"✅ {book_name} complete: {verse_count} verses added")
            
            # Final stats
            total_verses = await bible_verses_collection.count_documents({"version": "kjv1611_divine"})
            total_books = await bible_books_collection.count_documents({"version": "kjv1611_divine"})
            
            logger.info("🎉 === Precise Loading Complete ===")
            logger.info(f"📊 Session summary: {total_added} verses added")
            logger.info(f"📊 Database totals: {total_books} books, {total_verses} verses")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = PreciseBooksLoader()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())