#!/usr/bin/env python3
"""
Final fix for YHWH/YHUH consistency - process entire record together
"""

import os
import re
import random
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def replace_with_consistent_form(title, source_verse, keywords, chosen_form):
    """Replace all God/Lord terms in a record with the same chosen form"""
    
    def replace_terms(text):
        if not text:
            return text
        # Replace all variations with the chosen form
        text = re.sub(r'\bGod\b(?!s)', chosen_form, text)
        text = re.sub(r'\bLord\b', chosen_form, text)
        text = re.sub(r'\bLORD\b', chosen_form, text)
        text = re.sub(r'\bthe Lord\b', chosen_form, text, flags=re.IGNORECASE)
        # Also standardize existing mixed YHWH/YHUH to the chosen form
        text = re.sub(r'\bYHWH\b', chosen_form, text)
        text = re.sub(r'\bYHUH\b', chosen_form, text)
        return text
    
    new_title = replace_terms(title)
    new_source = replace_terms(source_verse)
    new_keywords = [replace_terms(str(keyword)) for keyword in keywords]
    
    return new_title, new_source, new_keywords

def fix_consistency_final():
    """Final fix - process each record as a unit with consistent form"""
    print("=== FINAL YHWH/YHUH CONSISTENCY FIX ===")
    print("Processing each record as a unit with ONE consistent form")
    
    all_mitzvot = list(db.mitzvot.find({}))
    total_count = len(all_mitzvot)
    
    print(f"Processing {total_count} records...")
    
    updated_count = 0
    examples = []
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 'Unknown')
        original_title = mitzvah.get('title', '')
        original_source = mitzvah.get('sourceVerse', '')
        original_keywords = mitzvah.get('keywords', [])
        
        # Choose ONE form for this entire record
        chosen_form = random.choice(['YHWH', 'YHUH'])
        
        # Apply consistent replacement across the entire record
        new_title, new_source, new_keywords = replace_with_consistent_form(
            original_title, original_source, original_keywords, chosen_form
        )
        
        # Check if this record has divine names (for tracking)
        has_divine_name = any(term in (new_title + ' ' + new_source) for term in ['YHWH', 'YHUH'])
        
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
                
                # Collect examples
                if has_divine_name and len(examples) < 5:
                    examples.append({
                        'number': number,
                        'chosen_form': chosen_form,
                        'title': new_title,
                        'source_preview': new_source[:100] + "..."
                    })
                    
        except Exception as e:
            print(f"❌ Error updating #{number}: {e}")
        
        if updated_count % 100 == 0 and updated_count > 0:
            print(f"   Processed {updated_count}/{total_count}...")
    
    print(f"\n✅ Processed {updated_count} records with consistent forms")
    
    # Show examples
    if examples:
        print(f"\n📋 Examples of consistent divine name usage:")
        for ex in examples:
            print(f"\n  Mitzvah #{ex['number']} (using {ex['chosen_form']}):")
            print(f"    Title: {ex['title']}")
            print(f"    Source: {ex['source_preview']}")
    
    return updated_count

def final_verification():
    """Final verification - should find NO mixed records"""
    print("\n=== FINAL VERIFICATION ===")
    
    # Find any remaining mixed records (should be 0)
    mixed_query = {
        '$and': [
            {
                '$or': [
                    {'title': {'$regex': r'\bYHWH\b'}},
                    {'sourceVerse': {'$regex': r'\bYHWH\b'}}
                ]
            },
            {
                '$or': [
                    {'title': {'$regex': r'\bYHUH\b'}},
                    {'sourceVerse': {'$regex': r'\bYHUH\b'}}
                ]
            }
        ]
    }
    
    mixed_records = list(db.mitzvot.find(mixed_query))
    
    # Count pure forms
    pure_yhwh = db.mitzvot.count_documents({
        '$and': [
            {
                '$or': [
                    {'title': {'$regex': r'\bYHWH\b'}},
                    {'sourceVerse': {'$regex': r'\bYHWH\b'}}
                ]
            },
            {
                '$and': [
                    {'title': {'$not': {'$regex': r'\bYHUH\b'}}},
                    {'sourceVerse': {'$not': {'$regex': r'\bYHUH\b'}}}
                ]
            }
        ]
    })
    
    pure_yhuh = db.mitzvot.count_documents({
        '$and': [
            {
                '$or': [
                    {'title': {'$regex': r'\bYHUH\b'}},
                    {'sourceVerse': {'$regex': r'\bYHUH\b'}}
                ]
            },
            {
                '$and': [
                    {'title': {'$not': {'$regex': r'\bYHWH\b'}}},
                    {'sourceVerse': {'$not': {'$regex': r'\bYHWH\b'}}}
                ]
            }
        ]
    })
    
    # Test search functionality
    yhwh_search = list(db.mitzvot.find({'title': {'$regex': r'\bYHWH\b'}}).limit(2))
    yhuh_search = list(db.mitzvot.find({'title': {'$regex': r'\bYHUH\b'}}).limit(2))
    
    print(f"📊 FINAL RESULTS:")
    print(f"Mixed forms (should be 0): {len(mixed_records)}")
    print(f"Pure YHWH records: {pure_yhwh}")  
    print(f"Pure YHUH records: {pure_yhuh}")
    print(f"Total with divine name: {pure_yhwh + pure_yhuh}")
    
    if mixed_records:
        print(f"\n❌ Still found {len(mixed_records)} mixed records")
        for record in mixed_records[:2]:
            title = record.get('title', '')
            source = record.get('sourceVerse', '')
            print(f"  #{record.get('number', 'N/A')}: {title}")
            print(f"    Source: {source[:80]}...")
    else:
        print("✅ Perfect consistency achieved!")
    
    # Show clean examples
    print(f"\n📝 CLEAN EXAMPLES:")
    if yhwh_search:
        for ex in yhwh_search:
            print(f"  YHWH: #{ex.get('number', 'N/A')} - {ex.get('title', '')}")
    
    if yhuh_search:
        for ex in yhuh_search:
            print(f"  YHUH: #{ex.get('number', 'N/A')} - {ex.get('title', '')}")
    
    return len(mixed_records) == 0, pure_yhwh + pure_yhuh

def main():
    """Main execution"""
    print("=== FINAL YHWH/YHUH CONSISTENCY CORRECTION ===")
    print("Each record will use only ONE form throughout (YHWH OR YHUH, never both)")
    
    # Apply final fix
    updated_count = fix_consistency_final()
    
    # Final verification
    is_perfect, total_divine = final_verification()
    
    # Summary
    print(f"\n🏆 FINAL SUMMARY:")
    print(f"Records processed: {updated_count}")
    print(f"Total with divine names: {total_divine}")
    print(f"Perfect consistency: {'YES' if is_perfect else 'NO'}")
    
    if is_perfect:
        print("✅ SUCCESS: Each verse now uses only ONE form of the divine name")
        print("   Logic implemented correctly - no mixed forms remain")
    else:
        print("⚠️  Some inconsistencies remain - manual review may be needed")
    
    print(f"\n🔄 Ready for final testing...")

if __name__ == "__main__":
    main()