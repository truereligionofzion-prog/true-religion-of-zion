#!/usr/bin/env python3
"""
Update existing precepts data with scholarly divine name replacements
Based on ancient Hebrew manuscripts (Dead Sea Scrolls, Masoretic Text)
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from scholarly_divine_names import ScholarlyDivineNameReplacer

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

async def update_precepts_divine_names():
    """Update all precepts verses with scholarly divine name replacements"""
    
    replacer = ScholarlyDivineNameReplacer()
    
    print("🔍 Fetching all precepts...")
    precepts = await db.precepts.find({}).to_list(length=None)
    print(f"Found {len(precepts)} precepts to process")
    
    if not precepts:
        print("No precepts found in database. Nothing to update.")
        return
    
    total_replacements = 0
    updated_precepts = 0
    updated_verses = 0
    replacement_stats = {}
    
    print("🔄 Processing precepts with scholarly divine name replacements...")
    
    for i, precept in enumerate(precepts):
        precept_updated = False
        
        # Process verses in this precept
        for verse_idx, verse in enumerate(precept.get('verses', [])):
            original_text = verse.get('text', '')
            
            if not original_text:
                continue
            
            # Apply scholarly replacements
            result = replacer.apply_replacements(original_text, preserve_elohim=True)
            new_text = result['text']
            
            # Check if text changed
            if new_text != original_text:
                verse_replacements = result['total_replacements']
                total_replacements += verse_replacements
                updated_verses += 1
                precept_updated = True
                
                # Update the verse text in the precept
                precept['verses'][verse_idx]['text'] = new_text
                
                print(f"  Updated {precept.get('title', 'Unknown')} - Verse {verse.get('book', 'Unknown')} {verse.get('chapter', '?')}:{verse.get('verse', '?')}")
                print(f"    Original: {original_text[:80]}...")
                print(f"    Updated:  {new_text[:80]}...")
                print(f"    Changes:  {verse_replacements} divine name replacements")
                
                # Aggregate replacement statistics
                for hebrew_name, details in result['replacements'].items():
                    if hebrew_name not in replacement_stats:
                        replacement_stats[hebrew_name] = 0
                    replacement_stats[hebrew_name] += details['count']
        
        # Update the entire precept in database if any verses changed
        if precept_updated:
            await db.precepts.update_one(
                {'_id': precept['_id']},
                {'$set': {'verses': precept['verses']}}
            )
            updated_precepts += 1
        
        # Progress indicator
        if (i + 1) % 5 == 0:
            print(f"  Progress: {i + 1}/{len(precepts)} precepts processed")
    
    print(f"\n✅ Precepts divine name update completed!")
    print(f"📊 Summary:")
    print(f"   Total precepts processed: {len(precepts)}")
    print(f"   Precepts updated: {updated_precepts}")
    print(f"   Verses updated: {updated_verses}")
    print(f"   Total divine name replacements: {total_replacements}")
    
    if replacement_stats:
        print(f"\n📈 Replacement breakdown:")
        for hebrew_name, count in replacement_stats.items():
            print(f"   {hebrew_name}: {count} occurrences")
    
    if total_replacements > 0:
        print(f"\n🎯 The precepts now use scholarly divine names:")
        print(f"   - YHWH (for original Hebrew Tetragrammaton)")
        print(f"   - YHWH Elohim (for compound divine names)")  
        print(f"   - YHUH (for Adonai - reverence substitute)")
        print(f"   - God (preserved for Elohim - correct translation)")
    else:
        print(f"\n📝 Note: No additional divine name replacements were needed.")
        print(f"   The precepts may already have the correct scholarly divine names.")

if __name__ == "__main__":
    print("📜 Precepts Divine Name Update - Scholarly Approach")
    print("=" * 60)
    print("Based on Dead Sea Scrolls and Masoretic Text research")
    print()
    
    asyncio.run(update_precepts_divine_names())