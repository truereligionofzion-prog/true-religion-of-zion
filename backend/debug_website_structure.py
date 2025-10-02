#!/usr/bin/env python3
"""
Debug the thepreceptbible.com website structure to understand verse parsing
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_website_structure():
    """Check the actual HTML structure of thepreceptbible.com"""
    
    print("🔍 Debugging thepreceptbible.com HTML structure...")
    
    # Test with Genesis 1
    url = "https://thepreceptbible.com/genesis-1"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for verse-related divs
            verse_divs = soup.find_all('div', class_=re.compile(r'verse'))
            print(f"📊 Found {len(verse_divs)} verse-related divs")
            
            # Show first few verse structures
            for i, div in enumerate(verse_divs[:3]):
                print(f"\n📖 Verse {i+1} structure:")
                print(f"   Classes: {div.get('class', [])}")
                print(f"   Text (first 100 chars): {div.get_text()[:100]}...")
                
                # Check spans inside
                spans = div.find_all('span')
                print(f"   Contains {len(spans)} spans:")
                for j, span in enumerate(spans[:3]):
                    span_text = span.get_text(strip=True)
                    print(f"     Span {j+1}: '{span_text[:50]}...' (classes: {span.get('class', [])})")
            
            # Look for different patterns
            print(f"\n🔍 Looking for different verse patterns...")
            
            # Pattern 1: verse-number class
            verse_numbers = soup.find_all(class_=re.compile(r'verse-?number'))
            print(f"   Verse-number elements: {len(verse_numbers)}")
            
            # Pattern 2: verse-text class  
            verse_texts = soup.find_all(class_=re.compile(r'verse-?text'))
            print(f"   Verse-text elements: {len(verse_texts)}")
            
            # Pattern 3: Check raw structure
            print(f"\n📋 Sample HTML structure:")
            if verse_divs:
                print(verse_divs[0].prettify()[:500])
            
        else:
            print(f"❌ Failed to fetch page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error debugging website: {e}")

if __name__ == "__main__":
    debug_website_structure()