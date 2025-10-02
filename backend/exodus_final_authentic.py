#!/usr/bin/env python3
"""
Exodus Final Authentic Loader

Extracts authentic Exodus text preserving legitimate KJV brackets.
Only removes placeholder brackets that reference "see Exodus" or similar.
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

class ExodusFinalAuthentic:
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
    
    def extract_authentic_exodus_only(self) -> List[Dict]:
        """Extract authentic Exodus text with proper bracket handling"""
        
        logger.info("📖 Extracting authentic Exodus text...")
        
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return []
        
        verses = []
        
        # Find Exodus section
        exodus_start = content.find("The Second Book of Moses, Called Exodus")
        if exodus_start == -1:
            logger.error("Could not find Exodus")
            return []
        
        # Find Leviticus boundary
        leviticus_pos = content.find("The Third Book of Moses", exodus_start + 10000)
        if leviticus_pos == -1:
            exodus_content = content[exodus_start:exodus_start + 50000]
        else:
            exodus_content = content[exodus_start:leviticus_pos]
        
        logger.info(f"📝 Exodus section: {len(exodus_content)} characters")
        
        # Extract verses using {chapter:verse} pattern
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
                end_pos = start_pos + 400
            
            # Extract raw text
            raw_text = exodus_content[start_pos:end_pos]
            
            # Clean text properly
            clean_text = self.clean_authentic_text_properly(raw_text)
            
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
    
    def clean_authentic_text_properly(self, raw_text: str) -> str:
        """Clean text while preserving authentic KJV brackets"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'Exodus\s+Page \d+', '', text)
        
        # Remove verse markers
        text = re.sub(r'\{\d+:\d+\}', '', text)
        
        # Remove obvious artifacts
        text = re.sub(r'^\s*Exodus\s*', '', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Take first substantial sentence
        if '.' in text:
            sentences = text.split('.')
            if len(sentences) > 0 and len(sentences[0]) > 10:
                text = sentences[0].strip()
                if not text.endswith('.'):
                    text += '.'
        
        # Remove leading non-word chars except brackets
        text = re.sub(r'^[^\w\[\]]+', '', text)
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def is_authentic_biblical_text(self, text: str) -> bool:
        """Check if text is authentic biblical content"""
        
        # Reject placeholder references
        reject_patterns = [
            r'see Exodus.*text',
            r'complete KJV text',
            r'KJV.*text'
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Check for biblical content indicators
        biblical_words = [
            r'\bAnd\b',
            r'\bthe LORD\b', 
            r'\bMoses\b',
            r'\bIsrael\b',
            r'\bEgypt\b',
            r'\bPharaoh\b',
            r'\bchildren of Israel\b',
            r'\bGod\b'
        ]
        
        has_biblical_content = any(re.search(word, text, re.IGNORECASE) for word in biblical_words)
        
        return len(text) > 15 and has_biblical_content
    
    def get_web_verified_foundation(self) -> List[Dict]:
        """Get web-verified Exodus foundation"""
        
        foundation = [
            # Exodus 1 - Israel in Egypt
            (1, 1, "Now these are the names of the children of Israel, which came into Egypt; every man and his household came with Jacob."),
            (1, 2, "Reuben, Simeon, Levi, and Judah,"),
            (1, 3, "Issachar, Zebulun, and Benjamin,"),
            (1, 4, "Dan, and Naphtali, Gad, and Asher."),
            (1, 5, "And all the souls that came out of the loins of Jacob were seventy souls: for Joseph was in Egypt already."),
            
            # Exodus 3 - Burning Bush
            (3, 1, "Now Moses kept the flock of Jethro his father in law, the priest of Midian: and he led the flock to the backside of the desert, and came to the mountain of God, even to Horeb."),
            (3, 2, "And the angel of the LORD appeared unto him in a flame of fire out of the midst of a bush: and he looked, and, behold, the bush burned with fire, and the bush was not consumed."),
            (3, 14, "And God said unto Moses, I AM THAT I AM: and he said, Thus shalt thou say unto the children of Israel, I AM hath sent me unto you."),
            
            # Exodus 20 - Ten Commandments
            (20, 1, "And God spake all these words, saying,"),
            (20, 2, "I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage."),
            (20, 3, "Thou shalt have no other gods before me.")
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
        """Combine only authentic sources"""
        
        logger.info("🔧 Combining authentic Exodus sources...")
        
        all_verses = []
        
        # Add web-verified foundation
        foundation = self.get_web_verified_foundation()
        all_verses.extend(foundation)
        
        # Add extracted authentic verses
        extracted = self.extract_authentic_exodus_only()
        
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
    
    def validate_final_content(self, verses: List[Dict]) -> bool:
        """Validate final content is authentic"""
        
        if not verses:
            return False
        
        # Check each verse
        for verse in verses:
            text = verse['text']
            
            # Must not contain placeholder references
            if re.search(r'see Exodus.*text', text, re.IGNORECASE):
                logger.error(f"❌ Placeholder found in {verse['chapter']}:{verse['verse']}")
                return False
            
            # Must be substantial
            if len(text) < 10:
                logger.error(f"❌ Verse too short: {verse['chapter']}:{verse['verse']}")
                return False
        
        # Check for key verses
        verse_map = {(v['chapter'], v['verse']): v for v in verses}
        
        # Exodus 1:1 should mention Israel's children
        if (1, 1) in verse_map:
            text = verse_map[(1, 1)]['text']
            if not ("children of Israel" in text and "Egypt" in text):
                logger.error(f"❌ Exodus 1:1 content invalid")
                return False
        
        logger.info(f"✅ Final content validation passed: {len(verses)} authentic verses")
        return True
    
    def print_final_summary(self, verses: List[Dict]):
        """Print summary of final authentic content"""
        
        logger.info("📊 FINAL AUTHENTIC EXODUS SUMMARY:")
        
        # Chapter coverage
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        # Show coverage
        logger.info(f"📊 Chapters covered: {sorted(chapters.keys())}")
        logger.info(f"📊 Total chapters: {len(chapters)}")
        
        # Show key chapters
        for ch in [1, 3, 12, 20]:
            count = chapters.get(ch, 0)
            logger.info(f"   Chapter {ch}: {count} verses")
        
        # Show authentic sample
        logger.info("📝 Sample authentic verses:")
        for verse in verses[:5]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:70]}...")
        
        logger.info(f"📊 Total authentic verses: {len(verses)}")
    
    async def load_final_exodus(self, verses: List[Dict]):
        """Load final authentic Exodus"""
        
        logger.info("💾 Loading final authentic Exodus...")
        
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
        
        logger.info(f"✅ Final authentic Exodus loaded: {len(verses)} verses")
    
    async def run(self):
        """Main execution - final authentic Exodus"""
        try:
            logger.info("🎯 === Exodus Final Authentic - Real Biblical Text Only ===")
            
            # Clear existing data
            await self.clear_exodus_completely()
            
            # Combine authentic sources
            verses = self.combine_authentic_sources()
            
            # Validate authenticity
            if not self.validate_final_content(verses):
                logger.error("❌ Final content validation failed")
                return
            
            # Print summary
            self.print_final_summary(verses)
            
            # Load to database
            await self.load_final_exodus(verses)
            
            logger.info("🎉 === Final Authentic Exodus Complete ===")
            logger.info("✅ Only authentic biblical text - no placeholders")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = ExodusFinalAuthentic()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())