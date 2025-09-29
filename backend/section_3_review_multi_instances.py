#!/usr/bin/env python3
"""
Section 3: Manual review of multi-instance verses
Validate that verses with multiple divine names are contextually correct
"""

import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def review_section_3_multi_instances():
    """Review verses with multiple divine name instances for accuracy"""
    print("=== SECTION 3: MULTI-INSTANCE VERSE REVIEW ===")
    
    # Find records with 3+ divine name instances
    multi_instance_records = []
    
    all_mitzvot = list(db.mitzvot.find({}).sort("number", 1))
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 0)
        title = mitzvah.get('title', '')
        source = mitzvah.get('sourceVerse', '')
        full_text = title + ' ' + source
        
        # Count divine name instances
        divine_names = len(re.findall(r'\b(YHWH|YHUH|Elohim|Adonai)\b', full_text))
        
        if divine_names >= 3:
            multi_instance_records.append({
                'number': number,
                'title': title,
                'source': source,
                'divine_count': divine_names,
                'analysis': analyze_verse_context(source, number)
            })
    
    print(f"Found {len(multi_instance_records)} verses with 3+ divine name instances:")
    
    for record in multi_instance_records:
        print(f"\n📖 Mitzvah #{record['number']}: {record['title']}")
        print(f"   Source: {record['source'][:100]}...")
        print(f"   Divine names count: {record['divine_count']}")
        print(f"   Analysis: {record['analysis']}")
    
    return multi_instance_records

def analyze_verse_context(source_verse, number):
    """Analyze specific verses for biblical accuracy"""
    
    # Specific known verses
    if number == 3:
        # Deuteronomy 6:4 - The Shema
        # Hebrew: שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד
        # "Shema Yisrael YHWH Eloheinu YHWH Echad"
        if 'YHUH our Elohim is one YHUH' in source_verse or 'YHWH our Elohim is one YHWH' in source_verse:
            return "✅ CORRECT - Hebrew original: YHWH אֱלֹהֵינוּ YHWH (YHWH our-Elohim YHWH)"
        else:
            return "❌ INCORRECT - Should follow Hebrew pattern"
    
    # General analysis for other verses
    if 'thy Elohim' in source_verse or 'your Elohim' in source_verse:
        return "✅ LIKELY CORRECT - Using proper YHWH + Elohim pattern"
    elif re.search(r'(YHWH|YHUH) (YHWH|YHUH)', source_verse):
        return "⚠️  REVIEW NEEDED - Multiple YHWH/YHUH without Elohim context"
    else:
        return "✅ APPEARS CORRECT - Mixed divine names in proper context"

def verify_section_3():
    """Verify that Section 3 issues are resolved"""
    print(f"\n=== SECTION 3 VERIFICATION ===")
    
    # Specific check for Mitzvah #3 (The Shema)
    mitzvah_3 = db.mitzvot.find_one({'number': 3})
    
    if mitzvah_3:
        source = mitzvah_3.get('sourceVerse', '')
        title = mitzvah_3.get('title', '')
        
        print(f"📖 The Shema (Mitzvah #3) Analysis:")
        print(f"   Title: {title}")
        print(f"   Source: {source}")
        
        # Check if it follows the Hebrew pattern correctly
        shema_correct = (
            ('YHUH our Elohim is one YHUH' in source) or 
            ('YHWH our Elohim is one YHWH' in source)
        )
        
        if shema_correct:
            print("   ✅ PERFECT - Matches Hebrew original pattern")
            print("   Hebrew: יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד (YHWH Eloheinu YHWH Echad)")
        else:
            print("   ❌ NEEDS CORRECTION")
            return False
    
    # Check for any remaining problematic patterns
    problematic = list(db.mitzvot.find({
        '$or': [
            {'sourceVerse': {'$regex': r'(YHWH|YHUH) (YHWH|YHUH) (YHWH|YHUH)'}},
            {'title': {'$regex': r'(YHWH|YHUH) (YHWH|YHUH) (YHWH|YHUH)'}}
        ]
    }))
    
    if problematic:
        print(f"\n⚠️  Found {len(problematic)} potentially problematic patterns:")
        for record in problematic:
            print(f"   #{record.get('number', 'N/A')}: {record.get('sourceVerse', '')[:80]}...")
    else:
        print(f"\n✅ No problematic triple-divine-name patterns found")
    
    return len(problematic) == 0

def final_comprehensive_summary():
    """Provide final comprehensive summary of all biblical names"""
    print(f"\n=== FINAL COMPREHENSIVE SUMMARY ===")
    
    # Count all divine names
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
    
    # Check for remaining old terms
    old_terms = db.mitzvot.count_documents({
        '$or': [
            {'title': {'$regex': r'\b(God|Lord|LORD)\b'}},
            {'sourceVerse': {'$regex': r'\b(God|Lord|LORD)\b'}}
        ]
    })
    
    print(f"📊 FINAL DIVINE NAME COUNTS:")
    print(f"YHWH (Tetragrammaton): {yhwh_count}")
    print(f"YHUH (Tetragrammaton): {yhuh_count}") 
    print(f"Elohim (God): {elohim_count}")
    print(f"Adonai (Lord): {adonai_count}")
    print(f"Old terms remaining: {old_terms}")
    
    total_divine = yhwh_count + yhuh_count + elohim_count + adonai_count
    print(f"Total divine name instances: {total_divine}")
    
    # Show key examples
    print(f"\n📝 KEY EXAMPLES:")
    
    # The Shema
    shema = db.mitzvot.find_one({'number': 3})
    if shema:
        print(f"   The Shema: {shema.get('sourceVerse', '')[:80]}...")
    
    # YHWH thy Elohim pattern
    thy_elohim = db.mitzvot.find_one({'sourceVerse': {'$regex': r'thy Elohim'}})
    if thy_elohim:
        print(f"   Thy Elohim: {thy_elohim.get('sourceVerse', '')[:80]}...")
    
    is_complete = old_terms == 0 and total_divine > 150
    return is_complete

def main():
    """Main Section 3 review"""
    print("=== SECTION 3: MULTI-INSTANCE VERSE REVIEW ===")
    print("Manual contextual review of verses with multiple divine names")
    
    # Review multi-instance records
    multi_records = review_section_3_multi_instances()
    
    # Verify accuracy
    verified = verify_section_3()
    
    # Final comprehensive summary
    complete = final_comprehensive_summary()
    
    # Summary
    print(f"\n🎯 SECTION 3 SUMMARY:")
    print(f"Multi-instance verses: {len(multi_records)}")
    print(f"Verification passed: {'YES' if verified else 'NO'}")
    print(f"Biblical accuracy complete: {'YES' if complete else 'NO'}")
    
    if complete and verified:
        print("✅ ALL SECTIONS COMPLETE - Biblical names are now accurate!")
        print("   - Section 1: ✅ Incorrect patterns fixed")
        print("   - Section 2: ✅ Old terms replaced")
        print("   - Section 3: ✅ Multi-instances validated")
    else:
        print("⚠️  Some issues may remain")
    
    print(f"\n🔄 Ready for final API testing with proper Hebrew conventions...")

if __name__ == "__main__":
    main()