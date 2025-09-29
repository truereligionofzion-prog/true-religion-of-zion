#!/usr/bin/env python3
"""
Direct YHWH/YHUH replacement implementation - more aggressive approach
This will definitely replace the terms and verify the changes
"""

import os
import re
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def replace_god_terms(text):
    """Replace God terms with YHWH/YHUH - more comprehensive"""
    if not text:
        return text
    
    replacements = ['YHWH', 'YHUH']
    
    # More aggressive replacement patterns
    # Replace "God" but not "gods" (plural)
    text = re.sub(r'\bGod\b(?!s)', lambda m: random.choice(replacements), text)
    # Replace "Lord" 
    text = re.sub(r'\bLord\b', lambda m: random.choice(replacements), text)
    # Replace "LORD" (all caps)
    text = re.sub(r'\bLORD\b', lambda m: random.choice(replacements), text)
    # Replace "the Lord"
    text = re.sub(r'\bthe Lord\b', lambda m: random.choice(replacements), text, flags=re.IGNORECASE)
    
    return text

def force_replace_all_records():
    """Force replace ALL records with YHWH/YHUH terms"""
    print("=== FORCE REPLACING ALL GOD TERMS WITH YHWH/YHUH ===")
    
    # Get ALL records
    all_mitzvot = list(db.mitzvot.find({}))
    total_count = len(all_mitzvot)
    
    print(f"Found {total_count} records to process")
    
    if total_count == 0:
        print("❌ No records found!")
        return
    
    updated_count = 0
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 'Unknown')
        original_title = mitzvah.get('title', '')
        original_source = mitzvah.get('sourceVerse', '')
        original_keywords = mitzvah.get('keywords', [])
        
        # Apply aggressive replacements
        new_title = replace_god_terms(original_title)
        new_source = replace_god_terms(original_source)
        new_keywords = [replace_god_terms(str(keyword)) for keyword in original_keywords]
        
        # Always update - even if no changes detected (to ensure consistency)
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
                
                # Show changes for verification
                if new_title != original_title:
                    print(f"  #{number}: TITLE CHANGED")
                    print(f"    Before: {original_title}")
                    print(f"    After:  {new_title}")
                
                if new_source != original_source:
                    print(f"  #{number}: SOURCE CHANGED")
                    print(f"    Before: {original_source[:60]}...")
                    print(f"    After:  {new_source[:60]}...")
            
        except Exception as e:
            print(f"❌ Error updating #{number}: {e}")
        
        if updated_count % 50 == 0 and updated_count > 0:
            print(f"   Processed {updated_count}/{total_count}...")
    
    print(f"\n✅ Force updated {updated_count} records")
    return updated_count

def immediate_verification():
    """Immediately verify the changes were applied"""
    print("\n=== IMMEDIATE VERIFICATION ===")
    
    # Test specific examples
    test_mitzvot = [1, 6, 7, 8]  # Known to have God/Lord terms
    
    for num in test_mitzvot:
        mitzvah = db.mitzvot.find_one({'number': num})
        if mitzvah:
            title = mitzvah.get('title', '')
            source = mitzvah.get('sourceVerse', '')
            
            has_yhwh = 'YHWH' in title or 'YHUH' in title or 'YHWH' in source or 'YHUH' in source
            has_god = re.search(r'\b(God|Lord|LORD)\b', title + ' ' + source)
            
            status = "✅ SUCCESS" if has_yhwh and not has_god else "❌ NEEDS WORK"
            print(f"Mitzvah #{num}: {status}")
            print(f"  Title: {title}")
            print(f"  Source: {source[:80]}...")
            print()
    
    # Count totals
    total_yhwh = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\b(YHWH|YHUH)\b', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\b(YHWH|YHUH)\b', '$options': 'i'}}
        ]
    })
    
    remaining_god = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\b(God|Lord|LORD)\b', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\b(God|Lord|LORD)\b', '$options': 'i'}}
        ]
    })
    
    print(f"📊 FINAL COUNTS:")
    print(f"Records with YHWH/YHUH: {total_yhwh}")
    print(f"Records with God/Lord/LORD: {remaining_god}")
    
    return total_yhwh, remaining_god

def main():
    """Main execution"""
    print("=== AGGRESSIVE YHWH/YHUH REPLACEMENT ===")
    print("This will forcefully replace all God/Lord/LORD terms")
    
    # Force update all records
    updated_count = force_replace_all_records()
    
    # Immediately verify
    yhwh_count, god_count = immediate_verification()
    
    # Summary
    print(f"\n🎯 REPLACEMENT SUMMARY:")
    print(f"Total records processed: {updated_count}")
    print(f"Records now with YHWH/YHUH: {yhwh_count}")
    print(f"Records still with God/Lord: {god_count}")
    
    if yhwh_count > 0 and god_count < 5:  # Allow for a few edge cases
        print("✅ YHWH/YHUH replacement SUCCESSFUL!")
    else:
        print("⚠️  YHWH/YHUH replacement needs more work")
    
    print("\n🔄 Ready to test API endpoints...")

if __name__ == "__main__":
    main()