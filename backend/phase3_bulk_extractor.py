#!/usr/bin/env python3
"""
Phase 3B: Bulk Bible Extraction System
Extract ALL chapters and verses from discovered books with ancient Hebrew divine names
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from scholarly_divine_names import ScholarlyDivineNameReplacer
from typing import List, Dict, Optional
import re

class Phase3BulkExtractor:
    """Complete Bible extraction system with divine name processing"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Load book mapping from Phase 3A
        with open('/app/backend/phase3_book_mapping.json', 'r') as f:
            self.book_data = json.load(f)
        
        self.divine_replacer = ScholarlyDivineNameReplacer()
        self.base_url = 'https://thepreceptbible.com/bible'
        
        # MongoDB connection
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Statistics tracking
        self.stats = {
            'books_processed': 0,
            'total_chapters': 0,
            'total_verses': 0,
            'divine_name_replacements': 0,
            'errors': 0
        }
    
    def extract_book_completely(self, book_id: int, book_name: str) -> List[Dict]:
        """Extract ALL chapters and verses from a single book"""
        print(f"📖 Extracting {book_name} (ID: {book_id})")
        
        all_verses = []
        page = 0
        
        while True:
            url = f"{self.base_url}?field_book_target_id={book_id}&page={page}"
            
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                verses = soup.select('div.verse')
                
                if not verses:  # No more verses on this page
                    break
                
                page_verses = []
                for verse_div in verses:
                    verse_data = self._extract_verse_data(verse_div, book_name)
                    if verse_data:
                        # Apply ancient Hebrew divine name logic
                        verse_data = self._apply_divine_names(verse_data)
                        page_verses.append(verse_data)
                
                all_verses.extend(page_verses)
                print(f"   Page {page}: {len(page_verses)} verses")
                
                # Check for pagination
                next_page = soup.select_one('a[title="Go to next page"]')
                if not next_page:
                    break
                
                page += 1
                time.sleep(0.5)  # Be respectful
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                self.stats['errors'] += 1
                break
        
        print(f"   ✅ Complete: {len(all_verses)} total verses")
        return all_verses
    
    def _extract_verse_data(self, verse_div, book_name: str) -> Optional[Dict]:
        """Extract individual verse data from HTML element"""
        try:
            # Get verse text
            verse_span = verse_div.find('span')
            if not verse_span:
                return None
            
            verse_text = verse_span.get_text(strip=True)
            
            # Extract verse number (usually at the beginning)
            verse_number_match = re.match(r'^(\d+)', verse_text)
            if not verse_number_match:
                return None
            
            verse_number = int(verse_number_match.group(1))
            verse_content = verse_text[len(verse_number_match.group(1)):].strip()
            
            # Try to determine chapter (this might need refinement)
            # For now, we'll use a simple approach - this can be enhanced
            chapter_number = self._determine_chapter(verse_div, verse_number)
            
            # Check for precepts
            has_precept = 'has-precept' in verse_div.get('class', [])
            
            return {
                'book': book_name,
                'chapter': chapter_number,
                'verse': verse_number,
                'text': verse_content,
                'has_precept': has_precept
            }
            
        except Exception as e:
            print(f"      Error extracting verse: {e}")
            return None
    
    def _determine_chapter(self, verse_div, verse_number: int) -> int:
        """Determine chapter number - simplified approach"""
        # Look for chapter context in parent containers
        parent = verse_div.parent
        while parent:
            chapter_text = parent.get_text()
            chapter_match = re.search(r'Chapter (\d+)', chapter_text, re.IGNORECASE)
            if chapter_match:
                return int(chapter_match.group(1))
            parent = parent.parent
        
        # Fallback: estimate based on verse number patterns
        # This is a simplified approach - Genesis 1 starts with verse 1, etc.
        if verse_number == 1:
            return getattr(self, '_current_chapter', 1)
        
        # For now, assume chapter 1 for all - this needs enhancement
        return 1
    
    def _apply_divine_names(self, verse_data: Dict) -> Dict:
        """Apply ancient Hebrew divine name replacements"""
        original_text = verse_data['text']
        
        # Apply our perfected divine name logic
        result = self.divine_replacer.apply_replacements(original_text)
        
        if result['total_replacements'] > 0:
            verse_data['text'] = result['text']
            self.stats['divine_name_replacements'] += result['total_replacements']
        
        return verse_data
    
    async def save_verses_to_database(self, verses: List[Dict], book_name: str):
        """Save extracted verses to MongoDB with duplicate prevention"""
        if not verses:
            return
        
        print(f"   💾 Saving {len(verses)} verses to database...")
        
        # Remove existing verses for this book to prevent duplicates
        await self.db.bible_verses.delete_many({'book': book_name})
        
        # Insert new verses
        await self.db.bible_verses.insert_many(verses)
        
        print(f"   ✅ Saved {len(verses)} verses for {book_name}")
    
    async def extract_all_books(self):
        """Extract all discovered books completely"""
        print("🚀 Phase 3B: Complete Bible Extraction")
        print("=" * 60)
        print(f"📚 Extracting {self.book_data['total_books']} books with ancient Hebrew divine names")
        print()
        
        book_mapping = self.book_data['book_mapping']
        
        for book_id_str, book_info in book_mapping.items():
            book_id = int(book_id_str)
            book_name = book_info['name']
            
            # Extract complete book
            verses = self.extract_book_completely(book_id, book_name)
            
            if verses:
                # Save to database
                await self.save_verses_to_database(verses, book_name)
                
                # Update statistics
                self.stats['books_processed'] += 1
                self.stats['total_verses'] += len(verses)
                
                # Estimate chapters (simplified)
                chapters = max([v['chapter'] for v in verses] + [1])
                self.stats['total_chapters'] += chapters
            
            # Progress report
            progress = (self.stats['books_processed'] / self.book_data['total_books']) * 100
            print(f"   📊 Progress: {progress:.1f}% ({self.stats['books_processed']}/{self.book_data['total_books']} books)")
            print(f"   📈 Total verses: {self.stats['total_verses']:,}")
            print(f"   ✨ Divine name replacements: {self.stats['divine_name_replacements']:,}")
            print()
            
            # Small delay between books
            time.sleep(1)
        
        # Final report
        await self._generate_final_report()
    
    async def _generate_final_report(self):
        """Generate comprehensive extraction report"""
        print("🎯 Phase 3B Complete - Final Report")
        print("=" * 50)
        print(f"📚 Books extracted: {self.stats['books_processed']}")
        print(f"📖 Chapters processed: {self.stats['total_chapters']}")
        print(f"📝 Verses extracted: {self.stats['total_verses']:,}")
        print(f"✨ Divine name replacements: {self.stats['divine_name_replacements']:,}")
        print(f"❌ Errors encountered: {self.stats['errors']}")
        
        # Verify database content
        db_verse_count = await self.db.bible_verses.count_documents({})
        print(f"💾 Database verification: {db_verse_count:,} verses stored")
        
        # Coverage analysis
        expected_verses = 31000  # Approximate Bible size
        coverage = (self.stats['total_verses'] / expected_verses) * 100
        print(f"📊 Coverage: {coverage:.1f}% of complete Bible")
        
        if coverage > 80:
            print("✅ EXCELLENT: Near-complete Bible extraction achieved!")
        elif coverage > 50:
            print("✅ GOOD: Substantial Bible content extracted")
        else:
            print("⚠️  PARTIAL: May need additional book discovery")
        
        print(f"\\n🎯 Ready for Phase 3C: UI Integration & Testing")

if __name__ == "__main__":
    async def main():
        extractor = Phase3BulkExtractor()
        await extractor.extract_all_books()
    
    print("Starting Phase 3B: Complete Bible Extraction...")
    print("This will extract ALL chapters and verses from discovered books")
    print("with ancient Hebrew divine name processing (YHWH, Elohim, YHUH)")
    print()
    
    asyncio.run(main())