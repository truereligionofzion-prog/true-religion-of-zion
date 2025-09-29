#!/usr/bin/env python3
"""
Smart biblical name correction using contextual patterns and biblical knowledge
Fix common patterns where YHWH was incorrectly used instead of Elohim
"""

import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def smart_biblical_corrections(text):
    """Apply smart corrections based on biblical patterns"""
    if not text:
        return text
    
    # Common patterns that should use Elohim instead of YHWH
    
    # Pattern 1: "YHWH thy/your YHWH" should be "YHWH thy/your Elohim"
    text = re.sub(r'\bYHWH thy YHWH\b', 'YHWH thy Elohim', text)
    text = re.sub(r'\bYHWH your YHWH\b', 'YHWH your Elohim', text)
    text = re.sub(r'\bYHUH thy YHUH\b', 'YHUH thy Elohim', text)
    text = re.sub(r'\bYHUH your YHUH\b', 'YHUH your Elohim', text)
    
    # Pattern 2: "the YHWH our YHWH" should be "the YHWH our Elohim"  
    text = re.sub(r'\bthe YHWH our YHWH\b', 'the YHWH our Elohim', text)
    text = re.sub(r'\bthe YHUH our YHUH\b', 'the YHUH our Elohim', text)
    
    # Pattern 3: Multiple YHWH in sequence should often be YHWH + Elohim
    text = re.sub(r'\bYHWH YHWH\b', 'YHWH Elohim', text)  
    text = re.sub(r'\bYHUH YHUH\b', 'YHUH Elohim', text)
    
    # Pattern 4: Common phrases that should have Elohim
    text = re.sub(r'\blove YHWH thy YHWH\b', 'love YHWH thy Elohim', text)
    text = re.sub(r'\blove YHUH thy YHUH\b', 'love YHUH thy Elohim', text)
    text = re.sub(r'\bfear YHWH thy YHWH\b', 'fear YHWH thy Elohim', text)
    text = re.sub(r'\bfear YHUH thy YHUH\b', 'fear YHUH thy Elohim', text)
    
    # Pattern 5: "serve YHWH thy YHWH" should be "serve YHWH thy Elohim"
    text = re.sub(r'\bserve YHWH thy YHWH\b', 'serve YHWH thy Elohim', text)
    text = re.sub(r'\bserve YHUH thy YHUH\b', 'serve YHUH thy Elohim', text)
    
    return text

def apply_smart_corrections():
    """Apply smart contextual corrections to fix YHWH/Elohim usage"""
    print("=== SMART BIBLICAL NAME CORRECTIONS ===")
    print("Fixing common patterns where Elohim should be used instead of repeated YHWH/YHUH")
    print("Examples: 'YHWH thy YHWH' → 'YHWH thy Elohim'")
    
    all_mitzvot = list(db.mitzvot.find({}))
    total_count = len(all_mitzvot)
    
    print(f"\nProcessing {total_count} records...")
    
    updated_count = 0
    corrections_made = []
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 'Unknown')
        original_title = mitzvah.get('title', '')
        original_source = mitzvah.get('sourceVerse', '')
        original_keywords = mitzvah.get('keywords', [])
        
        # Apply smart corrections
        new_title = smart_biblical_corrections(original_title)
        new_source = smart_biblical_corrections(original_source)
        new_keywords = [smart_biblical_corrections(str(keyword)) for keyword in original_keywords]
        
        # Check if changes were made
        title_changed = new_title != original_title
        source_changed = new_source != original_source
        
        if title_changed or source_changed:
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
                
                if result.modified_count > 0:
                    updated_count += 1
                    
                    # Track corrections for examples
                    if len(corrections_made) < 10:
                        corrections_made.append({
                            'number': number,
                            'title_before': original_title if title_changed else None,
                            'title_after': new_title if title_changed else None,
                            'source_before': original_source[:100] + "..." if source_changed else None,
                            'source_after': new_source[:100] + "..." if source_changed else None
                        })
                        
            except Exception as e:
                print(f"❌ Error updating #{number}: {e}")
        
        if updated_count % 50 == 0 and updated_count > 0:
            print(f"   Corrected {updated_count} records...")
    
    print(f"\n✅ Applied smart corrections to {updated_count} records")
    
    # Show examples
    if corrections_made:
        print(f"\n📋 Examples of corrections made:")
        for i, corr in enumerate(corrections_made[:5]):
            print(f"\n  Mitzvah #{corr['number']}:")
            if corr['title_before']:
                print(f"    TITLE FIXED:")
                print(f"      Before: {corr['title_before']}")
                print(f"      After:  {corr['title_after']}")
            if corr['source_before']:
                print(f"    SOURCE FIXED:")
                print(f"      Before: {corr['source_before']}")
                print(f"      After:  {corr['source_after']}")
    
    return updated_count

