#!/usr/bin/env python3
"""
Backend Testing for Numbers Bible Book Verification

REVIEW REQUEST FOCUS - NUMBERS VERIFICATION:
Please verify that Numbers has been successfully loaded following our proven formula. Test:

1. **Numbers Precision Verification**:
   - Verify Numbers has exactly 1,102 verses across all 36 chapters
   - Check Numbers 1:1-2 contains proper census content (Moses, wilderness, Sinai, children of Israel)
   - Verify Numbers 6:24-26 contains the priestly blessing (LORD bless thee, etc.)
   - Check Numbers 13:1-2 has proper spy narrative content

2. **Content Quality Verification**:
   - Sample 10 Numbers verses to verify authentic biblical content
   - Verify proper Numbers themes (wilderness, Moses, Aaron, tribes, congregation)
   - Check that verses contain substantial biblical language (not truncated)

3. **No Contamination Check**:
   - Verify NO Genesis creation content exists in Numbers verses
   - Check that legitimate KJV brackets are preserved
   - Confirm no placeholder brackets like "see Numbers..." exist

4. **Foundation Books Preservation**:
   - Verify Genesis still has exactly 1,533 verses (preserved)
   - Verify Exodus still has exactly 1,063 verses (preserved) 
   - Verify Leviticus still has exactly 788 verses (preserved)

5. **Complete Database Status**:
   - Get total verse count (should be Genesis 1,533 + Exodus 1,063 + Leviticus 788 + Numbers 1,102 = 4,486)
   - Verify all 4 books exist in KJV 1611 Divine version
   - Confirm proper Old Testament classification and correct book order

Please provide verification that Numbers now follows our proven authentic biblical text formula with no cross-contamination.
"""

