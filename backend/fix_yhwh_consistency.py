#!/usr/bin/env python3
"""
Corrected YHWH/YHUH replacement - consistent per verse
Choose ONE form per verse and apply it consistently throughout that verse
"""

import os
import re
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def replace_god_terms_consistently(text):
    """Replace God terms with YHWH or YHUH - but consistently within the same text"""
    if not text:
        return text
    
    # Choose ONE form for this entire text/verse
    chosen_form = random.choice(['YHWH', 'YHUH'])
    
    # Replace all instances with the same chosen form
    # Replace "God" but not "gods" (plural)
    text = re.sub(r'\bGod\b(?!s)', chosen_form, text)
    # Replace "Lord" 
    text = re.sub(r'\bLord\b', chosen_form, text)
    # Replace "LORD" (all caps)
    text = re.sub(r'\bLORD\b', chosen_form, text)
    # Replace "the Lord"
    text = re.sub(r'\bthe Lord\b', chosen_form, text, flags=re.IGNORECASE)
    
    return text

def correct_inconsistent_replacements():
    """Fix the inconsistent YHWH/YHUH replacements"""
    print("=== CORRECTING INCONSISTENT YHWH/YHUH REPLACEMENTS ===")
    print("Each verse will now use only ONE form consistently")
    
    # Get ALL records
    all_mitzvot = list(db.mitzvot.find({}))
    total_count = len(all_mitzvot)
    
    print(f"Found {total_count} records to correct")
    
    updated_count = 0
    examples = []
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 'Unknown')
        original_title = mitzvah.get('title', '')
        original_source = mitzvah.get('sourceVerse', '')
        original_keywords = mitzvah.get('keywords', [])
        
        # Apply consistent replacements (choose one form per record)
        new_title = replace_god_terms_consistently(original_title)
        new_source = replace_god_terms_consistently(original_source)  
        new_keywords = [replace_god_terms_consistently(str(keyword)) for keyword in original_keywords]
        
        # Check if this record had mixed forms (the problem we're fixing)
        mixed_before = ('YHWH' in original_title + ' ' + original_source and 
                       'YHUH' in original_title + ' ' + original_source)
        
        try:
            result = db.mitzvot.update_one(
                {'_id': mitzvah['_id']},
                {
                    '$set': {
                        'title': new_title,
                        'sourceVerse': new_source,
                        'keywords': new_keywords
                    }
                }
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                updated_count += 1
                
                # Show examples of corrections
                if mixed_before and len(examples) < 5:
                    examples.append({
                        'number': number,
                        'before_title': original_title,
                        'after_title': new_title,
                        'before_source': original_source[:80] + "...",
                        'after_source': new_source[:80] + "..."
                    })
                    
        except Exception as e:
            print(f"❌ Error updating #{number}: {e}")
        
        if updated_count % 100 == 0 and updated_count > 0:
            print(f"   Corrected {updated_count}/{total_count}...")
    
    print(f"\n✅ Corrected {updated_count} records for consistency")
    
    # Show examples
    if examples:
        print(f"\n📋 Examples of corrections (mixed forms fixed):")
        for ex in examples:
            print(f"\n  Mitzvah #{ex['number']}:")
            print(f"    BEFORE Title: {ex['before_title']}")
            print(f"    AFTER Title:  {ex['after_title']}")
            print(f"    BEFORE Source: {ex['before_source']}")
            print(f"    AFTER Source:  {ex['after_source']}")
    
    return updated_count

def verify_consistency():
    """Verify that no verses have mixed YHWH/YHUH forms"""
    print("\n=== VERIFYING CONSISTENCY ===")
    
    # Find records with mixed forms (this should be zero after correction)
    mixed_records = list(db.mitzvot.find({
        '$and': [
            {
                '$or': [
                    {'title': {'$regex': r'\bYHWH\b', '$options': 'i'}},
                    {'sourceVerse': {'$regex': r'\bYHWH\b', '$options': 'i'}}
                ]
            },
            {
                '$or': [
                    {'title': {'$regex': r'\bYHUH\b', '$options': 'i'}},
                    {'sourceVerse': {'$regex': r'\bYHUH\b', '$options': 'i'}}
                ]
            }
        ]
    }))
    
    # Count pure forms
    pure_yhwh = db.mitzvot.count_documents({
        '$and': [
            {
                '$or': [
                    {'title': {'$regex': r'\bYHWH\b', '$options': 'i'}},
                    {'sourceVerse': {'$regex': r'\bYHWH\b', '$options': 'i'}}
                ]
            },
            {
                '$and': [
                    {'title': {'$not': {'$regex': r'\bYHUH\b', '$options': 'i'}}},
                    {'sourceVerse': {'$not': {'$regex': r'\bYHUH\b', '$options': 'i'}}}
                ]
            }
        ]
    })
    
    pure_yhuh = db.mitzvot.count_documents({
        '$and': [
            {
                '$or': [
                    {'title': {'$regex': r'\bYHUH\b', '$options': 'i'}},
                    {'sourceVerse': {'$regex': r'\bYHUH\b', '$options': 'i'}}
                ]
            },
            {
                '$and': [
                    {'title': {'$not': {'$regex': r'\bYHWH\b', '$options': 'i'}}},
                    {'sourceVerse': {'$not': {'$regex': r'\bYHWH\b', '$options': 'i'}}}
                ]
            }
        ]
    })
    
    # Show examples of each form
    yhwh_example = db.mitzvot.find_one({'title': {'$regex': r'\bYHWH\b', '$options': 'i'}})
    yhuh_example = db.mitzvot.find_one({'title': {'$regex': r'\bYHUH\b', '$options': 'i'}})
    
    print(f"📊 CONSISTENCY RESULTS:")
    print(f"Mixed forms (should be 0): {len(mixed_records)}")
    print(f"Pure YHWH records: {pure_yhwh}")
    print(f"Pure YHUH records: {pure_yhuh}")
    print(f"Total with divine name: {pure_yhwh + pure_yhuh}")
    
    if mixed_records:
        print(f"\n⚠️  Found {len(mixed_records)} records with mixed forms:")
        for record in mixed_records[:3]:  # Show first 3
            print(f"  #{record.get('number', 'N/A')}: {record.get('title', '')[:60]}...")
    else:
        print("✅ No mixed forms found - consistency achieved!")
    
    # Show examples
    if yhwh_example:
        print(f"\n📝 YHWH Example (#{yhwh_example.get('number', 'N/A')}):")
        print(f"  {yhwh_example.get('title', '')}")
    
    if yhuh_example:
        print(f"\n📝 YHUH Example (#{yhuh_example.get('number', 'N/A')}):")
        print(f"  {yhuh_example.get('title', '')}")
    
    return len(mixed_records) == 0

def main():
    """Main correction function"""
    print("=== CORRECTING YHWH/YHUH CONSISTENCY ISSUE ===")
    print("Logic: Each verse uses only ONE form (either YHWH OR YHUH, not both)")
    
    # Correct inconsistent replacements
    updated_count = correct_inconsistent_replacements()
    
    # Verify consistency
    is_consistent = verify_consistency()
    
    # Summary
    print(f"\n🎯 CORRECTION SUMMARY:")
    print(f"Records corrected: {updated_count}")
    print(f"Consistency achieved: {'Yes' if is_consistent else 'No'}")
    
    if is_consistent:
        print("✅ YHWH/YHUH consistency correction SUCCESSFUL!")
        print("   Each verse now uses only one form of the divine name")
    else:
        print("⚠️  Some consistency issues remain - may need another pass")
    
    print("\n🔄 Ready to test with consistent divine names...")

if __name__ == "__main__":
    main()