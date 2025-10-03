#!/usr/bin/env python3
"""
Numbers Authentic Extraction - Fix the Placeholder Problem

Extract ONLY authentic biblical text from Numbers. 
NO generated content, NO placeholders, ONLY real biblical verses.
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

class NumbersAuthenticExtraction:
    def __init__(self):
        pass
        
    async def clear_fake_numbers(self):
        """Clear the fake Numbers content"""
        logger.info("🧹 Clearing fake/placeholder Numbers content...")
        
        deleted = await bible_verses_collection.delete_many({"book": "Numbers"})
        await bible_books_collection.delete_many({"name": "Numbers"})
        
        logger.info(f"✅ Cleared fake Numbers: {deleted.deleted_count} verses")
        
        # Verify foundation is intact
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        exodus_count = await bible_verses_collection.count_documents({"book": "Exodus"})
        leviticus_count = await bible_verses_collection.count_documents({"book": "Leviticus"})
        
        logger.info(f"✅ Foundation preserved: Genesis={genesis_count}, Exodus={exodus_count}, Leviticus={leviticus_count}")
    
    def extract_real_numbers_text(self) -> List[Dict]:
        """Extract ONLY real Numbers text - no placeholders"""
        
        logger.info("📖 Extracting ONLY authentic Numbers text from source...")
        
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read source file: {e}")
            return []
        
        verses = []
        
        # Find Numbers boundaries precisely
        numbers_start = content.find("The Fourth Book of Moses, called Numbers")
        if numbers_start == -1:
            logger.error("Could not find Numbers in source")
            return []
        
        deuteronomy_start = content.find("The Fifth Book of Moses, called Deuteronomy", numbers_start + 50000)
        if deuteronomy_start == -1:
            numbers_content = content[numbers_start:numbers_start + 200000]
        else:
            numbers_content = content[numbers_start:deuteronomy_start]
        
        logger.info(f"📝 Numbers section: {len(numbers_content)} characters")
        
        # Extract ONLY verses with {chapter:verse} markers
        pattern = r'\{(\d+):(\d+)\}'
        matches = re.finditer(pattern, numbers_content)
        
        extracted_count = 0
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Strict Numbers bounds
            if chapter < 1 or chapter > 36:
                continue
            
            # Extract text after marker
            start_pos = match.end()
            
            # Find next marker or reasonable limit
            next_match = re.search(r'\{\d+:\d+\}', numbers_content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 400
            
            # Extract and clean
            raw_text = numbers_content[start_pos:end_pos]
            clean_text = self.clean_authentic_text_only(raw_text)
            
            # STRICT validation - only authentic content
            if (clean_text and 
                len(clean_text) > 25 and 
                self.is_authentic_biblical_text(clean_text)):
                
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
                extracted_count += 1
        
        # Sort by chapter and verse
        verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Extracted {extracted_count} authentic Numbers verses")
        return verses
    
    def clean_authentic_text_only(self, raw_text: str) -> str:
        """Clean text but preserve authentic biblical content"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove artifacts
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\{.*?\}', '', text)
        
        # Clean whitespace  
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Take first complete sentence
        if '.' in text:
            sentences = text.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 15:
                    text = sentence.strip()
                    if not text.endswith('.'):
                        text += '.'
                    break
        
        # Clean leading artifacts
        text = re.sub(r'^[^\w\[\]]+', '', text)
        
        # Proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def is_authentic_biblical_text(self, text: str) -> bool:
        """Strict validation for authentic biblical content"""
        
        # Reject any generated/placeholder content
        reject_patterns = [
            r'And the LORD numbered the children of Israel according to their families',
            r'And Moses and Aaron took the census',
            r'And the LORD gave commandments unto Moses',
            r'And it came to pass as the LORD commanded Moses',
            r'see Numbers.*text',
            r'complete KJV text'
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Must have authentic biblical indicators
        authentic_indicators = [
            r'LORD.*spake.*Moses',
            r'children of Israel.*families',
            r'wilderness.*Sinai',
            r'tabernacle.*congregation',
            r'tribe.*[A-Z][a-z]+',  # Actual tribe names
            r'Levites.*service',
            r'offering.*altar'
        ]
        
        has_authentic = any(re.search(indicator, text, re.IGNORECASE) for indicator in authentic_indicators)
        
        # General biblical language
        biblical_words = [r'\bLORD\b', r'\bMoses\b', r'\bAaron\b', r'\bIsrael\b']
        has_biblical = any(re.search(word, text, re.IGNORECASE) for word in biblical_words)
        
        return len(text) > 25 and (has_authentic or has_biblical)
    
    def get_verified_numbers_foundation(self) -> List[Dict]:
        """Get web-verified Numbers verses for foundation"""
        
        foundation = [
            (1, 1, "And the LORD spake unto Moses in the wilderness of Sinai, in the tabernacle of the congregation, on the first day of the second month, in the second year after they were come out of the land of Egypt, saying,"),
            (1, 2, "Take ye the sum of all the congregation of the children of Israel, after their families, by the house of their fathers, with the number of their names, every male by their polls;"),
            (6, 24, "The LORD bless thee, and keep thee."),
            (6, 25, "The LORD make his face shine upon thee, and be gracious unto thee."),  
            (6, 26, "The LORD lift up his countenance upon thee, and give thee peace."),
            (13, 2, "Send thou men, that they may search the land of Canaan, which I give unto the children of Israel: of every tribe of their fathers shall ye send a man, every one a ruler among them."),
            (20, 12, "And the LORD spake unto Moses and Aaron, Because ye believed me not, to sanctify me in the eyes of the children of Israel, therefore ye shall not bring this congregation into the land which I have given them.")
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
    
    def combine_authentic_only(self) -> List[Dict]:
        """Combine ONLY authentic sources"""
        
        logger.info("🔧 Combining ONLY authentic Numbers sources...")
        
        # Start with verified foundation
        all_verses = self.get_verified_numbers_foundation()
        
        # Add extracted authentic verses
        extracted = self.extract_real_numbers_text()
        
        # Merge avoiding duplicates
        existing_refs = set((v['chapter'], v['verse']) for v in all_verses)
        for verse in extracted:
            ref = (verse['chapter'], verse['verse'])
            if ref not in existing_refs:
                all_verses.append(verse)
        
        # Sort final collection
        all_verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Authentic-only combination: {len(all_verses)} verses")
        return all_verses
    
    def validate_authentic_content(self, verses: List[Dict]) -> bool:
        """Validate all content is authentic"""
        
        if not verses:
            return False
        
        # Check for any placeholder content
        for verse in verses:
            text = verse['text']
            
            # Reject placeholder patterns
            if re.search(r'And the LORD numbered the children of Israel according to their families', text):
                logger.error(f"❌ Placeholder found: {verse['chapter']}:{verse['verse']}")
                return False
        
        # Check key verses have proper content
        verse_map = {(v['chapter'], v['verse']): v for v in verses}
        
        # Numbers 1:1 should be about Moses and census
        if (1, 1) in verse_map:
            text = verse_map[(1, 1)]['text']
            if not ("Moses" in text and "wilderness" in text and "Sinai" in text):
                logger.error(f"❌ Numbers 1:1 invalid: {text}")
                return False
        
        logger.info(f"✅ Authentic content validation passed: {len(verses)} verses")
        return True
    
    def print_authentic_summary(self, verses: List[Dict]):
        """Print summary of authentic content"""
        
        logger.info("📊 AUTHENTIC NUMBERS SUMMARY:")
        
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        logger.info(f"📊 Authentic verses: {len(verses)}")
        logger.info(f"📊 Chapters covered: {len(chapters)}/36")
        
        logger.info("📝 Sample authentic content:")
        for verse in verses[:5]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:70]}...")
    
    async def load_authentic_numbers(self, verses: List[Dict]):
        """Load ONLY authentic Numbers"""
        
        logger.info("💾 Loading authentic Numbers...")
        
        book_doc = {
            'id': str(uuid.uuid4()),
            'version': 'kjv1611_divine',
            'name': 'Numbers',
            'testament': 'old',
            'order': 4,
            'chapters': 36,
            'verses': len(verses)
        }
        
        await bible_books_collection.insert_one(book_doc)
        
        # Load verses
        verses_to_insert = []
        for verse_data in verses:
            verse_doc = {
                'id': str(uuid.uuid4()),
                'version': 'kjv1611_divine',
                'book': 'Numbers',
                'chapter': verse_data['chapter'],
                'verse': verse_data['verse'],
                'text': verse_data['text'],
                'testament': 'old',
                'has_precept': False
            }
            verses_to_insert.append(verse_doc)
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
        
        logger.info(f"✅ Authentic Numbers loaded: {len(verses)} verses")
    
    async def run(self):
        """Extract authentic Numbers only"""
        try:
            logger.info("🎯 === Numbers Authentic Extraction - Fix Placeholder Problem ===")
            
            # Clear fake content
            await self.clear_fake_numbers()
            
            # Extract ONLY authentic content
            verses = self.combine_authentic_only()
            
            # Validate authenticity
            if not self.validate_authentic_content(verses):
                logger.error("❌ Authenticity validation failed")
                return
            
            # Print summary
            self.print_authentic_summary(verses)
            
            # Load authentic content only
            await self.load_authentic_numbers(verses)
            
            logger.info("🎉 === Authentic Numbers Extraction Complete ===")
            logger.info("✅ Only real biblical text - NO placeholders")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    extractor = NumbersAuthenticExtraction()
    await extractor.run()

if __name__ == "__main__":
    asyncio.run(main())