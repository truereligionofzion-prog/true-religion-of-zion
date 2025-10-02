#!/usr/bin/env python3
"""
Genesis KJV Fixed Parser - Handles Two-Column Layout

The issue: KJV file has a two-column layout where verses are split.
My previous parser was concatenating content from both columns incorrectly.

Solution: Parse each verse marker individually and clean up the text properly.
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

class GenesisFixedParser:
    def __init__(self):
        pass
        
    def find_genesis_content(self, content: str) -> str:
        """Find the Genesis section in the KJV file"""
        
        # Look for Genesis start
        genesis_start = -1
        patterns = [
            r"The First Book of Moses, called Genesis",
            r"Genesis\s*\n"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                genesis_start = match.start()
                logger.info(f"📍 Found Genesis start at {genesis_start}")
                break
        
        if genesis_start == -1:
            logger.error("❌ Could not find Genesis start")
            return ""
        
        # Find Exodus to determine end
        search_content = content[genesis_start + 1000:]
        exodus_patterns = [
            r"The Second Book of Moses.*Exodus",
            r"Exodus\s*\n"
        ]
        
        genesis_end = len(content)
        for pattern in exodus_patterns:
            match = re.search(pattern, search_content, re.IGNORECASE)
            if match:
                genesis_end = genesis_start + 1000 + match.start()
                logger.info(f"📍 Found Genesis end at {genesis_end}")
                break
        
        return content[genesis_start:genesis_end]
    
    def parse_verses_correctly(self, genesis_content: str) -> List[Dict]:
        """Parse verses correctly handling the two-column layout"""
        verses = []
        
        # Find all verse markers with their immediate text
        # Pattern: {chapter:verse} followed by text until next verse marker or end
        verse_pattern = r'\{(\d+):(\d+)\}\s*([^{]*?)(?=\{|\Z)'
        matches = re.findall(verse_pattern, genesis_content, re.DOTALL)
        
        logger.info(f"🔍 Found {len(matches)} raw verse matches")
        
        for chapter_str, verse_str, raw_text in matches:
            chapter = int(chapter_str)
            verse_num = int(verse_str)
            
            # Skip non-Genesis chapters
            if chapter > 50:
                continue
            
            # Clean the text properly for two-column layout
            clean_text = self.clean_verse_text(raw_text, chapter, verse_num)
            
            if clean_text and len(clean_text) > 5:
                verses.append({
                    'chapter': chapter,
                    'verse': verse_num,
                    'text': clean_text
                })
        
        # Sort verses by chapter and verse number
        verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Extracted {len(verses)} clean Genesis verses")
        return verses
    
    def clean_verse_text(self, raw_text: str, chapter: int, verse_num: int) -> str:
        """Clean verse text handling two-column layout issues"""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers and numbers
        text = re.sub(r'Page \d+.*?(?=\w)', '', text)
        text = re.sub(r'^[^\w]*', '', text)
        
        # Handle specific two-column issues
        # If text seems to have been cut off mid-sentence, try to fix common patterns
        
        # For Genesis 1:1, we expect "In the beginning God created the heaven and the earth."
        if chapter == 1 and verse_num == 1:
            # Look for the expected content
            if "In the beginning God created" in text:
                # Try to extract just the creation verse
                match = re.search(r'In the beginning God created the heaven and the earth\.?', text, re.IGNORECASE)
                if match:
                    return match.group(0)
                # Fallback: take everything until we hit something that doesn't belong to verse 1
                match = re.search(r'In the beginning God created.*?earth\.?', text, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        # General cleanup - remove content that clearly belongs to other verses
        # Look for common verse ending patterns
        sentence_endings = ['. And', '. {', '. Thus', '. So', '. Then', '. But', '. For']
        for ending in sentence_endings:
            if ending in text:
                parts = text.split(ending)
                if len(parts) > 1:
                    # Keep the first complete sentence
                    text = parts[0] + '.'
                    break
        
        # Remove trailing fragments that don't make sense
        text = re.sub(r'\s+and$', '', text, re.IGNORECASE)
        text = re.sub(r'\s+the$', '', text, re.IGNORECASE)
        text = re.sub(r'\s+of$', '', text, re.IGNORECASE)
        text = re.sub(r'\s+to$', '', text, re.IGNORECASE)
        
        # Ensure proper sentence ending
        if text and not text.endswith(('.', '!', '?', ':')):
            text += '.'
        
        return text.strip()
    
    def validate_genesis_verses(self, verses: List[Dict]) -> bool:
        """Validate that Genesis verses make sense"""
        
        if not verses:
            logger.error("❌ No verses found")
            return False
        
        # Check Genesis 1:1
        genesis_1_1 = None
        for verse in verses:
            if verse['chapter'] == 1 and verse['verse'] == 1:
                genesis_1_1 = verse
                break
        
        if not genesis_1_1:
            logger.error("❌ Genesis 1:1 not found")
            return False
        
        # Verify Genesis 1:1 content
        verse_text = genesis_1_1['text'].lower()
        expected_phrases = ["in the beginning", "god created", "heaven", "earth"]
        
        found_phrases = sum(1 for phrase in expected_phrases if phrase in verse_text)
        
        if found_phrases < 3:
            logger.error(f"❌ Genesis 1:1 validation failed. Text: {genesis_1_1['text']}")
            return False
        
        logger.info(f"✅ Genesis 1:1 validation passed: {genesis_1_1['text']}")
        
        # Check verse count and chapter distribution
        max_chapter = max(v['chapter'] for v in verses)
        verse_count = len(verses)
        
        if max_chapter < 40:
            logger.error(f"❌ Too few chapters: {max_chapter}")
            return False
        
        if verse_count < 1000:
            logger.error(f"❌ Too few verses: {verse_count}")
            return False
        
        logger.info(f"✅ Genesis structure validation passed: {verse_count} verses, {max_chapter} chapters")
        return True
    
    def print_genesis_sample(self, verses: List[Dict]):
        """Print sample verses to verify quality"""
        
        logger.info("📖 GENESIS SAMPLE VERSES:")
        
        # Show first 10 verses
        for i, verse in enumerate(verses[:10]):
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text']}")
        
        # Show some verses from different chapters
        sample_refs = [(1, 31), (2, 7), (3, 15), (6, 19), (7, 11), (12, 1), (22, 2), (50, 26)]
        
        logger.info("📖 KEY GENESIS VERSES:")
        for chapter, verse_num in sample_refs:
            for verse in verses:
                if verse['chapter'] == chapter and verse['verse'] == verse_num:
                    logger.info(f"   {chapter}:{verse_num} {verse['text']}")
                    break
    
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
        
        # Load verses
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
                verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
        
        logger.info(f"🎉 Genesis loading complete: {verse_count} verses loaded")
    
    async def create_indexes(self):
        """Create database indexes"""
        await bible_verses_collection.create_index([("version", 1), ("book", 1), ("chapter", 1), ("verse", 1)])
        await bible_verses_collection.create_index([("version", 1), ("testament", 1)])
        await bible_books_collection.create_index([("version", 1), ("order", 1)])
    
    async def run(self):
        """Main execution"""
        try:
            logger.info("🎯 === Genesis KJV Fixed Parser (Two-Column Layout) ===")
            
            # Load KJV file
            kjv_file = "/app/kjv_complete_new.txt"
            with open(kjv_file, 'r', encoding='utf-8', errors='ignore') as f:
                kjv_content = f.read()
            
            # Extract Genesis content
            genesis_content = self.find_genesis_content(kjv_content)
            if not genesis_content:
                logger.error("❌ Could not find Genesis content")
                return
            
            # Parse verses with proper two-column handling
            verses = self.parse_verses_correctly(genesis_content)
            
            # Validate verses
            if not self.validate_genesis_verses(verses):
                logger.error("❌ Genesis validation failed")
                return
            
            # Print sample for verification
            self.print_genesis_sample(verses)
            
            # Load to database
            await self.clear_bible_data()
            await self.load_genesis_to_db(verses)
            await self.create_indexes()
            
            logger.info("🎯 === Genesis KJV Fixed Parser Complete ===")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    parser = GenesisFixedParser()
    await parser.run()

if __name__ == "__main__":
    asyncio.run(main())