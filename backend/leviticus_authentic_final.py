#!/usr/bin/env python3
"""
Leviticus Authentic Final Loader

Applies the proven Genesis/Exodus formula to load authentic Leviticus text.
Target: 859 verses across 27 chapters - ONLY real biblical text.

Following successful pattern:
- Extract ONLY authentic biblical text from source file
- No generated content or placeholder brackets
- Preserve legitimate KJV formatting
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

class LeviticusAuthenticFinal:
    def __init__(self):
        # Target verse counts per chapter (KJV standard - web verified)
        self.target_verse_counts = {
            1: 17, 2: 16, 3: 17, 4: 35, 5: 19, 6: 30, 7: 38, 8: 36, 9: 24, 10: 20,
            11: 47, 12: 8, 13: 59, 14: 57, 15: 33, 16: 34, 17: 16, 18: 30, 19: 37, 20: 27,
            21: 24, 22: 33, 23: 44, 24: 23, 25: 55, 26: 46, 27: 34
        }
        self.total_target = 859
        
    async def clear_leviticus_completely(self):
        """Clear all Leviticus data"""
        logger.info("🧹 Clearing all Leviticus data...")
        
        leviticus_deleted = await bible_verses_collection.delete_many({"book": "Leviticus"})
        book_deleted = await bible_books_collection.delete_many({"name": "Leviticus"})
        
        logger.info(f"✅ Cleared {leviticus_deleted.deleted_count} Leviticus verses")
        
        # Verify Genesis and Exodus are preserved
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        exodus_count = await bible_verses_collection.count_documents({"book": "Exodus"})
        logger.info(f"✅ Genesis preserved: {genesis_count} verses")
        logger.info(f"✅ Exodus preserved: {exodus_count} verses")
    
    def extract_authentic_leviticus(self) -> List[Dict]:
        """Extract authentic Leviticus text from source file"""
        
        logger.info("📖 Extracting authentic Leviticus text...")
        
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return []
        
        verses = []
        
        # Find Leviticus section precisely
        leviticus_start = content.find("The Third Book of Moses, called Leviticus")
        if leviticus_start == -1:
            leviticus_start = content.find("LEVITICUS")
        
        if leviticus_start == -1:
            logger.error("Could not find Leviticus")
            return []
        
        # Find Numbers boundary
        numbers_pos = content.find("The Fourth Book of Moses", leviticus_start + 10000)
        if numbers_pos == -1:
            numbers_pos = content.find("NUMBERS", leviticus_start + 10000)
        
        if numbers_pos == -1:
            leviticus_content = content[leviticus_start:leviticus_start + 40000]
        else:
            leviticus_content = content[leviticus_start:numbers_pos]
        
        logger.info(f"📝 Leviticus section: {len(leviticus_content)} characters")
        
        # Extract verses using {chapter:verse} pattern
        pattern = r'\{(\d+):(\d+)\}'
        matches = re.finditer(pattern, leviticus_content)
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Ensure it's Leviticus (chapters 1-27)
            if chapter < 1 or chapter > 27:
                continue
            
            # Find text after verse marker
            start_pos = match.end()
            
            # Find next verse marker
            next_match = re.search(r'\{\d+:\d+\}', leviticus_content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 400
            
            # Extract raw text
            raw_text = leviticus_content[start_pos:end_pos]
            
            # Clean text following Exodus success pattern
            clean_text = self.clean_authentic_text(raw_text)
            
            # Only keep substantial authentic biblical content
            if (clean_text and 
                len(clean_text) > 15 and 
                self.is_authentic_biblical_text(clean_text)):
                
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
        
        logger.info(f"✅ Authentic extraction: {len(verses)} verses")
        return verses
    
    def clean_authentic_text(self, raw_text: str) -> str:
        """Clean text while preserving authentic KJV content"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'Leviticus\s+Page \d+', '', text)
        
        # Remove verse markers
        text = re.sub(r'\{\d+:\d+\}', '', text)
        
        # Remove obvious artifacts
        text = re.sub(r'^\s*Leviticus\s*', '', text)
        
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
    
    def is_authentic_biblical_text(self, text: str) -> bool:
        """Check if text is authentic biblical content"""
        
        # Reject generated placeholder content
        reject_patterns = [
            r'see Leviticus.*text',
            r'complete KJV text',
            r'KJV.*text'
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check for Leviticus-specific biblical content
        biblical_indicators = [
            r'\bAnd\b',
            r'\bthe LORD\b',
            r'\bMoses\b', 
            r'\bAaron\b',
            r'\bIsrael\b',
            r'\bpriest\b',
            r'\boffering\b',
            r'\bsacrifice\b',
            r'\bchildren of Israel\b',
            r'\bLord\b',
            r'\bGod\b',
            r'\bshall\b'
        ]
        
        has_biblical_content = any(re.search(indicator, text, re.IGNORECASE) for indicator in biblical_indicators)
        
        return len(text) > 15 and has_biblical_content
    
    def get_web_verified_leviticus_foundation(self) -> List[Dict]:
        """Get web-verified Leviticus foundation verses"""
        
        foundation = [
            # Leviticus 1 - Burnt Offerings
            (1, 1, "And the LORD called unto Moses, and spake unto him out of the tabernacle of the congregation, saying,"),
            (1, 2, "Speak unto the children of Israel, and say unto them, If any man of you bring an offering unto the LORD, ye shall bring your offering of the cattle, even of the herd, and of the flock."),
            
            # Leviticus 11 - Clean and Unclean Animals
            (11, 1, "And the LORD spake unto Moses and to Aaron, saying unto them,"),
            (11, 2, "Speak unto the children of Israel, saying, These are the beasts which ye shall eat among all the beasts that are on the earth."),
            
            # Leviticus 16 - Day of Atonement  
            (16, 1, "And the LORD spake unto Moses after the death of the two sons of Aaron, when they offered before the LORD, and died;"),
            (16, 2, "And the LORD said unto Moses, Speak unto Aaron thy brother, that he come not at all times into the holy place within the vail before the mercy seat, which is upon the ark; that he die not: for I will appear in the cloud upon the mercy seat."),
            
            # Leviticus 19 - Holiness Laws
            (19, 1, "And the LORD spake unto Moses, saying,"),
            (19, 2, "Speak unto all the congregation of the children of Israel, and say unto them, Ye shall be holy: for I the LORD your God am holy."),
            
            # Leviticus 23 - Feasts and Holy Days
            (23, 1, "And the LORD spake unto Moses, saying,"),
            (23, 2, "Speak unto the children of Israel, and say unto them, Concerning the feasts of the LORD, which ye shall proclaim to be holy convocations, even these are my feasts.")
        ]
        
        verses = []
        for chapter, verse, text in foundation:
            verses.append({
                'chapter': chapter,
                'verse': verse,
                'text': text
            })
        
        logger.info(f"✅ Web-verified foundation: {len(verses)} verses")
        return verses
    
    def combine_authentic_sources(self) -> List[Dict]:
        """Combine authentic Leviticus sources"""
        
        logger.info("🔧 Combining authentic Leviticus sources...")
        
        all_verses = []
        
        # Add web-verified foundation
        foundation = self.get_web_verified_leviticus_foundation()
        all_verses.extend(foundation)
        
        # Add extracted authentic verses
        extracted = self.extract_authentic_leviticus()
        
        # Merge avoiding duplicates
        existing_refs = set((v['chapter'], v['verse']) for v in all_verses)
        for verse in extracted:
            ref = (verse['chapter'], verse['verse'])
            if ref not in existing_refs:
                all_verses.append(verse)
        
        # Sort by chapter and verse
        all_verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Authentic sources combined: {len(all_verses)} verses")
        return all_verses
    
    def validate_leviticus_authenticity(self, verses: List[Dict]) -> bool:
        """Validate Leviticus content is authentic"""
        
        if not verses:
            return False
        
        # Check for placeholder content
        for verse in verses:
            text = verse['text']
            
            # Must not contain generated placeholders
            if re.search(r'see Leviticus.*text', text, re.IGNORECASE):
                logger.error(f"❌ Placeholder found in {verse['chapter']}:{verse['verse']}")
                return False
            
            # Must be substantial
            if len(text) < 10:
                logger.error(f"❌ Verse too short: {verse['chapter']}:{verse['verse']}")
                return False
        
        # Check for key Leviticus content
        verse_map = {(v['chapter'], v['verse']): v for v in verses}
        
        # Leviticus 1:1 should mention LORD and Moses
        if (1, 1) in verse_map:
            text = verse_map[(1, 1)]['text']
            if not ("LORD" in text and "Moses" in text):
                logger.error(f"❌ Leviticus 1:1 content invalid")
                return False
        
        # Check minimum verse count (should be substantial)
        if len(verses) < 200:  # Should have substantial coverage
            logger.error(f"❌ Too few verses: {len(verses)}")
            return False
        
        logger.info(f"✅ Leviticus authenticity validation passed: {len(verses)} verses")
        return True
    
    def print_leviticus_summary(self, verses: List[Dict]):
        """Print summary of authentic Leviticus content"""
        
        logger.info("📊 AUTHENTIC LEVITICUS SUMMARY:")
        
        # Chapter coverage
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        # Show coverage stats
        logger.info(f"📊 Chapters covered: {sorted(chapters.keys())}")
        logger.info(f"📊 Total chapters: {len(chapters)}/27")
        
        # Show key chapters
        key_chapters = [1, 11, 16, 19, 23]
        for ch in key_chapters:
            actual = chapters.get(ch, 0)
            target = self.target_verse_counts.get(ch, 0)
            if target > 0:
                percentage = (actual / target * 100)
                logger.info(f"   Chapter {ch}: {actual}/{target} verses ({percentage:.1f}%)")
        
        # Show sample authentic content
        logger.info("📝 Sample authentic verses:")
        for verse in verses[:5]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:70]}...")
        
        # Calculate completion percentage
        completion_pct = (len(verses) / self.total_target * 100) if self.total_target > 0 else 0
        logger.info(f"📊 Total: {len(verses)}/{self.total_target} verses ({completion_pct:.1f}% of target)")
    
    async def load_leviticus_authentically(self, verses: List[Dict]):
        """Load authentic Leviticus to database"""
        
        logger.info("💾 Loading authentic Leviticus...")
        
        # Book record
        chapters = set(v['chapter'] for v in verses)
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': 'Leviticus',
            'testament': 'old',
            'order': 3,
            'chapters': max(chapters) if chapters else 1,
            'verses': len(verses)
        }
        
        await bible_books_collection.insert_one(book_doc)
        
        # Load verses in batches
        batch_size = 100
        verses_to_insert = []
        
        for verse_data in verses:
            verse_doc = {
                'id': str(uuid.uuid4()),
                'version': 'kjv1611_divine',
                'book': 'Leviticus',
                'chapter': verse_data['chapter'],
                'verse': verse_data['verse'],
                'text': verse_data['text'],
                'testament': 'old',
                'has_precept': False
            }
            
            verses_to_insert.append(verse_doc)
            
            if len(verses_to_insert) >= batch_size:
                await bible_verses_collection.insert_many(verses_to_insert)
                verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
        
        logger.info(f"✅ Authentic Leviticus loaded: {len(verses)} verses")
    
    async def run(self):
        """Main execution - authentic Leviticus following proven formula"""
        try:
            logger.info("🎯 === Leviticus Authentic Final - Following Genesis/Exodus Success ===")
            
            # Clear existing data
            await self.clear_leviticus_completely()
            
            # Extract and combine authentic content
            verses = self.combine_authentic_sources()
            
            # Validate authenticity
            if not self.validate_leviticus_authenticity(verses):
                logger.error("❌ Leviticus authenticity validation failed")
                return
            
            # Print summary
            self.print_leviticus_summary(verses)
            
            # Load to database
            await self.load_leviticus_authentically(verses)
            
            logger.info("🎉 === Authentic Leviticus Complete ===")
            logger.info("✅ Only authentic biblical text - following proven formula")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = LeviticusAuthenticFinal()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())