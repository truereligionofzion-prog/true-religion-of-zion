#!/usr/bin/env python3
"""
Test script to check for divine names in scraped content
"""

import requests
from bs4 import BeautifulSoup
import re

def test_book_extraction(book_id):
    """Test extracting content from a specific book ID to check for divine names"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    url = f"https://thepreceptbible.com/bible?field_book_target_id={book_id}&page=0"
    print(f"Testing book ID {book_id}: {url}")
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all text content
        page_text = soup.get_text()
        
        # Count divine names
        lord_count = len(re.findall(r'\bLORD\b', page_text))
        god_count = len(re.findall(r'\bGod\b', page_text))
        
        print(f"  LORD count: {lord_count}")
        print(f"  God count: {god_count}")
        
        if lord_count > 0:
            # Find first few instances of LORD
            lord_matches = re.finditer(r'.{0,50}\bLORD\b.{0,50}', page_text)
            print("  Sample LORD contexts:")
            for i, match in enumerate(lord_matches):
                if i >= 3:  # Limit to 3 examples
                    break
                print(f"    {match.group().strip()}")
        
        return lord_count > 0
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

if __name__ == "__main__":
    # Test several book IDs to find ones with LORD
    test_ids = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 75, 78, 80]
    
    found_lord = False
    for book_id in test_ids:
        has_lord = test_book_extraction(book_id)
        if has_lord:
            found_lord = True
            print(f"*** Book ID {book_id} contains LORD! ***\n")
        else:
            print()
    
    if not found_lord:
        print("No books with LORD found in tested IDs.")