def verify_elohim_usage():
    """Verify that Elohim is now properly used"""
    print("\n=== VERIFYING ELOHIM USAGE ===")
    
    # Count divine names after correction
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
    
    # Check for problematic patterns (should be 0 after correction)
    thy_yhwh_count = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'YHWH thy YHWH|YHUH thy YHUH'}},
            {'sourceVerse': {'$regex': r'YHWH thy YHWH|YHUH thy YHUH'}}
        ]
    })
    
    our_yhwh_count = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'YHWH our YHWH|YHUH our YHUH'}},
            {'sourceVerse': {'$regex': r'YHWH our YHWH|YHUH our YHUH'}}
        ]
    })
    
    print(f"📊 DIVINE NAME COUNTS:")
    print(f"YHWH: {yhwh_count}")
    print(f"YHUH: {yhuh_count}") 
    print(f"Elohim: {elohim_count}")
    print(f"")
    print(f"🔍 PROBLEMATIC PATTERNS (should be 0):")
    print(f"'YHWH/YHUH thy YHWH/YHUH': {thy_yhwh_count}")
    print(f"'YHWH/YHUH our YHWH/YHUH': {our_yhwh_count}")
    
    # Show examples
    elohim_examples = list(db.mitzvot.find({'sourceVerse': {'$regex': r'\bElohim\b'}}).limit(3))
    if elohim_examples:
        print(f"\n📝 ELOHIM EXAMPLES:")
        for ex in elohim_examples:
            print(f"  #{ex.get('number', 'N/A')}: {ex.get('title', '')}")
            print(f"    Source: {ex.get('sourceVerse', '')[:80]}...")
    else:
        print("\n⚠️  No Elohim examples found")
    
    # Show fixed patterns
    thy_elohim = list(db.mitzvot.find({'sourceVerse': {'$regex': r'thy Elohim'}}).limit(2))
    if thy_elohim:
        print(f"\n📝 CORRECTED PATTERNS ('thy Elohim'):")
        for ex in thy_elohim:
            print(f"  #{ex.get('number', 'N/A')}: {ex.get('sourceVerse', '')[:80]}...")
    
    is_improved = elohim_count > 0 and thy_yhwh_count == 0 and our_yhwh_count == 0
    return is_improved, elohim_count

def main():
    """Main execution"""
    print("=== SMART BIBLICAL NAME CORRECTION ===")
    print("Using contextual patterns to fix YHWH/Elohim usage")
    
    # Apply smart corrections
    corrected_count = apply_smart_corrections()
    
    # Verify improvements
    is_improved, elohim_count = verify_elohim_usage()
    
    # Summary
    print(f"\n🎯 SMART CORRECTION SUMMARY:")
    print(f"Records corrected: {corrected_count}")
    print(f"Elohim instances: {elohim_count}")
    print(f"Biblical accuracy improved: {'YES' if is_improved else 'NO'}")
    
    if is_improved:
        print("✅ SUCCESS: Contextual patterns fixed")
        print("   YHWH thy YHWH → YHWH thy Elohim")
        print("   Following proper Hebrew conventions")
    else:
        print("⚠️  May need additional pattern corrections")
    
    print(f"\n🔄 Ready for testing with improved biblical terminology...")

if __name__ == "__main__":
    main()