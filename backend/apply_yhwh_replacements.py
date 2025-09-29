#!/usr/bin/env python3
"""
Apply YHWH/YHUH replacements to existing mitzvot data
This script will update existing records in the database
"""

import os
import re
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def replace_god_with_yhwh(text):
    """Replace 'God' with 'YHWH' or 'YHUH' randomly, including related terms"""
    if not text:
        return text
        
    replacements = ['YHWH', 'YHUH']
    
    # Replace various forms - preserve case sensitivity
    # 'God' -> YHWH/YHUH (but not 'gods' plural)
    text = re.sub(r'\bGod\b(?!s)', lambda m: random.choice(replacements), text)
    # 'Lord' -> YHWH/YHUH  
    text = re.sub(r'\bLord\b', lambda m: random.choice(replacements), text)
    # 'LORD' -> YHWH/YHUH
    text = re.sub(r'\bLORD\b', lambda m: random.choice(replacements), text)
    
    return text

def apply_yhwh_replacements():
    """Apply YHWH/YHUH replacements to existing mitzvot"""
    print("=== Applying YHWH/YHUH Replacements to Existing Data ===")
    
    # Get all mitzvot
    mitzvot = list(db.mitzvot.find({}))
    total_count = len(mitzvot)
    
    if total_count == 0:
        print("❌ No mitzvot found in database")
        return
    
    print(f"Processing {total_count} mitzvot...")
    
    updated_count = 0
    
    for mitzvah in mitzvot:
        original_title = mitzvah.get('title', '')
        original_source = mitzvah.get('sourceVerse', '')
        
        # Apply replacements
        new_title = replace_god_with_yhwh(original_title)
        new_source = replace_god_with_yhwh(original_source)
        
        # Update keywords as well
        original_keywords = mitzvah.get('keywords', [])
        new_keywords = [replace_god_with_yhwh(keyword) for keyword in original_keywords]
        
        # Check if any changes were made
        if (new_title != original_title or 
            new_source != original_source or 
            new_keywords != original_keywords):
            
            # Update the record
            db.mitzvot.update_one(
                {'_id': mitzvah['_id']},
                {
                    '$set': {
                        'title': new_title,
                        'sourceVerse': new_source,
                        'keywords': new_keywords
                    }
                }
            )
            updated_count += 1
            
            if updated_count % 10 == 0:
                print(f"   Updated {updated_count}/{total_count}...")
    
    print(f"✅ Updated {updated_count} mitzvot with YHWH/YHUH replacements")
    return updated_count

def verify_replacements():
    """Verify YHWH/YHUH replacements were applied correctly"""
    print("\n=== Verifying YHWH/YHUH Replacements ===")
    
    # Count old terms that should have been replaced
    old_god = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\bGod\b(?!s)', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\bGod\b(?!s)', '$options': 'i'}}
        ]
    })
    
    old_lord = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\bLord\b', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\bLord\b', '$options': 'i'}}
        ]
    })
    
    old_terms_total = old_god + old_lord
    
    # Count YHWH/YHUH instances
    yhwh_count = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\bYHWH\b', '$options': 'i'}},
            {'title': {'$regex': r'\bYHUH\b', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\bYHWH\b', '$options': 'i'}},
            {'sourceVerse': {'$regex': r'\bYHUH\b', '$options': 'i'}}
        ]
    })
    
    # Test search functionality
    yhwh_search = list(db.mitzvot.find({'title': {'$regex': r'\bYHWH\b', '$options': 'i'}}).limit(3))
    elohim_search = list(db.mitzvot.find({'sourceVerse': {'$regex': r'\bElohim\b', '$options': 'i'}}).limit(3))
    
    print(f"Old 'God' terms remaining: {old_god}")
    print(f"Old 'Lord' terms remaining: {old_lord}")
    print(f"Total old terms: {old_terms_total}")
    print(f"YHWH/YHUH instances found: {yhwh_count}")
    print(f"YHWH in titles: {len(yhwh_search)} (showing first 3)")
    print(f"Elohim in verses: {len(elohim_search)} (showing first 3)")
    
    if yhwh_search:
        print("\nSample YHWH replacements:")
        for mitzvah in yhwh_search:
            print(f"  #{mitzvah.get('number', 'N/A')}: {mitzvah.get('title', 'N/A')}")
    
    if elohim_search:
        print("\nSample Elohim verses:")
        for mitzvah in elohim_search:
            verse_preview = mitzvah.get('sourceVerse', '')[:60] + "..."
            print(f"  #{mitzvah.get('number', 'N/A')}: {verse_preview}")
    
    return {
        'old_terms': old_terms_total,
        'yhwh_instances': yhwh_count,
        'success': old_terms_total == 0 and yhwh_count > 0
    }

def main():
    """Main function"""
    print("=== YHWH/YHUH Replacement Application ===")
    
    # Apply replacements
    updated_count = apply_yhwh_replacements()
    
    # Verify results
    results = verify_replacements()
    
    # Summary
    total_mitzvot = db.mitzvot.count_documents({})
    
    print(f"\n✅ Replacement Summary:")
    print(f"📊 Total Mitzvot: {total_mitzvot}")
    print(f"📊 Updated Records: {updated_count}")
    print(f"📊 YHWH/YHUH Instances: {results['yhwh_instances']}")
    print(f"📊 Old Terms Remaining: {results['old_terms']}")
    
    if results['success']:
        print("✅ YHWH/YHUH replacements successful!")
    else:
        print("⚠️  YHWH/YHUH replacements need review")
    
    print("\n🔄 Ready for final testing")

if __name__ == "__main__":
    main()