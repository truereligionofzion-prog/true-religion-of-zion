#!/usr/bin/env python3
"""
Analyze the Yah Scriptures PDF to understand structure and extract sample content
"""

import pdfplumber
import re
from typing import List, Dict

class YahScripturesPDFAnalyzer:
    """Analyze the Yah Scriptures PDF structure"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def analyze_structure(self):
        """Analyze the overall PDF structure"""
        
        print("📖 Analyzing Yah Scriptures PDF structure...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📊 Total pages: {total_pages}")
                
                # Sample first few pages
                print(f"\n🔍 Analyzing first 5 pages for structure...")
                
                for i in range(min(5, total_pages)):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    
                    if text:
                        print(f"\n📄 Page {i+1} (first 200 chars):")
                        print(f"   {text[:200].replace(chr(10), ' ')}...")
                        
                        # Look for book names
                        book_pattern = r'(Genesis|Exodus|Matthew|Mark|Luke|John|Romans|Corinthians)'
                        books = re.findall(book_pattern, text)
                        if books:
                            print(f"   📚 Books found: {', '.join(set(books))}")
                        
                        # Look for chapter/verse patterns
                        verse_patterns = re.findall(r'(\d+:\d+)', text)
                        if verse_patterns:
                            print(f"   📝 Verse patterns: {verse_patterns[:5]}")
                
        except Exception as e:
            print(f"❌ Error analyzing PDF: {e}")
    
    def find_book_boundaries(self, sample_pages=10):
        """Find where books start and end"""
        
        print(f"\n📚 Finding book boundaries (sampling {sample_pages} pages)...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                # Sample pages throughout the document
                sample_indices = [i * (total_pages // sample_pages) for i in range(sample_pages)]
                
                books_found = []
                
                for page_num in sample_indices:
                    if page_num < total_pages:
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            # Look for book titles (usually at start of line or page)
                            lines = text.split('\n')
                            for line in lines[:10]:  # Check first 10 lines of each page
                                line = line.strip()
                                
                                # Common Bible book patterns
                                book_patterns = [
                                    r'^(Genesis|Exodus|Leviticus|Numbers|Deuteronomy)$',
                                    r'^(Joshua|Judges|Ruth|Samuel|Kings|Chronicles)$', 
                                    r'^(Ezra|Nehemiah|Esther|Job|Psalms|Proverbs)$',
                                    r'^(Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations)$',
                                    r'^(Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah)$',
                                    r'^(Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai)$',
                                    r'^(Zechariah|Malachi)$',
                                    r'^(Matthew|Mark|Luke|John|Acts|Romans)$',
                                    r'^(\d?\s?Corinthians|Galatians|Ephesians|Philippians)$',
                                    r'^(Colossians|Thessalonians|Timothy|Titus|Philemon)$',
                                    r'^(Hebrews|James|Peter|John|Jude|Revelation)$'
                                ]
                                
                                for pattern in book_patterns:
                                    match = re.search(pattern, line)
                                    if match:
                                        book_name = match.group(1)
                                        if book_name not in [b['name'] for b in books_found]:
                                            books_found.append({
                                                'name': book_name,
                                                'page': page_num + 1,
                                                'sample_text': text[:100].replace('\n', ' ')
                                            })
                
                print(f"📚 Found {len(books_found)} unique books:")
                for book in books_found:
                    print(f"   📖 {book['name']} (page {book['page']})")
                
                return books_found
                
        except Exception as e:
            print(f"❌ Error finding book boundaries: {e}")
            return []
    
    def extract_sample_verses(self):
        """Extract sample verses to understand format"""
        
        print(f"\n📝 Extracting sample verses...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Look for Genesis 1:1 and other key verses
                target_verses = ['Genesis 1:1', 'Matthew 1:1', 'John 3:16', 'Psalms 23:1']
                
                for page_num, page in enumerate(pdf.pages[:50]):  # Check first 50 pages
                    text = page.extract_text()
                    
                    if text:
                        # Look for verse patterns
                        verse_matches = re.findall(r'(\d+:\d+[^\d\n]*)', text)
                        
                        for match in verse_matches[:3]:  # Show first 3 verses per page
                            print(f"   Page {page_num + 1}: {match.strip()}")
                        
                        # Look for specific verses
                        for target in target_verses:
                            if target.lower() in text.lower():
                                # Try to extract the verse text
                                lines = text.split('\n')
                                for i, line in enumerate(lines):
                                    if target.lower() in line.lower():
                                        # Get this line and maybe next few
                                        verse_text = line.strip()
                                        if i + 1 < len(lines):
                                            verse_text += ' ' + lines[i + 1].strip()
                                        
                                        print(f"   🎯 FOUND {target}: {verse_text[:100]}...")
                                        break
                
        except Exception as e:
            print(f"❌ Error extracting sample verses: {e}")
    
    def check_divine_names(self):
        """Check what divine names are used in the PDF"""
        
        print(f"\n✨ Checking divine names usage...")
        
        divine_names = ['YHWH', 'YHUH', 'Elohim', 'Adonai', 'LORD', 'God', 'יהוה']
        name_counts = {name: 0 for name in divine_names}
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Sample 20 pages throughout the document
                total_pages = len(pdf.pages)
                sample_pages = min(20, total_pages)
                
                for i in range(sample_pages):
                    page_num = i * (total_pages // sample_pages)
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        for name in divine_names:
                            count = text.count(name)
                            name_counts[name] += count
                
                print("📊 Divine name frequency (sampled):")
                for name, count in name_counts.items():
                    if count > 0:
                        print(f"   {name}: {count} occurrences")
                        
        except Exception as e:
            print(f"❌ Error checking divine names: {e}")
    
    def run_full_analysis(self):
        """Run complete PDF analysis"""
        
        print("🚀 Starting Complete Yah Scriptures PDF Analysis")
        print("=" * 60)
        
        try:
            # Basic structure
            self.analyze_structure()
            
            # Find books
            books = self.find_book_boundaries()
            
            # Sample verses
            self.extract_sample_verses()
            
            # Divine names
            self.check_divine_names()
            
            print("\n" + "=" * 60)
            print("🎉 PDF Analysis Complete!")
            
            return books
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return []

def main():
    analyzer = YahScripturesPDFAnalyzer('/app/yah_scriptures.pdf')
    books = analyzer.run_full_analysis()
    
    if books:
        print(f"\n📋 Summary: Found {len(books)} books in PDF")

if __name__ == "__main__":
    main()