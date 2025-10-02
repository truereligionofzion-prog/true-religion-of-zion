#!/usr/bin/env python3
"""
Phase 3B: Complete 81-Book Bible Extraction
Extract ALL chapters and verses from all discovered books with ancient Hebrew divine names
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

class CompleteExtractionSystem:
    """Complete Bible extraction system for all 81 books"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Load complete book mapping
        with open('/app/backend/phase3_complete_mapping.json', 'r') as f:
            self.mapping_data = json.load(f)
        
        self.divine_replacer = ScholarlyDivineNameReplacer()
        self.base_url = 'https://thepreceptbible.com/bible'
        
        # MongoDB connection
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Enhanced statistics tracking
        self.stats = {
            'books_processed': 0,
            'total_books': len(self.mapping_data['book_mapping']),
            'total_chapters': 0,
            'total_verses': 0,
            'divine_name_replacements': 0,
            'errors': 0,
            'processing_time': 0
        }
        
        self.current_chapter = 1
    
    def extract_book_with_chapters(self, book_id: int, book_name: str) -> List[Dict]:
        """Extract complete book with proper chapter detection"""
        print(f"📖 Extracting {book_name} (ID: {book_id})")
        start_time = time.time()
        
        all_verses = []
        page = 0
        self.current_chapter = 1
        
        while True:
            url = f"{self.base_url}?field_book_target_id={book_id}&page={page}"
            
            try:
                response = self.session.get(url, timeout=12)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                verses = soup.select('div.verse')
                
                if not verses:  # No more verses
                    break
                
                page_verses = []
                for verse_div in verses:
                    verse_data = self._extract_verse_with_chapter(verse_div, book_name)
                    if verse_data:
                        # Apply ancient Hebrew divine name logic
                        verse_data = self._apply_divine_names(verse_data)
                        page_verses.append(verse_data)
                
                all_verses.extend(page_verses)
                
                # Enhanced progress reporting
                chapters_found = len(set(v['chapter'] for v in all_verses))
                print(f"   Page {page}: {len(page_verses)} verses, {chapters_found} chapters total")
                
                # Check pagination
                next_page = soup.select_one('a[title="Go to next page"]')
                if not next_page:
                    break
                
                page += 1
                time.sleep(0.4)  # Balanced speed and respect
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {e}")
                self.stats['errors'] += 1
                break
        
        # Final book statistics
        chapters = len(set(v['chapter'] for v in all_verses))
        duration = time.time() - start_time
        
        print(f"   ✅ Complete: {len(all_verses)} verses, {chapters} chapters ({duration:.1f}s)")
        
        return all_verses
    
    def _extract_verse_with_chapter(self, verse_div, book_name: str) -> Optional[Dict]:
        """Enhanced verse extraction with better chapter detection"""
        try:
            # METHOD 1: Try to get full text from the entire div
            full_div_text = verse_div.get_text(strip=True)
            
            # METHOD 2: Try to find verse number and text separately
            verse_spans = verse_div.find_all('span')
            
            # Debug logging
            print(f"   DEBUG: verse_div classes: {verse_div.get('class', [])}")
            print(f"   DEBUG: full_div_text: '{full_div_text[:100]}...'")
            print(f"   DEBUG: found {len(verse_spans)} spans")
            
            # Try different extraction methods
            verse_number = None
            verse_content = None
            
            # Method 1: Extract from full div text
            if full_div_text:
                verse_match = re.match(r'^(\d+)(.+)', full_div_text)
                if verse_match:
                    verse_number = int(verse_match.group(1))
                    verse_content = verse_match.group(2).strip()
                    print(f"   DEBUG Method 1: verse {verse_number}, content: '{verse_content[:50]}...'")
            
            # Method 2: If that failed, try span-by-span
            if not verse_content and verse_spans:
                for i, span in enumerate(verse_spans):
                    span_text = span.get_text(strip=True)
                    print(f"   DEBUG span {i}: '{span_text[:50]}...' classes: {span.get('class', [])}")
                    
                    # Look for verse number
                    if span_text.isdigit() and not verse_number:
                        verse_number = int(span_text)
                        print(f"   DEBUG: Found verse number {verse_number}")
                    
                    # Look for verse content (longer text)
                    elif len(span_text) > 10 and not verse_content:
                        verse_content = span_text
                        print(f"   DEBUG: Found verse content: '{verse_content[:50]}...'")
            
            # Validation
            if not verse_number or not verse_content or len(verse_content) < 5:
                print(f"   DEBUG: FAILED - verse_number: {verse_number}, content length: {len(verse_content) if verse_content else 0}")
                return None
            
            # Enhanced chapter detection
            chapter_number = self._detect_chapter_enhanced(verse_div, verse_number, verse_content)
            
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
            return None
    
    def _detect_chapter_enhanced(self, verse_div, verse_number: int, verse_content: str) -> int:
        """Enhanced chapter detection using multiple methods"""
        
        # Method 1: Look for chapter indicators in surrounding HTML
        parent = verse_div.parent
        while parent and parent.name != 'body':
            text = parent.get_text()
            
            # Look for "Chapter X" patterns
            chapter_match = re.search(r'chapter\s+(\d+)', text, re.IGNORECASE)
            if chapter_match:
                found_chapter = int(chapter_match.group(1))
                self.current_chapter = found_chapter
                return found_chapter
            
            parent = parent.parent
        
        # Method 2: Detect chapter breaks by verse 1 patterns
        if verse_number == 1:
            # Check if this looks like a new chapter
            content_lower = verse_content.lower()
            
            # Common chapter 1 starting patterns
            chapter_1_patterns = [
                'in the beginning',
                'and it came to pass',
                'now it came to pass', 
                'the book of',
                'paul'  # Epistles often start with Paul
            ]
            
            if any(pattern in content_lower for pattern in chapter_1_patterns):
                if verse_number == 1 and len(verse_content) > 20:
                    self.current_chapter += 1
        
        # Method 3: Sequential chapter tracking
        elif verse_number == 1:
            self.current_chapter += 1
        
        return self.current_chapter
    
    def _apply_divine_names(self, verse_data: Dict) -> Dict:
        """Apply perfected ancient Hebrew divine name replacements"""
        original_text = verse_data['text']
        
        # Apply our ancient manuscript-based logic
        result = self.divine_replacer.apply_replacements(original_text)
        
        if result['total_replacements'] > 0:
            verse_data['text'] = result['text']
            self.stats['divine_name_replacements'] += result['total_replacements']
        
        return verse_data
    
    async def save_book_to_database(self, verses: List[Dict], book_name: str):
        """Save complete book with duplicate prevention and statistics"""
        if not verses:
            return
        
        # Remove existing verses for this book
        deleted = await self.db.bible_verses.delete_many({'book': book_name})
        
        # Insert new verses
        await self.db.bible_verses.insert_many(verses)
        
        # Update statistics
        chapters = len(set(v['chapter'] for v in verses))
        self.stats['total_chapters'] += chapters
        self.stats['total_verses'] += len(verses)
        
        print(f"   💾 Database: Saved {len(verses)} verses, {chapters} chapters")
        if deleted.deleted_count > 0:
            print(f"   🔄 Replaced {deleted.deleted_count} existing verses")
    
    async def extract_all_81_books(self):
        """Complete extraction of all 81 discovered books"""
        print("🚀 Phase 3B: Complete 81-Book Bible Extraction")
        print("=" * 65)
        print(f"📚 Extracting {self.stats['total_books']} books with ancient Hebrew divine names")
        print(f"🎯 Target: Complete 1611 KJV Bible + Apocrypha")
        print()
        
        start_time = time.time()
        book_mapping = self.mapping_data['book_mapping']
        
        for i, (book_id_str, book_info) in enumerate(book_mapping.items(), 1):
            book_id = int(book_id_str)
            book_name = book_info['name']
            
            print(f"📖 Book {i}/{self.stats['total_books']}: {book_name}")
            
            # Extract complete book
            verses = self.extract_book_with_chapters(book_id, book_name)
            
            if verses:
                # Save to database
                await self.save_book_to_database(verses, book_name)
                self.stats['books_processed'] += 1
            
            # Progress report every 5 books
            if i % 5 == 0 or i == self.stats['total_books']:
                await self._progress_report(i, start_time)
            
            # Respectful delay between books
            time.sleep(1.5)
        
        # Final comprehensive report
        await self._final_extraction_report(start_time)
    
    async def _progress_report(self, current_book: int, start_time: float):
        """Generate detailed progress report"""
        elapsed = time.time() - start_time
        progress_percent = (current_book / self.stats['total_books']) * 100
        
        print(f"\\n📊 Progress Report:")
        print(f"   📚 Books: {current_book}/{self.stats['total_books']} ({progress_percent:.1f}%)")
        print(f"   📖 Chapters: {self.stats['total_chapters']:,}")
        print(f"   📝 Verses: {self.stats['total_verses']:,}")
        print(f"   ✨ Divine replacements: {self.stats['divine_name_replacements']:,}")
        print(f"   ⏱️  Time elapsed: {elapsed/60:.1f} minutes")
        
        if current_book > 0:
            avg_time = elapsed / current_book
            eta = (self.stats['total_books'] - current_book) * avg_time
            print(f"   🎯 ETA: {eta/60:.1f} minutes")
        
        print()
    
    async def _final_extraction_report(self, start_time: float):
        """Generate comprehensive final report"""
        total_time = time.time() - start_time
        
        print("🎯 Phase 3B Complete - Final Extraction Report")
        print("=" * 60)
        print(f"📚 Books extracted: {self.stats['books_processed']}/{self.stats['total_books']}")
        print(f"📖 Total chapters: {self.stats['total_chapters']:,}")
        print(f"📝 Total verses: {self.stats['total_verses']:,}")
        print(f"✨ Divine name replacements: {self.stats['divine_name_replacements']:,}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"⏱️  Total time: {total_time/60:.1f} minutes")
        
        # Database verification
        db_count = await self.db.bible_verses.count_documents({})
        db_books = await self.db.bible_verses.distinct('book')
        
        print(f"\\n💾 Database Verification:")
        print(f"   📊 Verses in database: {db_count:,}")
        print(f"   📚 Books in database: {len(db_books)}")
        
        # Coverage analysis
        expected_bible_verses = 31000  # Approximate full Bible
        coverage = (self.stats['total_verses'] / expected_bible_verses) * 100
        
        print(f"\\n📈 Coverage Analysis:")
        print(f"   🎯 Bible completion: {coverage:.1f}%")
        
        if coverage > 90:
            print("   ✅ EXCELLENT: Near-complete Bible achieved!")
        elif coverage > 70:
            print("   ✅ VERY GOOD: Substantial Bible coverage")
        elif coverage > 50:
            print("   ✅ GOOD: Major Bible portions extracted")
        
        # Divine name analysis
        yhwh_verses = await self.db.bible_verses.count_documents({'text': {'$regex': 'YHWH'}})
        elohim_verses = await self.db.bible_verses.count_documents({'text': {'$regex': 'Elohim'}})
        
        print(f"\\n✨ Ancient Hebrew Divine Names:")
        print(f"   🔥 YHWH appears in: {yhwh_verses:,} verses")
        print(f"   ⭐ Elohim appears in: {elohim_verses:,} verses")
        print(f"   📜 Total divine replacements: {self.stats['divine_name_replacements']:,}")
        
        print(f"\\n🚀 Ready for Phase 3C: UI Integration & Testing")
        
        # Save extraction statistics
        extraction_stats = {
            'completion_time': total_time,
            'books_extracted': self.stats['books_processed'],
            'total_verses': self.stats['total_verses'],
            'total_chapters': self.stats['total_chapters'],
            'divine_replacements': self.stats['divine_name_replacements'],
            'coverage_percent': coverage
        }
        
        with open('/app/backend/phase3b_extraction_stats.json', 'w') as f:
            json.dump(extraction_stats, f, indent=2)
        
        print(f"📊 Extraction statistics saved to phase3b_extraction_stats.json")

if __name__ == "__main__":
    async def main():
        extractor = CompleteExtractionSystem()
        await extractor.extract_all_81_books()
    
    print("🚀 Starting Phase 3B: Complete 81-Book Bible Extraction")
    print("📖 This will extract ALL chapters and verses from every discovered book")
    print("✨ Ancient Hebrew divine name logic will be applied throughout")
    print("🎯 Target: Complete 1611 KJV Bible + Apocrypha integration")
    print()
    
    asyncio.run(main())