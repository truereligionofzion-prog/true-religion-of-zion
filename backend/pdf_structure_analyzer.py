#!/usr/bin/env python3
"""
Analyze PDF structure by sampling pages throughout the document
"""

import PyPDF2
import re

def sample_pdf_structure():
    """Sample pages throughout the PDF to understand structure"""
    
    print("📖 Sampling PDF structure...")
    
    try:
        with open('/app/yah_scriptures.pdf', 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            print(f"   Total pages: {total_pages}")
            
            # Sample key pages throughout the document
            sample_pages = [
                10,    # Early pages (likely table of contents)
                50,    # Early content
                100,   # 
                200,   # 
                500,   # 
                1000,  # Middle
                1500,  # 
                2000,  # Later content (likely NT)
                2200,  #
                2400,  #
                2600,  # Near end
                2800   # Very end
            ]
            
            for page_num in sample_pages:
                if page_num < total_pages:
                    print(f"\n📄 SAMPLING PAGE {page_num + 1}:")
                    
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            # Show first 10 lines
                            lines = text.split('\n')
                            for i, line in enumerate(lines[:10]):
                                line = line.strip()
                                if line:
                                    print(f"   Line {i+1}: {line[:80]}...")
                            
                            # Look for specific patterns
                            patterns_found = []
                            
                            # Check for book names
                            if re.search(r'Matthew|Mark|Luke|John|Acts|Romans', text, re.IGNORECASE):
                                patterns_found.append("NT book names (English)")
                            
                            if re.search(r'MATTITHYAHU|MARQOS|LUQAS|YOḤANAN', text, re.IGNORECASE):
                                patterns_found.append("NT book names (Hebrew)")
                                
                            if re.search(r'Genesis|Exodus|Leviticus|BERĔSHITH|SHEMOTH', text, re.IGNORECASE):
                                patterns_found.append("OT book names")
                            
                            if re.search(r'\d+:\d+', text):
                                patterns_found.append("Verse references")
                            
                            if re.search(r'^\d+\s+\w+.*', text, re.MULTILINE):
                                patterns_found.append("Numbered verses")
                                
                            if patterns_found:
                                print(f"   🔍 Patterns found: {', '.join(patterns_found)}")
                            
                        else:
                            print("   (No extractable text)")
                            
                    except Exception as e:
                        print(f"   ❌ Error reading page: {e}")
    
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

if __name__ == "__main__":
    sample_pdf_structure()