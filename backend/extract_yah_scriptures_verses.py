#!/usr/bin/env python3
"""
Extract verses from Yah Scriptures PDF for comparison and New Testament addition
"""

import pdfplumber
import re
from typing import List, Dict, Optional

class YahScripturesExtractor:
    """Extract structured verse data from PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extracted_verses = []
        
    def find_genesis_start(self):
        """Find where Genesis actually starts in the PDF"""
        
        print("🔍 Finding Genesis starting page...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text:
                        # Look for Genesis chapter 1 start
                        if re.search(r'BERĔSHITH|Genesis.*1\s*1', text, re.IGNORECASE):
                            print(f"   📖 Found Genesis starting at page {page_num + 1}")
                            
                            # Extract sample text
                            lines = text.split('\n')
                            print(f"   📝 Sample content:")
                            for line in lines[:20]:
                                line = line.strip()
                                if line and len(line) > 5:
                                    print(f"      {line[:100]}...")
                            
                            return page_num
                            
        except Exception as e:
            print(f"❌ Error finding Genesis: {e}")
            
        return None
    
    def extract_sample_verses_genesis(self, start_page: int, num_pages: int = 5):
        """Extract sample verses from Genesis to understand format"""
        
        print(f"\n📝 Extracting sample Genesis verses (pages {start_page+1} to {start_page+num_pages})...")
        
        verses = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_offset in range(num_pages):
                    page_num = start_page + page_offset
                    if page_num < len(pdf.pages):
                        page = pdf.pages[page_num]
                        text = page.extract_text()
                        
                        if text:
                            print(f"\n📄 Page {page_num + 1}:")
                            
                            # Try different verse extraction patterns
                            lines = text.split('\n')
                            
                            current_chapter = None
                            
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Check for chapter headers
                                chapter_match = re.match(r'^(\d+)$', line)
                                if chapter_match:
                                    current_chapter = int(chapter_match.group(1))
                                    print(f"   📖 Chapter {current_chapter}")
                                    continue
                                
                                # Check for verse patterns: "1 In the beginning..."
                                verse_match = re.match(r'^(\d+)\s+(.+)', line)
                                if verse_match and current_chapter:
                                    verse_num = int(verse_match.group(1))
                                    verse_text = verse_match.group(2).strip()
                                    
                                    if len(verse_text) > 10:  # Ignore short fragments
                                        verse_data = {
                                            'book': 'Genesis',
                                            'chapter': current_chapter,
                                            'verse': verse_num,
                                            'text': verse_text
                                        }
                                        verses.append(verse_data)
                                        print(f"      {current_chapter}:{verse_num} {verse_text[:80]}...")
        
        except Exception as e:
            print(f"❌ Error extracting verses: {e}")
            
        return verses
    
    def find_new_testament_start(self):
        """Find where New Testament starts"""
        
        print("\n🔍 Finding New Testament starting page...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Search in second half of document
                start_search = len(pdf.pages) // 2
                
                for page_num in range(start_search, len(pdf.pages)):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        # Look for New Testament markers
                        if re.search(r'BRIT CHADASHAH|New.*Testament|Matthew.*1\s*1', text, re.IGNORECASE):
                            print(f"   📖 Found New Testament starting at page {page_num + 1}")
                            
                            # Extract sample
                            lines = text.split('\n')
                            print(f"   📝 Sample content:")
                            for line in lines[:15]:
                                line = line.strip()
                                if line and len(line) > 5:
                                    print(f"      {line[:80]}...")
                                    
                            return page_num
                            
        except Exception as e:
            print(f"❌ Error finding New Testament: {e}")
            
        return None
    
    def compare_with_csv_data(self):
        """Compare PDF verses with existing CSV data"""
        
        print("\n🔄 Comparing with existing CSV data...")
        
        # Get a sample of Genesis verses from PDF
        genesis_start = self.find_genesis_start()
        if genesis_start:
            pdf_verses = self.extract_sample_verses_genesis(genesis_start, 3)
            
            if pdf_verses:
                print(f"\n📊 Extracted {len(pdf_verses)} sample verses from PDF")
                
                # Compare with CSV data - let's check Genesis 1:1
                genesis_1_1_pdf = None
                for verse in pdf_verses:
                    if verse['chapter'] == 1 and verse['verse'] == 1:
                        genesis_1_1_pdf = verse['text']
                        break
                
                if genesis_1_1_pdf:
                    print(f"\n🎯 Genesis 1:1 from PDF:")
                    print(f"   {genesis_1_1_pdf}")
                    
                    # Check what we have in database
                    try:
                        import asyncio
                        from motor.motor_asyncio import AsyncIOMotorClient
                        import os
                        
                        async def get_csv_verse():
                            client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
                            db = client[os.environ.get('DB_NAME', 'test_database')]
                            
                            verse = await db.bible_verses.find_one({
                                'version': 'yah_scriptures',
                                'book': 'Genesis', 
                                'chapter': 1,
                                'verse': 1
                            })
                            
                            await client.close()
                            return verse
                        
                        csv_verse = asyncio.run(get_csv_verse())
                        
                        if csv_verse:
                            print(f"\n🎯 Genesis 1:1 from CSV:")
                            print(f"   {csv_verse['text']}")
                            
                            # Compare
                            if genesis_1_1_pdf == csv_verse['text']:
                                print(f"   ✅ MATCH - CSV and PDF are identical")
                            else:
                                print(f"   ⚠️  DIFFERENCE detected")
                                print(f"   📊 PDF length: {len(genesis_1_1_pdf)}")
                                print(f"   📊 CSV length: {len(csv_verse['text'])}")
                        else:
                            print(f"   ❌ No Genesis 1:1 found in CSV data")
                            
                    except Exception as e:
                        print(f"   ❌ Error comparing with database: {e}")
                
    def run_analysis(self):
        """Run complete analysis and comparison"""
        
        print("🚀 Starting Yah Scriptures PDF Analysis & Comparison")
        print("=" * 60)
        
        try:
            # Find Genesis
            genesis_start = self.find_genesis_start()
            
            # Compare with existing data
            self.compare_with_csv_data()
            
            # Find New Testament
            nt_start = self.find_new_testament_start()
            
            print("\n" + "=" * 60)
            print("🎉 Analysis Complete!")
            print(f"📖 Genesis starts at page: {genesis_start + 1 if genesis_start else 'Not found'}")
            print(f"📖 New Testament starts at page: {nt_start + 1 if nt_start else 'Not found'}")
            
            return genesis_start, nt_start
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None, None

def main():
    extractor = YahScripturesExtractor('/app/yah_scriptures.pdf')
    genesis_start, nt_start = extractor.run_analysis()

if __name__ == "__main__":
    main()