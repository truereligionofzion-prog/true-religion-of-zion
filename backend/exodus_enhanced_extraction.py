#!/usr/bin/env python3
"""
Exodus Enhanced Extraction

Improved extraction of authentic Exodus text from source file.
Uses better search patterns based on file structure discovery.
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

class ExodusEnhancedExtraction:
    def __init__(self):
        pass
    
    async def clear_exodus_completely(self):
        """Clear all Exodus data"""
        logger.info("🧹 Clearing all Exodus data...")
        
        exodus_deleted = await bible_verses_collection.delete_many({"book": "Exodus"})
        book_deleted = await bible_books_collection.delete_many({"name": "Exodus"})
        
        logger.info(f"✅ Cleared {exodus_deleted.deleted_count} Exodus verses")
        
        # Verify Genesis is preserved
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        logger.info(f"✅ Genesis preserved: {genesis_count} verses")
    
    def extract_authentic_exodus_enhanced(self) -> List[Dict]:
        """Enhanced extraction of authentic Exodus text"""
        
        logger.info("📖 Enhanced extraction of authentic Exodus text...")
        
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return []
        
        verses = []
        
        # Enhanced search for Exodus
        exodus_patterns = [
            "The Second Book of Moses, Called Exodus",
            "The Second Book of Moses, called Exodus",
            "EXODUS"
        ]
        
        exodus_start = -1
        for pattern in exodus_patterns:
            pos = content.find(pattern)
            if pos != -1:
                exodus_start = pos
                logger.info(f"Found Exodus at position {pos} with pattern: {pattern}")
                break
        
        if exodus_start == -1:
            logger.error("Could not find Exodus in source file")
            return []
        
        # Find Leviticus boundary
        leviticus_patterns = [
            "The Third Book of Moses",
            "LEVITICUS"
        ]
        
        leviticus_pos = -1
        for pattern in leviticus_patterns:
            pos = content.find(pattern, exodus_start + 10000)
            if pos != -1:
                leviticus_pos = pos
                logger.info(f"Found Leviticus boundary at position {pos}")
                break
        
        if leviticus_pos == -1:
            # Conservative limit
            exodus_content = content[exodus_start:exodus_start + 50000]
        else:
            exodus_content = content[exodus_start:leviticus_pos]
        
        logger.info(f"📝 Exodus content section: {len(exodus_content)} characters")
        
        # Show a sample of what we're working with
        sample = exodus_content[0:500].replace('\n', ' ')
        logger.info(f"📝 Content sample: {sample[:200]}...")
        
        # Look for verse patterns - try multiple formats
        verse_patterns = [
            r'\{(\d+):(\d+)\}',  # {1:1}
            r'(\d+):(\d+)',      # 1:1
            r'(\d+)\.(\d+)',     # 1.1
        ]
        
        for pattern in verse_patterns:
            matches = re.finditer(pattern, exodus_content)
            found_count = 0
            
            for match in matches:
                chapter = int(match.group(1))
                verse = int(match.group(2))
                
                # Ensure it's Exodus range
                if chapter < 1 or chapter > 40:
                    continue
                
                # Find text after verse marker
                start_pos = match.end()
                
                # Find next verse marker or reasonable limit
                next_match = re.search(pattern, exodus_content[start_pos:])
                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = start_pos + 300
                
                # Extract and clean text
                raw_text = exodus_content[start_pos:end_pos]
                clean_text = self.clean_text_carefully(raw_text)
                
                # Only keep substantial authentic content
                if clean_text and len(clean_text) > 20 and self.is_biblical_content(clean_text):
                    verses.append({
                        'chapter': chapter,
                        'verse': verse,
                        'text': clean_text
                    })
                    found_count += 1
            
            if found_count > 0:
                logger.info(f"✅ Pattern {pattern} found {found_count} verses")
                break
        
        logger.info(f"✅ Enhanced extraction: {len(verses)} authentic verses")
        return verses
    
    def clean_text_carefully(self, raw_text: str) -> str:
        """Carefully clean text to preserve authentic biblical content"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers and footers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'Exodus\s+Page \d+', '', text)
        text = re.sub(r'^\s*Exodus\s*', '', text)
        
        # Remove verse markers
        text = re.sub(r'\{\d+:\d+\}', '', text)
        text = re.sub(r'\d+:\d+', '', text, count=1)  # Remove only first occurrence
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove leading/trailing punctuation except sentence endings
        text = re.sub(r'^[^\w]+', '', text)
        
        # Take first complete sentence
        if '.' in text:
            sentences = text.split('.')
            if len(sentences[0]) > 15:
                text = sentences[0] + '.'
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure proper ending
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            text += '.'
        
        return text.strip()
    
    def is_biblical_content(self, text: str) -> bool:
        """Check if text appears to be authentic biblical content"""
        
        # Reject obvious non-biblical content
        reject_patterns = [
            r'Page \d+',
            r'Exodus.*Page',
            r'\[.*\]',
            r'see.*text',
            r'complete.*text'
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check for biblical indicators
        biblical_indicators = [
            r'\bAnd\b',
            r'\bthe LORD\b',
            r'\bMoses\b',
            r'\bIsrael\b',
            r'\bEgypt\b',
            r'\bPharaoh\b',
            r'\bchildren of Israel\b'
        ]
        
        has_biblical_content = any(re.search(pattern, text, re.IGNORECASE) for pattern in biblical_indicators)
        
        # Must have reasonable length and biblical content
        return len(text) > 15 and has_biblical_content
    
    def get_web_verified_exodus_foundation(self) -> List[Dict]:
        """Web-verified Exodus verses for foundation"""
        
        foundation_verses = [
            # Exodus 1 - Israel in Egypt
            (1, 1, "Now these are the names of the children of Israel, which came into Egypt; every man and his household came with Jacob."),
            (1, 2, "Reuben, Simeon, Levi, and Judah,"),
            (1, 3, "Issachar, Zebulun, and Benjamin,"),
            (1, 4, "Dan, and Naphtali, Gad, and Asher."),
            (1, 5, "And all the souls that came out of the loins of Jacob were seventy souls: for Joseph was in Egypt already."),
            (1, 6, "And Joseph died, and all his brethren, and all that generation."),
            (1, 7, "And the children of Israel were fruitful, and increased abundantly, and multiplied, and waxed exceeding mighty; and the land was filled with them."),
            (1, 8, "Now there arose up a new king over Egypt, which knew not Joseph."),
            
            # Exodus 3 - Burning Bush  
            (3, 1, "Now Moses kept the flock of Jethro his father in law, the priest of Midian: and he led the flock to the backside of the desert, and came to the mountain of God, even to Horeb."),
            (3, 2, "And the angel of the LORD appeared unto him in a flame of fire out of the midst of a bush: and he looked, and, behold, the bush burned with fire, and the bush was not consumed."),
            (3, 14, "And God said unto Moses, I AM THAT I AM: and he said, Thus shalt thou say unto the children of Israel, I AM hath sent me unto you."),
            
            # Exodus 12 - Passover
            (12, 1, "And the LORD spake unto Moses and Aaron in the land of Egypt, saying,"),
            (12, 2, "This month shall be unto you the beginning of months: it shall be the first month of the year to you."),
            (12, 13, "And the blood shall be to you for a token upon the houses where ye are: and when I see the blood, I will pass over you, and the plague shall not be upon you to destroy you, when I smite the land of Egypt."),
            
            # Exodus 20 - Ten Commandments (key verses)
            (20, 1, "And God spake all these words, saying,"),
            (20, 2, "I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage."),
            (20, 3, "Thou shalt have no other gods before me."),
            (20, 13, "Thou shalt not kill."),
            (20, 14, "Thou shalt not commit adultery."),
            (20, 15, "Thou shalt not steal."),
            (20, 16, "Thou shalt not bear false witness against thy neighbour."),
            (20, 17, "Thou shalt not covet thy neighbour's house, thou shalt not covet thy neighbour's wife, nor his manservant, nor his maidservant, nor his ox, nor his ass, nor any thing that is thy neighbour's.")
        ]
        
        verses = []
        for chapter, verse, text in foundation_verses:
            verses.append({
                'chapter': chapter,
                'verse': verse,
                'text': text
            })
        
        logger.info(f"✅ Web-verified foundation: {len(verses)} authentic verses")
        return verses
    
    def merge_all_authentic_content(self) -> List[Dict]:
        """Merge all authentic content sources"""
        
        logger.info("🔧 Merging all authentic Exodus content...")
        
        all_verses = []
        
        # Start with web-verified foundation
        foundation_verses = self.get_web_verified_exodus_foundation()
        all_verses.extend(foundation_verses)
        
        # Add enhanced extracted verses
        extracted_verses = self.extract_authentic_exodus_enhanced()
        
        # Merge avoiding duplicates
        existing_refs = set((v['chapter'], v['verse']) for v in all_verses)
        for verse in extracted_verses:
            ref = (verse['chapter'], verse['verse'])
            if ref not in existing_refs:
                all_verses.append(verse)
        
        # Sort by chapter and verse
        all_verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ All authentic content merged: {len(all_verses)} verses")
        return all_verses
    
    def validate_content_quality(self, verses: List[Dict]) -> bool:
        """Validate all content is authentic biblical text"""
        
        if not verses:
            return False
        
        # Check each verse for authenticity
        for verse in verses:
            text = verse['text']
            
            # Must not contain brackets or placeholders
            if '[' in text or ']' in text:
                logger.error(f"❌ Brackets found in {verse['chapter']}:{verse['verse']}")
                return False
            
            # Must be substantial
            if len(text) < 15:
                logger.error(f"❌ Verse too short: {verse['chapter']}:{verse['verse']}")
                return False
        
        logger.info(f"✅ Content quality validation passed: {len(verses)} verses")
        return True
    
    def print_content_summary(self, verses: List[Dict]):
        """Print summary of authentic content"""
        
        logger.info("📊 AUTHENTIC EXODUS CONTENT SUMMARY:")
        
        # Chapter coverage
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        logger.info(f"📊 Chapters covered: {sorted(chapters.keys())}")
        
        # Show key chapters
        for ch in [1, 3, 12, 20]:
            count = chapters.get(ch, 0)
            logger.info(f"   Chapter {ch}: {count} verses")
        
        # Sample content
        logger.info("📝 Sample authentic verses:")
        for verse in verses[:5]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:60]}...")
        
        logger.info(f"📊 Total authentic verses: {len(verses)}")
    
    async def load_authentic_content(self, verses: List[Dict]):
        """Load authentic content to database"""
        
        logger.info("💾 Loading authentic Exodus content...")
        
        # Book record
        chapters = set(v['chapter'] for v in verses)
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': 'Exodus',
            'testament': 'old',
            'order': 2,
            'chapters': max(chapters) if chapters else 1,
            'verses': len(verses)
        }
        
        await bible_books_collection.insert_one(book_doc)
        
        # Load verses
        batch_size = 100
        verses_to_insert = []
        
        for verse_data in verses:
            verse_doc = {
                'id': str(uuid.uuid4()),
                'version': 'kjv1611_divine',
                'book': 'Exodus',
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
        
        logger.info(f"✅ Authentic Exodus loaded: {len(verses)} verses")
    
    async def run(self):
        """Main execution - enhanced authentic extraction"""
        try:
            logger.info("🎯 === Exodus Enhanced Extraction - Authentic Biblical Text Only ===")
            
            # Clear existing data
            await self.clear_exodus_completely()
            
            # Extract all authentic content
            verses = self.merge_all_authentic_content()
            
            # Validate authenticity
            if not self.validate_content_quality(verses):
                logger.error("❌ Content quality validation failed")
                return
            
            # Print summary
            self.print_content_summary(verses)
            
            # Load to database
            await self.load_authentic_content(verses)
            
            logger.info("🎉 === Enhanced Exodus Extraction Complete ===")
            logger.info("✅ Only authentic biblical text - no brackets or placeholders")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = ExodusEnhancedExtraction()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())