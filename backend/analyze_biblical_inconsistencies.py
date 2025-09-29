#!/usr/bin/env python3
"""
Comprehensive analysis of biblical name inconsistencies
Identify all patterns that need correction before systematic fixing
"""

import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

def analyze_current_state():
    """Comprehensive analysis of current biblical name usage"""
    print("=== COMPREHENSIVE BIBLICAL NAME ANALYSIS ===")
    print("Analyzing all 613 mitzvot for inconsistencies...")
    
    all_mitzvot = list(db.mitzvot.find({}).sort("number", 1))
    
    # Categories for analysis
    issues = {
        'incorrect_patterns': [],
        'missing_elohim': [],
        'missing_adonai': [], 
        'inconsistent_verses': [],
        'good_examples': []
    }
    
    for mitzvah in all_mitzvot:
        number = mitzvah.get('number', 0)
        title = mitzvah.get('title', '')
        source = mitzvah.get('sourceVerse', '')
        full_text = title + ' ' + source
        
        # Check for problematic patterns
        
        # 1. Still has "YHWH/YHUH thy/your YHWH/YHUH" (should be Elohim)
        if re.search(r'(YHWH|YHUH) (thy|your) (YHWH|YHUH)', full_text):
            issues['incorrect_patterns'].append({
                'number': number,
                'issue': 'thy/your pattern still wrong',
                'text': source[:100] + "..."
            })
        
        # 2. Still has "YHWH/YHUH our YHWH/YHUH" (should be Elohim)  
        if re.search(r'(YHWH|YHUH) our (YHWH|YHUH)', full_text):
            issues['incorrect_patterns'].append({
                'number': number,
                'issue': 'our pattern still wrong',
                'text': source[:100] + "..."
            })
        
        # 3. Multiple YHWH/YHUH in sequence without context
        yhwh_matches = len(re.findall(r'\b(YHWH|YHUH)\b', full_text))
        if yhwh_matches > 2:
            issues['inconsistent_verses'].append({
                'number': number,
                'issue': f'{yhwh_matches} instances of YHWH/YHUH - may need Elohim',
                'text': source[:100] + "..."
            })
        
        # 4. Verses that should probably have Elohim but don't
        if re.search(r'(God|gods|Lord|LORD)', full_text, re.IGNORECASE):
            if 'gods' not in full_text.lower():  # Ignore plural "gods"
                issues['missing_elohim'].append({
                    'number': number,
                    'issue': 'Still has God/Lord/LORD terms',
                    'text': full_text[:100] + "..."
                })
        
        # 5. Good examples (for reference)
        if 'thy Elohim' in full_text and len(issues['good_examples']) < 5:
            issues['good_examples'].append({
                'number': number,
                'pattern': 'thy Elohim',
                'text': source[:80] + "..."
            })
        elif 'YHWH' in full_text and 'Elohim' not in full_text and len(issues['good_examples']) < 10:
            if not re.search(r'(thy|your|our) (YHWH|YHUH)', full_text):
                issues['good_examples'].append({
                    'number': number,
                    'pattern': 'standalone YHWH/YHUH',
                    'text': source[:80] + "..."
                })
    
    return issues

def print_analysis_results(issues):
    """Print comprehensive analysis results"""
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"=" * 50)
    
    # Incorrect patterns
    print(f"\n❌ INCORRECT PATTERNS ({len(issues['incorrect_patterns'])}):")
    for item in issues['incorrect_patterns'][:10]:  # Show first 10
        print(f"  #{item['number']}: {item['issue']}")
        print(f"    Text: {item['text']}")
    
    if len(issues['incorrect_patterns']) > 10:
        print(f"    ... and {len(issues['incorrect_patterns']) - 10} more")
    
    # Missing terms
    print(f"\n⚠️  STILL HAS OLD TERMS ({len(issues['missing_elohim'])}):")
    for item in issues['missing_elohim'][:5]:
        print(f"  #{item['number']}: {item['text']}")
    
    # Inconsistent verses
    print(f"\n🔍 POTENTIALLY INCONSISTENT ({len(issues['inconsistent_verses'])}):")
    for item in issues['inconsistent_verses'][:5]:
        print(f"  #{item['number']}: {item['issue']}")
        print(f"    Text: {item['text']}")
    
    # Good examples
    print(f"\n✅ GOOD EXAMPLES ({len(issues['good_examples'])}):")
    for item in issues['good_examples'][:3]:
        print(f"  #{item['number']} ({item['pattern']}): {item['text']}")

def create_correction_plan(issues):
    """Create systematic correction plan broken into sections"""
    print(f"\n📋 SYSTEMATIC CORRECTION PLAN:")
    print(f"=" * 50)
    
    total_issues = (len(issues['incorrect_patterns']) + 
                   len(issues['missing_elohim']) + 
                   len(issues['inconsistent_verses']))
    
    print(f"Total issues to address: {total_issues}")
    
    if len(issues['incorrect_patterns']) > 0:
        print(f"\n🎯 SECTION 1: Fix Incorrect Patterns ({len(issues['incorrect_patterns'])} records)")
        print(f"   - YHWH/YHUH thy/your YHWH/YHUH → YHWH/YHUH thy/your Elohim")
        print(f"   - YHWH/YHUH our YHWH/YHUH → YHWH/YHUH our Elohim")
        print(f"   Priority: HIGH (these are definitely wrong)")
    
    if len(issues['missing_elohim']) > 0:
        print(f"\n🎯 SECTION 2: Replace Remaining Old Terms ({len(issues['missing_elohim'])} records)")
        print(f"   - God → Elohim")
        print(f"   - Lord → Adonai") 
        print(f"   - LORD → YHWH/YHUH")
        print(f"   Priority: HIGH (these were missed)")
    
    if len(issues['inconsistent_verses']) > 0:
        print(f"\n🎯 SECTION 3: Review Multi-Instance Verses ({len(issues['inconsistent_verses'])} records)")
        print(f"   - Manual review of verses with 3+ divine name instances")
        print(f"   - Determine which should be YHWH vs Elohim based on context")
        print(f"   Priority: MEDIUM (needs contextual analysis)")
    
    print(f"\n📝 RECOMMENDATION:")
    print(f"   Process Section 1 first (incorrect patterns) - these are clear errors")
    print(f"   Then Section 2 (old terms) - these are missed replacements")
    print(f"   Finally Section 3 (multi-instances) - these need careful review")

def main():
    """Main analysis function"""
    print("=== THOROUGH BIBLICAL NAME INCONSISTENCY ANALYSIS ===")
    print("Before systematic corrections, let's identify all issues...")
    
    # Analyze current state
    issues = analyze_current_state()
    
    # Print results
    print_analysis_results(issues)
    
    # Create correction plan
    create_correction_plan(issues)
    
    print(f"\n💡 NEXT STEPS:")
    print(f"   1. Run Section 1 corrections (incorrect patterns)")
    print(f"   2. Verify Section 1 results")
    print(f"   3. Run Section 2 corrections (old terms)")
    print(f"   4. Verify Section 2 results") 
    print(f"   5. Manual review Section 3 (multi-instances)")
    
    print(f"\n🔄 Ready to proceed with systematic section-by-section corrections...")

if __name__ == "__main__":
    main()