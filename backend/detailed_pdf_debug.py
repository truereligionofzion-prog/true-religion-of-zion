#!/usr/bin/env python3
"""
Detailed PDF debugging to understand verse structure
"""

import pdfplumber
import re

def analyze_matthew_structure():
    """Analyze the structure of Matthew specifically"""
    
    pdf_path = '/app/yah_scriptures.pdf'
    
    print("🔍 Analyzing Matthew structure in detail...")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Start from page 2169 where Matthew begins
            for page_num in range(2168, 2173):  # Check 5 pages
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                print(f"\n📄 PAGE {page_num + 1} DETAILED ANALYSIS:")
                print("=" * 80)
                
                if text:
                    lines = text.split('\n')
                    
                    for i, line in enumerate(lines):
                        line_clean = line.strip()
                        if line_clean:
                            # Categorize each line
                            category = "TEXT"
                            
                            # Check if it's a book header
                            if line_clean.upper() in ['MATTHEW', 'MATTITHYAHU']:
                                category = "BOOK_HEADER"
                            # Check if it's just a number (could be chapter or verse)
                            elif re.match(r'^\d+$', line_clean):
                                num = int(line_clean)
                                if num <= 28:  # Matthew has 28 chapters
                                    category = f"NUMBER(ch?/v?) = {num}"
                                else:
                                    category = f"NUMBER(v?) = {num}"
                            # Check if it starts with a number (verse pattern)
                            elif re.match(r'^(\d+)\s+', line_clean):
                                category = "VERSE_PATTERN"
                            # Check for other patterns
                            elif re.match(r'^[A-Z\s]+$', line_clean) and len(line_clean) > 1:
                                category = "ALL_CAPS"
                            elif len(line_clean.split()) == 1 and len(line_clean) < 10:
                                category = "SINGLE_WORD"
                            
                            print(f"{i+1:2d}: [{category:15}] {line_clean}")
                    
                print("\n" + "=" * 80)
    
    except Exception as e:
        print(f"❌ Error analyzing: {e}")

def trace_verse_collection():
    """Trace how verses should be collected based on the pattern"""
    
    pdf_path = '/app/yah_scriptures.pdf'
    
    print("\n🔬 TRACING VERSE COLLECTION LOGIC:")
    print("=" * 60)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[2168]  # Page 2169 (0-indexed)
            text = page.extract_text()
            
            if text:
                lines = text.split('\n')
                
                # Simulate the parsing logic step by step
                current_book = None
                current_chapter = None
                current_verse = None
                verse_lines = []
                
                print("📝 STEP-BY-STEP PARSING:")
                
                for i, line in enumerate(lines[:40]):  # First 40 lines
                    line_clean = line.strip()
                    if not line_clean:
                        continue
                    
                    print(f"\nLine {i+1}: '{line_clean}'")
                    
                    # Book detection
                    if line_clean.upper() == 'MATTHEW':
                        current_book = 'Matthew'
                        print(f"   → 📖 BOOK: {current_book}")
                        continue
                    
                    # Chapter detection
                    if re.match(r'^\d+$', line_clean) and len(line_clean) <= 2:
                        num = int(line_clean)
                        if current_book and 1 <= num <= 28:
                            if current_verse and verse_lines:
                                verse_text = ' '.join(verse_lines)
                                print(f"   → ✅ COLLECTED VERSE: {current_chapter}:{current_verse} = {verse_text[:50]}...")
                            
                            current_chapter = num
                            current_verse = None
                            verse_lines = []
                            print(f"   → 📄 CHAPTER: {current_chapter}")
                            continue
                    
                    # Verse number detection  
                    if (current_book and current_chapter and 
                        re.match(r'^\d+$', line_clean) and len(line_clean) <= 3):
                        num = int(line_clean)
                        if 1 <= num <= 200:
                            if current_verse and verse_lines:
                                verse_text = ' '.join(verse_lines)
                                print(f"   → ✅ COLLECTED VERSE: {current_chapter}:{current_verse} = {verse_text[:50]}...")
                            
                            current_verse = num
                            verse_lines = []
                            print(f"   → 🔢 VERSE: {current_verse}")
                            continue
                    
                    # Text collection
                    if current_verse and current_chapter and current_book:
                        if (not re.match(r'^[A-Z\s]+$', line_clean) and
                            not line_clean.isdigit() and
                            len(line_clean) > 1):
                            verse_lines.append(line_clean)
                            print(f"   → ➕ TEXT: {line_clean}")
                        else:
                            print(f"   → ⏭️ SKIP: {line_clean}")
                    else:
                        print(f"   → ⏭️ WAITING (book:{current_book}, ch:{current_chapter}, v:{current_verse})")
                
                # Final verse if any
                if current_verse and verse_lines:
                    verse_text = ' '.join(verse_lines)
                    print(f"\n   → ✅ FINAL VERSE: {current_chapter}:{current_verse} = {verse_text[:50]}...")
    
    except Exception as e:
        print(f"❌ Error tracing: {e}")

def main():
    print("🚀 DETAILED PDF STRUCTURE DEBUGGING")
    print("=" * 80)
    
    # First analyze the structure
    analyze_matthew_structure()
    
    # Then trace the collection logic  
    trace_verse_collection()

if __name__ == "__main__":
    main()