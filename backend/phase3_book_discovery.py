#!/usr/bin/env python3
"""
Phase 3A: Discover all 80 book IDs on thepreceptbible.com
Research and map the complete 1611 KJV Bible + Apocrypha structure
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from typing import Dict, List, Optional

class BibleBookDiscovery:
    """Discovers all available Bible books and their IDs on thepreceptbible.com"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Expected 80 books (66 canonical + 14 Apocrypha)
        self.canonical_books = [
            # Old Testament (39)
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings',
            '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job',
            'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah',
            'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
            'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah',
            'Haggai', 'Zechariah', 'Malachi',
            # New Testament (27)  
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians',
            '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
            '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
            'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John',
            '2 John', '3 John', 'Jude', 'Revelation'
        ]
        
        self.apocryphal_books = [
            # Apocrypha (14 typically in 1611 KJV)
            '1 Esdras', '2 Esdras', 'Tobit', 'Judith', 'Additions to Esther',
            'Wisdom of Solomon', 'Ecclesiasticus', 'Baruch', 'Letter of Jeremiah',
            'Prayer of Azariah', 'Susanna', 'Bel and the Dragon', '1 Maccabees', '2 Maccabees'
        ]
        
        self.discovered_books = {}
        self.base_url = 'https://thepreceptbible.com/bible'
    
    def test_book_id(self, book_id: int) -> Optional[Dict]:
        """Test a specific book ID to see if it exists and extract book info"""
        url = f"{self.base_url}?field_book_target_id={book_id}&page=0"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for verse content to confirm it's a real book
                verse_rows = soup.find_all('div', class_='views-row')
                if len(verse_rows) > 0:
                    # Try to extract book name from the content
                    first_verse = verse_rows[0]
                    verse_text = first_verse.get_text(strip=True)
                    
                    # Look for chapter/verse pattern to identify book
                    if len(verse_text) > 20:  # Substantial content
                        return {
                            'id': book_id,
                            'url': url,
                            'verse_count': len(verse_rows),
                            'sample_text': verse_text[:100],
                            'status': 'active'
                        }
            
            return None
            
        except Exception as e:
            print(f"Error testing book ID {book_id}: {e}")
            return None
    
    def discover_all_books(self, id_range_start: int = 50, id_range_end: int = 150):
        """Systematically discover all book IDs in the given range"""
        print(f"🔍 Phase 3A: Discovering Bible books (IDs {id_range_start}-{id_range_end})")
        print("=" * 60)
        
        discovered = {}
        
        for book_id in range(id_range_start, id_range_end + 1):
            print(f"Testing book ID {book_id}...", end=" ")
            
            book_info = self.test_book_id(book_id)
            if book_info:
                discovered[book_id] = book_info
                print(f"✅ FOUND! ({book_info['verse_count']} verses)")
                print(f"   Sample: {book_info['sample_text']}...")
            else:
                print("❌")
            
            # Be respectful with requests
            time.sleep(0.5)
            
            # Progress update every 10 IDs
            if book_id % 10 == 0:
                print(f"   Progress: {book_id - id_range_start + 1}/{id_range_end - id_range_start + 1} IDs tested")
                print(f"   Found so far: {len(discovered)} books")
                print()
        
        return discovered
    
    def analyze_discovered_books(self, discovered: Dict) -> Dict:
        """Analyze discovered books and try to identify them"""
        print(f"\n📊 Analysis of {len(discovered)} discovered books:")
        print("=" * 50)
        
        analysis = {
            'total_found': len(discovered),
            'books': {},
            'total_verses': 0,
            'id_mapping': {}
        }
        
        for book_id, info in discovered.items():
            analysis['total_verses'] += info['verse_count']
            analysis['books'][book_id] = info
            analysis['id_mapping'][book_id] = {
                'verses': info['verse_count'],
                'sample': info['sample_text']
            }
            
            print(f"Book ID {book_id}: {info['verse_count']} verses")
            print(f"   Sample: {info['sample_text']}...")
            print()
        
        print(f"📈 Total verses discovered: {analysis['total_verses']}")
        print(f"📚 Expected for complete Bible: ~31,000 verses")
        
        if analysis['total_verses'] > 25000:
            print("✅ Looks like we found most/all of the Bible!")
        elif analysis['total_verses'] > 15000:
            print("⚠️  Found substantial portion - may need to expand search range")
        else:
            print("❌ May need to search different ID ranges")
        
        return analysis
    
    def save_discovery_results(self, analysis: Dict, filename: str = 'phase3_book_discovery.json'):
        """Save discovery results for Phase 3B"""
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"💾 Discovery results saved to {filename}")

if __name__ == "__main__":
    print("🚀 Phase 3A: Bible Book Discovery")
    print("Mapping all 80 books of 1611 KJV Bible + Apocrypha")
    print()
    
    discoverer = BibleBookDiscovery()
    
    # Start with the range around Genesis (60) that we know works
    discovered_books = discoverer.discover_all_books(50, 120)
    
    # If we don't find enough, expand the search
    if len(discovered_books) < 40:
        print("\n🔄 Expanding search range to find more books...")
        additional_books = discoverer.discover_all_books(20, 49)
        discovered_books.update(additional_books)
        
        if len(discovered_books) < 60:
            print("\n🔄 Searching higher ID range...")
            higher_books = discoverer.discover_all_books(121, 180)
            discovered_books.update(higher_books)
    
    # Analyze results
    analysis = discoverer.analyze_discovered_books(discovered_books)
    
    # Save for next phase
    discoverer.save_discovery_results(analysis)
    
    print(f"\n🎯 Phase 3A Complete!")
    print(f"   Books discovered: {analysis['total_found']}")
    print(f"   Total verses: {analysis['total_verses']}")
    print(f"   Ready for Phase 3B: Bulk Extraction")