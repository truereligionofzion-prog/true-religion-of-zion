#!/usr/bin/env python3
"""
Update existing Bible data with scholarly divine name replacements
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

async def update_bible_divine_names():
    """Update all Bible verses with scholarly divine name replacements"""
    
    replacer = ScholarlyDivineNameReplacer()
    
    print("🔍 Fetching all Bible verses...")
    bible_verses = await db.bible_verses.find({}).to_list(length=None)
    print(f"Found {len(bible_verses)} verses to process")
    
    if not bible_verses:
        print("No Bible verses found in database. Nothing to update.")
        return
    
    total_replacements = 0
    updated_verses = 0
    replacement_stats = {}
    
    print("🔄 Processing verses with scholarly divine name replacements...")
    
    for i, verse in enumerate(bible_verses):
        original_text = verse.get('text', '')
        
        # Apply scholarly replacements
        result = replacer.apply_replacements(original_text, preserve_elohim=True)
        new_text = result['text']
        
        # Track statistics
        verse_replacements = result['total_replacements']
        if verse_replacements > 0:
            total_replacements += verse_replacements
            updated_verses += 1
            
            # Update the verse in database
            await db.bible_verses.update_one(
                {'_id': verse['_id']},
                {'$set': {'text': new_text}}
            )
            
            print(f"  Updated {verse.get('book', 'Unknown')} {verse.get('chapter', '?')}:{verse.get('verse', '?')}")
            print(f"    Original: {original_text[:80]}...")
            print(f"    Updated:  {new_text[:80]}...")
            print(f"    Changes:  {verse_replacements} divine name replacements")
            
            # Aggregate replacement statistics
            for hebrew_name, details in result['replacements'].items():
                if hebrew_name not in replacement_stats:
                    replacement_stats[hebrew_name] = 0
                replacement_stats[hebrew_name] += details['count']
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(bible_verses)} verses processed")
    
    print(f"\n✅ Bible divine name update completed!")
    print(f"📊 Summary:")
    print(f"   Total verses processed: {len(bible_verses)}")
    print(f"   Verses updated: {updated_verses}")
    print(f"   Total divine name replacements: {total_replacements}")
    
    if replacement_stats:
        print(f"\n📈 Replacement breakdown:")
        for hebrew_name, count in replacement_stats.items():
            print(f"   {hebrew_name}: {count} occurrences")
    
    if total_replacements > 0:
        print(f"\n🎯 The Bible verses now use scholarly divine names:")
        print(f"   - YHWH (for original Hebrew Tetragrammaton)")
        print(f"   - YHWH Elohim (for compound divine names)")  
        print(f"   - YHUH (for Adonai - reverence substitute)")
        print(f"   - God (preserved for Elohim - correct translation)")
    else:
        print(f"\n📝 Note: No divine name replacements were needed.")
        print(f"   This likely means the current Bible sample (Genesis 1, Tobit 1)")
        print(f"   uses 'Elohim' (God) rather than 'YHWH' (LORD), which is correct.")

if __name__ == "__main__":
    print("📖 Bible Divine Name Update - Scholarly Approach")
    print("=" * 60)
    print("Based on Dead Sea Scrolls and Masoretic Text research")
    print()
    
    asyncio.run(update_bible_divine_names())