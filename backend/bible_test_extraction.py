#!/usr/bin/env python3
"""
Phase 1: Test Extraction Script for 80-Book Bible
Extract sample chapters from thepreceptbible.com to validate data structure
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from typing import Dict, List, Any

class BibleExtractor:
    def __init__(self):
        self.base_url = "https://thepreceptbible.com/bible"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Book mapping (from website analysis)
        self.book_mapping = {
            'Genesis': 60,
            'Tobit': 99,  # Apocrypha book for testing
        }
    
    def apply_divine_name_replacements(self, text: str) -> str:
        """Apply YHWH/YHUH divine name replacements like in precepts"""
        # Replace common divine name references
        replacements = {
            r'\bLORD\b': 'YHWH',  # All caps LORD -> YHWH
            r'\bGod\b': 'YHWH',   # Some God references -> YHWH
            r'\bLord\b': 'YHUH',  # Mixed case Lord -> YHUH
        }
        
        processed_text = text
        for pattern, replacement in replacements.items():
            processed_text = re.sub(pattern, replacement, processed_text)
        
        return processed_text
    
    def extract_chapter(self, book_name: str, chapter_num: int = 1) -> Dict[str, Any]:
        """Extract a specific chapter from a book"""
        if book_name not in self.book_mapping:
            raise ValueError(f"Book {book_name} not found in mapping")
        
        book_id = self.book_mapping[book_name]
        page_num = chapter_num - 1  # Page is 0-indexed
        
        url = f"{self.base_url}?field_book_target_id={book_id}&page={page_num}"
        
        print(f"Extracting {book_name} {chapter_num} from: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract chapter title
            chapter_title = self.extract_chapter_title(soup, book_name, chapter_num)
            
            # Extract verses
            verses = self.extract_verses(soup)
            
            # Apply divine name replacements
            processed_verses = []
            for verse in verses:
                processed_verse = verse.copy()
                processed_verse['text'] = self.apply_divine_name_replacements(verse['text'])
                processed_verses.append(processed_verse)
            
            chapter_data = {
                'book': book_name,
                'chapter': chapter_num,
                'title': chapter_title,
                'verses': processed_verses,
                'verse_count': len(processed_verses),
                'source_url': url
            }
            
            return chapter_data
            
        except requests.RequestException as e:
            print(f"Error fetching {book_name} {chapter_num}: {e}")
            return None
    
    def extract_chapter_title(self, soup: BeautifulSoup, book_name: str, chapter_num: int) -> str:
        """Extract chapter title from the page"""
        # Look for chapter heading
        headings = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(f'{book_name}.*{chapter_num}'))
        if headings:
            return headings[0].get_text().strip()
        
        return f"{book_name} {chapter_num}"
    
    def extract_verses(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all verses from the chapter page"""
        verses = []
        
        # Look for the actual chapter heading (e.g., "## Genesis 1")
        chapter_heading = soup.find(['h1', 'h2', 'h3'], string=re.compile(r'^\w+\s+\d+$'))
        
        if not chapter_heading:
            print("Warning: Could not find chapter heading")
            return verses
        
        # Get text content starting from after the chapter heading
        content_start = chapter_heading.parent
        
        # Extract all text after the chapter heading
        full_text = ""
        for element in content_start.find_all_next(text=True):
            parent = element.parent
            # Stop at contact info or navigation elements
            if parent.name in ['a'] and 'mailto:' in str(element):
                break
            if 'contact' in str(element).lower() or 'support' in str(element).lower():
                break
            full_text += str(element) + " "
        
        # Parse verses using regex - looking for number followed by verse text
        verse_pattern = r'(\d+)([A-Z][^0-9]+?)(?=\d+[A-Z]|\Z)'
        matches = re.findall(verse_pattern, full_text, re.DOTALL)
        
        for match in matches:
            verse_num_str, verse_text = match
            verse_num = int(verse_num_str)
            
            # Clean up the text
            verse_text = re.sub(r'\s+', ' ', verse_text.strip())
            
            # Skip if it's too short or contains navigation words
            nav_words = ['VERSES', 'CHAPTERS', 'Book', 'Contact', 'Support', 'mailto']
            if any(word in verse_text for word in nav_words):
                continue
            
            if len(verse_text) > 10:  # Minimum meaningful verse length
                verses.append({
                    'verse': verse_num,
                    'text': verse_text
                })
        
        return verses
    
    def test_extraction(self) -> Dict[str, Any]:
        """Run test extraction on Genesis 1 and Tobit 1"""
        results = {
            'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'chapters': {},
            'summary': {},
            'validation': {}
        }
        
        # Extract test chapters
        test_books = [
            ('Genesis', 1),
            ('Tobit', 1)
        ]
        
        for book_name, chapter_num in test_books:
            print(f"\n--- Extracting {book_name} {chapter_num} ---")
            
            chapter_data = self.extract_chapter(book_name, chapter_num)
            
            if chapter_data:
                results['chapters'][f"{book_name}_{chapter_num}"] = chapter_data
                print(f"✅ Extracted {len(chapter_data['verses'])} verses")
                
                # Show first few verses as sample
                for i, verse in enumerate(chapter_data['verses'][:3]):
                    print(f"   {verse['verse']}: {verse['text'][:100]}...")
            else:
                print(f"❌ Failed to extract {book_name} {chapter_num}")
        
        # Generate summary
        results['summary'] = self.generate_summary(results['chapters'])
        
        # Validate data quality
        results['validation'] = self.validate_extraction(results['chapters'])
        
        return results
    
    def generate_summary(self, chapters: Dict) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_verses = sum(chapter['verse_count'] for chapter in chapters.values())
        
        return {
            'total_chapters_extracted': len(chapters),
            'total_verses_extracted': total_verses,
            'books_tested': list(set(chapter['book'] for chapter in chapters.values())),
            'average_verses_per_chapter': round(total_verses / len(chapters), 1) if chapters else 0
        }
    
    def validate_extraction(self, chapters: Dict) -> Dict[str, Any]:
        """Validate extraction quality"""
        validation = {
            'issues': [],
            'divine_name_replacements': 0,
            'data_quality_score': 0
        }
        
        for chapter_key, chapter in chapters.items():
            # Check for divine name replacements
            for verse in chapter['verses']:
                if 'YHWH' in verse['text'] or 'YHUH' in verse['text']:
                    validation['divine_name_replacements'] += 1
            
            # Validate verse numbering
            verse_numbers = [verse['verse'] for verse in chapter['verses']]
            expected_numbers = list(range(1, len(verse_numbers) + 1))
            
            if verse_numbers != expected_numbers:
                validation['issues'].append(f"{chapter_key}: Verse numbering gaps detected")
            
            # Check for very short verses (potential extraction errors)
            short_verses = [v for v in chapter['verses'] if len(v['text']) < 20]
            if len(short_verses) > len(chapter['verses']) * 0.2:  # More than 20% short
                validation['issues'].append(f"{chapter_key}: High number of short verses detected")
        
        # Calculate quality score
        issues_penalty = len(validation['issues']) * 10
        validation['data_quality_score'] = max(0, 100 - issues_penalty)
        
        return validation
    
    def save_results(self, results: Dict[str, Any], filename: str = "/app/backend/bible_test_results.json"):
        """Save extraction results to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Results saved to {filename}")

def main():
    """Run the test extraction"""
    print("🔍 Starting Phase 1: Bible Test Extraction")
    print("=" * 50)
    
    extractor = BibleExtractor()
    
    try:
        results = extractor.test_extraction()
        extractor.save_results(results)
        
        # Print summary
        print(f"\n📊 EXTRACTION SUMMARY")
        print("=" * 30)
        for key, value in results['summary'].items():
            print(f"{key}: {value}")
        
        print(f"\n🔍 VALIDATION RESULTS")
        print("=" * 30)
        validation = results['validation']
        print(f"Data Quality Score: {validation['data_quality_score']}/100")
        print(f"Divine Name Replacements: {validation['divine_name_replacements']}")
        
        if validation['issues']:
            print("Issues found:")
            for issue in validation['issues']:
                print(f"  ⚠️  {issue}")
        else:
            print("✅ No validation issues found")
        
        print(f"\n🎉 Phase 1 extraction completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()