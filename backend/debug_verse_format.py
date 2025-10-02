#!/usr/bin/env python3
"""
Debug the exact verse format in the NT section
"""

import PyPDF2
import re

def debug_verse_format():
    """Debug verse format in pages around 2200-2210"""
    
    print("🔍 Debugging verse format in NT section...")
    
    try:
        with open('/app/yah_scriptures.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check pages around Matthew
            for page_num in [2200, 2201, 2202, 2203, 2204]:
                if page_num < len(pdf_reader.pages):
                    print(f"\n📄 PAGE {page_num + 1} DETAILED ANALYSIS:")
                    
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        lines = text.split('\n')
                        print(f"   Total lines: {len(lines)}")
                        
                        for i, line in enumerate(lines):
                            line = line.strip()
                            if line:
                                print(f"   Line {i+1:2d}: '{line}'")
                                
                                # Check different patterns
                                patterns = {
                                    'Just number': re.match(r'^\d+$', line),
                                    'Number + text': re.match(r'^(\d+)\s+(.+)', line),
                                    'Verse ref': re.match(r'^(\d+):(\d+)', line),
                                    'Chapter:verse text': re.match(r'^(\d+):(\d+)\s+(.+)', line)
                                }
                                
                                found_patterns = [name for name, match in patterns.items() if match]
                                if found_patterns:
                                    print(f"        → Patterns: {', '.join(found_patterns)}")
                                
                                # Stop after 25 lines to avoid too much output
                                if i >= 24:
                                    print(f"   ... (showing first 25 lines)")
                                    break
                    else:
                        print("   No extractable text")
    
    except Exception as e:
        print(f"❌ Error debugging: {e}")

if __name__ == "__main__":
    debug_verse_format()