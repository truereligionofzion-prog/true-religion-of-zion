#!/usr/bin/env python3
"""
Phase 3A Optimized: Quick discovery of all Bible books using correct HTML structure
"""

import requests
from bs4 import BeautifulSoup
import time
import json

class OptimizedBibleDiscovery:
    """Optimized Bible book discovery using correct HTML structure"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = 'https://thepreceptbible.com/bible'
        
    def test_book_id_optimized(self, book_id: int) -> dict:
        """Test book ID using correct HTML structure"""
        url = f"{self.base_url}?field_book_target_id={book_id}&page=0"
        
        try:
            response = self.session.get(url, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for verses using correct selector
                verses = soup.select('div.verse')
                
                if len(verses) > 0:
                    # Get first verse to identify book
                    first_verse = verses[0]
                    verse_text = first_verse.get_text(strip=True)
                    
                    # Extract chapter info if available  
                    chapter_container = soup.select_one('div.chapter-verses')
                    
                    # Try to identify book name from page content
                    book_name = self._extract_book_name(soup, verse_text)
                    
                    return {
                        'id': book_id,
                        'name': book_name,
                        'verse_count': len(verses),
                        'first_verse': verse_text[:100],
                        'url': url,
                        'has_chapters': chapter_container is not None
                    }
            
            return None
            
        except Exception as e:
            print(f"Error with ID {book_id}: {e}")
            return None
    
    def _extract_book_name(self, soup, verse_text: str) -> str:
        """Try to extract book name from page content"""
        # Look for book selection dropdown or similar
        book_selectors = soup.select('select option[selected]')
        if book_selectors:
            return book_selectors[0].get_text(strip=True)
        
        # Fallback: guess from verse content
        if 'beginning' in verse_text.lower() and 'created' in verse_text.lower():
            return 'Genesis'
        elif 'Egypt' in verse_text or 'Pharaoh' in verse_text:
            return 'Exodus'
        elif 'beginning was the Word' in verse_text:
            return 'John'
        
        return f'Book_{id}'  # Fallback
    
    def quick_discovery(self) -> dict:
        """Quick discovery focusing on known ranges"""
        print("🔍 Phase 3A Optimized: Quick Bible Discovery")
        print("=" * 50)
        
        discovered = {}
        
        # Test strategic ranges based on patterns
        test_ranges = [
            (50, 70),   # Around Genesis (60)
            (70, 100),  # Likely OT books  
            (100, 130), # More OT + NT
            (130, 160), # NT + Apocrypha
            (160, 190), # Extended search
        ]
        
        total_tested = 0
        for start, end in test_ranges:
            print(f"\n🎯 Testing range {start}-{end}...")
            
            for book_id in range(start, end + 1):
                total_tested += 1
                book_info = self.test_book_id_optimized(book_id)
                
                if book_info:
                    discovered[book_id] = book_info
                    print(f"✅ ID {book_id}: {book_info['name']} ({book_info['verse_count']} verses)")
                else:
                    print(f"❌ ID {book_id}", end=" ")
                
                # Progress update
                if total_tested % 10 == 0:
                    print(f"\\n   📊 Progress: {total_tested} tested, {len(discovered)} books found")
                
                time.sleep(0.3)  # Be respectful
            
            print(f"\\n   Range {start}-{end}: Found {len([d for d in discovered.values() if start <= d['id'] <= end])} books")
            
            # If we found a good number, we can optimize further
            if len(discovered) > 50:
                print("   🎯 Found substantial books - continuing...")
            
        return discovered
    
    def analyze_results(self, discovered: dict) -> dict:
        """Analyze discovery results"""
        total_verses = sum(book['verse_count'] for book in discovered.values())
        
        print(f"\n📊 Phase 3A Results:")
        print(f"   📚 Books found: {len(discovered)}")
        print(f"   📝 Total verses: {total_verses:,}")
        print(f"   🎯 Coverage: {total_verses/31000*100:.1f}% of expected Bible")
        
        # Sort by ID for analysis
        sorted_books = sorted(discovered.items())
        
        analysis = {
            'total_books': len(discovered),
            'total_verses': total_verses,
            'book_mapping': {},
            'id_ranges': [],
            'ready_for_extraction': total_verses > 20000
        }
        
        print(f"\\n📋 Book List (ID: Name - Verses):")
        for book_id, info in sorted_books:
            analysis['book_mapping'][book_id] = {
                'name': info['name'],
                'verses': info['verse_count'],
                'url': info['url']
            }
            print(f"   {book_id:3d}: {info['name']:20s} - {info['verse_count']:4d} verses")
        
        return analysis
    
    def save_results(self, analysis: dict):
        """Save results for Phase 3B"""
        with open('/app/backend/phase3_book_mapping.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\\n💾 Results saved to phase3_book_mapping.json")
        return analysis

if __name__ == "__main__":
    discoverer = OptimizedBibleDiscovery()
    
    # Quick discovery
    discovered_books = discoverer.quick_discovery()
    
    # Analyze
    analysis = discoverer.analyze_results(discovered_books)
    
    # Save for next phase
    discoverer.save_results(analysis)
    
    print(f"\\n🚀 Phase 3A Complete!")
    if analysis['ready_for_extraction']:
        print(f"   ✅ Ready for Phase 3B: Bulk Extraction")
    else:
        print(f"   ⚠️  May need expanded search for complete coverage")
    
    print(f"   📊 {analysis['total_books']} books, {analysis['total_verses']:,} verses mapped")