#!/usr/bin/env python3
"""
Update 613 Mitzvot data with scholarly divine name replacements
To match the Bible with Apocrypha tab formatting
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from scholarly_divine_names import ScholarlyDivineNameReplacer

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

async def update_mitzvot_divine_names():
    """Update all 613 Mitzvot with scholarly divine name replacements"""
    
    replacer = ScholarlyDivineNameReplacer()
    
    print("🔍 Fetching all 613 Mitzvot...")
    mitzvot = await db.mitzvot.find({}).to_list(length=None)
    print(f"Found {len(mitzvot)} mitzvot to process")
    
    if not mitzvot:
        print("No mitzvot found in database. Nothing to update.")
        return
    
    total_replacements = 0
    updated_mitzvot = 0
    replacement_stats = {}
    
    print("🔄 Processing mitzvot with scholarly divine name replacements...")
    
    for i, mitzvah in enumerate(mitzvot):
        mitzvah_updated = False
        changes_made = []
        
        # Fields to process
        fields_to_update = ['title', 'traditionalWording', 'sourceVerse', 'scholarlyNote', 'keywords']
        
        for field in fields_to_update:
            original_text = mitzvah.get(field, '')
            
            if not original_text or not isinstance(original_text, str):
                continue
            
            # Apply scholarly replacements
            result = replacer.apply_replacements(original_text, preserve_elohim=False)
            new_text = result['text']
            
            # Check if text changed
            if new_text != original_text:
                field_replacements = result['total_replacements']
                total_replacements += field_replacements
                mitzvah_updated = True
                
                # Update the field
                mitzvah[field] = new_text
                changes_made.append(f"{field}: {field_replacements} changes")
                
                # Aggregate replacement statistics
                for hebrew_name, details in result['replacements'].items():
                    if hebrew_name not in replacement_stats:
                        replacement_stats[hebrew_name] = 0
                    replacement_stats[hebrew_name] += details['count']
        
        # Update the mitzvah in database if any fields changed
        if mitzvah_updated:
            # Remove _id for update operation
            mitzvah_id = mitzvah.pop('_id')
            await db.mitzvot.update_one(
                {'_id': mitzvah_id},
                {'$set': mitzvah}
            )
            updated_mitzvot += 1
            
            print(f"  Updated Mitzvah {i+1}: {mitzvah.get('title', 'Unknown')[:60]}...")
            for change in changes_made:
                print(f"    - {change}")
        
        # Progress indicator
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{len(mitzvot)} mitzvot processed")
    
    print(f"\n✅ 613 Mitzvot divine name update completed!")
    print(f"📊 Summary:")
    print(f"   Total mitzvot processed: {len(mitzvot)}")
    print(f"   Mitzvot updated: {updated_mitzvot}")
    print(f"   Total divine name replacements: {total_replacements}")
    
    if replacement_stats:
        print(f"\n📈 Replacement breakdown:")
        for hebrew_name, count in replacement_stats.items():
            print(f"   {hebrew_name}: {count} occurrences")
    
    if total_replacements > 0:
        print(f"\n🎯 The 613 Mitzvot now use consistent divine names:")
        print(f"   - YHWH (for original Hebrew Tetragrammaton)")
        print(f"   - YHWH Elohim (for compound divine names)")  
        print(f"   - YHUH (for Adonai - reverence substitute)")
        print(f"   - Elohim (for Hebrew Elohim)")
        print(f"\n   This matches the Bible with Apocrypha formatting!")
    else:
        print(f"\n📝 Note: No divine name replacements were needed.")

if __name__ == "__main__":
    print("⚖️  613 Mitzvot Divine Name Update")
    print("=" * 50)
    print("Updating to match Bible with Apocrypha formatting")
    print()
    
    asyncio.run(update_mitzvot_divine_names())