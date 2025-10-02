#!/usr/bin/env python3
"""
Cleanup script to remove erroneous "BERĔSHITH [number]" artifacts from verse text
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
from datetime import datetime, timezone

class BereshithCleanup:
    """Remove BERĔSHITH artifacts from verse text"""
    
    def __init__(self):
        # MongoDB connection
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Pattern to match BERĔSHITH followed by numbers
        self.bereshith_pattern = re.compile(r'\s*BERĔSHITH\s+\d+\s*', re.IGNORECASE)
        
        # Statistics
        self.stats = {
            'verses_found': 0,
            'verses_cleaned': 0,
            'total_removals': 0
        }
    
    async def find_affected_verses(self):
        """Find all verses containing BERĔSHITH artifacts"""
        
        print("🔍 Searching for verses with BERĔSHITH artifacts...")
        
        # Search for verses containing BERĔSHITH pattern
        cursor = self.db.bible_verses.find({
            'version': 'yah_scriptures',
            'text': {'$regex': 'BERĔSHITH', '$options': 'i'}
        })
        
        affected_verses = await cursor.to_list(length=None)
        self.stats['verses_found'] = len(affected_verses)
        
        print(f"   📊 Found {len(affected_verses)} verses with BERĔSHITH artifacts")
        
        # Show some examples
        if affected_verses:
            print("   📋 Examples:")
            for i, verse in enumerate(affected_verses[:3]):
                text_preview = verse['text'][:100] + "..." if len(verse['text']) > 100 else verse['text']
                print(f"      {i+1}. {verse['book']} {verse['chapter']}:{verse['verse']} - {text_preview}")
        
        return affected_verses
    
    async def clean_verse_text(self, verse):
        """Clean BERĔSHITH artifacts from a single verse"""
        
        original_text = verse['text']
        
        # Remove BERĔSHITH pattern
        cleaned_text = self.bereshith_pattern.sub('', original_text)
        
        # Clean up any double spaces that might result
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text.strip())
        
        # Count removals
        removals = len(self.bereshith_pattern.findall(original_text))
        self.stats['total_removals'] += removals
        
        return cleaned_text, removals > 0
    
    async def update_verse(self, verse_id, cleaned_text):
        """Update verse in database with cleaned text"""
        
        result = await self.db.bible_verses.update_one(
            {'id': verse_id},
            {
                '$set': {
                    'text': cleaned_text,
                    'updatedAt': datetime.now(timezone.utc),
                    'cleaned': True
                }
            }
        )
        
        return result.modified_count > 0
    
    async def run_cleanup(self):
        """Run the complete cleanup process"""
        
        start_time = datetime.now()
        print("🧹 Starting BERĔSHITH Cleanup Process")
        print("=" * 50)
        
        try:
            # Find affected verses
            affected_verses = await self.find_affected_verses()
            
            if not affected_verses:
                print("✅ No BERĔSHITH artifacts found. Database is clean!")
                return True
            
            print(f"\n🔧 Cleaning {len(affected_verses)} verses...")
            
            # Process each verse
            for i, verse in enumerate(affected_verses):
                # Clean the text
                cleaned_text, was_changed = await self.clean_verse_text(verse)
                
                if was_changed:
                    # Update in database
                    success = await self.update_verse(verse['id'], cleaned_text)
                    
                    if success:
                        self.stats['verses_cleaned'] += 1
                        
                        if i < 3:  # Show first 3 examples
                            print(f"   ✅ {verse['book']} {verse['chapter']}:{verse['verse']}")
                            print(f"      Before: {verse['text'][:80]}...")
                            print(f"      After:  {cleaned_text[:80]}...")
                            print()
                
                # Progress update
                if (i + 1) % 10 == 0:
                    print(f"   📊 Processed {i + 1}/{len(affected_verses)} verses...")
            
            # Final summary
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 50)
            print("🎉 BERĔSHITH CLEANUP COMPLETE!")
            print(f"⏱️  Processing time: {processing_time:.1f} seconds")
            print(f"🔍 Verses found: {self.stats['verses_found']}")
            print(f"🧹 Verses cleaned: {self.stats['verses_cleaned']}")
            print(f"🗑️  Total artifacts removed: {self.stats['total_removals']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
        
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    cleanup = BereshithCleanup()
    await cleanup.run_cleanup()

if __name__ == "__main__":
    asyncio.run(main())