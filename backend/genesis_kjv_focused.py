#!/usr/bin/env python3
"""
Genesis KJV 1611 Focused Parser

Target: Extract COMPLETE Genesis with all 50 chapters and 1533 verses
Validation: Must start with "In the beginning God created the heaven and the earth"
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

class GenesisKJVFocused:
    def __init__(self):
        self.genesis_verses = []
        
        # Genesis specifications (web-verified)
        self.genesis_spec = {
            "name": "Genesis",
            "order": 1,
            "testament": "old", 
            "expected_chapters": 50,
            "expected_verses": 1533,
            "first_verse": "In the beginning God created the heaven and the earth",
            "key_content": ["heaven", "earth", "Adam", "Eve", "Noah", "Abraham"]
        }
    
    def find_genesis_boundaries(self, content: str) -> tuple:
        """Find exact Genesis boundaries in KJV file"""
        
        # Look for Genesis patterns
        genesis_patterns = [
            r"The First Book of Moses, called Genesis",
            r"Genesis\s*\n",
            r"Page \d+.*Genesis\b"
        ]
        
        genesis_start = -1
        for pattern in genesis_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                genesis_start = match.start()
                logger.info(f"📍 Found Genesis start at position {genesis_start} using pattern: {pattern}")
                break
        
        if genesis_start == -1:
            logger.error("❌ Could not find Genesis start")
            return -1, -1
        
        # Find end by looking for Exodus
        exodus_patterns = [
            r"The Second Book of Moses.*Exodus",
            r"Exodus\s*\n",
            r"Page \d+.*Exodus\b"
        ]
        
        # Search from Genesis start
        search_content = content[genesis_start + 1000:]  # Skip Genesis header
        genesis_end = len(content)
        
        for pattern in exodus_patterns:
            match = re.search(pattern, search_content, re.IGNORECASE)
            if match:
                genesis_end = genesis_start + 1000 + match.start()
                logger.info(f"📍 Found Genesis end at position {genesis_end} (Exodus starts)")
                break
        
        return genesis_start, genesis_end
    
    def extract_genesis_verses(self, content: str, start: int, end: int) -> List[Dict]:
        """Extract all Genesis verses using {chapter:verse} format"""
        verses = []
        
        genesis_content = content[start:end]
        logger.info(f"📏 Genesis content size: {len(genesis_content)} characters")
        
        # Extract verses using {chapter:verse} pattern
        verse_pattern = r'\{(\d+):(\d+)\}([^{]*?)(?=\{|\Z)'
        matches = re.findall(verse_pattern, genesis_content, re.DOTALL)
        
        logger.info(f"🔍 Found {len(matches)} verse matches")
        
        for chapter_str, verse_str, verse_text in matches:
            chapter = int(chapter_str)
            verse_num = int(verse_str)
            
            # Only include Genesis chapters (1-50)
            if chapter > 50:
                continue
            
            # Clean verse text
            clean_text = re.sub(r'\s+', ' ', verse_text).strip()
            clean_text = re.sub(r'Page \d+[^\w]*', '', clean_text).strip()
            clean_text = re.sub(r'^[^\w]*', '', clean_text).strip()
            
            # Quality check
            if len(clean_text) < 5:
                continue
            
            verses.append({
                'chapter': chapter,
                'verse': verse_num,
                'text': clean_text
            })
        
        # Sort by chapter and verse
        verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        return verses
    
    def validate_genesis_content(self, verses: List[Dict]) -> bool:
        """Validate Genesis content meets specifications"""
        
        if not verses:
            logger.error("❌ No verses found")
            return False
        
        # Check first verse
        first_verse = verses[0]
        if first_verse['chapter'] != 1 or first_verse['verse'] != 1:
            logger.error(f"❌ First verse not Genesis 1:1. Got {first_verse['chapter']}:{first_verse['verse']}")
            return False
        
        # Check first verse content
        first_text = first_verse['text'].lower()
        expected_start = "in the beginning god created"
        if not first_text.startswith(expected_start):
            logger.error(f"❌ Genesis 1:1 doesn't start correctly. Got: {first_text[:50]}...")
            return False
        
        # Check chapter count
        max_chapter = max(v['chapter'] for v in verses)
        if max_chapter < 45:  # At least 45 chapters (allowing some flexibility)
            logger.error(f"❌ Too few chapters. Got {max_chapter}, expected ~50")
            return False
        
        # Check verse count
        verse_count = len(verses)
        if verse_count < 1200:  # At least 1200 verses (allowing some flexibility)
            logger.error(f"❌ Too few verses. Got {verse_count}, expected ~1533")
            return False
        
        # Check for key content
        all_text = ' '.join([v['text'].lower() for v in verses[:100]])  # First 100 verses
        key_content = self.genesis_spec["key_content"]
        found_content = sum(1 for word in key_content if word.lower() in all_text)
        
        if found_content < len(key_content) / 2:
            logger.warning(f"⚠️ Limited key content found. Got {found_content}/{len(key_content)}")
        
        logger.info(f"✅ Genesis validation passed: {verse_count} verses, {max_chapter} chapters")
        return True
    
    def print_genesis_summary(self, verses: List[Dict]):
        """Print detailed Genesis summary"""
        
        if not verses:
            return
        
        # Chapter analysis
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            if chapter not in chapters:
                chapters[chapter] = 0
            chapters[chapter] += 1
        
        total_verses = len(verses)
        total_chapters = len(chapters)
        max_chapter = max(chapters.keys())
        
        logger.info(f"📊 GENESIS SUMMARY:")
        logger.info(f"   Total verses: {total_verses}")
        logger.info(f"   Total chapters: {total_chapters}")
        logger.info(f"   Chapter range: 1-{max_chapter}")
        logger.info(f"   Expected: 50 chapters, 1533 verses")
        logger.info(f"   Coverage: {total_verses/1533*100:.1f}% verses, {total_chapters/50*100:.1f}% chapters")
        
        # Show first few verses
        logger.info(f"📖 First verses:")
        for i, verse in enumerate(verses[:5]):
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:80]}...")
        
        # Show chapter distribution
        logger.info(f"📈 Chapter verse counts (first 10):")
        for chapter in sorted(chapters.keys())[:10]:
            logger.info(f"   Chapter {chapter}: {chapters[chapter]} verses")
    
    async def clear_bible_data(self):
        """Clear existing Bible data"""
        logger.info("🧹 Clearing existing Bible data...")
        await bible_verses_collection.delete_many({})
        await bible_books_collection.delete_many({})
        logger.info("✅ Database cleared")
    
    async def load_genesis_to_db(self, verses: List[Dict]):
        """Load Genesis to database"""
        
        if not verses:
            logger.error("❌ No Genesis verses to load")
            return
        
        # Load book metadata
        logger.info("📚 Loading Genesis book metadata...")
        
        max_chapter = max(v['chapter'] for v in verses)
        verse_count = len(verses)
        
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': 'Genesis',
            'testament': 'old',
            'order': 1,
            'chapters': max_chapter,
            'verses': verse_count
        }
        
        await bible_books_collection.insert_one(book_doc)
        logger.info(f"✅ Inserted Genesis book: {verse_count} verses, {max_chapter} chapters")
        
        # Load verses in batches
        logger.info("📝 Loading Genesis verses...")
        
        batch_size = 100
        verses_to_insert = []
        
        for verse_data in verses:
            verse_doc = {
                'id': str(uuid.uuid4()),
                'version': 'kjv1611_divine',
                'book': 'Genesis',
                'chapter': verse_data['chapter'],
                'verse': verse_data['verse'],
                'text': verse_data['text'],
                'testament': 'old',
                'has_precept': False
            }
            
            verses_to_insert.append(verse_doc)
            
            if len(verses_to_insert) >= batch_size:
                await bible_verses_collection.insert_many(verses_to_insert)
                logger.info(f"✅ Inserted batch of {len(verses_to_insert)} verses")
                verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
            logger.info(f"✅ Inserted final batch of {len(verses_to_insert)} verses")
        
        logger.info(f"🎉 Genesis loading complete: {verse_count} verses loaded")
    
    async def create_indexes(self):
        """Create database indexes"""
        logger.info("📊 Creating database indexes...")
        
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
        
        logger.info("✅ Database indexes created")
    
    async def run(self):
        """Main execution - focused Genesis extraction"""
        try:
            logger.info("🎯 === Genesis KJV 1611 Focused Extraction ===")
            
            # Load KJV file
            kjv_file = "/app/kjv_complete_new.txt"
            if not os.path.exists(kjv_file):
                logger.error(f"❌ KJV file not found: {kjv_file}")
                return
            
            with open(kjv_file, 'r', encoding='utf-8', errors='ignore') as f:
                kjv_content = f.read()
            
            logger.info(f"📖 Loaded KJV file: {len(kjv_content)} characters")
            
            # Find Genesis boundaries
            genesis_start, genesis_end = self.find_genesis_boundaries(kjv_content)
            
            if genesis_start == -1:
                logger.error("❌ Could not find Genesis boundaries")
                return
            
            # Extract Genesis verses
            verses = self.extract_genesis_verses(kjv_content, genesis_start, genesis_end)
            
            if not self.validate_genesis_content(verses):
                logger.error("❌ Genesis validation failed")
                return
            
            # Print detailed analysis
            self.print_genesis_summary(verses)
            
            # Clear database and load Genesis
            await self.clear_bible_data()
            await self.load_genesis_to_db(verses)
            await self.create_indexes()
            
            logger.info("🎯 === Genesis KJV 1611 Extraction Complete ===")
            logger.info(f"✅ Successfully loaded Genesis with {len(verses)} verses")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    parser = GenesisKJVFocused()
    await parser.run()

if __name__ == "__main__":
    asyncio.run(main())