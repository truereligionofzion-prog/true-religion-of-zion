#!/usr/bin/env python3
"""
Targeted New Testament extraction from Yah Scriptures PDF
"""

import pdfplumber
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class TargetedNTExtractor:
    """Extract New Testament verses efficiently"""
    
    def __init__(self):
        self.pdf_path = '/app/yah_scriptures.pdf'
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
    def find_matthew_start(self):
        """Find where Matthew actually begins (not just mentioned in TOC)"""
        
        print("🔍 Finding actual Matthew content start...")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Search in second half of document (likely where NT actually starts)
                start_search = len(pdf.pages) // 2
                
                for page_num in range(start_search, len(pdf.pages)):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        # Look for Matthew 1:1 specifically
                        if re.search(r'1\s*1\s+.*Abraham|genealogy.*Abraham|Matthew.*1.*1', text, re.IGNORECASE):
                            print(f"   📖 Found Matthew content at page {page_num + 1}")
                            
                            # Show sample content
                            lines = text.split('\n')[:15]
                            print(f"   📝 Sample content:")
                            for line in lines:
                                line = line.strip()
                                if line:
                                    print(f"      {line[:100]}...")
                            
                            return page_num
                    
                    if (page_num - start_search) % 100 == 0:
                        print(f"   🔍 Searched {page_num - start_search} pages...")
                        
        except Exception as e:
            print(f"❌ Error finding Matthew: {e}")
            
        return None
    
    def extract_sample_nt_verses(self, start_page: int):
        """Extract sample New Testament verses from starting page"""
        
        print(f"\n📝 Extracting sample NT verses from page {start_page + 1}...")
        
        verses = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Process 10 pages to get a good sample
                for page_offset in range(10):
                    page_num = start_page + page_offset
                    if page_num >= len(pdf.pages):
                        break
                        
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text:
                        lines = text.split('\n')
                        current_chapter = None
                        current_book = 'Matthew'  # Start with Matthew
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            # Look for chapter numbers
                            if re.match(r'^\d+$', line) and len(line) <= 2:
                                try:
                                    chapter_num = int(line)
                                    if 1 <= chapter_num <= 28:  # Valid chapter range for Matthew
                                        current_chapter = chapter_num
                                        print(f"      📖 Chapter {current_chapter}")
                                        continue
                                except:
                                    pass
                            
                            # Look for verse patterns
                            if current_chapter:
                                verse_match = re.match(r'^(\d+)\s+(.+)', line)
                                if verse_match:
                                    verse_num = int(verse_match.group(1))
                                    verse_text = verse_match.group(2).strip()
                                    
                                    if len(verse_text) > 10:
                                        verses.append({
                                            'book': current_book,
                                            'chapter': current_chapter,
                                            'verse': verse_num,
                                            'text': verse_text
                                        })
                                        
                                        if len(verses) <= 10:  # Show first 10
                                            print(f"         {current_chapter}:{verse_num} {verse_text[:60]}...")
        
        except Exception as e:
            print(f"❌ Error extracting verses: {e}")
            
        return verses
    
    async def save_sample_nt_verses(self, verses: list):
        """Save sample NT verses to database"""
        
        if not verses:
            print("❌ No verses to save")
            return False
            
        print(f"\n💾 Saving {len(verses)} sample NT verses to database...")
        
        try:
            saved_count = 0
            
            for verse in verses:
                # Create verse document
                verse_doc = {
                    'id': f"{verse['book'].lower().replace(' ', '_')}_{verse['chapter']}_{verse['verse']}_yah_scriptures",
                    'book': verse['book'],
                    'chapter': verse['chapter'],
                    'verse': verse['verse'],
                    'text': verse['text'],
                    'version': 'yah_scriptures',
                    'testament': 'new',
                    'has_precept': False,
                    'source': 'yah_scriptures_pdf',
                    'createdAt': datetime.now(timezone.utc)
                }
                
                # Insert or update
                await self.db.bible_verses.replace_one(
                    {'id': verse_doc['id']},
                    verse_doc,
                    upsert=True
                )
                
                saved_count += 1
            
            print(f"   ✅ Saved {saved_count} verses")
            return True
            
        except Exception as e:
            print(f"❌ Error saving verses: {e}")
            return False
    
    async def run_targeted_extraction(self):
        """Run targeted NT extraction"""
        
        print("🚀 Starting Targeted New Testament Extraction")
        print("=" * 50)
        
        try:
            # Find Matthew start
            matthew_start = self.find_matthew_start()
            
            if matthew_start:
                # Extract sample verses
                sample_verses = self.extract_sample_nt_verses(matthew_start)
                
                print(f"\n📊 Extracted {len(sample_verses)} sample NT verses")
                
                # Save to database
                if sample_verses:
                    success = await self.save_sample_nt_verses(sample_verses)
                    
                    if success:
                        print(f"\n🎉 Success! Added sample New Testament verses")
                        
                        # Check updated stats
                        stats_result = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
                        nt_count = await self.db.bible_verses.count_documents({'version': 'yah_scriptures', 'testament': 'new'})
                        
                        print(f"📊 Total Yah Scriptures verses: {stats_result}")
                        print(f"📊 New Testament verses: {nt_count}")
                        
                        return True
                
            else:
                print("❌ Could not find Matthew content in PDF")
                
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()
                
        return False

async def main():
    extractor = TargetedNTExtractor()
    success = await extractor.run_targeted_extraction()
    
    if success:
        print("\n✅ Targeted extraction completed successfully!")
    else:
        print("\n❌ Targeted extraction failed")

if __name__ == "__main__":
    asyncio.run(main())