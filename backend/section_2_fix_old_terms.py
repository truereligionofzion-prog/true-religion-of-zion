#!/usr/bin/env python3
"""
Section 2: Fix the 1 remaining old term
Mitzvah #62: Replace remaining "God/Lord/LORD" terms
"""

import os
import re
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def fix_section_2_old_terms():
    """Fix remaining old biblical terms"""
    print("=== SECTION 2: FIXING OLD TERMS ===")
    
    # Find records with old terms
    old_term_records = list(db.mitzvot.find({
        '$or': [
            {'title': {'$regex': r'\b(God|Lord|LORD)\b', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\b(God|Lord|LORD)\b', '$options': 'i'}}
        ]
    }))
    
    print(f"Found {len(old_term_records)} records with old terms")
    
    if not old_term_records:
        print("✅ No old terms found")
        return True
    
    updated_count = 0
    
    for record in old_term_records:
        number = record.get('number', 'Unknown')
        original_title = record.get('title', '')
        original_source = record.get('sourceVerse', '')
        
        print(f"\nMitzvah #{number} BEFORE:")
        print(f"  Title: {original_title}")
        print(f"  Source: {original_source[:100]}...")
        
        # Apply proper biblical replacements
        new_title = apply_proper_replacements(original_title)
        new_source = apply_proper_replacements(original_source)
        
        # Update if changes were made
        if new_title != original_title or new_source != original_source:
            result = db.mitzvot.update_one(
                {'_id': record['_id']},
                {
                    '$set': {
                        'title': new_title,
                        'sourceVerse': new_source
                    }
                }
            )
            
            print(f"Mitzvah #{number} AFTER:")
            print(f"  Title: {new_title}")
            print(f"  Source: {new_source[:100]}...")
            print(f"  ✅ Updated successfully")
            
            updated_count += 1
        else:
            print(f"  No changes needed")
    
    print(f"\n✅ Updated {updated_count} records")
    return updated_count > 0

def apply_proper_replacements(text):
    """Apply proper biblical name replacements based on conventions"""
    if not text:
        return text
    
    # Choose one form for consistency within this text
    chosen_yhwh = random.choice(['YHWH', 'YHUH'])
    
    # Apply replacements based on biblical conventions:
    # "LORD" (all caps) = Hebrew YHWH → YHWH/YHUH
    text = re.sub(r'\bLORD\b', chosen_yhwh, text)
    
    # "God" = Hebrew Elohim → Elohim  
    text = re.sub(r'\bGod\b(?!s)', 'Elohim', text)  # Avoid "gods" plural
    
    # "Lord" = Hebrew Adonai → Adonai
    text = re.sub(r'\bLord\b', 'Adonai', text)
    
    return text

def verify_section_2():
    """Verify Section 2 correction"""
    print(f"\n=== SECTION 2 VERIFICATION ===")
    
    # Check for remaining old terms (excluding "gods" plural)
    remaining_old_terms = list(db.mitzvot.find({
        '$or': [
            {'title': {'$regex': r'\b(God|Lord|LORD)\b'}},
            {'sourceVerse': {'$regex': r'\b(God|Lord|LORD)\b'}}
        ]
    }))
    
    # Filter out legitimate "gods" (plural) usage
    legitimate_remaining = []
    for record in remaining_old_terms:
        title = record.get('title', '')
        source = record.get('sourceVerse', '')
        full_text = title + ' ' + source
        
        # Check if it's legitimate "gods" plural usage
        if 'other gods' in full_text.lower() or 'gods before' in full_text.lower():
            continue  # This is legitimate
        else:
            legitimate_remaining.append(record)
    
    print(f"Remaining old terms (excluding legitimate 'gods'): {len(legitimate_remaining)}")
    
    if legitimate_remaining:
        for record in legitimate_remaining:
            full_text = record.get('title', '') + ' ' + record.get('sourceVerse', '')
            print(f"  #{record.get('number', 'N/A')}: {full_text[:80]}...")
        return False
    else:
        print("✅ All old terms properly replaced!")
        
        # Show new divine name counts
        yhwh_count = db.mitzvot.count_documents({
            '$or': [
                {'title': {'$regex': r'\bYHWH\b'}},
                {'sourceVerse': {'$regex': r'\bYHWH\b'}}
            ]
        })
        
        yhuh_count = db.mitzvot.count_documents({
            '$or': [
                {'title': {'$regex': r'\bYHUH\b'}},
                {'sourceVerse': {'$regex': r'\bYHUH\b'}}
            ]
        })
        
        elohim_count = db.mitzvot.count_documents({
            '$or': [
                {'title': {'$regex': r'\bElohim\b'}},
                {'sourceVerse': {'$regex': r'\bElohim\b'}}
            ]
        })
        
        adonai_count = db.mitzvot.count_documents({
            '$or': [
                {'title': {'$regex': r'\bAdonai\b'}},
                {'sourceVerse': {'$regex': r'\bAdonai\b'}}
            ]
        })
        
        print(f"\n📊 Updated divine name counts:")
        print(f"YHWH: {yhwh_count}")
        print(f"YHUH: {yhuh_count}")
        print(f"Elohim: {elohim_count}")
        print(f"Adonai: {adonai_count}")
        
        return True

def main():
    """Main Section 2 correction"""
    print("=== SECTION 2: OLD TERMS CORRECTION ===")
    print("Target: Replace remaining God/Lord/LORD with proper Hebrew terms")
    
    # Fix old terms
    fixed = fix_section_2_old_terms()
    
    # Verify the fix
    verified = verify_section_2()
    
    # Summary
    print(f"\n🎯 SECTION 2 SUMMARY:")
    print(f"Old terms replaced: {'YES' if fixed else 'NO'}")
    print(f"Verification passed: {'YES' if verified else 'NO'}")
    
    if verified:
        print("✅ SECTION 2 COMPLETE - Ready for Section 3")
    else:
        print("⚠️  SECTION 2 needs attention")
    
    print(f"\n🔄 Next: Section 3 (manual review of multi-instance verses)")

if __name__ == "__main__":
    main()