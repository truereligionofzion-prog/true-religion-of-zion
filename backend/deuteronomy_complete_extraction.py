#!/usr/bin/env python3
"""
Deuteronomy Complete Extraction

Extract the COMPLETE Deuteronomy (all 34 chapters, 959 verses) from the source file.
Use the actual KJV text that's clearly present in kjv_complete_new.txt
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

class DeuteronomyCompleteExtraction:
    def __init__(self):
        # Target specifications for complete Deuteronomy
        self.target_chapters = 34
        self.target_verses = 959
        
    async def clear_incomplete_deuteronomy(self):
        """Clear incomplete Deuteronomy"""
        logger.info("🧹 Clearing incomplete Deuteronomy...")
        
        deleted = await bible_verses_collection.delete_many({"book": "Deuteronomy"})
        await bible_books_collection.delete_many({"name": "Deuteronomy"})
        
        logger.info(f"✅ Cleared incomplete Deuteronomy: {deleted.deleted_count} verses")
        
        # Verify foundation books
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        exodus_count = await bible_verses_collection.count_documents({"book": "Exodus"})
        leviticus_count = await bible_verses_collection.count_documents({"book": "Leviticus"})
        numbers_count = await bible_verses_collection.count_documents({"book": "Numbers"})
        
        logger.info(f"✅ Foundation preserved: Genesis={genesis_count}, Exodus={exodus_count}, Leviticus={leviticus_count}, Numbers={numbers_count}")
    
    def extract_complete_deuteronomy(self) -> List[Dict]:
        """Extract COMPLETE Deuteronomy from the source file"""
        
        logger.info("📖 Extracting COMPLETE Deuteronomy from kjv_complete_new.txt...")
        
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Cannot read source file: {e}")
            return []
        
        verses = []
        
        # Find Deuteronomy section precisely (we know it starts around line 7655)
        deuteronomy_start = content.find("The Fifth Book of Moses, called Deuteronomy")
        if deuteronomy_start == -1:
            logger.error("Cannot find Deuteronomy in source file")
            return []
        
        logger.info(f"📍 Found Deuteronomy at position {deuteronomy_start}")
        
        # Find Joshua boundary (next book after Deuteronomy)
        joshua_markers = [
            "Joshua",
            "JOSHUA",
            "The Book of Joshua"
        ]
        
        deuteronomy_end = -1
        for marker in joshua_markers:
            pos = content.find(marker, deuteronomy_start + 100000)  # Look well after Deuteronomy start
            if pos != -1:
                deuteronomy_end = pos
                logger.info(f"📍 Found Deuteronomy end at position {pos} (marker: {marker})")
                break
        
        if deuteronomy_end == -1:
            # Conservative boundary - Deuteronomy is long (34 chapters)
            deuteronomy_end = deuteronomy_start + 300000
            logger.info(f"📍 Using conservative Deuteronomy end: {deuteronomy_end}")
        
        # Extract complete Deuteronomy section
        deuteronomy_content = content[deuteronomy_start:deuteronomy_end]
        logger.info(f"📄 Complete Deuteronomy section: {len(deuteronomy_content)} characters")
        
        # Extract ALL verses using {chapter:verse} pattern
        pattern = r'\{(\d+):(\d+)\}'
        matches = list(re.finditer(pattern, deuteronomy_content))
        
        logger.info(f"🔍 Found {len(matches)} verse markers in Deuteronomy section")
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Deuteronomy bounds (chapters 1-34)
            if chapter < 1 or chapter > 34:
                continue
            
            # Extract verse text
            start_pos = match.end()
            
            # Find next verse marker or reasonable boundary
            next_match = re.search(r'\{\d+:\d+\}', deuteronomy_content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 500  # Conservative limit for last verses
            
            # Extract and clean text
            raw_text = deuteronomy_content[start_pos:end_pos]
            clean_text = self.clean_verse_text(raw_text)
            
            # Only keep substantial authentic content
            if clean_text and len(clean_text) > 15:
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
        
        # Sort by chapter and verse
        verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Complete extraction: {len(verses)} Deuteronomy verses")
        return verses
    
    def clean_verse_text(self, raw_text: str) -> str:
        """Clean verse text using proven method"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers and artifacts
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'Deuteronomy\s*', '', text)
        text = re.sub(r'\{.*?\}', '', text)  # Remove verse markers
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Take first meaningful sentence
        if '.' in text:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
            if sentences:
                text = sentences[0]
                if not text.endswith('.'):
                    text += '.'
        
        # Remove leading artifacts
        text = re.sub(r'^[^\w\[\]]+', '', text)
        
        # Proper capitalization
        if text and len(text) > 0 and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def validate_complete_extraction(self, verses: List[Dict]) -> bool:
        """Validate we extracted complete Deuteronomy"""
        
        # Check minimum verse count
        if len(verses) < 800:  # Should be close to 959
            logger.error(f"❌ Too few verses: {len(verses)} (expected ~959)")
            return False
        
        # Check chapter coverage
        chapters = set(v['chapter'] for v in verses)
        if len(chapters) < 30:  # Should have most chapters
            logger.error(f"❌ Missing chapters: {len(chapters)}/34")
            return False
        
        # Check for repetitive content
        texts = [v['text'] for v in verses]
        unique_texts = set(texts)
        uniqueness_pct = len(unique_texts) / len(texts) * 100
        
        if uniqueness_pct < 80:
            logger.error(f"❌ Too much repetitive content: {uniqueness_pct:.1f}% unique")
            return False
        
        # Check key verses
        verse_map = {(v['chapter'], v['verse']): v for v in verses}
        
        key_verses = [(1, 1), (6, 4), (34, 12)]
        for ch, v in key_verses:
            if (ch, v) not in verse_map:
                logger.error(f"❌ Missing key verse: Deuteronomy {ch}:{v}")
                return False
        
        logger.info(f"✅ Complete extraction validation passed: {len(verses)} verses")
        return True
    
    def print_extraction_summary(self, verses: List[Dict]):
        """Print summary of complete extraction"""
        
        logger.info("📊 COMPLETE DEUTERONOMY EXTRACTION SUMMARY:")
        
        # Chapter analysis
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        completion_pct = (len(verses) / self.target_verses * 100)
        logger.info(f"📊 Total: {len(verses)}/{self.target_verses} verses ({completion_pct:.1f}%)")
        logger.info(f"📊 Chapters: {len(chapters)}/34 covered")
        
        # Show chapter range
        if chapters:
            min_ch = min(chapters.keys())
            max_ch = max(chapters.keys())
            logger.info(f"📊 Chapter range: {min_ch} to {max_ch}")
        
        # Show key chapters
        key_chapters = [1, 6, 12, 28, 34]
        for ch in key_chapters:
            count = chapters.get(ch, 0)
            logger.info(f"   Chapter {ch}: {count} verses")
        
        # Sample content
        logger.info("📝 Sample complete Deuteronomy content:")
        for verse in verses[:5]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:70]}...")
        
        # Check for uniqueness
        texts = [v['text'] for v in verses]
        unique_texts = set(texts)
        uniqueness_pct = len(unique_texts) / len(texts) * 100
        logger.info(f"📊 Content uniqueness: {uniqueness_pct:.1f}%")
    
    async def load_complete_deuteronomy(self, verses: List[Dict]):
        """Load complete Deuteronomy to database"""
        
        logger.info("💾 Loading complete Deuteronomy...")
        
        # Book record
        chapters = set(v['chapter'] for v in verses)
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': 'Deuteronomy',
            'testament': 'old',
            'order': 5,
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
                'book': 'Deuteronomy',
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
        
        logger.info(f"✅ Complete Deuteronomy loaded: {len(verses)} verses")
    
    async def run(self):
        """Extract and load complete Deuteronomy"""
        try:
            logger.info("🎯 === Deuteronomy Complete Extraction - Extract ALL 34 Chapters ===")
            
            # Clear incomplete version
            await self.clear_incomplete_deuteronomy()
            
            # Extract complete Deuteronomy
            verses = self.extract_complete_deuteronomy()
            
            # Validate completeness
            if not self.validate_complete_extraction(verses):
                logger.error("❌ Complete extraction validation failed")
                return
            
            # Print summary
            self.print_extraction_summary(verses)
            
            # Load complete version
            await self.load_complete_deuteronomy(verses)
            
            logger.info("🎉 === Complete Deuteronomy Extraction Successful ===")
            logger.info("✅ Extracted complete Deuteronomy from source file")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    extractor = DeuteronomyCompleteExtraction()
    await extractor.run()

if __name__ == "__main__":
    asyncio.run(main())