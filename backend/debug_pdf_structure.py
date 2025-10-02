#!/usr/bin/env python3
"""
Debug PDF structure to understand verse formatting
"""

import pdfplumber
import re

def sample_pdf_pages(pdf_path: str, start_page: int, num_pages: int = 5):
    """Sample pages from PDF to understand structure"""
    
    print(f"🔍 Sampling {num_pages} pages starting from page {start_page}...")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_offset in range(num_pages):
                page_num = start_page - 1 + page_offset  # Convert to 0-based index
                
                if page_num >= len(pdf.pages):
                    print(f"   ⚠️ Page {start_page + page_offset} exceeds PDF length")
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                print(f"\n📄 PAGE {start_page + page_offset} CONTENT:")
                print("=" * 60)
                
                if text:
                    lines = text.split('\n')
                    for i, line in enumerate(lines[:30]):  # Show first 30 lines
                        line_clean = line.strip()
                        if line_clean:
                            print(f"{i+1:2d}: {line_clean}")
                else:
                    print("   ❌ No text content found")
                    
                print("\n" + "=" * 60)
    
    except Exception as e:
        print(f"❌ Error sampling PDF: {e}")

def find_nt_start(pdf_path: str):
    """Find where New Testament actually starts"""
    
    print("🔍 Searching for New Testament start...")
    
    # Common NT book names to search for
    nt_markers = [
        'MATTHEW', 'MATTITHYAHU', 'MARK', 'MARQOS', 
        'LUKE', 'LUQAS', 'JOHN', 'YOḤANAN'
    ]
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            # Search in second half where NT likely starts
            search_start = total_pages // 2
            search_end = min(search_start + 1000, total_pages)
            
            print(f"   📖 Searching pages {search_start} to {search_end} of {total_pages}")
            
            for page_num in range(search_start, search_end):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if text:
                    text_upper = text.upper()
                    
                    for marker in nt_markers:
                        if marker in text_upper:
                            # Check if this looks like a book header (not just a mention)
                            lines = text.split('\n')
                            for line in lines:
                                line_clean = line.strip().upper()
                                if line_clean == marker or line_clean.endswith(marker):
                                    print(f"   📖 Found '{marker}' at page {page_num + 1}")
                                    
                                    # Show context
                                    print(f"   📝 Context around '{marker}':")
                                    for j, context_line in enumerate(lines):
                                        context_clean = context_line.strip()
                                        if context_clean:
                                            if marker.lower() in context_line.lower():
                                                print(f"      >>> {context_clean}")
                                            elif j < len(lines) - 1:  # Show a few lines after
                                                next_few = lines[j+1:j+6]
                                                for next_line in next_few:
                                                    next_clean = next_line.strip()
                                                    if next_clean:
                                                        print(f"          {next_clean}")
                                                break
                                    
                                    return page_num + 1
                
                # Progress indicator
                if (page_num - search_start) % 100 == 0:
                    progress = page_num - search_start
                    total_search = search_end - search_start
                    print(f"   🔍 Searched {progress}/{total_search} pages...")
    
    except Exception as e:
        print(f"❌ Error finding NT start: {e}")
    
    return None

def analyze_verse_patterns(pdf_path: str, start_page: int, num_pages: int = 10):
    """Analyze verse number patterns in the PDF"""
    
    print(f"📊 Analyzing verse patterns from page {start_page} for {num_pages} pages...")
    
    verse_patterns = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_offset in range(num_pages):
                page_num = start_page - 1 + page_offset
                
                if page_num >= len(pdf.pages):
                    break
                    
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if text:
                    lines = text.split('\n')
                    
                    for line in lines:
                        line_clean = line.strip()
                        if not line_clean:
                            continue
                            
                        # Look for patterns that might be verse numbers + text
                        patterns = [
                            r'^(\d+)\s+(.+)',          # "1 In the beginning..."
                            r'^(\d+)\.\s*(.+)',        # "1. In the beginning..."
                            r'^(\d+):\s*(.+)',         # "1: In the beginning..."
                            r'^(\d+)\)\s*(.+)',        # "1) In the beginning..."
                            r'^(\d+)\s*-\s*(.+)',      # "1 - In the beginning..."
                        ]
                        
                        for pattern in patterns:
                            match = re.match(pattern, line_clean)
                            if match:
                                verse_num = match.group(1)
                                verse_text = match.group(2).strip()
                                
                                if (len(verse_text) > 10 and  # Reasonable text length
                                    int(verse_num) <= 200 and  # Reasonable verse number
                                    len(verse_text.split()) > 2):  # More than 2 words
                                    
                                    verse_patterns.append({
                                        'page': start_page + page_offset,
                                        'pattern': pattern,
                                        'verse_num': verse_num,
                                        'text_sample': verse_text[:80] + "..." if len(verse_text) > 80 else verse_text,
                                        'full_line': line_clean
                                    })
    
    except Exception as e:
        print(f"❌ Error analyzing patterns: {e}")
    
    # Show results
    print(f"\n📊 Found {len(verse_patterns)} potential verse patterns:")
    
    for i, pattern in enumerate(verse_patterns[:20]):  # Show first 20
        print(f"{i+1:2d}. Page {pattern['page']}, Verse {pattern['verse_num']}: {pattern['text_sample']}")
    
    # Show pattern frequency
    pattern_counts = {}
    for p in verse_patterns:
        pattern_counts[p['pattern']] = pattern_counts.get(p['pattern'], 0) + 1
    
    print(f"\n📈 Pattern frequency:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {pattern}: {count} matches")
    
    return verse_patterns

def main():
    pdf_path = '/app/yah_scriptures.pdf'
    
    print("🚀 Starting PDF Structure Analysis")
    print("=" * 60)
    
    # First, find where NT actually starts
    nt_start_page = find_nt_start(pdf_path)
    
    if nt_start_page:
        print(f"\n✅ Found NT starting at page {nt_start_page}")
        
        # Sample pages around NT start
        sample_pdf_pages(pdf_path, nt_start_page, 3)
        
        # Analyze verse patterns
        verse_patterns = analyze_verse_patterns(pdf_path, nt_start_page, 5)
        
        print(f"\n📋 ANALYSIS SUMMARY:")
        print(f"   📖 NT starts at page: {nt_start_page}")
        print(f"   📊 Found {len(verse_patterns)} potential verses")
        
    else:
        print("\n❌ Could not find NT start")
        # Sample some pages around expected location (2200)
        print("\n🔍 Sampling pages around expected NT location (page 2200)...")
        sample_pdf_pages(pdf_path, 2200, 3)

if __name__ == "__main__":
    main()