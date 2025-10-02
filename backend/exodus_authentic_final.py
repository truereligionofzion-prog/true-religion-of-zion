#!/usr/bin/env python3
"""
Exodus Authentic Final Loader

Extracts ONLY actual biblical text from source file - no placeholders, no brackets.
Uses the exact Genesis success approach: real biblical content only.

Target: Extract authentic Exodus verses from KJV source file
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

class ExodusAuthenticFinal:
    def __init__(self):
        pass
    
    async def clear_exodus_completely(self):
        """Clear all Exodus data to start fresh"""
        logger.info("🧹 Clearing all Exodus data...")
        
        exodus_deleted = await bible_verses_collection.delete_many({"book": "Exodus"})
        book_deleted = await bible_books_collection.delete_many({"name": "Exodus"})
        
        logger.info(f"✅ Cleared {exodus_deleted.deleted_count} Exodus verses")
        
        # Verify Genesis is preserved
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        logger.info(f"✅ Genesis preserved: {genesis_count} verses")
    
    def extract_authentic_exodus_text(self) -> List[Dict]:
        """Extract ONLY authentic Exodus text from source file"""
        
        logger.info("📖 Extracting authentic Exodus text from source file...")
        
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return []
        
        verses = []
        
        # Find Exodus section precisely
        exodus_start = content.find("The Second Book of Moses, called Exodus")
        if exodus_start == -1:
            # Try alternative
            exodus_start = content.find("EXODUS")
            if exodus_start == -1:
                logger.error("Could not find Exodus in source file")
                return []
        
        # Find Leviticus to determine end boundary
        leviticus_pos = content.find("The Third Book of Moses", exodus_start + 5000)
        if leviticus_pos == -1:
            leviticus_pos = content.find("LEVITICUS", exodus_start + 5000)
        
        if leviticus_pos == -1:
            # Conservative limit
            exodus_content = content[exodus_start:exodus_start + 40000]
        else:
            exodus_content = content[exodus_start:leviticus_pos]
        
        logger.info(f"📝 Exodus content section: {len(exodus_content)} characters")
        
        # Extract verses using {chapter:verse} pattern - same as Genesis
        pattern = r'\{(\d+):(\d+)\}'
        matches = re.finditer(pattern, exodus_content)
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Ensure it's Exodus (chapters 1-40)
            if chapter < 1 or chapter > 40:
                continue
            
            # Find text after verse marker
            start_pos = match.end()
            
            # Find next verse marker
            next_match = re.search(r'\{\d+:\d+\}', exodus_content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 500  # Conservative limit
            
            # Extract raw text
            raw_text = exodus_content[start_pos:end_pos]
            
            # Clean text using same method as Genesis
            clean_text = self.clean_authentic_text(raw_text)
            
            # Only keep if it's substantial authentic content
            if clean_text and len(clean_text) > 15 and not self.is_placeholder_text(clean_text):
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
        
        logger.info(f"✅ Extracted authentic verses: {len(verses)}")
        return verses
    
    def clean_authentic_text(self, raw_text: str) -> str:
        """Clean text while preserving authentic biblical content"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page numbers and obvious artifacts
        text = re.sub(r'Page \d+.*?(?=\w)', '', text).strip()
        text = re.sub(r'\s*\n\s*', ' ', text)
        text = re.sub(r'\s*\t\s*', ' ', text)
        
        # Remove any remaining verse markers
        text = re.sub(r'\{.*?\}', '', text)
        
        # Remove leading/trailing non-word characters
        text = re.sub(r'^\W+', '', text)
        text = re.sub(r'\W+$', '', text)
        
        # Take first substantial sentence
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        if sentences:
            text = sentences[0]
            
            # Ensure it ends properly
            if not text.endswith(('.', '!', '?', ':', ';')):
                text += '.'
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def is_placeholder_text(self, text: str) -> bool:
        """Check if text is placeholder/generated content"""
        
        # Reject any text with brackets, placeholders, or obvious artifacts
        reject_patterns = [
            r'\[.*\]',  # Any brackets
            r'see.*text',  # "see ... text" patterns
            r'KJV.*text',  # Reference to KJV text
            r'complete.*text',  # Reference to complete text
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_web_verified_exodus_verses(self) -> List[Dict]:
        """Get essential web-verified Exodus verses for foundation"""
        
        # Only absolutely verified authentic Exodus content
        web_verses = [
            # Exodus 1:1-5 (Israel's sons in Egypt)
            (1, 1, "Now these are the names of the children of Israel, which came into Egypt; every man and his household came with Jacob."),
            (1, 2, "Reuben, Simeon, Levi, and Judah,"),
            (1, 3, "Issachar, Zebulun, and Benjamin,"),
            (1, 4, "Dan, and Naphtali, Gad, and Asher."),
            (1, 5, "And all the souls that came out of the loins of Jacob were seventy souls: for Joseph was in Egypt already."),
            
            # Exodus 3:1-2 (Burning Bush)
            (3, 1, "Now Moses kept the flock of Jethro his father in law, the priest of Midian: and he led the flock to the backside of the desert, and came to the mountain of God, even to Horeb."),
            (3, 2, "And the angel of the LORD appeared unto him in a flame of fire out of the midst of a bush: and he looked, and, behold, the bush burned with fire, and the bush was not consumed."),
            (3, 14, "And God said unto Moses, I AM THAT I AM: and he said, Thus shalt thou say unto the children of Israel, I AM hath sent me unto you."),
            
            # Exodus 12:1-2 (Passover)
            (12, 1, "And the LORD spake unto Moses and Aaron in the land of Egypt, saying,"),
            (12, 2, "This month shall be unto you the beginning of months: it shall be the first month of the year to you."),
            
            # Exodus 20:1-17 (Ten Commandments)
            (20, 1, "And God spake all these words, saying,"),
            (20, 2, "I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage."),
            (20, 3, "Thou shalt have no other gods before me."),
            (20, 4, "Thou shalt not make unto thee any graven image, or any likeness of any thing that is in heaven above, or that is in the earth beneath, or that is in the water under the earth."),
            (20, 13, "Thou shalt not kill."),
            (20, 14, "Thou shalt not commit adultery."),
            (20, 15, "Thou shalt not steal."),
            (20, 16, "Thou shalt not bear false witness against thy neighbour."),
            (20, 17, "Thou shalt not covet thy neighbour's house, thou shalt not covet thy neighbour's wife, nor his manservant, nor his maidservant, nor his ox, nor his ass, nor any thing that is thy neighbour's.")
        ]
        
        verses = []
        for chapter, verse, text in web_verses:
            verses.append({
                'chapter': chapter,
                'verse': verse,
                'text': text
            })
        
        logger.info(f"✅ Web-verified foundation: {len(verses)} authentic verses")
        return verses
    
    def merge_authentic_sources(self) -> List[Dict]:
        """Merge only authentic sources"""
        
        logger.info("🔧 Merging authentic Exodus sources...")
        
        all_verses = []
        
        # Start with web-verified verses
        web_verses = self.get_web_verified_exodus_verses()
        all_verses.extend(web_verses)
        
        # Add extracted verses (avoiding duplicates)
        extracted_verses = self.extract_authentic_exodus_text()
        
        existing_refs = set((v['chapter'], v['verse']) for v in all_verses)
        for verse in extracted_verses:
            ref = (verse['chapter'], verse['verse'])
            if ref not in existing_refs:
                all_verses.append(verse)
        
        # Sort by chapter and verse
        all_verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Authentic Exodus merged: {len(all_verses)} verses")
        return all_verses
    
    def validate_authentic_content(self, verses: List[Dict]) -> bool:
        """Validate content is authentic biblical text"""
        
        if not verses:
            return False
        
        # Check for placeholder content
        for verse in verses:
            if self.is_placeholder_text(verse['text']):
                logger.error(f"❌ Placeholder text found in {verse['chapter']}:{verse['verse']}")
                return False
        
        # Check key verses have proper content
        verse_map = {(v['chapter'], v['verse']): v for v in verses}
        
        # Exodus 1:1 should mention Israel's sons
        if (1, 1) in verse_map:
            text = verse_map[(1, 1)]['text']
            if not ("children of Israel" in text and "Egypt" in text):
                logger.error(f"❌ Exodus 1:1 content invalid: {text}")
                return False
        
        # Check minimum quality
        good_verses = sum(1 for v in verses if len(v['text']) > 20)
        if good_verses < len(verses) * 0.8:
            logger.error(f"❌ Too many short verses: {good_verses}/{len(verses)}")
            return False
        
        logger.info(f"✅ Authentic content validation passed: {len(verses)} verses")
        return True
    
    def print_authentic_summary(self, verses: List[Dict]):
        """Print summary of authentic Exodus content"""
        
        logger.info("📊 AUTHENTIC EXODUS SUMMARY:")
        
        # Chapter distribution
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        # Show key chapters
        key_chapters = [1, 3, 12, 20]
        for ch in key_chapters:
            count = chapters.get(ch, 0)
            logger.info(f"   Chapter {ch}: {count} authentic verses")
        
        # Show sample authentic content
        logger.info("📝 Sample authentic verses:")
        for verse in verses[:3]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:70]}...")
        
        logger.info(f"📊 Total authentic verses: {len(verses)}")
        logger.info(f"📊 Chapters covered: {len(chapters)}")
    
    async def load_authentic_exodus(self, verses: List[Dict]):
        """Load authentic Exodus to database"""
        
        logger.info("💾 Loading authentic Exodus to database...")
        
        # Book record
        chapters = set(v['chapter'] for v in verses)
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': 'Exodus',
            'testament': 'old',
            'order': 2,
            'chapters': max(chapters),
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
        """Main execution - authentic Exodus only"""
        try:
            logger.info("🎯 === Exodus Authentic Final - Real Biblical Text Only ===")
            
            # Clear existing Exodus
            await self.clear_exodus_completely()
            
            # Extract and merge authentic content
            verses = self.merge_authentic_sources()
            
            # Validate authenticity
            if not self.validate_authentic_content(verses):
                logger.error("❌ Authentic content validation failed")
                return
            
            # Print summary
            self.print_authentic_summary(verses)
            
            # Load to database
            await self.load_authentic_exodus(verses)
            
            logger.info("🎉 === Exodus Authentic Final Complete ===")
            logger.info("✅ Only authentic biblical text loaded - no placeholders")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = ExodusAuthenticFinal()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())