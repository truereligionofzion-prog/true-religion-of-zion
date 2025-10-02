#!/usr/bin/env python3
"""
Extract New Testament from Yah Scriptures PDF and verify Old Testament accuracy
"""

import pdfplumber
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional

class YahScripturesPDFProcessor:
    """Process Yah Scriptures PDF for accuracy check and New Testament extraction"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Book name mappings
        self.ot_book_mapping = {
            'BERĔSHITH': 'Genesis',
            'SHEMOTH': 'Exodus', 
            'WAYYIQRA': 'Leviticus',
            'BEMIḎBAR': 'Numbers',
            'DEḆARIM': 'Deuteronomy',
            'YAHOSHUA': 'Joshua',
            'SHOPHETIM': 'Judges',
            'RUTH': 'Ruth',
            'SHEMU\'EL ALEPH': '1 Samuel',
            'SHEMU\'EL BETH': '2 Samuel',
            'MELAḴIM ALEPH': '1 Kings',
            'MELAḴIM BETH': '2 Kings',
            'DIḆRE HAYYAMIM ALEPH': '1 Chronicles',
            'DIḆRE HAYYAMIM BETH': '2 Chronicles',
            'EZRA': 'Ezra',
            'NEḤEMYAH': 'Nehemiah',
            'ESTER': 'Esther',
            'IYOḆ': 'Job',
            'TEHILLIM': 'Psalms',
            'MISHLĔY': 'Proverbs',
            'QOHELETH': 'Ecclesiastes',
            'SHIR HASHIRIM': 'Song of Solomon',
            'YESHAYAHU': 'Isaiah',
            'YIRMEYAHU': 'Jeremiah',
            'ĔYḴAH': 'Lamentations',
            'YEḤEZQĔL': 'Ezekiel',
            'DANIYĔL': 'Daniel',
            'HOSHĔA': 'Hosea',
            'YO\'ĔL': 'Joel',
            'AMOS': 'Amos',
            'OḆAḎYAH': 'Obadiah',
            'YONAH': 'Jonah',
            'MIḴAH': 'Micah',
            'NAḤUM': 'Nahum',
            'ḤAḆAQQUQ': 'Habakkuk',
            'TSEPHANYAH': 'Zephaniah',
            'ḤAGGAI': 'Haggai',
            'ZEḴARYAH': 'Zechariah',
            'MAL\'AḴI': 'Malachi'
        }
        
        # New Testament book names (likely in Hebrew/Greek transliteration)
        self.nt_book_patterns = [
            r'MATTITHYAHU|Matthew',
            r'MARQOS|Mark', 
            r'LUQAS|Luke',
            r'YOḤANAN|John',
            r'MA\'ASEH|Acts',
            r'ROMIYIM|Romans',
            r'QORINTIYIM|Corinthians',
            r'GALATIYIM|Galatians', 
            r'EPHESIYIM|Ephesians',
            r'PHILIPPIYIM|Philippians',
            r'QOLASIYIM|Colossians',
            r'TESLONIQIYIM|Thessalonians',
            r'TIMOTHIYOS|Timothy',
            r'TITOS|Titus',
            r'PHILĔMON|Philemon',
            r'IḆRIM|Hebrews',
            r'YA\'AQOḆ|James',
            r'KĔPHA|Peter',
            r'YOḤANAN|John',
            r'YAHUDAH|Jude',
            r'ḤAZON|Revelation'
        ]
        
    async def get_current_csv_data(self):
        """Get sample of current CSV data for comparison"""
        
        print("📊 Getting current CSV data for comparison...")
        
        # Get Genesis 1:1-3 for comparison
        sample_verses = await self.db.bible_verses.find({
            'version': 'yah_scriptures',
            'book': 'Genesis',
            'chapter': 1,
            'verse': {'$lte': 3}
        }).to_list(length=10)
        
        print(f"   Found {len(sample_verses)} sample verses from Genesis")
        for verse in sample_verses:
            print(f"   {verse['book']} {verse['chapter']}:{verse['verse']} - {verse['text'][:100]}...")
            
        return sample_verses
    
    def find_section_boundaries(self):
        """Find Old Testament, New Testament, and Apocrypha boundaries"""
        
        print("🔍 Finding section boundaries in PDF...")
        
        boundaries = {
            'old_testament': None,
            'new_testament': None,
            'apocrypha': None
        }
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"   📖 Total pages: {total_pages}")
                
                # Search throughout document
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text:
                        # Look for Old Testament start (Genesis/BERĔSHITH)
                        if not boundaries['old_testament'] and re.search(r'BERĔSHITH|Genesis.*1.*1', text, re.IGNORECASE):
                            boundaries['old_testament'] = page_num
                            print(f"   📖 Old Testament starts at page {page_num + 1}")
                        
                        # Look for New Testament markers
                        if not boundaries['new_testament']:
                            for pattern in self.nt_book_patterns[:3]:  # Check Matthew, Mark, Luke
                                if re.search(pattern, text, re.IGNORECASE):
                                    boundaries['new_testament'] = page_num
                                    print(f"   📖 New Testament starts at page {page_num + 1}")
                                    break
                        
                        # Look for Apocrypha (typically between OT and NT)
                        apocrypha_patterns = [r'TOḆIYAH|Tobit', r'YAHUDITH|Judith', r'WISDOM', r'SIRACH']
                        if not boundaries['apocrypha']:
                            for pattern in apocrypha_patterns:
                                if re.search(pattern, text, re.IGNORECASE):
                                    boundaries['apocrypha'] = page_num
                                    print(f"   📖 Apocrypha starts at page {page_num + 1}")
                                    break
                    
                    # Progress indicator
                    if (page_num + 1) % 500 == 0:
                        print(f"   🔍 Searched {page_num + 1}/{total_pages} pages...")
                        
                    # Stop if we found all boundaries
                    if all(boundaries.values()):
                        break
                        
        except Exception as e:
            print(f"❌ Error finding boundaries: {e}")
            
        return boundaries
    
    def extract_verses_from_section(self, start_page: int, end_page: int, section_name: str):
        """Extract verses from a specific section of the PDF"""
        
        print(f"\n📝 Extracting verses from {section_name} (pages {start_page + 1} to {end_page + 1})...")
        
        verses = []
        current_book = None
        current_chapter = None
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num in range(start_page, min(end_page + 1, len(pdf.pages))):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        lines = text.split('\n')
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Check for book headers (usually uppercase and alone on line)
                            book_match = None
                            for hebrew_name, english_name in self.ot_book_mapping.items():
                                if line.upper() == hebrew_name.upper():
                                    current_book = english_name
                                    current_chapter = None
                                    print(f"      📖 Found book: {english_name}")
                                    book_match = True
                                    break
                            
                            if book_match:
                                continue
                            
                            # Check for New Testament books
                            if not current_book:
                                for pattern in self.nt_book_patterns:
                                    if re.match(pattern, line, re.IGNORECASE):
                                        # Extract book name - this needs refinement based on actual PDF format
                                        current_book = self.extract_nt_book_name(line)
                                        current_chapter = None
                                        print(f"      📖 Found NT book: {current_book}")
                                        break
                            
                            # Check for chapter numbers (usually just a number on its own line)
                            if current_book and re.match(r'^\d+$', line):
                                current_chapter = int(line)
                                print(f"         📖 Chapter {current_chapter}")
                                continue
                            
                            # Check for verses (number followed by text)
                            if current_book and current_chapter:
                                verse_match = re.match(r'^(\d+)\s+(.+)', line)
                                if verse_match:
                                    verse_num = int(verse_match.group(1))
                                    verse_text = verse_match.group(2).strip()
                                    
                                    if len(verse_text) > 5:  # Ignore fragments
                                        verses.append({
                                            'book': current_book,
                                            'chapter': current_chapter,
                                            'verse': verse_num,
                                            'text': verse_text
                                        })
                    
                    # Progress indicator
                    if (page_num - start_page + 1) % 100 == 0:
                        print(f"   📊 Processed {page_num - start_page + 1}/{end_page - start_page + 1} pages, found {len(verses)} verses")
        
        except Exception as e:
            print(f"❌ Error extracting verses: {e}")
        
        print(f"   ✅ Extracted {len(verses)} verses from {section_name}")
        return verses
    
    def extract_nt_book_name(self, line: str) -> str:
        """Extract New Testament book name from line"""
        # This is a simplified mapping - needs refinement based on actual PDF format
        nt_mappings = {
            'MATTITHYAHU': 'Matthew',
            'MARQOS': 'Mark',
            'LUQAS': 'Luke',
            'YOḤANAN': 'John',  # Handle John vs 1,2,3 John later
            'MA\'ASEH': 'Acts',
            'ROMIYIM': 'Romans',
            'QORINTIYIM ALEPH': '1 Corinthians',
            'QORINTIYIM BETH': '2 Corinthians',
            'GALATIYIM': 'Galatians',
            'EPHESIYIM': 'Ephesians',
            'PHILIPPIYIM': 'Philippians',
            'QOLASIYIM': 'Colossians',
            'TESLONIQIYIM ALEPH': '1 Thessalonians',
            'TESLONIQIYIM BETH': '2 Thessalonians',
            'TIMOTHIYOS ALEPH': '1 Timothy',
            'TIMOTHIYOS BETH': '2 Timothy',
            'TITOS': 'Titus',
            'PHILĔMON': 'Philemon',
            'IḆRIM': 'Hebrews',
            'YA\'AQOḆ': 'James',
            'KĔPHA ALEPH': '1 Peter',
            'KĔPHA BETH': '2 Peter',
            'YOḤANAN ALEPH': '1 John',
            'YOḤANAN BETH': '2 John', 
            'YOḤANAN GIMEL': '3 John',
            'YAHUDAH': 'Jude',
            'ḤAZON': 'Revelation'
        }
        
        line_upper = line.upper().strip()
        for hebrew, english in nt_mappings.items():
            if hebrew.upper() in line_upper:
                return english
                
        # Fallback - extract first word and try to map
        first_word = line.split()[0] if line.split() else line
        return first_word  # This needs refinement
    
    async def run_extraction_and_comparison(self):
        """Run complete extraction and comparison process"""
        
        print("🚀 Starting Yah Scriptures PDF Processing")
        print("=" * 60)
        
        try:
            # Get current data
            csv_data = await self.get_current_csv_data()
            
            # Find boundaries
            boundaries = self.find_section_boundaries()
            
            if boundaries['new_testament']:
                print(f"\n📖 New Testament found at page {boundaries['new_testament'] + 1}")
                
                # Extract New Testament verses (from NT start to end of document)
                nt_verses = self.extract_verses_from_section(
                    boundaries['new_testament'], 
                    2846,  # Near end of PDF
                    "New Testament"
                )
                
                print(f"\n📊 EXTRACTION SUMMARY:")
                print(f"   📖 New Testament verses found: {len(nt_verses)}")
                
                if nt_verses:
                    # Show sample of NT verses
                    print(f"\n📝 Sample New Testament verses:")
                    for verse in nt_verses[:5]:
                        print(f"   {verse['book']} {verse['chapter']}:{verse['verse']} - {verse['text'][:80]}...")
                
                return nt_verses
            else:
                print("❌ New Testament section not found in PDF")
                return []
                
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            return []
        
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    processor = YahScripturesPDFProcessor()
    nt_verses = await processor.run_extraction_and_comparison()
    
    if nt_verses:
        print(f"\n🎉 Success! Extracted {len(nt_verses)} New Testament verses")
    else:
        print(f"\n❌ No New Testament verses extracted")

if __name__ == "__main__":
    asyncio.run(main())