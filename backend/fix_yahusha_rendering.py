#!/usr/bin/env python3
"""
Fix Yahusha rendering in New Testament - replace paleo Hebrew with proper name
"""

import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

class YahushaRenderer:
    """Replace paleo Hebrew patterns with Yahusha in NT"""
    
    def __init__(self):
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
    
    def fix_yahusha_patterns(self, text: str) -> str:
        """Replace paleo Hebrew patterns with Yahusha"""
        
        # Common patterns for Yahusha (Jesus) in the text
        patterns_to_replace = [
            (r'\{vWHY\}', 'Yahusha'),  # {vWHY} pattern
            (r'\{vWHY', 'Yahusha'),    # {vWHY without closing brace
            (r'vWHY\}', 'Yahusha'),    # vWHY} without opening brace  
            (r'\[vWHY\]', 'Yahusha'),  # [vWHY] pattern
            (r'\[vWHY', 'Yahusha'),    # [vWHY without closing bracket
            (r'vWHY\]', 'Yahusha'),    # vWHY] without opening bracket
            (r'\{FWHY\}', 'Yahusha'),  # Alternative pattern
            (r'\[FWHY\]', 'Yahusha'),  # Alternative pattern
            (r'FWHY', 'Yahusha'),      # Direct pattern
        ]
        
        original_text = text
        
        for pattern, replacement in patterns_to_replace:
            text = re.sub(pattern, replacement, text)
        
        # Log changes for verification
        if text != original_text:
            return text, True
        
        return text, False
    
    async def update_nt_verses(self):
        """Update all NT verses to fix Yahusha rendering"""
        
        print("🔄 Fixing Yahusha rendering in New Testament verses...")
        
        try:
            # Get all NT verses
            nt_verses = await self.db.bible_verses.find({
                'version': 'yah_scriptures',
                'testament': 'new'
            }).to_list(length=None)
            
            print(f"   📖 Processing {len(nt_verses)} NT verses...")
            
            updated_count = 0
            total_replacements = 0
            
            for verse in nt_verses:
                original_text = verse['text']
                fixed_text, changed = self.fix_yahusha_patterns(original_text)
                
                if changed:
                    # Update the verse in database
                    await self.db.bible_verses.update_one(
                        {'_id': verse['_id']},
                        {'$set': {'text': fixed_text}}
                    )
                    
                    updated_count += 1
                    
                    # Count replacements
                    replacement_count = len(re.findall(r'Yahusha', fixed_text)) - len(re.findall(r'Yahusha', original_text))
                    total_replacements += replacement_count
                    
                    # Show examples of first few changes
                    if updated_count <= 10:
                        print(f"      {verse['book']} {verse['chapter']}:{verse['verse']}")
                        print(f"         Before: {original_text[:100]}...")
                        print(f"         After:  {fixed_text[:100]}...")
            
            print(f"\n✅ Updated {updated_count} verses")
            print(f"📊 Total 'Yahusha' replacements: {total_replacements}")
            
            return updated_count, total_replacements
            
        except Exception as e:
            print(f"❌ Error updating verses: {e}")
            return 0, 0
    
    async def verify_yahusha_changes(self):
        """Verify the Yahusha changes were applied"""
        
        print("\n🔍 Verifying Yahusha changes...")
        
        try:
            # Count verses with Yahusha
            yahusha_count = await self.db.bible_verses.count_documents({
                'version': 'yah_scriptures',
                'testament': 'new',
                'text': {'$regex': 'Yahusha'}
            })
            
            # Check for remaining old patterns
            old_pattern_count = await self.db.bible_verses.count_documents({
                'version': 'yah_scriptures', 
                'testament': 'new',
                'text': {'$regex': r'\{vWHY|\[vWHY|FWHY'}
            })
            
            print(f"   📊 Verses containing 'Yahusha': {yahusha_count}")
            print(f"   🔍 Verses with old patterns remaining: {old_pattern_count}")
            
            # Show some sample verses with Yahusha
            sample_verses = await self.db.bible_verses.find({
                'version': 'yah_scriptures',
                'testament': 'new',
                'text': {'$regex': 'Yahusha'}
            }).limit(5).to_list(5)
            
            print(f"\n📝 Sample verses with 'Yahusha':")
            for verse in sample_verses:
                yahusha_part = verse['text'][:verse['text'].find('Yahusha') + 20] if 'Yahusha' in verse['text'] else verse['text'][:80]
                print(f"   {verse['book']} {verse['chapter']}:{verse['verse']} - ...{yahusha_part}...")
            
            return yahusha_count, old_pattern_count
            
        except Exception as e:
            print(f"❌ Error verifying changes: {e}")
            return 0, 0
    
    async def run_yahusha_fix(self):
        """Run the complete Yahusha fix process"""
        
        print("🚀 STARTING YAHUSHA RENDERING FIX")
        print("=" * 50)
        
        try:
            # Update verses
            updated_count, replacements = await self.update_nt_verses()
            
            if updated_count > 0:
                # Verify changes
                yahusha_verses, old_patterns = await self.verify_yahusha_changes()
                
                print(f"\n🎉 YAHUSHA FIX COMPLETED:")
                print(f"   ✅ Updated {updated_count} verses")  
                print(f"   📊 Made {replacements} Yahusha replacements")
                print(f"   📖 {yahusha_verses} verses now contain 'Yahusha'")
                print(f"   🔍 {old_patterns} verses with old patterns remaining")
                
                return True
            else:
                print("ℹ️ No verses needed Yahusha fixes")
                return True
                
        except Exception as e:
            print(f"❌ Yahusha fix failed: {e}")
            return False
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    renderer = YahushaRenderer()
    success = await renderer.run_yahusha_fix()
    
    if success:
        print("\n✅ Yahusha rendering fix completed successfully!")
    else:
        print("\n❌ Yahusha rendering fix failed")

if __name__ == "__main__":
    asyncio.run(main())