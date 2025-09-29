#!/usr/bin/env python3
"""
Section 1: Fix the 1 remaining incorrect pattern
Mitzvah #3: "YHUH our YHUH" should be "YHUH our Elohim"
"""

import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def fix_section_1_incorrect_patterns():
    """Fix the remaining incorrect 'our' pattern"""
    print("=== SECTION 1: FIXING INCORRECT PATTERNS ===")
    
    # Target specific mitzvah #3
    mitzvah_3 = db.mitzvot.find_one({'number': 3})
    
    if not mitzvah_3:
        print("❌ Mitzvah #3 not found")
        return False
    
    print(f"Mitzvah #3 BEFORE:")
    print(f"  Title: {mitzvah_3.get('title', '')}")
    print(f"  Source: {mitzvah_3.get('sourceVerse', '')}")
    
    # Apply the specific fix for "our" pattern
    original_source = mitzvah_3.get('sourceVerse', '')
    
    # Fix "YHUH our YHUH" → "YHUH our Elohim"
    new_source = re.sub(r'\bYHUH our YHUH\b', 'YHUH our Elohim', original_source)
    # Also fix "YHWH our YHWH" just in case
    new_source = re.sub(r'\bYHWH our YHWH\b', 'YHWH our Elohim', new_source)
    
    if new_source != original_source:
        # Update the record
        result = db.mitzvot.update_one(
            {'number': 3},
            {'$set': {'sourceVerse': new_source}}
        )
        
        print(f"\nMitzvah #3 AFTER:")
        print(f"  Title: {mitzvah_3.get('title', '')}")
        print(f"  Source: {new_source}")
        print(f"  ✅ Updated successfully ({result.modified_count} record)")
        return True
    else:
        print("  No changes needed")
        return False

def verify_section_1():
    """Verify Section 1 correction"""
    print(f"\n=== SECTION 1 VERIFICATION ===")
    
    # Check for remaining "our" patterns
    remaining_our_patterns = list(db.mitzvot.find({
        '$or': [
            {'title': {'$regex': r'(YHWH|YHUH) our (YHWH|YHUH)'}},
            {'sourceVerse': {'$regex': r'(YHWH|YHUH) our (YHWH|YHUH)'}}
        ]
    }))
    
    print(f"Remaining 'our' patterns: {len(remaining_our_patterns)}")
    
    if remaining_our_patterns:
        for record in remaining_our_patterns:
            print(f"  #{record.get('number', 'N/A')}: {record.get('sourceVerse', '')[:80]}...")
        return False
    else:
        print("✅ All 'our' patterns fixed!")
        
        # Show the corrected example
        mitzvah_3 = db.mitzvot.find_one({'number': 3})
        if mitzvah_3:
            print(f"\n📝 Corrected example:")
            print(f"  #{mitzvah_3.get('number', 'N/A')}: {mitzvah_3.get('title', '')}")
            print(f"  Source: {mitzvah_3.get('sourceVerse', '')[:100]}...")
        
        return True

def main():
    """Main Section 1 correction"""
    print("=== SECTION 1: INCORRECT PATTERN CORRECTION ===")
    print("Target: Fix 'YHUH our YHUH' → 'YHUH our Elohim' in Mitzvah #3")
    
    # Fix the pattern
    fixed = fix_section_1_incorrect_patterns()
    
    # Verify the fix
    verified = verify_section_1()
    
    # Summary
    print(f"\n🎯 SECTION 1 SUMMARY:")
    print(f"Pattern fixed: {'YES' if fixed else 'NO'}")
    print(f"Verification passed: {'YES' if verified else 'NO'}")
    
    if fixed and verified:
        print("✅ SECTION 1 COMPLETE - Ready for Section 2")
    else:
        print("⚠️  SECTION 1 needs attention")
    
    print(f"\n🔄 Next: Section 2 (old terms) then Section 3 (multi-instances)")

if __name__ == "__main__":
    main()