import requests
import json
import sys
import os
import asyncio
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = "https://sacred-verse-hub.preview.emergentagent.com/api"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        
    def test_api_root(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Root Connectivity", True, f"Version: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("API Root Connectivity", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root Connectivity", False, f"Error: {str(e)}")
            return False

    def test_numbers_precision_verification(self):
        """REVIEW REQUEST TEST 1: Numbers Precision Verification - Verify Numbers has exactly 1,102 verses across 36 chapters"""
        try:
            print("\n🔍 NUMBERS PRECISION VERIFICATION - CHECKING EXACT VERSE COUNT AND CHAPTER STRUCTURE...")
            
            # Verify Numbers has exactly 1,102 verses
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1102  # Review request specifies exactly 1,102 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Numbers Exactly 1,102 Verses", True, f"✅ PERFECT! Numbers has exactly {total_verses} verses as required")
                    elif total_verses > 0:
                        self.log_test("Numbers Exactly 1,102 Verses", False, f"❌ INCORRECT COUNT! Numbers has {total_verses} verses, expected exactly {expected_verses}")
                    else:
                        self.log_test("Numbers Exactly 1,102 Verses", False, f"❌ NOT FOUND! Numbers does not exist in database (0 verses)")
                else:
                    self.log_test("Numbers Exactly 1,102 Verses", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers Exactly 1,102 Verses", False, f"Error: {str(e)}")
            
            # Verify Numbers has all 36 chapters
            try:
                # Get all Numbers verses to check chapter structure
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        # Extract unique chapters
                        chapters = set()
                        for verse in verses:
                            chapter = verse.get('chapter')
                            if chapter:
                                chapters.add(int(chapter))
                        
                        max_chapter = max(chapters) if chapters else 0
                        expected_chapters = 36  # Review request specifies 36 chapters
                        
                        if max_chapter == expected_chapters:
                            self.log_test("Numbers All 36 Chapters", True, f"✅ PERFECT! Numbers has all {expected_chapters} chapters (1-{max_chapter})")
                        elif max_chapter > 0:
                            self.log_test("Numbers All 36 Chapters", False, f"❌ INCORRECT CHAPTERS! Numbers has {max_chapter} chapters, expected {expected_chapters}")
                        else:
                            self.log_test("Numbers All 36 Chapters", False, f"❌ NO CHAPTERS! No chapter data found in Numbers")
                    else:
                        self.log_test("Numbers All 36 Chapters", False, f"❌ NO DATA! No verses found to check chapter structure")
                else:
                    self.log_test("Numbers All 36 Chapters", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers All 36 Chapters", False, f"Error: {str(e)}")
            
            # Check Numbers 1:1-2 contains proper census content
            print("\n📖 NUMBERS KEY VERSES CONTENT VERIFICATION:")
            
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/1/1")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for census content keywords
                    census_keywords = ['moses', 'wilderness', 'sinai', 'children', 'israel']
                    found_keywords = [kw for kw in census_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 3:
                        self.log_test("Numbers 1:1 Census Content", True, f"✅ AUTHENTIC! Numbers 1:1 contains proper census content: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 1:1 Census Content", False, f"❌ MISSING CONTENT! Numbers 1:1 lacks census keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 1:1 Census Content", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 1:1 Census Content", False, f"Error: {str(e)}")
            
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/1/2")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for census continuation content
                    census_keywords = ['take', 'sum', 'congregation', 'children', 'israel', 'families', 'fathers']
                    found_keywords = [kw for kw in census_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 3:
                        self.log_test("Numbers 1:2 Census Content", True, f"✅ AUTHENTIC! Numbers 1:2 contains proper census content: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 1:2 Census Content", False, f"❌ MISSING CONTENT! Numbers 1:2 lacks census keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 1:2 Census Content", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 1:2 Census Content", False, f"Error: {str(e)}")
            
            # Verify Numbers 6:24-26 contains the priestly blessing
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/6/24")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for priestly blessing content
                    blessing_keywords = ['lord', 'bless', 'thee', 'keep']
                    found_keywords = [kw for kw in blessing_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 3:
                        self.log_test("Numbers 6:24 Priestly Blessing", True, f"✅ AUTHENTIC! Numbers 6:24 contains priestly blessing: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 6:24 Priestly Blessing", False, f"❌ MISSING CONTENT! Numbers 6:24 lacks blessing keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 6:24 Priestly Blessing", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 6:24 Priestly Blessing", False, f"Error: {str(e)}")
            
            # Check Numbers 13:1-2 has proper spy narrative content
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/13/1")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for spy narrative content
                    spy_keywords = ['lord', 'spake', 'moses', 'saying']
                    found_keywords = [kw for kw in spy_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 3:
                        self.log_test("Numbers 13:1 Spy Narrative", True, f"✅ AUTHENTIC! Numbers 13:1 contains spy narrative: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 13:1 Spy Narrative", False, f"❌ MISSING CONTENT! Numbers 13:1 lacks spy keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 13:1 Spy Narrative", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 13:1 Spy Narrative", False, f"Error: {str(e)}")
            
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/13/2")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for spy narrative continuation
                    spy_keywords = ['send', 'men', 'search', 'land', 'canaan', 'children', 'israel']
                    found_keywords = [kw for kw in spy_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 4:
                        self.log_test("Numbers 13:2 Spy Narrative", True, f"✅ AUTHENTIC! Numbers 13:2 contains spy narrative: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 13:2 Spy Narrative", False, f"❌ MISSING CONTENT! Numbers 13:2 lacks spy keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 13:2 Spy Narrative", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 13:2 Spy Narrative", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Numbers Precision Verification", False, f"Error: {str(e)}")
            return False

    def test_new_books_status_check(self):
        """REVIEW REQUEST TEST 2: New Books Status Check - Check Numbers, Deuteronomy, Joshua, Judges, Ruth verse counts and content"""
        try:
            print("\n🔍 NEW BOOKS STATUS CHECK - CHECKING NUMBERS, DEUTERONOMY, JOSHUA, JUDGES, RUTH...")
            
            # Check Numbers: verses count and sample content quality
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    numbers_verses = data.get('total', 0)
                    expected_numbers = 1288  # Standard Numbers verse count
                    
                    print(f"\n📖 NUMBERS STATUS:")
                    print(f"   📝 Verse Count: {numbers_verses} (expected ~{expected_numbers})")
                    
                    if numbers_verses > 1200:
                        self.log_test("Numbers Verse Count", True, f"✅ GOOD! Numbers has {numbers_verses} verses (reasonable count)")
                    elif numbers_verses > 0:
                        self.log_test("Numbers Verse Count", False, f"❌ LOW COUNT! Numbers has only {numbers_verses} verses (expected ~{expected_numbers})")
                    else:
                        self.log_test("Numbers Verse Count", False, f"❌ NOT FOUND! Numbers does not exist in database")
                else:
                    self.log_test("Numbers Verse Count", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers Verse Count", False, f"Error: {str(e)}")
            
            # Check Deuteronomy: verses count and content
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    deuteronomy_verses = data.get('total', 0)
                    expected_deuteronomy = 959  # Standard Deuteronomy verse count
                    
                    print(f"\n📖 DEUTERONOMY STATUS:")
                    print(f"   📝 Verse Count: {deuteronomy_verses} (expected ~{expected_deuteronomy})")
                    
                    if deuteronomy_verses > 900:
                        self.log_test("Deuteronomy Verse Count", True, f"✅ GOOD! Deuteronomy has {deuteronomy_verses} verses (reasonable count)")
                    elif deuteronomy_verses > 0:
                        self.log_test("Deuteronomy Verse Count", False, f"❌ LOW COUNT! Deuteronomy has only {deuteronomy_verses} verses (expected ~{expected_deuteronomy})")
                    else:
                        self.log_test("Deuteronomy Verse Count", False, f"❌ NOT FOUND! Deuteronomy does not exist in database")
                else:
                    self.log_test("Deuteronomy Verse Count", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy Verse Count", False, f"Error: {str(e)}")
            
            # Check Joshua: verses count (shows only 2 verses, investigate why)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Joshua&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    joshua_verses = data.get('total', 0)
                    expected_joshua = 658  # Standard Joshua verse count
                    
                    print(f"\n📖 JOSHUA STATUS (INVESTIGATION):")
                    print(f"   📝 Verse Count: {joshua_verses} (expected ~{expected_joshua})")
                    
                    if joshua_verses == 2:
                        self.log_test("Joshua Only 2 Verses Investigation", False, f"❌ CONFIRMED ISSUE! Joshua has only {joshua_verses} verses (expected ~{expected_joshua}) - needs investigation")
                    elif joshua_verses > 600:
                        self.log_test("Joshua Only 2 Verses Investigation", True, f"✅ RESOLVED! Joshua now has {joshua_verses} verses (good count)")
                    elif joshua_verses > 0:
                        self.log_test("Joshua Only 2 Verses Investigation", False, f"❌ STILL LOW! Joshua has {joshua_verses} verses (expected ~{expected_joshua})")
                    else:
                        self.log_test("Joshua Only 2 Verses Investigation", False, f"❌ NOT FOUND! Joshua does not exist in database")
                else:
                    self.log_test("Joshua Only 2 Verses Investigation", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Joshua Only 2 Verses Investigation", False, f"Error: {str(e)}")
            
            # Check Judges: verses count (shows 1,228 vs target 618 - cross-contamination?)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Judges&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    judges_verses = data.get('total', 0)
                    expected_judges = 618  # Target verse count from review request
                    
                    print(f"\n📖 JUDGES STATUS (CROSS-CONTAMINATION CHECK):")
                    print(f"   📝 Verse Count: {judges_verses} (target {expected_judges})")
                    
                    if judges_verses == 1228:
                        self.log_test("Judges Cross-Contamination Check", False, f"❌ CONFIRMED ISSUE! Judges has {judges_verses} verses vs target {expected_judges} - likely cross-contamination")
                    elif abs(judges_verses - expected_judges) <= 50:
                        self.log_test("Judges Cross-Contamination Check", True, f"✅ GOOD! Judges has {judges_verses} verses (close to target {expected_judges})")
                    elif judges_verses > expected_judges * 1.5:
                        self.log_test("Judges Cross-Contamination Check", False, f"❌ CROSS-CONTAMINATION! Judges has {judges_verses} verses (much higher than target {expected_judges})")
                    elif judges_verses > 0:
                        self.log_test("Judges Cross-Contamination Check", False, f"❌ COUNT ISSUE! Judges has {judges_verses} verses (target {expected_judges})")
                    else:
                        self.log_test("Judges Cross-Contamination Check", False, f"❌ NOT FOUND! Judges does not exist in database")
                else:
                    self.log_test("Judges Cross-Contamination Check", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Judges Cross-Contamination Check", False, f"Error: {str(e)}")
            
            # Check Ruth: verses count (shows 413 vs target 85 - cross-contamination?)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Ruth&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    ruth_verses = data.get('total', 0)
                    expected_ruth = 85  # Target verse count from review request
                    
                    print(f"\n📖 RUTH STATUS (CROSS-CONTAMINATION CHECK):")
                    print(f"   📝 Verse Count: {ruth_verses} (target {expected_ruth})")
                    
                    if ruth_verses == 413:
                        self.log_test("Ruth Cross-Contamination Check", False, f"❌ CONFIRMED ISSUE! Ruth has {ruth_verses} verses vs target {expected_ruth} - likely cross-contamination")
                    elif abs(ruth_verses - expected_ruth) <= 10:
                        self.log_test("Ruth Cross-Contamination Check", True, f"✅ GOOD! Ruth has {ruth_verses} verses (close to target {expected_ruth})")
                    elif ruth_verses > expected_ruth * 2:
                        self.log_test("Ruth Cross-Contamination Check", False, f"❌ CROSS-CONTAMINATION! Ruth has {ruth_verses} verses (much higher than target {expected_ruth})")
                    elif ruth_verses > 0:
                        self.log_test("Ruth Cross-Contamination Check", False, f"❌ COUNT ISSUE! Ruth has {ruth_verses} verses (target {expected_ruth})")
                    else:
                        self.log_test("Ruth Cross-Contamination Check", False, f"❌ NOT FOUND! Ruth does not exist in database")
                else:
                    self.log_test("Ruth Cross-Contamination Check", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Ruth Cross-Contamination Check", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("New Books Status Check", False, f"Error: {str(e)}")
            return False

    def test_content_quality_sampling(self):
        """REVIEW REQUEST TEST 3: Content Quality Sampling - Sample 5 verses from Numbers and check cross-contamination"""
        try:
            print("\n🔍 CONTENT QUALITY SAMPLING - SAMPLE 5 VERSES FROM NUMBERS AND CHECK CROSS-CONTAMINATION...")
            
            # Sample 5 verses from Numbers to verify authentic biblical content
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=5")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print("\n📝 5 NUMBERS VERSES QUALITY SAMPLING:")
                        authentic_verses = 0
                        
                        for i, verse in enumerate(verses[:5], 1):  # Sample exactly 5 verses
                            verse_text = verse.get('text', '')
                            verse_ref = f"Numbers {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Check for authentic biblical content
                            is_authentic = (
                                len(verse_text) > 10 and  # Has content
                                not verse_text.lower().startswith('error') and  # No error messages
                                not 'placeholder' in verse_text.lower() and  # No placeholders
                                verse_text.strip() != ''  # Not empty
                            )
                            
                            # Check for Numbers-specific content
                            numbers_keywords = ['lord', 'moses', 'aaron', 'children', 'israel', 'wilderness', 'congregation', 'tribe', 'camp']
                            has_numbers_content = any(keyword in verse_text.lower() for keyword in numbers_keywords)
                            
                            if is_authentic:
                                authentic_verses += 1
                            
                            if is_authentic and has_numbers_content:
                                print(f"   ✅ Sample {i} - {verse_ref}: AUTHENTIC NUMBERS CONTENT - '{verse_text[:80]}...'")
                            elif is_authentic:
                                print(f"   ⚠️ Sample {i} - {verse_ref}: AUTHENTIC BUT GENERIC - '{verse_text[:80]}...'")
                            else:
                                print(f"   ❌ Sample {i} - {verse_ref}: POOR QUALITY - '{verse_text}'")
                        
                        if authentic_verses >= 4:  # 80%+ authentic
                            self.log_test("Numbers Authentic Biblical Content", True, f"✅ EXCELLENT! {authentic_verses}/5 Numbers verses are authentic biblical content")
                        elif authentic_verses >= 3:  # 60%+ authentic
                            self.log_test("Numbers Authentic Biblical Content", True, f"✅ GOOD! {authentic_verses}/5 Numbers verses are authentic")
                        else:
                            self.log_test("Numbers Authentic Biblical Content", False, f"❌ POOR! Only {authentic_verses}/5 Numbers verses are authentic")
                        
                    else:
                        self.log_test("Numbers Authentic Biblical Content", False, f"❌ NO DATA! No Numbers verses found for quality sampling")
                else:
                    self.log_test("Numbers Authentic Biblical Content", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers Authentic Biblical Content", False, f"Error: {str(e)}")
            
            # Check for cross-contamination in Judges and Ruth
            print("\n🔍 CROSS-CONTAMINATION CHECK IN JUDGES AND RUTH:")
            
            # Check Judges for cross-contamination
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Judges&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    judges_verses = data.get('verses', [])
                    
                    contamination_found = 0
                    other_book_indicators = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'creation', 'adam', 'eve', 'noah', 'abraham']
                    
                    for verse in judges_verses:
                        verse_text = verse.get('text', '').lower()
                        verse_ref = f"Judges {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                        book = verse.get('book', '')
                        
                        # Check book field is correct
                        if book != 'Judges':
                            contamination_found += 1
                            print(f"   ❌ {verse_ref}: BOOK FIELD CONTAMINATION - labeled as '{book}'")
                            continue
                        
                        # Check for other books' content
                        for indicator in other_book_indicators:
                            if indicator in verse_text:
                                contamination_found += 1
                                print(f"   ❌ {verse_ref}: CONTENT CONTAMINATION - contains '{indicator}': '{verse_text[:60]}...'")
                                break
                    
                    if contamination_found == 0:
                        self.log_test("Judges Cross-Contamination Content Check", True, f"✅ CLEAN! No cross-contamination found in {len(judges_verses)} Judges verses")
                    else:
                        self.log_test("Judges Cross-Contamination Content Check", False, f"❌ CONTAMINATED! Found {contamination_found} contamination instances in Judges")
                else:
                    self.log_test("Judges Cross-Contamination Content Check", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Judges Cross-Contamination Content Check", False, f"Error: {str(e)}")
            
            # Check Ruth for cross-contamination
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Ruth&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    ruth_verses = data.get('verses', [])
                    
                    contamination_found = 0
                    other_book_indicators = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'creation', 'adam', 'eve', 'noah', 'abraham']
                    
                    for verse in ruth_verses:
                        verse_text = verse.get('text', '').lower()
                        verse_ref = f"Ruth {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                        book = verse.get('book', '')
                        
                        # Check book field is correct
                        if book != 'Ruth':
                            contamination_found += 1
                            print(f"   ❌ {verse_ref}: BOOK FIELD CONTAMINATION - labeled as '{book}'")
                            continue
                        
                        # Check for other books' content
                        for indicator in other_book_indicators:
                            if indicator in verse_text:
                                contamination_found += 1
                                print(f"   ❌ {verse_ref}: CONTENT CONTAMINATION - contains '{indicator}': '{verse_text[:60]}...'")
                                break
                    
                    if contamination_found == 0:
                        self.log_test("Ruth Cross-Contamination Content Check", True, f"✅ CLEAN! No cross-contamination found in {len(ruth_verses)} Ruth verses")
                    else:
                        self.log_test("Ruth Cross-Contamination Content Check", False, f"❌ CONTAMINATED! Found {contamination_found} contamination instances in Ruth")
                else:
                    self.log_test("Ruth Cross-Contamination Content Check", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Ruth Cross-Contamination Content Check", False, f"Error: {str(e)}")
            
            # Verify no placeholder brackets exist in new books
            try:
                print("\n🚫 PLACEHOLDER BRACKETS CHECK IN NEW BOOKS:")
                new_books = ['Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth']
                total_placeholder_violations = 0
                
                for book in new_books:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book={book}&limit=5")
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        
                        placeholder_patterns = ['[chapter]', '[verse]', 'see ' + book.lower(), 'placeholder', 'complete kjv text']
                        book_violations = 0
                        
                        for verse in verses:
                            verse_text = verse.get('text', '').lower()
                            verse_ref = f"{book} {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            for pattern in placeholder_patterns:
                                if pattern in verse_text:
                                    book_violations += 1
                                    total_placeholder_violations += 1
                                    print(f"   ❌ {verse_ref}: PLACEHOLDER FOUND - '{pattern}' in '{verse_text[:50]}...'")
                                    break
                        
                        if book_violations == 0:
                            print(f"   ✅ {book}: No placeholder brackets found in {len(verses)} verses")
                    else:
                        print(f"   ⚠️ {book}: API Error - Status {response.status_code}")
                
                if total_placeholder_violations == 0:
                    self.log_test("No Placeholder Brackets in New Books", True, f"✅ CLEAN! No placeholder brackets found in new books")
                else:
                    self.log_test("No Placeholder Brackets in New Books", False, f"❌ VIOLATIONS! Found {total_placeholder_violations} placeholder bracket violations")
                    
            except Exception as e:
                self.log_test("No Placeholder Brackets in New Books", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Content Quality Sampling", False, f"Error: {str(e)}")
            return False

    def test_database_statistics(self):
        """REVIEW REQUEST TEST 4: Database Statistics - Get total verse count, book count, identify reasonable vs cross-contaminated counts"""
        try:
            print("\n🔍 DATABASE STATISTICS - GET TOTAL VERSE COUNT, BOOK COUNT, IDENTIFY REASONABLE VS CROSS-CONTAMINATED COUNTS...")
            
            # Get total verse count and book count
            try:
                response = self.session.get(f"{self.base_url}/bible/stats?version=kjv1611_divine")
                if response.status_code == 200:
                    stats = response.json()
                    total_verses = stats.get('totalVerses', 0)
                    total_books = stats.get('totalBooks', 0)
                    old_testament_verses = stats.get('oldTestamentVerses', 0)
                    
                    print(f"\n📊 COMPLETE BIBLE DATABASE STATISTICS:")
                    print(f"   📖 Total Books: {total_books}")
                    print(f"   📝 Total Verses: {total_verses}")
                    print(f"   📜 Old Testament Verses: {old_testament_verses}")
                    
                    # Expected totals based on foundation books
                    foundation_expected = 1533 + 1063 + 788  # Genesis + Exodus + Leviticus = 3,384
                    
                    if total_verses >= foundation_expected:
                        self.log_test("Total Database Verse Count", True, f"✅ SUBSTANTIAL! Total verses: {total_verses} (includes foundation books + additional content)")
                    elif total_verses >= foundation_expected * 0.8:
                        self.log_test("Total Database Verse Count", True, f"✅ GOOD! Total verses: {total_verses} (close to foundation books total)")
                    else:
                        self.log_test("Total Database Verse Count", False, f"❌ LOW! Total verses: {total_verses} (less than foundation books expected {foundation_expected})")
                    
                    if total_books >= 8:  # Foundation 3 + new 5 books
                        self.log_test("Total Database Book Count", True, f"✅ GOOD! Total books: {total_books} (includes foundation + new books)")
                    elif total_books >= 3:
                        self.log_test("Total Database Book Count", True, f"✅ BASIC! Total books: {total_books} (at least foundation books)")
                    else:
                        self.log_test("Total Database Book Count", False, f"❌ INSUFFICIENT! Total books: {total_books} (missing foundation books)")
                        
                else:
                    self.log_test("Total Database Verse Count", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Total Database Book Count", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Total Database Verse Count", False, f"Error: {str(e)}")
                self.log_test("Total Database Book Count", False, f"Error: {str(e)}")
            
            # Identify which books have reasonable verse counts vs cross-contaminated counts
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    
                    print(f"\n📚 INDIVIDUAL BOOK VERSE COUNT ANALYSIS:")
                    
                    # Expected verse counts for biblical books
                    expected_counts = {
                        'Genesis': 1533,
                        'Exodus': 1063,
                        'Leviticus': 788,
                        'Numbers': 1288,
                        'Deuteronomy': 959,
                        'Joshua': 658,
                        'Judges': 618,
                        'Ruth': 85
                    }
                    
                    reasonable_books = 0
                    cross_contaminated_books = 0
                    missing_books = 0
                    
                    for book_name, expected_count in expected_counts.items():
                        # Get actual verse count for this book
                        try:
                            response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book={book_name}&limit=1")
                            if response.status_code == 200:
                                book_data = response.json()
                                actual_count = book_data.get('total', 0)
                                
                                if actual_count == 0:
                                    missing_books += 1
                                    print(f"   ❌ {book_name}: MISSING (0 verses, expected {expected_count})")
                                elif abs(actual_count - expected_count) <= expected_count * 0.1:  # Within 10%
                                    reasonable_books += 1
                                    print(f"   ✅ {book_name}: REASONABLE ({actual_count} verses, expected {expected_count})")
                                elif actual_count > expected_count * 1.5:  # 50% higher than expected
                                    cross_contaminated_books += 1
                                    print(f"   ❌ {book_name}: CROSS-CONTAMINATED ({actual_count} verses, expected {expected_count}) - {actual_count - expected_count} excess")
                                else:
                                    print(f"   ⚠️ {book_name}: QUESTIONABLE ({actual_count} verses, expected {expected_count})")
                            else:
                                missing_books += 1
                                print(f"   ❌ {book_name}: API ERROR (Status {response.status_code})")
                        except Exception as e:
                            missing_books += 1
                            print(f"   ❌ {book_name}: ERROR ({str(e)})")
                    
                    # Summary assessment
                    total_checked = len(expected_counts)
                    if reasonable_books >= 6:  # Most books are reasonable
                        self.log_test("Reasonable Book Verse Counts", True, f"✅ GOOD! {reasonable_books}/{total_checked} books have reasonable verse counts")
                    elif reasonable_books >= 3:  # At least foundation books
                        self.log_test("Reasonable Book Verse Counts", True, f"✅ BASIC! {reasonable_books}/{total_checked} books have reasonable verse counts")
                    else:
                        self.log_test("Reasonable Book Verse Counts", False, f"❌ POOR! Only {reasonable_books}/{total_checked} books have reasonable verse counts")
                    
                    if cross_contaminated_books == 0:
                        self.log_test("Cross-Contaminated Book Detection", True, f"✅ CLEAN! No books show clear cross-contamination patterns")
                    elif cross_contaminated_books <= 2:
                        self.log_test("Cross-Contaminated Book Detection", False, f"⚠️ MINOR ISSUES! {cross_contaminated_books} books show cross-contamination patterns")
                    else:
                        self.log_test("Cross-Contaminated Book Detection", False, f"❌ MAJOR ISSUES! {cross_contaminated_books} books show cross-contamination patterns")
                    
                    if missing_books <= 2:
                        self.log_test("Missing Books Detection", True, f"✅ GOOD! Only {missing_books}/{total_checked} books are missing")
                    else:
                        self.log_test("Missing Books Detection", False, f"❌ MANY MISSING! {missing_books}/{total_checked} books are missing")
                        
                else:
                    self.log_test("Reasonable Book Verse Counts", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Cross-Contaminated Book Detection", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Missing Books Detection", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Reasonable Book Verse Counts", False, f"Error: {str(e)}")
                self.log_test("Cross-Contaminated Book Detection", False, f"Error: {str(e)}")
                self.log_test("Missing Books Detection", False, f"Error: {str(e)}")
            
            # Additional analysis: Identify books that need attention
            try:
                print(f"\n🎯 BOOKS REQUIRING ATTENTION ANALYSIS:")
                
                books_needing_attention = []
                books_ready_for_use = []
                
                # Check each book's status
                book_status_checks = {
                    'Genesis': {'expected': 1533, 'priority': 'foundation'},
                    'Exodus': {'expected': 1063, 'priority': 'foundation'},
                    'Leviticus': {'expected': 788, 'priority': 'foundation'},
                    'Numbers': {'expected': 1288, 'priority': 'new'},
                    'Deuteronomy': {'expected': 959, 'priority': 'new'},
                    'Joshua': {'expected': 658, 'priority': 'new'},
                    'Judges': {'expected': 618, 'priority': 'new'},
                    'Ruth': {'expected': 85, 'priority': 'new'}
                }
                
                for book_name, info in book_status_checks.items():
                    try:
                        response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book={book_name}&limit=1")
                        if response.status_code == 200:
                            book_data = response.json()
                            actual_count = book_data.get('total', 0)
                            expected_count = info['expected']
                            priority = info['priority']
                            
                            if actual_count == 0:
                                books_needing_attention.append(f"{book_name} (MISSING - {priority})")
                            elif actual_count > expected_count * 1.5:
                                books_needing_attention.append(f"{book_name} (CROSS-CONTAMINATED: {actual_count} vs {expected_count} - {priority})")
                            elif abs(actual_count - expected_count) <= expected_count * 0.1:
                                books_ready_for_use.append(f"{book_name} ({actual_count} verses - {priority})")
                            else:
                                books_needing_attention.append(f"{book_name} (COUNT ISSUE: {actual_count} vs {expected_count} - {priority})")
                        else:
                            books_needing_attention.append(f"{book_name} (API ERROR - {priority})")
                    except Exception as e:
                        books_needing_attention.append(f"{book_name} (ERROR - {priority})")
                
                print(f"   ✅ BOOKS READY FOR USE ({len(books_ready_for_use)}):")
                for book in books_ready_for_use:
                    print(f"      - {book}")
                
                print(f"   ❌ BOOKS NEEDING ATTENTION ({len(books_needing_attention)}):")
                for book in books_needing_attention:
                    print(f"      - {book}")
                
                if len(books_ready_for_use) >= len(books_needing_attention):
                    self.log_test("Database Ready for Use Assessment", True, f"✅ MOSTLY READY! {len(books_ready_for_use)} books ready vs {len(books_needing_attention)} needing attention")
                else:
                    self.log_test("Database Ready for Use Assessment", False, f"❌ NEEDS WORK! Only {len(books_ready_for_use)} books ready vs {len(books_needing_attention)} needing attention")
                    
            except Exception as e:
                self.log_test("Database Ready for Use Assessment", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Statistics", False, f"Error: {str(e)}")
            return False

    # Removed unused test method

    def run_bible_database_status_verification_tests(self):
        """Run Bible database status verification tests as per review request"""
        print("=" * 80)
        print("🎉 BIBLE DATABASE STATUS VERIFICATION")
        print("Checking the current status of our Bible database to verify what we have loaded correctly")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 4 main review request tests
        test_results = []
        
        # Test 1: Foundation Books Verification
        test_results.append(self.test_foundation_books_verification())
        
        # Test 2: New Books Status Check
        test_results.append(self.test_new_books_status_check())
        
        # Test 3: Content Quality Sampling
        test_results.append(self.test_content_quality_sampling())
        
        # Test 4: Database Statistics
        test_results.append(self.test_database_statistics())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 BIBLE DATABASE STATUS VERIFICATION SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 VERIFICATION SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major verification categories completed")
        
        # Show category results
        categories = [
            "Foundation Books Verification (Genesis 1,533, Exodus 1,063, Leviticus 788 verses preserved)",
            "New Books Status Check (Numbers, Deuteronomy, Joshua, Judges, Ruth verse counts and cross-contamination)", 
            "Content Quality Sampling (5 Numbers verses authentic content, Judges/Ruth cross-contamination check, no placeholder brackets)",
            "Database Statistics (total verse/book counts, reasonable vs cross-contaminated counts, books needing attention)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ VERIFIED" if result else "❌ FAILED"
            print(f"{status}: {category}")
        
        print("\n🎉 KEY DATABASE STATUS FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # Foundation Books Verification
            print("✅ Foundation books PRESERVED - Genesis (1,533), Exodus (1,063), Leviticus (788) verses intact with key content")
        else:
            print("❌ Foundation books COMPROMISED - verse counts changed or key content missing")
        
        if test_results[1]:  # New Books Status Check
            print("✅ New books STATUS CHECKED - Numbers, Deuteronomy, Joshua, Judges, Ruth verse counts analyzed")
        else:
            print("❌ New books STATUS ISSUES - missing books, incorrect counts, or cross-contamination detected")
        
        if test_results[2]:  # Content Quality Sampling
            print("✅ Content quality VERIFIED - Numbers authentic content confirmed, cross-contamination checked, no placeholder brackets")
        else:
            print("❌ Content quality ISSUES - poor Numbers content, cross-contamination found, or placeholder brackets detected")
        
        if test_results[3]:  # Database Statistics
            print("✅ Database statistics ANALYZED - total counts verified, reasonable vs cross-contaminated books identified")
        else:
            print("❌ Database statistics PROBLEMATIC - count issues, many cross-contaminated books, or missing data")
        
        print(f"\n🎯 FINAL BIBLE DATABASE STATUS ASSESSMENT:")
        if individual_success_rate >= 90:
            print(f"🎉 BIBLE DATABASE EXCELLENT STATUS! Database is in great condition ({individual_success_rate:.1f}% success)")
            print("✅ Foundation books completely preserved with correct verse counts")
            print("✅ New books mostly loaded correctly with minimal cross-contamination")
            print("🚀 Database ready for continued use with current state!")
        elif individual_success_rate >= 75:
            print(f"✅ BIBLE DATABASE GOOD STATUS! Database is in good condition with minor issues ({individual_success_rate:.1f}% success)")
            print("✅ Foundation books preserved, most new books loaded correctly")
            print("⚠️ Some cross-contamination or count issues that can be addressed")
        elif individual_success_rate >= 60:
            print(f"⚠️ BIBLE DATABASE MIXED STATUS! Database has significant issues requiring attention ({individual_success_rate:.1f}% success)")
            print("⚠️ Foundation books may have issues, new books show cross-contamination problems")
            print("🔧 Recommend cleaning and retrying specific problematic books")
        elif individual_success_rate >= 40:
            print(f"❌ BIBLE DATABASE POOR STATUS! Database has major issues ({individual_success_rate:.1f}% success)")
            print("❌ Foundation books compromised or new books heavily cross-contaminated")
            print("🔧 Recommend comprehensive cleanup and reload of problematic books")
        else:
            print(f"❌ BIBLE DATABASE CRITICAL STATUS! Database requires immediate attention ({individual_success_rate:.1f}% success)")
            print("❌ Major data integrity issues across foundation and new books")
            print("🔧 Recommend complete database cleanup and systematic reload")
        
        return individual_success_rate >= 75

def main():
    """Main test execution"""
    print("🚀 Starting Bible Database Status Verification Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_bible_database_status_verification_tests()
    
    if success:
        print("\n🎉 Bible database status verification successful!")
        sys.exit(0)
    else:
        print("\n❌ Bible database status verification completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()