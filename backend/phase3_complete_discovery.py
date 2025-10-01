#!/usr/bin/env python3
"""
Phase 3A Complete: Find ALL 80 books on thepreceptbible.com
Comprehensive discovery to locate every book of 1611 KJV + Apocrypha
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import Dict, List, Set
import re

class CompleteBibleDiscovery:
    """Comprehensive discovery to find all 80 Bible books"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = 'https://thepreceptbible.com/bible'
        
        # Complete list of 80 books (66 canonical + 14 Apocrypha)
        self.expected_books = {
            # Old Testament (39 books)
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', 
            '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
            'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
            'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah',
            'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
            'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk',
            'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
            
            # New Testament (27 books)
            'Matthew', 'Mark', 'Luke', 'John', 'Acts',
            'Romans', '1 Corinthians', '2 Corinthians', 'Galatians',
            'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians',
            '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
            'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter',
            '1 John', '2 John', '3 John', 'Jude', 'Revelation',
            
            # Apocrypha (14 books in 1611 KJV)
            '1 Esdras', '2 Esdras', 'Tobit', 'Judith',
            'Additions to Esther', 'Wisdom of Solomon', 'Ecclesiasticus',
            'Baruch', 'Letter of Jeremiah', 'Prayer of Azariah',
            'Susanna', 'Bel and the Dragon', '1 Maccabees', '2 Maccabees'
        }
        
        # Alternative names the website might use
        self.book_name_variants = {
            'Song of Solomon': ['Songs of Solomon', 'Song of Songs'],
            'Ecclesiasticus': ['Ecclesiasticus (Sirach)', 'Sirach'],
            'Revelation': ['Revelations'],
            '1 Corinthians': ['1Corinthians'],
            '2 Corinthians': ['2Corinthians'],
            '1 Thessalonians': ['1Thessalonians'],
            '2 Thessalonians': ['2Thessalonians'],
            '1 Timothy': ['1Timothy'],
            '2 Timothy': ['2Timothy'],
            'Letter of Jeremiah': ['Epistle of Jeremiah'],
            'Prayer of Azariah': ['Prayer of Azariah'],
            'Bel and the Dragon': ['Bel and Dragon']
        }
        
        self.discovered_books = {}
        self.found_book_names = set()
    
    def test_expanded_id_range(self, start_id: int, end_id: int) -> Dict:
        """Test much wider ID range systematically"""
        print(f"🔍 Testing ID range {start_id}-{end_id}")
        discovered = {}
        
        for book_id in range(start_id, end_id + 1):
            book_info = self._test_single_id(book_id)
            if book_info:
                discovered[book_id] = book_info
                print(f"✅ ID {book_id}: {book_info['name']} ({book_info['verse_count']} verses)")
            
            # Progress indicator
            if book_id % 25 == 0:
                print(f"   📊 {book_id - start_id + 1}/{end_id - start_id + 1} tested, {len(discovered)} found")
            
            time.sleep(0.2)  # Faster but still respectful
        
        return discovered
    
    def _test_single_id(self, book_id: int) -> Dict:
        """Test a single book ID with improved name detection"""
        url = f"{self.base_url}?field_book_target_id={book_id}&page=0"
        
        try:
            response = self.session.get(url, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                verses = soup.select('div.verse')
                
                if len(verses) > 0:
                    # Enhanced book name detection
                    book_name = self._detect_book_name(soup, verses[0])
                    
                    if book_name and book_name != 'Unknown':
                        self.found_book_names.add(book_name)
                        
                        return {
                            'id': book_id,
                            'name': book_name,
                            'verse_count': len(verses),
                            'first_verse': verses[0].get_text(strip=True)[:100],
                            'url': url
                        }
            
            return None
            
        except Exception:
            return None
    
    def _detect_book_name(self, soup, first_verse) -> str:
        """Enhanced book name detection"""
        verse_text = first_verse.get_text(strip=True)
        
        # Method 1: Look for book selector or dropdown
        selectors = soup.select('select option[selected]')
        for selector in selectors:
            text = selector.get_text(strip=True)
            if text and len(text) < 50:  # Reasonable book name length
                return text
        
        # Method 2: Look in page title or headers
        title = soup.title.string if soup.title else ""
        if " | " in title:
            potential_book = title.split(" | ")[0].strip()
            if potential_book and len(potential_book) < 50:
                return potential_book
        
        # Method 3: Content-based detection using first verse
        return self._guess_book_from_content(verse_text)
    
    def _guess_book_from_content(self, verse_text: str) -> str:
        """Guess book name from verse content"""
        verse_lower = verse_text.lower()
        
        # Known first verse patterns
        if 'beginning' in verse_lower and 'created' in verse_lower:
            return 'Genesis'
        elif 'egypt' in verse_lower and ('israelites' in verse_lower or 'children' in verse_lower):
            return 'Exodus'
        elif 'beginning was the word' in verse_lower:
            return 'John'
        elif 'book of the generation' in verse_lower:
            return 'Matthew'
        elif 'former treatise' in verse_lower or 'theophilus' in verse_lower:
            return 'Acts'
        elif 'paul' in verse_lower and ('apostle' in verse_lower or 'servant' in verse_lower):
            if 'romans' in verse_lower:
                return 'Romans'
            elif 'corinth' in verse_lower:
                return '1 Corinthians'
        
        # Extract book name from verse number pattern (e.g., "1In the beginning...")
        verse_match = re.match(r'^(\d+)(.+)', verse_text)
        if verse_match and verse_match.group(1) == '1':
            # This is verse 1, might give us clues
            content = verse_match.group(2).strip()
            
            # Check against expected book patterns
            if len(content) > 20:  # Substantial first verse
                return f"Book_ID_Unknown"  # Placeholder for unknown books
        
        return "Unknown"
    
    def comprehensive_discovery(self) -> Dict:
        """Comprehensive discovery across multiple strategies"""
        print("🚀 Phase 3A Complete: Finding ALL 80 Bible Books")
        print("=" * 60)
        print(f"🎯 Target: {len(self.expected_books)} books (66 canonical + 14 Apocrypha)")
        print()
        
        all_discovered = {}
        
        # Strategy 1: Extended range search
        print("📋 Strategy 1: Extended ID Range Search")
        ranges = [
            (1, 50),     # Lower IDs
            (50, 150),   # Known good range  
            (150, 250),  # Higher IDs
            (250, 350),  # Even higher
            (350, 500),  # Extended search
        ]
        
        for start, end in ranges:
            range_results = self.test_expanded_id_range(start, end)
            all_discovered.update(range_results)
            
            print(f"   Range {start}-{end}: Found {len(range_results)} books")
            print(f"   Running total: {len(all_discovered)} books")
            
            # If we found a lot, we might be in the right range
            if len(range_results) > 20:
                print("   🎯 Rich range found - expanding nearby...")
                # Test nearby ranges more thoroughly
                if start > 50:
                    extra_range = self.test_expanded_id_range(start - 50, start - 1)
                    all_discovered.update(extra_range)
                if end < 450:
                    extra_range = self.test_expanded_id_range(end + 1, end + 50)
                    all_discovered.update(extra_range)
            
            print()
        
        return all_discovered
    
    def analyze_completeness(self, discovered: Dict) -> Dict:
        """Analyze how complete our discovery is"""
        print("📊 Completeness Analysis")
        print("=" * 40)
        
        found_names = {book['name'] for book in discovered.values()}
        
        # Check against expected books
        missing_books = []
        found_expected = []
        
        for expected in self.expected_books:
            found = False
            
            # Check direct match
            if expected in found_names:
                found_expected.append(expected)
                found = True
            else:
                # Check variants
                variants = self.book_name_variants.get(expected, [])
                for variant in variants:
                    if variant in found_names:
                        found_expected.append(f"{expected} (as {variant})")
                        found = True
                        break
            
            if not found:
                missing_books.append(expected)
        
        print(f"✅ Found: {len(found_expected)}/80 expected books ({len(found_expected)/80*100:.1f}%)")
        print(f"❌ Missing: {len(missing_books)} books")
        
        if missing_books:
            print(f"\\nMissing books:")
            for book in sorted(missing_books):
                print(f"   - {book}")
        
        # Calculate total verses
        total_verses = sum(book['verse_count'] for book in discovered.values())
        
        analysis = {
            'discovered_count': len(discovered),
            'expected_count': 80,
            'found_expected': len(found_expected),
            'missing_books': missing_books,
            'total_verses': total_verses,
            'completeness_percent': len(found_expected) / 80 * 100,
            'book_mapping': {str(k): v for k, v in discovered.items()},
            'ready_for_full_extraction': len(missing_books) <= 5  # Allow for minor discrepancies
        }
        
        return analysis
    
    def save_complete_mapping(self, analysis: Dict):
        """Save complete book mapping for full extraction"""
        with open('/app/backend/phase3_complete_mapping.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\\n💾 Complete mapping saved to phase3_complete_mapping.json")
        print(f"🎯 Ready for Phase 3B: Complete 80-Book Extraction")

if __name__ == "__main__":
    discoverer = CompleteBibleDiscovery()
    
    # Run comprehensive discovery
    all_books = discoverer.comprehensive_discovery()
    
    # Analyze results
    analysis = discoverer.analyze_completeness(all_books)
    
    # Save results
    discoverer.save_complete_mapping(analysis)
    
    print(f"\\n🏁 Complete Discovery Finished!")
    print(f"   📚 Found: {analysis['discovered_count']} books")
    print(f"   📊 Expected coverage: {analysis['completeness_percent']:.1f}%")
    print(f"   📝 Total verses (first pages): {analysis['total_verses']:,}")
    
    if analysis['ready_for_full_extraction']:
        print(f"   ✅ READY for complete 80-book extraction!")
    else:
        print(f"   ⚠️  Need to find {len(analysis['missing_books'])} more books")