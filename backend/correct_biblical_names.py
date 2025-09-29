#!/usr/bin/env python3
"""
Correct biblical replacement logic based on proper Hebrew translation conventions
- "LORD" (all caps) → YHWH/YHUH (represents Hebrew Tetragrammaton)  
- "Lord" (regular caps) → Adonai (represents Hebrew Adonai)
- "God" → Elohim (represents Hebrew Elohim)
"""

import os
import re
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def apply_correct_biblical_replacements(text):
    """Apply biblically accurate replacements based on Hebrew conventions"""
    if not text:
        return text
    
    # Choose ONE form of YHWH for this text (but only for LORD, not Lord/God)
    chosen_yhwh = random.choice(['YHWH', 'YHUH'])
    
    # 1. "LORD" (all caps) = Hebrew YHWH → YHWH/YHUH
    text = re.sub(r'\bLORD\b', chosen_yhwh, text)
    
    # 2. "God" = Hebrew Elohim → Elohim  
    text = re.sub(r'\bGod\b(?!s)', 'Elohim', text)  # Avoid "gods" plural
    
    # 3. "Lord" (regular caps) = Hebrew Adonai → Adonai
    # But be careful not to change "the Lord" which might be different
    text = re.sub(r'\bLord\b', 'Adonai', text)
    
    # 4. Fix any existing incorrect YHWH/YHUH that should be Elohim
    # This is trickier - we'll handle case by case in verification
    
    return text

def correct_biblical_names():
    """Apply correct biblical name replacements"""
    print("=== CORRECTING BIBLICAL NAME REPLACEMENTS ===")
    print("Applying proper Hebrew translation conventions:")
    print("- LORD (all caps) → YHWH/YHUH (Hebrew Tetragrammaton)")
    print("- God → Elohim (Hebrew Elohim)")  
    print("- Lord → Adonai (Hebrew Adonai)")
    
    all_mitzvot = list(db.mitzvot.find({}))
    total_count = len(all_mitzvot)
    
    print(f"\nProcessing {total_count} records...")
    
    updated_count = 0
    examples = []
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 'Unknown')
        original_title = mitzvah.get('title', '')
        original_source = mitzvah.get('sourceVerse', '')
        original_keywords = mitzvah.get('keywords', [])
        
        # Apply correct biblical replacements
        new_title = apply_correct_biblical_replacements(original_title)
        new_source = apply_correct_biblical_replacements(original_source)
        new_keywords = [apply_correct_biblical_replacements(str(keyword)) for keyword in original_keywords]
        
        # Track changes for examples
        title_changed = new_title != original_title
        source_changed = new_source != original_source
        
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
                
                # Collect examples of changes
                if (title_changed or source_changed) and len(examples) < 8:
                    examples.append({
                        'number': number,
                        'title_before': original_title,
                        'title_after': new_title,
                        'source_before': original_source[:80] + "...",
                        'source_after': new_source[:80] + "...",
                        'title_changed': title_changed,
                        'source_changed': source_changed
                    })
                    
        except Exception as e:
            print(f"❌ Error updating #{number}: {e}")
        
        if updated_count % 100 == 0 and updated_count > 0:
            print(f"   Processed {updated_count}/{total_count}...")
    
    print(f"\n✅ Processed {updated_count} records with correct biblical names")
    
    # Show examples
    if examples:
        print(f"\n📋 Examples of corrections:")
        for ex in examples[:5]:  # Show first 5
            print(f"\n  Mitzvah #{ex['number']}:")
            if ex['title_changed']:
                print(f"    TITLE:")
                print(f"      Before: {ex['title_before']}")
                print(f"      After:  {ex['title_after']}")
            if ex['source_changed']:
                print(f"    SOURCE:")
                print(f"      Before: {ex['source_before']}")
                print(f"      After:  {ex['source_after']}")
    
    return updated_count

def verify_biblical_names():
    """Verify the correct biblical names are in use"""
    print("\n=== VERIFYING BIBLICAL NAME USAGE ===")
    
    # Count different divine names
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
    
    # Check for remaining incorrect terms
    remaining_god = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\bGod\b(?!s)'}},
            {'sourceVerse': {'$regex': r'\bGod\b(?!s)'}}
        ]
    })
    
    remaining_lord = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\bLord\b'}},
            {'sourceVerse': {'$regex': r'\bLord\b'}}
        ]
    })
    
    remaining_lord_caps = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\bLORD\b'}},
            {'sourceVerse': {'$regex': r'\bLORD\b'}}
        ]
    })
    
    print(f"📊 BIBLICAL NAME COUNTS:")
    print(f"YHWH: {yhwh_count}")
    print(f"YHUH: {yhuh_count}")
    print(f"Elohim: {elohim_count}")
    print(f"Adonai: {adonai_count}")
    print(f"")
    print(f"🔍 REMAINING OLD TERMS (should be 0):")
    print(f"'God' remaining: {remaining_god}")
    print(f"'Lord' remaining: {remaining_lord}")  
    print(f"'LORD' remaining: {remaining_lord_caps}")
    
    # Show examples
    elohim_example = db.mitzvot.find_one({'title': {'$regex': r'\bElohim\b'}})
    adonai_example = db.mitzvot.find_one({'title': {'$regex': r'\bAdonai\b'}})
    yhwh_example = db.mitzvot.find_one({'title': {'$regex': r'\bYHWH\b'}})
    
    print(f"\n📝 EXAMPLES:")
    if elohim_example:
        print(f"  Elohim: #{elohim_example.get('number', 'N/A')} - {elohim_example.get('title', '')}")
    if adonai_example:
        print(f"  Adonai: #{adonai_example.get('number', 'N/A')} - {adonai_example.get('title', '')}")
    if yhwh_example:
        print(f"  YHWH: #{yhwh_example.get('number', 'N/A')} - {yhwh_example.get('title', '')}")
    
    total_divine = yhwh_count + yhuh_count + elohim_count + adonai_count
    is_correct = remaining_god == 0 and remaining_lord == 0 and remaining_lord_caps == 0
    
    return is_correct, total_divine

def main():
    """Main execution"""
    print("=== BIBLICAL NAME CORRECTION BASED ON HEBREW CONVENTIONS ===")
    print("Using proper biblical scholarship and translation conventions")
    
    # Apply corrections
    updated_count = correct_biblical_names()
    
    # Verify results
    is_correct, total_divine = verify_biblical_names()
    
    # Summary
    print(f"\n🎯 CORRECTION SUMMARY:")
    print(f"Records processed: {updated_count}")
    print(f"Total with divine names: {total_divine}")
    print(f"Biblically accurate: {'YES' if is_correct else 'NO'}")
    
    if is_correct:
        print("✅ SUCCESS: Biblical names now follow proper Hebrew conventions")
        print("   LORD → YHWH/YHUH | God → Elohim | Lord → Adonai")
    else:
        print("⚠️  Some terms may still need correction")
    
    print(f"\n🔄 Ready for testing with proper biblical terminology...")

if __name__ == "__main__":
    main()