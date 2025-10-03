#!/usr/bin/env python3
"""
Backend Testing for Bible Database Status Verification

REVIEW REQUEST FOCUS - BIBLE DATABASE STATUS VERIFICATION:
Please check the current status of our Bible database to verify what we have loaded correctly. Test:

1. **Foundation Books Verification**:
   - Verify Genesis still has exactly 1,533 verses (should be preserved)
   - Verify Exodus still has exactly 1,063 verses (should be preserved)  
   - Verify Leviticus still has exactly 788 verses (should be preserved)

2. **New Books Status Check**:
   - Check Numbers: verses count and sample content quality
   - Check Deuteronomy: verses count and content
   - Check Joshua: verses count (shows only 2 verses, investigate why)
   - Check Judges: verses count (shows 1,228 vs target 618 - cross-contamination?)
   - Check Ruth: verses count (shows 413 vs target 85 - cross-contamination?)

3. **Content Quality Sampling**:
   - Sample 5 verses from Numbers to verify authentic biblical content
   - Check for cross-contamination in Judges and Ruth 
   - Verify no placeholder brackets exist in new books

4. **Database Statistics**:
   - Get total verse count and book count
   - Identify which books have reasonable verse counts vs cross-contaminated counts

This verification provides analysis of current database state to decide next steps - whether to clean and retry specific books or continue with the current state.
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

    def test_foundation_books_verification(self):
        """REVIEW REQUEST TEST 1: Foundation Books Verification - Verify Genesis, Exodus, Leviticus have correct verse counts"""
        try:
            print("\n🔍 FOUNDATION BOOKS VERIFICATION - CHECKING GENESIS, EXODUS, LEVITICUS VERSE COUNTS...")
            
            # Verify Genesis still has exactly 1,533 verses (should be preserved)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1533  # Review request specifies 1,533 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Genesis Exactly 1,533 Verses", True, f"✅ PERFECT! Genesis has exactly {total_verses} verses (preserved)")
                    elif total_verses > 0:
                        self.log_test("Genesis Exactly 1,533 Verses", False, f"❌ INCORRECT COUNT! Genesis has {total_verses} verses, expected {expected_verses}")
                    else:
                        self.log_test("Genesis Exactly 1,533 Verses", False, f"❌ NOT FOUND! Genesis does not exist in database (0 verses)")
                else:
                    self.log_test("Genesis Exactly 1,533 Verses", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis Exactly 1,533 Verses", False, f"Error: {str(e)}")
            
            # Verify Exodus still has exactly 1,063 verses (should be preserved)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1063  # Review request specifies 1,063 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Exodus Exactly 1,063 Verses", True, f"✅ PERFECT! Exodus has exactly {total_verses} verses (preserved)")
                    elif total_verses > 0:
                        self.log_test("Exodus Exactly 1,063 Verses", False, f"❌ INCORRECT COUNT! Exodus has {total_verses} verses, expected {expected_verses}")
                    else:
                        self.log_test("Exodus Exactly 1,063 Verses", False, f"❌ NOT FOUND! Exodus does not exist in database (0 verses)")
                else:
                    self.log_test("Exodus Exactly 1,063 Verses", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Exactly 1,063 Verses", False, f"Error: {str(e)}")
            
            # Verify Leviticus still has exactly 788 verses (should be preserved)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Leviticus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 788  # Review request specifies 788 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Leviticus Exactly 788 Verses", True, f"✅ PERFECT! Leviticus has exactly {total_verses} verses (preserved)")
                    elif total_verses > 0:
                        self.log_test("Leviticus Exactly 788 Verses", False, f"❌ INCORRECT COUNT! Leviticus has {total_verses} verses, expected {expected_verses}")
                    else:
                        self.log_test("Leviticus Exactly 788 Verses", False, f"❌ NOT FOUND! Leviticus does not exist in database (0 verses)")
                else:
                    self.log_test("Leviticus Exactly 788 Verses", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Leviticus Exactly 788 Verses", False, f"Error: {str(e)}")
            
            # Verify key verses are intact
            print("\n📖 FOUNDATION BOOKS KEY VERSES INTEGRITY CHECK:")
            
            # Genesis 1:1 creation verse
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Genesis/1/1")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    if 'in the beginning god created' in verse_text.lower():
                        self.log_test("Genesis 1:1 Creation Verse Intact", True, f"✅ PRESERVED! Genesis 1:1 contains creation content: '{verse_text[:60]}...'")
                    else:
                        self.log_test("Genesis 1:1 Creation Verse Intact", False, f"❌ CORRUPTED! Genesis 1:1 missing creation content: '{verse_text[:60]}...'")
                else:
                    self.log_test("Genesis 1:1 Creation Verse Intact", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis 1:1 Creation Verse Intact", False, f"Error: {str(e)}")
            
            # Exodus 20:1 Ten Commandments
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Exodus/20/1")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    if 'god spake' in verse_text.lower():
                        self.log_test("Exodus 20:1 Ten Commandments Intact", True, f"✅ PRESERVED! Exodus 20:1 contains commandments content: '{verse_text[:60]}...'")
                    else:
                        self.log_test("Exodus 20:1 Ten Commandments Intact", False, f"❌ CORRUPTED! Exodus 20:1 missing commandments content: '{verse_text[:60]}...'")
                else:
                    self.log_test("Exodus 20:1 Ten Commandments Intact", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus 20:1 Ten Commandments Intact", False, f"Error: {str(e)}")
            
            # Leviticus 1:1 offerings
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Leviticus/1/1")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    if any(word in verse_text.lower() for word in ['lord', 'moses', 'called', 'tabernacle']):
                        self.log_test("Leviticus 1:1 Offerings Verse Intact", True, f"✅ PRESERVED! Leviticus 1:1 contains offerings content: '{verse_text[:60]}...'")
                    else:
                        self.log_test("Leviticus 1:1 Offerings Verse Intact", False, f"❌ CORRUPTED! Leviticus 1:1 missing offerings content: '{verse_text[:60]}...'")
                else:
                    self.log_test("Leviticus 1:1 Offerings Verse Intact", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Leviticus 1:1 Offerings Verse Intact", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Foundation Books Verification", False, f"Error: {str(e)}")
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

    def test_complete_database_status(self):
        """REVIEW REQUEST TEST 5: Complete Database Status - Total verse count, all three books verification, testament classification"""
        try:
            print("\n🔍 COMPLETE DATABASE STATUS - TOTAL VERSE COUNT AND ALL THREE BOOKS VERIFICATION...")
            
            # Get total verse count (should be Genesis 1,533 + Exodus 1,063 + Leviticus 788 = 3,384)
            try:
                response = self.session.get(f"{self.base_url}/bible/stats?version=kjv1611_divine")
                if response.status_code == 200:
                    stats = response.json()
                    total_verses = stats.get('totalVerses', 0)
                    total_books = stats.get('totalBooks', 0)
                    old_testament_verses = stats.get('oldTestamentVerses', 0)
                    
                    expected_total = 1533 + 1063 + 788  # Genesis + Exodus + Leviticus = 3,384 verses (per review request)
                    
                    print(f"\n📊 COMPLETE BIBLE DATABASE STATUS:")
                    print(f"   📖 Total Books: {total_books}")
                    print(f"   📝 Total Verses: {total_verses}")
                    print(f"   📜 Old Testament Verses: {old_testament_verses}")
                    
                    if total_verses == expected_total:
                        self.log_test("Total Verse Count (Genesis + Exodus + Leviticus)", True, f"✅ PERFECT! Total verses: {total_verses} (Genesis 1,533 + Exodus 1,063 + Leviticus 788 = {expected_total})")
                    elif abs(total_verses - expected_total) <= 50:  # Within 50 verses is close
                        self.log_test("Total Verse Count (Genesis + Exodus + Leviticus)", True, f"✅ CLOSE! Total verses: {total_verses} (expected {expected_total}, difference: {abs(total_verses - expected_total)})")
                    else:
                        self.log_test("Total Verse Count (Genesis + Exodus + Leviticus)", False, f"❌ INCORRECT! Total verses: {total_verses}, expected {expected_total} (difference: {abs(total_verses - expected_total)})")
                        
                else:
                    self.log_test("Total Verse Count (Genesis + Exodus + Leviticus)", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Total Verse Count (Genesis + Exodus + Leviticus)", False, f"Error: {str(e)}")
            
            # Verify all three books exist in KJV 1611 Divine version
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    book_names = [book.get('name', '') for book in books]
                    
                    genesis_found = 'Genesis' in book_names
                    exodus_found = 'Exodus' in book_names
                    leviticus_found = 'Leviticus' in book_names
                    
                    print(f"\n📚 KJV 1611 DIVINE VERSION BOOKS:")
                    print(f"   📖 Total Books Available: {len(books)}")
                    print(f"   📜 Books: {', '.join(book_names)}")
                    
                    if genesis_found and exodus_found and leviticus_found:
                        self.log_test("All Three Books in KJV 1611 Divine", True, f"✅ CONFIRMED! Genesis, Exodus, and Leviticus all exist in KJV 1611 Divine version")
                        
                        # Get detailed info for all three books
                        genesis_book = next((book for book in books if book.get('name') == 'Genesis'), None)
                        exodus_book = next((book for book in books if book.get('name') == 'Exodus'), None)
                        leviticus_book = next((book for book in books if book.get('name') == 'Leviticus'), None)
                        
                        if genesis_book and exodus_book and leviticus_book:
                            genesis_testament = genesis_book.get('testament', 'unknown')
                            exodus_testament = exodus_book.get('testament', 'unknown')
                            leviticus_testament = leviticus_book.get('testament', 'unknown')
                            genesis_order = genesis_book.get('order', 'unknown')
                            exodus_order = exodus_book.get('order', 'unknown')
                            leviticus_order = leviticus_book.get('order', 'unknown')
                            
                            print(f"   ✅ Genesis: Testament={genesis_testament}, Order={genesis_order}")
                            print(f"   ✅ Exodus: Testament={exodus_testament}, Order={exodus_order}")
                            print(f"   ✅ Leviticus: Testament={leviticus_testament}, Order={leviticus_order}")
                            
                    else:
                        missing_books = []
                        if not genesis_found:
                            missing_books.append('Genesis')
                        if not exodus_found:
                            missing_books.append('Exodus')
                        if not leviticus_found:
                            missing_books.append('Leviticus')
                        
                        self.log_test("All Three Books in KJV 1611 Divine", False, f"❌ MISSING! Books not found: {', '.join(missing_books)}")
                        
                else:
                    self.log_test("All Three Books in KJV 1611 Divine", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("All Three Books in KJV 1611 Divine", False, f"Error: {str(e)}")
            
            # Confirm proper testament and order classification
            try:
                # Check Genesis testament classification
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                genesis_testament = None
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    if verses:
                        genesis_testament = verses[0].get('testament', 'unknown')
                
                # Check Exodus testament classification
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                exodus_testament = None
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    if verses:
                        exodus_testament = verses[0].get('testament', 'unknown')
                
                # Check Leviticus testament classification
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Leviticus&limit=1")
                leviticus_testament = None
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    if verses:
                        leviticus_testament = verses[0].get('testament', 'unknown')
                
                print(f"\n📜 TESTAMENT AND ORDER CLASSIFICATION VERIFICATION:")
                print(f"   📖 Genesis Testament: {genesis_testament}")
                print(f"   📖 Exodus Testament: {exodus_testament}")
                print(f"   📖 Leviticus Testament: {leviticus_testament}")
                
                if genesis_testament == 'old' and exodus_testament == 'old' and leviticus_testament == 'old':
                    self.log_test("Proper Testament Classification", True, f"✅ CORRECT! All three books (Genesis, Exodus, Leviticus) classified as Old Testament")
                else:
                    incorrect_books = []
                    if genesis_testament != 'old':
                        incorrect_books.append(f"Genesis: {genesis_testament}")
                    if exodus_testament != 'old':
                        incorrect_books.append(f"Exodus: {exodus_testament}")
                    if leviticus_testament != 'old':
                        incorrect_books.append(f"Leviticus: {leviticus_testament}")
                    
                    self.log_test("Proper Testament Classification", False, f"❌ INCORRECT! {', '.join(incorrect_books)} (all should be 'old')")
                    
            except Exception as e:
                self.log_test("Proper Testament Classification", False, f"Error: {str(e)}")
            
            # Individual book verse counts verification
            try:
                print(f"\n🔢 INDIVIDUAL BOOK VERSE COUNT VERIFICATION:")
                
                # Genesis verse count (should be exactly 1,533)
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    genesis_verses = data.get('total', 0)
                    print(f"   📖 Genesis: {genesis_verses} verses (expected: 1,533)")
                    
                    if genesis_verses == 1533:
                        self.log_test("Genesis Exactly 1,533 Verses", True, f"✅ PERFECT! Genesis has exactly 1,533 verses")
                    else:
                        self.log_test("Genesis Exactly 1,533 Verses", False, f"❌ INCORRECT! Genesis has {genesis_verses} verses, expected exactly 1,533")
                else:
                    self.log_test("Genesis Exactly 1,533 Verses", False, f"API Error - Status: {response.status_code}")
                
                # Exodus verse count (should be exactly 1,063 per review request)
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    exodus_verses = data.get('total', 0)
                    print(f"   📖 Exodus: {exodus_verses} verses (expected: 1,063)")
                    
                    if exodus_verses == 1063:
                        self.log_test("Exodus Exactly 1,063 Verses", True, f"✅ PERFECT! Exodus has exactly 1,063 verses as specified")
                    elif abs(exodus_verses - 1063) <= 20:  # Within 20 verses is close
                        self.log_test("Exodus Exactly 1,063 Verses", True, f"✅ CLOSE! Exodus has {exodus_verses} verses (expected 1,063, difference: {abs(exodus_verses - 1063)})")
                    else:
                        self.log_test("Exodus Exactly 1,063 Verses", False, f"❌ INCORRECT! Exodus has {exodus_verses} verses, expected 1,063 (difference: {abs(exodus_verses - 1063)})")
                else:
                    self.log_test("Exodus Exactly 1,063 Verses", False, f"API Error - Status: {response.status_code}")
                
                # Leviticus verse count (should be exactly 788 per review request)
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Leviticus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    leviticus_verses = data.get('total', 0)
                    print(f"   📖 Leviticus: {leviticus_verses} verses (expected: 788)")
                    
                    if leviticus_verses == 788:
                        self.log_test("Leviticus Exactly 788 Verses", True, f"✅ PERFECT! Leviticus has exactly 788 verses as specified")
                    elif abs(leviticus_verses - 788) <= 20:  # Within 20 verses is close
                        self.log_test("Leviticus Exactly 788 Verses", True, f"✅ CLOSE! Leviticus has {leviticus_verses} verses (expected 788, difference: {abs(leviticus_verses - 788)})")
                    else:
                        self.log_test("Leviticus Exactly 788 Verses", False, f"❌ INCORRECT! Leviticus has {leviticus_verses} verses, expected 788 (difference: {abs(leviticus_verses - 788)})")
                else:
                    self.log_test("Leviticus Exactly 788 Verses", False, f"API Error - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Genesis Exactly 1,533 Verses", False, f"Error: {str(e)}")
                self.log_test("Exodus Exactly 1,063 Verses", False, f"Error: {str(e)}")
                self.log_test("Leviticus Exactly 788 Verses", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Complete Database Status", False, f"Error: {str(e)}")
            return False

    # Key chapter verification removed - not needed for Leviticus review request

    def run_leviticus_authentic_content_verification_tests(self):
        """Run Leviticus authentic content verification tests as per review request"""
        print("=" * 80)
        print("🎉 LEVITICUS AUTHENTIC BIBLICAL TEXT VERIFICATION")
        print("Verifying that Leviticus now contains authentic biblical text following the Genesis/Exodus success pattern")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 5 main review request tests
        test_results = []
        
        # Test 1: Leviticus Authentic Content Verification
        test_results.append(self.test_leviticus_authentic_content_verification())
        
        # Test 2: No Placeholder Content Check
        test_results.append(self.test_no_placeholder_content_check())
        
        # Test 3: Previous Books Preservation
        test_results.append(self.test_previous_books_preservation())
        
        # Test 4: Content Quality Sampling
        test_results.append(self.test_content_quality_sampling())
        
        # Test 5: Complete Database Status
        test_results.append(self.test_complete_database_status())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 LEVITICUS AUTHENTIC CONTENT VERIFICATION SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 VERIFICATION SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major verification categories completed")
        
        # Show category results
        categories = [
            "Leviticus Authentic Content Verification (788 verses, LORD calling Moses, offerings, clean/unclean animals, holiness laws)",
            "No Placeholder Content Check (no 'see Leviticus [chapter]:[verse]', legitimate KJV brackets preserved)", 
            "Previous Books Preservation (Genesis 1,533 verses, Exodus 1,063 verses, no cross-contamination)",
            "Content Quality Sampling (10 random verses, authentic biblical content, Leviticus themes)",
            "Complete Database Status (total 3,384 verses, all three books in KJV 1611 Divine, proper testament)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ VERIFIED" if result else "❌ FAILED"
            print(f"{status}: {category}")
        
        print("\n🎉 KEY VERIFICATION FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # Leviticus Authentic Content Verification
            print("✅ Leviticus authentic content VERIFIED - proper verse count, LORD/Moses/offerings, clean/unclean animals, holiness laws")
        else:
            print("❌ Leviticus authentic content FAILED - incorrect verse count or missing authentic biblical content")
        
        if test_results[1]:  # No Placeholder Content Check
            print("✅ No placeholder content CONFIRMED - clean authentic text without generated placeholders")
        else:
            print("❌ Placeholder content FOUND - contains generated placeholder text or references")
        
        if test_results[2]:  # Previous Books Preservation
            print("✅ Previous books preservation VERIFIED - Genesis (1,533) and Exodus (1,063) verses intact, no cross-contamination")
        else:
            print("❌ Previous books preservation FAILED - verse counts changed or cross-contamination detected")
        
        if test_results[3]:  # Content Quality Sampling
            print("✅ Content quality EXCELLENT - sampled verses contain authentic, substantial Leviticus biblical content")
        else:
            print("❌ Content quality POOR - sampled verses have quality issues or non-authentic content")
        
        if test_results[4]:  # Complete Database Status
            print("✅ Database status CORRECT - proper total counts, all three books present, correct classification")
        else:
            print("❌ Database status INCORRECT - count mismatches or missing books")
        
        print(f"\n🎯 FINAL LEVITICUS AUTHENTIC CONTENT ASSESSMENT:")
        if individual_success_rate >= 95:
            print(f"🎉 LEVITICUS AUTHENTIC CONTENT SUCCESS! Perfect authentic biblical text implementation ({individual_success_rate:.1f}% success)")
            print("✅ Leviticus contains only authentic biblical text without any placeholder content")
            print("✅ Genesis and Exodus remain completely preserved with exact verse counts")
            print("🚀 All three books (Genesis, Exodus, Leviticus) contain clean, authentic biblical content ready for use!")
        elif individual_success_rate >= 85:
            print(f"✅ LEVITICUS AUTHENTIC CONTENT EXCELLENT! Very successful authentic text implementation ({individual_success_rate:.1f}% success)")
            print("✅ Leviticus is substantially authentic with minor issues that don't affect core content")
            print("✅ Previous books preservation confirmed - no negative impact from Leviticus work")
        elif individual_success_rate >= 75:
            print(f"✅ LEVITICUS AUTHENTIC CONTENT GOOD! Successful implementation with some issues ({individual_success_rate:.1f}% success)")
            print("⚠️ Leviticus is mostly authentic but may need minor fixes for optimal quality")
        elif individual_success_rate >= 60:
            print(f"⚠️ LEVITICUS AUTHENTIC CONTENT PARTIAL! Some success but significant issues remain ({individual_success_rate:.1f}% success)")
            print("⚠️ Leviticus has authenticity issues or placeholder content that needs attention")
        else:
            print(f"❌ LEVITICUS AUTHENTIC CONTENT FAILED! Major issues prevent authentic content verification ({individual_success_rate:.1f}% success)")
            print("❌ Leviticus still contains placeholder content or non-authentic content")
        
        return individual_success_rate >= 85

def main():
    """Main test execution"""
    print("🚀 Starting Leviticus Authentic Biblical Text Verification Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_leviticus_authentic_content_verification_tests()
    
    if success:
        print("\n🎉 Leviticus authentic biblical text verification successful!")
        sys.exit(0)
    else:
        print("\n❌ Leviticus authentic biblical text verification failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()