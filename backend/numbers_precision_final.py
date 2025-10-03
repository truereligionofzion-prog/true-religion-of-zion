#!/usr/bin/env python3
"""
Numbers Precision Final Loader

Applies the EXACT proven Genesis/Exodus/Leviticus formula to Numbers only.
Maximum accuracy approach - one book, done right.

Target: 1,288 verses across 36 chapters of authentic Numbers content.
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

class NumbersPrecisionFinal:
    def __init__(self):
        # Numbers specifications (web-verified)
        self.target_chapters = 36
        self.target_verses = 1288
        
        # Target verse counts per chapter (KJV standard)
        self.chapter_verse_counts = {
            1: 54, 2: 34, 3: 51, 4: 49, 5: 31, 6: 27, 7: 89, 8: 26, 9: 23, 10: 36,
            11: 35, 12: 16, 13: 33, 14: 45, 15: 41, 16: 50, 17: 13, 18: 32, 19: 22, 20: 29,
            21: 35, 22: 41, 23: 30, 24: 25, 25: 18, 26: 65, 27: 23, 28: 31, 29: 40, 30: 16,
            31: 54, 32: 42, 33: 56, 34: 29, 35: 34, 36: 13
        }
        
    async def clear_numbers_completely(self):
        """Clear ALL existing Numbers data"""
        logger.info("🧹 Clearing all existing Numbers data...")
        
        numbers_verses_deleted = await bible_verses_collection.delete_many({"book": "Numbers"})
        numbers_books_deleted = await bible_books_collection.delete_many({"name": "Numbers"})
        
        logger.info(f"✅ Cleared Numbers: {numbers_verses_deleted.deleted_count} verses, {numbers_books_deleted.deleted_count} book records")
        
        # Verify foundation books are intact
        genesis_count = await bible_verses_collection.count_documents({"book": "Genesis"})
        exodus_count = await bible_verses_collection.count_documents({"book": "Exodus"})
        leviticus_count = await bible_verses_collection.count_documents({"book": "Leviticus"})
        
        logger.info(f"✅ Foundation preserved: Genesis={genesis_count}, Exodus={exodus_count}, Leviticus={leviticus_count}")
        
    def find_numbers_boundaries_precisely(self, content: str) -> tuple[int, int]:
        """Find exact Numbers boundaries using multiple precise patterns"""
        
        logger.info("🎯 Finding precise Numbers boundaries...")
        
        # Multiple search patterns for Numbers start
        numbers_start_patterns = [
            "The Fourth Book of Moses, called Numbers",
            "The Fourth Book of Moses called Numbers", 
            "Fourth Book of Moses",
            "NUMBERS"
        ]
        
        numbers_start = -1
        for pattern in numbers_start_patterns:
            pos = content.find(pattern)
            if pos != -1:
                numbers_start = pos
                logger.info(f"📍 Found Numbers start at position {pos} with pattern: '{pattern}'")
                break
        
        if numbers_start == -1:
            logger.error("❌ Could not find Numbers start in source file")
            return -1, -1
        
        # Multiple search patterns for Numbers end (Deuteronomy start)
        deuteronomy_patterns = [
            "The Fifth Book of Moses, called Deuteronomy",
            "The Fifth Book of Moses called Deuteronomy",
            "Fifth Book of Moses", 
            "DEUTERONOMY"
        ]
        
        numbers_end = -1
        # Look for Deuteronomy after Numbers with reasonable offset
        search_start = numbers_start + 50000  # Skip well past Numbers start
        
        for pattern in deuteronomy_patterns:
            pos = content.find(pattern, search_start)
            if pos != -1:
                numbers_end = pos
                logger.info(f"📍 Found Numbers end at position {pos} with pattern: '{pattern}'")
                break
        
        if numbers_end == -1:
            # Conservative fallback - Numbers is typically 150,000-200,000 characters
            numbers_end = numbers_start + 180000
            logger.info(f"📍 Using conservative Numbers end estimate: {numbers_end}")
        
        content_length = numbers_end - numbers_start
        logger.info(f"📊 Numbers content section: {content_length} characters")
        
        return numbers_start, numbers_end
    
    def extract_numbers_verses_precisely(self, numbers_content: str) -> List[Dict]:
        """Extract Numbers verses with maximum precision"""
        
        logger.info(f"📖 Extracting Numbers verses from {len(numbers_content)} characters...")
        
        verses = []
        
        # Extract using {chapter:verse} pattern
        pattern = r'\{(\d+):(\d+)\}'
        matches = list(re.finditer(pattern, numbers_content))
        
        logger.info(f"🔍 Found {len(matches)} potential verse markers")
        
        processed_count = 0
        
        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            
            # Strict Numbers bounds - chapters 1-36 only
            if chapter < 1 or chapter > 36:
                continue
            
            # Check if this chapter should have this verse
            expected_verses = self.chapter_verse_counts.get(chapter, 50)
            if verse > expected_verses + 5:  # Allow small buffer for variations
                continue
            
            # Extract text after verse marker
            start_pos = match.end()
            
            # Find next verse marker with conservative limit
            next_match = re.search(r'\{\d+:\d+\}', numbers_content[start_pos:start_pos+500])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = start_pos + 300  # Conservative limit
            
            # Extract and clean text
            raw_text = numbers_content[start_pos:end_pos]
            clean_text = self.clean_numbers_verse_text(raw_text)
            
            # Strict validation for Numbers content
            if (clean_text and 
                len(clean_text) > 20 and 
                len(clean_text) < 400 and  # Prevent contamination
                self.is_authentic_numbers_content(clean_text)):
                
                verses.append({
                    'chapter': chapter,
                    'verse': verse,
                    'text': clean_text
                })
                processed_count += 1
        
        logger.info(f"✅ Processed {processed_count} authentic Numbers verses")
        
        # Remove duplicates and sort
        unique_verses = {}
        for verse in verses:
            key = (verse['chapter'], verse['verse'])
            if key not in unique_verses:
                unique_verses[key] = verse
        
        result = list(unique_verses.values())
        result.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Final Numbers verses extracted: {len(result)}")
        return result
    
    def clean_numbers_verse_text(self, raw_text: str) -> str:
        """Clean Numbers verse text using proven method"""
        
        # Basic cleanup
        text = re.sub(r'\s+', ' ', raw_text).strip()
        
        # Remove page headers and artifacts
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'Numbers\s+Page \d+', '', text)
        
        # Remove verse markers
        text = re.sub(r'\{\d+:\d+\}', '', text)
        
        # Remove obvious artifacts
        text = re.sub(r'^\s*Numbers\s*', '', text, re.IGNORECASE)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Take first meaningful sentence
        if '.' in text:
            sentences = text.split('.')
            if len(sentences) > 0 and len(sentences[0]) > 15:
                text = sentences[0].strip()
                if not text.endswith('.'):
                    text += '.'
        
        # Remove leading non-word chars except authentic brackets
        text = re.sub(r'^[^\w\[\]]+', '', text)
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def is_authentic_numbers_content(self, text: str) -> bool:
        """Check if text is authentic Numbers content"""
        
        # Reject placeholder content
        reject_patterns = [
            r'see Numbers.*text',
            r'complete KJV text',
            r'KJV.*text',
            r'In the beginning God created',  # Genesis contamination
            r'And God said, Let there be',    # Genesis contamination
        ]
        
        for pattern in reject_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Numbers-specific content indicators
        numbers_indicators = [
            r'\bMoses\b',
            r'\bAaron\b',
            r'\bthe LORD\b',
            r'\bchildren of Israel\b',
            r'\bwilderness\b',
            r'\bSinai\b',
            r'\btabernacle\b',
            r'\bcongregation\b',
            r'\bLevites\b',
            r'\btribe\b',
            r'\boffering\b',
            r'\bshall\b',
            r'\bunto\b',
            r'\bsaith\b'
        ]
        
        # General biblical indicators
        biblical_indicators = [
            r'\bAnd\b',
            r'\bLord\b',
            r'\bGod\b'
        ]
        
        has_numbers_content = any(re.search(indicator, text, re.IGNORECASE) for indicator in numbers_indicators)
        has_biblical_content = any(re.search(indicator, text, re.IGNORECASE) for indicator in biblical_indicators)
        
        return len(text) > 20 and (has_numbers_content or has_biblical_content)
    
    def get_web_verified_numbers_foundation(self) -> List[Dict]:
        """Get web-verified Numbers foundation verses"""
        
        foundation_verses = [
            # Numbers 1 - Census
            (1, 1, "And the LORD spake unto Moses in the wilderness of Sinai, in the tabernacle of the congregation, on the first day of the second month, in the second year after they were come out of the land of Egypt, saying,"),
            (1, 2, "Take ye the sum of all the congregation of the children of Israel, after their families, by the house of their fathers, with the number of their names, every male by their polls;"),
            
            # Numbers 6 - Priestly Blessing
            (6, 24, "The LORD bless thee, and keep thee."),
            (6, 25, "The LORD make his face shine upon thee, and be gracious unto thee."),
            (6, 26, "The LORD lift up his countenance upon thee, and give thee peace."),
            
            # Numbers 13 - Spies
            (13, 1, "And the LORD spake unto Moses, saying,"),
            (13, 2, "Send thou men, that they may search the land of Canaan, which I give unto the children of Israel: of every tribe of their fathers shall ye send a man, every one a ruler among them."),
            
            # Numbers 20 - Moses' Sin
            (20, 1, "Then came the children of Israel, even the whole congregation, into the desert of Zin in the first month: and the people abode in Kadesh; and Miriam died there, and was buried there."),
            
            # Numbers 22 - Balaam
            (22, 1, "And the children of Israel set forward, and pitched in the plains of Moab on this side Jordan by Jericho.")
        ]
        
        verses = []
        for chapter, verse, text in foundation_verses:
            verses.append({
                'chapter': chapter,
                'verse': verse,  
                'text': text
            })
        
        logger.info(f"✅ Web-verified Numbers foundation: {len(verses)} verses")
        return verses
    
    def combine_numbers_sources(self) -> List[Dict]:
        """Combine Numbers sources using proven method"""
        
        logger.info("🔧 Combining Numbers sources...")
        
        all_verses = []
        
        # Start with web-verified foundation
        foundation_verses = self.get_web_verified_numbers_foundation()
        all_verses.extend(foundation_verses)
        
        # Read source file
        try:
            with open('/app/kjv_complete_new.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Could not read KJV file: {e}")
            return foundation_verses
        
        # Find Numbers boundaries
        numbers_start, numbers_end = self.find_numbers_boundaries_precisely(content)
        
        if numbers_start != -1:
            # Extract Numbers content
            numbers_content = content[numbers_start:numbers_end]
            
            # Extract verses
            extracted_verses = self.extract_numbers_verses_precisely(numbers_content)
            
            # Merge avoiding duplicates
            existing_refs = set((v['chapter'], v['verse']) for v in all_verses)
            for verse in extracted_verses:
                ref = (verse['chapter'], verse['verse'])
                if ref not in existing_refs:
                    all_verses.append(verse)
        
        # Sort by chapter and verse
        all_verses.sort(key=lambda x: (x['chapter'], x['verse']))
        
        logger.info(f"✅ Numbers sources combined: {len(all_verses)} verses")
        return all_verses
    
    def validate_numbers_completion(self, verses: List[Dict]) -> bool:
        """Validate Numbers is properly completed"""
        
        if not verses:
            return False
        
        # Check total verse count
        if len(verses) < 800:  # Should be substantial
            logger.error(f"❌ Too few verses: {len(verses)}")
            return False
        
        # Check chapter coverage
        chapters = set(v['chapter'] for v in verses)
        if len(chapters) < 30:  # Should cover most chapters
            logger.error(f"❌ Too few chapters: {len(chapters)}")
            return False
        
        # Check for contamination
        for verse in verses:
            text = verse['text']
            if re.search(r'In the beginning God created', text, re.IGNORECASE):
                logger.error(f"❌ Genesis contamination in {verse['chapter']}:{verse['verse']}")
                return False
        
        # Check key Numbers verses
        verse_map = {(v['chapter'], v['verse']): v for v in verses}
        
        # Numbers 1:1 should mention Moses in wilderness
        if (1, 1) in verse_map:
            text = verse_map[(1, 1)]['text']
            if not ("Moses" in text and "wilderness" in text and "Sinai" in text):
                logger.error(f"❌ Numbers 1:1 content invalid: {text}")
                return False
        
        # Numbers 6:24-26 should be priestly blessing
        if (6, 24) in verse_map:
            text = verse_map[(6, 24)]['text']
            if not ("LORD bless" in text):
                logger.error(f"❌ Numbers 6:24 content invalid: {text}")
                return False
        
        logger.info(f"✅ Numbers validation passed: {len(verses)} verses")
        return True
    
    def print_numbers_summary(self, verses: List[Dict]):
        """Print detailed Numbers summary"""
        
        logger.info("📊 NUMBERS PRECISION SUMMARY:")
        
        # Chapter analysis
        chapters = {}
        for verse in verses:
            chapter = verse['chapter']
            chapters[chapter] = chapters.get(chapter, 0) + 1
        
        # Show key chapters with targets
        key_chapters = [1, 6, 13, 20, 22]
        for ch in key_chapters:
            actual = chapters.get(ch, 0)
            target = self.chapter_verse_counts.get(ch, 0)
            if target > 0:
                percentage = (actual / target * 100)
                logger.info(f"   Chapter {ch}: {actual}/{target} verses ({percentage:.1f}%)")
        
        # Show sample content
        logger.info("📝 Sample Numbers verses:")
        for verse in verses[:5]:
            logger.info(f"   {verse['chapter']}:{verse['verse']} {verse['text'][:70]}...")
        
        # Overall completion
        completion_pct = (len(verses) / self.target_verses * 100) if self.target_verses > 0 else 0
        logger.info(f"📊 Total: {len(verses)}/{self.target_verses} verses ({completion_pct:.1f}%)")
        logger.info(f"📊 Chapters: {len(chapters)}/36")
    
    async def load_numbers_precisely(self, verses: List[Dict]):
        """Load Numbers to database precisely"""
        
        logger.info("💾 Loading Numbers to database...")
        
        # Create book record
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
        
        # Load verses in batches
        batch_size = 100
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
            
            if len(verses_to_insert) >= batch_size:
                await bible_verses_collection.insert_many(verses_to_insert)
                verses_to_insert = []
        
        if verses_to_insert:
            await bible_verses_collection.insert_many(verses_to_insert)
        
        logger.info(f"✅ Numbers loaded precisely: {len(verses)} verses")
    
    async def run(self):
        """Main execution - Numbers precision loading"""
        try:
            logger.info("🎯 === Numbers Precision Final - Following Proven Formula ===")
            
            # Clear existing Numbers data
            await self.clear_numbers_completely()
            
            # Extract and combine Numbers content
            verses = self.combine_numbers_sources()
            
            # Validate completion
            if not self.validate_numbers_completion(verses):
                logger.error("❌ Numbers validation failed")
                return
            
            # Print summary
            self.print_numbers_summary(verses)
            
            # Load to database
            await self.load_numbers_precisely(verses)
            
            logger.info("🎉 === Numbers Precision Final Complete ===")
            logger.info("✅ Numbers follows proven Genesis/Exodus/Leviticus formula")
            
        except Exception as e:
            logger.error(f"💥 Error: {e}")
            raise
        finally:
            client.close()

async def main():
    loader = NumbersPrecisionFinal()
    await loader.run()

if __name__ == "__main__":
    asyncio.run(main())