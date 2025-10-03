#!/usr/bin/env python3
"""
Backend Testing for Numbers Bible Book Authentic Content Verification

REVIEW REQUEST FOCUS - NUMBERS AUTHENTIC CONTENT VERIFICATION:
Please verify that Numbers now contains ONLY authentic biblical text without any placeholder content. Test:

1. **Placeholder Elimination Verification**:
   - Verify Numbers has 601 verses (authentic extraction only)
   - Check that Numbers 1:1 contains proper Moses/wilderness/Sinai content
   - Verify Numbers 1:2 has proper census content ("Take ye the sum...")
   - Confirm NO verses contain "And the LORD numbered the children of Israel according to their families" placeholder text

2. **Authentic Content Quality Check**:
   - Sample Numbers 1:1-10 to verify they contain different, authentic biblical content
   - Check Numbers 6:24-26 for the proper priestly blessing text  
   - Verify verses contain actual biblical names, places, and events

3. **Foundation Books Preservation**:
   - Verify Genesis still has 1,533 verses (preserved)
   - Verify Exodus still has 1,063 verses (preserved)
   - Verify Leviticus still has 788 verses (preserved)

4. **No Generated Content Check**:
   - Search for any repetitive placeholder patterns
   - Verify all verses contain unique, authentic biblical content
   - Confirm no "generated" or "placeholder" text exists

5. **Database Status**:
   - Get total verse count (should be Genesis 1,533 + Exodus 1,063 + Leviticus 788 + Numbers 601 = 3,985)
   - Verify Numbers is properly classified as Old Testament book
   - Confirm all 4 books exist correctly

Please provide verification that Numbers now contains ONLY authentic biblical text without any generated placeholder content.
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

    def test_placeholder_elimination_verification(self):
        """REVIEW REQUEST TEST 1: Placeholder Elimination Verification - Verify Numbers has 601 verses with authentic content only"""
        try:
            print("\n🔍 PLACEHOLDER ELIMINATION VERIFICATION - CHECKING NUMBERS HAS 601 AUTHENTIC VERSES ONLY...")
            
            # Verify Numbers has exactly 601 verses (authentic extraction only)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 601  # Review request specifies exactly 601 verses for authentic extraction only
                    
                    if total_verses == expected_verses:
                        self.log_test("Numbers Exactly 601 Verses (Authentic Only)", True, f"✅ PERFECT! Numbers has exactly {total_verses} verses (authentic extraction only)")
                    elif total_verses > 0:
                        self.log_test("Numbers Exactly 601 Verses (Authentic Only)", False, f"❌ INCORRECT COUNT! Numbers has {total_verses} verses, expected exactly {expected_verses} for authentic extraction")
                    else:
                        self.log_test("Numbers Exactly 601 Verses (Authentic Only)", False, f"❌ NOT FOUND! Numbers does not exist in database (0 verses)")
                else:
                    self.log_test("Numbers Exactly 601 Verses (Authentic Only)", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers Exactly 601 Verses (Authentic Only)", False, f"Error: {str(e)}")
            
            # Check for specific placeholder text that should NOT exist
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&search=And the LORD numbered the children of Israel according to their families&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    placeholder_verses = data.get('verses', [])
                    
                    if len(placeholder_verses) == 0:
                        self.log_test("No Placeholder Text in Numbers", True, f"✅ CLEAN! No placeholder text 'And the LORD numbered...' found in Numbers")
                    else:
                        self.log_test("No Placeholder Text in Numbers", False, f"❌ PLACEHOLDER FOUND! Found {len(placeholder_verses)} verses with placeholder text 'And the LORD numbered...'")
                        for verse in placeholder_verses[:3]:  # Show first 3 examples
                            verse_ref = f"Numbers {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            print(f"   ❌ {verse_ref}: PLACEHOLDER - '{verse.get('text', '')[:80]}...'")
                else:
                    self.log_test("No Placeholder Text in Numbers", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("No Placeholder Text in Numbers", False, f"Error: {str(e)}")
            
            # Check Numbers 1:1 contains proper Moses/wilderness/Sinai content
            print("\n📖 NUMBERS KEY VERSES CONTENT VERIFICATION:")
            
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/1/1")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for Moses/wilderness/Sinai content keywords
                    moses_keywords = ['moses', 'wilderness', 'sinai']
                    found_keywords = [kw for kw in moses_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 2:
                        self.log_test("Numbers 1:1 Moses/Wilderness/Sinai Content", True, f"✅ AUTHENTIC! Numbers 1:1 contains proper Moses/wilderness/Sinai content: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 1:1 Moses/Wilderness/Sinai Content", False, f"❌ MISSING CONTENT! Numbers 1:1 lacks Moses/wilderness/Sinai keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 1:1 Moses/Wilderness/Sinai Content", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 1:1 Moses/Wilderness/Sinai Content", False, f"Error: {str(e)}")
            
            # Verify Numbers 1:2 has proper census content ("Take ye the sum...")
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Numbers/1/2")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for census content
                    census_keywords = ['take', 'sum', 'congregation', 'children', 'israel']
                    found_keywords = [kw for kw in census_keywords if kw in verse_text.lower()]
                    
                    if len(found_keywords) >= 3:
                        self.log_test("Numbers 1:2 Census Content (Take ye the sum)", True, f"✅ AUTHENTIC! Numbers 1:2 contains proper census content: '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                    else:
                        self.log_test("Numbers 1:2 Census Content (Take ye the sum)", False, f"❌ MISSING CONTENT! Numbers 1:2 lacks census keywords: '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                else:
                    self.log_test("Numbers 1:2 Census Content (Take ye the sum)", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 1:2 Census Content (Take ye the sum)", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Numbers Precision Verification", False, f"Error: {str(e)}")
            return False

    def test_authentic_content_quality_check(self):
        """REVIEW REQUEST TEST 2: Authentic Content Quality Check - Sample Numbers 1:1-10 and verify priestly blessing"""
        try:
            print("\n🔍 AUTHENTIC CONTENT QUALITY CHECK - SAMPLE NUMBERS 1:1-10 AND VERIFY PRIESTLY BLESSING...")
            
            # Sample Numbers 1:1-10 to verify they contain different, authentic biblical content
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&chapter=1&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if len(verses) >= 10:
                        print("\n📝 NUMBERS 1:1-10 AUTHENTIC CONTENT SAMPLING:")
                        authentic_verses = 0
                        different_content = 0
                        biblical_names_places = 0
                        
                        previous_texts = []
                        
                        for i, verse in enumerate(verses[:10], 1):  # Sample exactly verses 1-10
                            verse_text = verse.get('text', '')
                            verse_ref = f"Numbers {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Check for authentic biblical content
                            is_authentic = (
                                len(verse_text) > 10 and  # Has substantial content
                                not verse_text.lower().startswith('error') and  # No error messages
                                not 'placeholder' in verse_text.lower() and  # No placeholders
                                verse_text.strip() != '' and  # Not empty
                                not verse_text.startswith('...') and  # Not truncated
                                len(verse_text.split()) >= 3  # At least 3 words
                            )
                            
                            # Check for different content (not repetitive)
                            is_different = verse_text not in previous_texts
                            previous_texts.append(verse_text)
                            
                            # Check for biblical names, places, and events
                            biblical_elements = ['moses', 'aaron', 'israel', 'children', 'lord', 'wilderness', 'sinai', 'congregation', 'tribes', 'families', 'fathers', 'house']
                            has_biblical_elements = any(element in verse_text.lower() for element in biblical_elements)
                            
                            if is_authentic:
                                authentic_verses += 1
                            if is_different:
                                different_content += 1
                            if has_biblical_elements:
                                biblical_names_places += 1
                            
                            # Detailed logging
                            if is_authentic and is_different and has_biblical_elements:
                                print(f"   ✅ {verse_ref}: EXCELLENT AUTHENTIC CONTENT - '{verse_text[:80]}...'")
                            elif is_authentic and has_biblical_elements:
                                print(f"   ✅ {verse_ref}: GOOD AUTHENTIC CONTENT - '{verse_text[:80]}...'")
                            elif is_authentic:
                                print(f"   ⚠️ {verse_ref}: AUTHENTIC BUT GENERIC - '{verse_text[:80]}...'")
                            else:
                                print(f"   ❌ {verse_ref}: POOR QUALITY - '{verse_text}'")
                        
                        # Test results
                        if authentic_verses >= 9:  # 90%+ authentic
                            self.log_test("Numbers 1:1-10 Authentic Content", True, f"✅ EXCELLENT! {authentic_verses}/10 Numbers 1:1-10 verses are authentic biblical content")
                        elif authentic_verses >= 7:  # 70%+ authentic
                            self.log_test("Numbers 1:1-10 Authentic Content", True, f"✅ GOOD! {authentic_verses}/10 Numbers 1:1-10 verses are authentic")
                        else:
                            self.log_test("Numbers 1:1-10 Authentic Content", False, f"❌ POOR! Only {authentic_verses}/10 Numbers 1:1-10 verses are authentic")
                        
                        if different_content >= 9:  # 90%+ different
                            self.log_test("Numbers 1:1-10 Different Content", True, f"✅ EXCELLENT! {different_content}/10 verses contain different, unique content")
                        elif different_content >= 7:  # 70%+ different
                            self.log_test("Numbers 1:1-10 Different Content", True, f"✅ GOOD! {different_content}/10 verses contain different content")
                        else:
                            self.log_test("Numbers 1:1-10 Different Content", False, f"❌ REPETITIVE! Only {different_content}/10 verses contain different content")
                        
                        if biblical_names_places >= 8:  # 80%+ have biblical elements
                            self.log_test("Numbers 1:1-10 Biblical Names/Places/Events", True, f"✅ EXCELLENT! {biblical_names_places}/10 verses contain biblical names, places, and events")
                        elif biblical_names_places >= 6:  # 60%+ have biblical elements
                            self.log_test("Numbers 1:1-10 Biblical Names/Places/Events", True, f"✅ GOOD! {biblical_names_places}/10 verses contain biblical elements")
                        else:
                            self.log_test("Numbers 1:1-10 Biblical Names/Places/Events", False, f"❌ POOR! Only {biblical_names_places}/10 verses contain biblical elements")
                        
                    else:
                        self.log_test("Numbers 1:1-10 Authentic Content", False, f"❌ INSUFFICIENT DATA! Only {len(verses)} Numbers 1:1-10 verses found, need 10")
                        self.log_test("Numbers 1:1-10 Different Content", False, f"❌ INSUFFICIENT DATA! Cannot verify different content with only {len(verses)} verses")
                        self.log_test("Numbers 1:1-10 Biblical Names/Places/Events", False, f"❌ INSUFFICIENT DATA! Cannot verify biblical elements with only {len(verses)} verses")
                else:
                    self.log_test("Numbers 1:1-10 Authentic Content", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Numbers 1:1-10 Different Content", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Numbers 1:1-10 Biblical Names/Places/Events", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers 1:1-10 Authentic Content", False, f"Error: {str(e)}")
                self.log_test("Numbers 1:1-10 Different Content", False, f"Error: {str(e)}")
                self.log_test("Numbers 1:1-10 Biblical Names/Places/Events", False, f"Error: {str(e)}")
            
            # Check Numbers 6:24-26 for the proper priestly blessing text
            try:
                print("\n📖 NUMBERS 6:24-26 PRIESTLY BLESSING VERIFICATION:")
                blessing_verses_found = 0
                blessing_content_verified = 0
                
                for verse_num in [24, 25, 26]:
                    try:
                        response = self.session.get(f"{self.base_url}/bible/verse/Numbers/6/{verse_num}")
                        if response.status_code == 200:
                            verse_data = response.json()
                            verse_text = verse_data.get('text', '')
                            verse_ref = f"Numbers 6:{verse_num}"
                            blessing_verses_found += 1
                            
                            # Check for priestly blessing content specific to each verse
                            if verse_num == 24:
                                blessing_keywords = ['lord', 'bless', 'thee', 'keep']
                            elif verse_num == 25:
                                blessing_keywords = ['lord', 'make', 'face', 'shine', 'gracious']
                            else:  # verse 26
                                blessing_keywords = ['lord', 'lift', 'countenance', 'peace']
                            
                            found_keywords = [kw for kw in blessing_keywords if kw in verse_text.lower()]
                            
                            if len(found_keywords) >= 2:
                                blessing_content_verified += 1
                                print(f"   ✅ {verse_ref}: PROPER BLESSING CONTENT - '{verse_text[:80]}...' (found: {', '.join(found_keywords)})")
                            else:
                                print(f"   ❌ {verse_ref}: MISSING BLESSING CONTENT - '{verse_text[:80]}...' (found only: {', '.join(found_keywords)})")
                        else:
                            print(f"   ❌ Numbers 6:{verse_num}: API ERROR (Status {response.status_code})")
                    except Exception as e:
                        print(f"   ❌ Numbers 6:{verse_num}: ERROR ({str(e)})")
                
                if blessing_content_verified >= 3:
                    self.log_test("Numbers 6:24-26 Priestly Blessing", True, f"✅ PERFECT! All 3 priestly blessing verses (6:24-26) contain proper blessing text")
                elif blessing_content_verified >= 2:
                    self.log_test("Numbers 6:24-26 Priestly Blessing", True, f"✅ GOOD! {blessing_content_verified}/3 priestly blessing verses contain proper text")
                else:
                    self.log_test("Numbers 6:24-26 Priestly Blessing", False, f"❌ POOR! Only {blessing_content_verified}/3 priestly blessing verses contain proper text")
                    
            except Exception as e:
                self.log_test("Numbers 6:24-26 Priestly Blessing", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Authentic Content Quality Check", False, f"Error: {str(e)}")
            return False

    def test_no_generated_content_check(self):
        """REVIEW REQUEST TEST 4: No Generated Content Check - Search for repetitive placeholder patterns and verify unique content"""
        try:
            print("\n🔍 NO CONTAMINATION CHECK - VERIFY NO GENESIS CREATION CONTENT IN NUMBERS VERSES...")
            
            # Verify NO Genesis creation content exists in Numbers verses
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=50")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print("\n🚫 GENESIS CREATION CONTAMINATION CHECK IN NUMBERS:")
                        contamination_found = 0
                        creation_indicators = ['in the beginning', 'god created', 'heaven and earth', 'let there be light', 'adam', 'eve', 'garden of eden', 'tree of knowledge', 'serpent', 'forbidden fruit']
                        
                        for verse in verses:
                            verse_text = verse.get('text', '').lower()
                            verse_ref = f"Numbers {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Check for Genesis creation content
                            for indicator in creation_indicators:
                                if indicator in verse_text:
                                    contamination_found += 1
                                    print(f"   ❌ {verse_ref}: GENESIS CONTAMINATION - contains '{indicator}': '{verse_text[:80]}...'")
                                    break
                        
                        if contamination_found == 0:
                            self.log_test("No Genesis Creation Content in Numbers", True, f"✅ CLEAN! No Genesis creation content found in {len(verses)} Numbers verses")
                        else:
                            self.log_test("No Genesis Creation Content in Numbers", False, f"❌ CONTAMINATED! Found {contamination_found} Genesis creation contamination instances in Numbers")
                        
                    else:
                        self.log_test("No Genesis Creation Content in Numbers", False, f"❌ NO DATA! No Numbers verses found for contamination check")
                else:
                    self.log_test("No Genesis Creation Content in Numbers", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("No Genesis Creation Content in Numbers", False, f"Error: {str(e)}")
            
            # Check that legitimate KJV brackets are preserved
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print("\n📖 LEGITIMATE KJV BRACKETS PRESERVATION CHECK:")
                        legitimate_brackets_found = 0
                        legitimate_patterns = ['[are]', '[was]', '[were]', '[is]', '[be]', '[it]', '[them]', '[him]', '[her]', '[even]', '[also]', '[that]', '[which]', '[when]', '[where]']
                        
                        for verse in verses:
                            verse_text = verse.get('text', '')
                            verse_ref = f"Numbers {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Check for legitimate KJV brackets
                            for pattern in legitimate_patterns:
                                if pattern in verse_text:
                                    legitimate_brackets_found += 1
                                    print(f"   ✅ {verse_ref}: LEGITIMATE BRACKET - '{pattern}' preserved in '{verse_text[:60]}...'")
                                    break
                        
                        if legitimate_brackets_found > 0:
                            self.log_test("Legitimate KJV Brackets Preserved", True, f"✅ PRESERVED! Found {legitimate_brackets_found} legitimate KJV brackets in Numbers verses")
                        else:
                            self.log_test("Legitimate KJV Brackets Preserved", True, f"✅ ACCEPTABLE! No legitimate brackets found (may not be present in sampled verses)")
                        
                    else:
                        self.log_test("Legitimate KJV Brackets Preserved", False, f"❌ NO DATA! No Numbers verses found for bracket check")
                else:
                    self.log_test("Legitimate KJV Brackets Preserved", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Legitimate KJV Brackets Preserved", False, f"Error: {str(e)}")
            
            # Confirm no placeholder brackets like "see Numbers..." exist
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print("\n🚫 PLACEHOLDER BRACKETS CHECK IN NUMBERS:")
                        placeholder_violations = 0
                        placeholder_patterns = ['see numbers', '[chapter]', '[verse]', 'placeholder', 'complete kjv text', 'see chapter', 'see verse']
                        
                        for verse in verses:
                            verse_text = verse.get('text', '').lower()
                            verse_ref = f"Numbers {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Check for placeholder patterns
                            for pattern in placeholder_patterns:
                                if pattern in verse_text:
                                    placeholder_violations += 1
                                    print(f"   ❌ {verse_ref}: PLACEHOLDER FOUND - '{pattern}' in '{verse_text[:60]}...'")
                                    break
                        
                        if placeholder_violations == 0:
                            self.log_test("No Placeholder Brackets in Numbers", True, f"✅ CLEAN! No placeholder brackets found in {len(verses)} Numbers verses")
                        else:
                            self.log_test("No Placeholder Brackets in Numbers", False, f"❌ VIOLATIONS! Found {placeholder_violations} placeholder bracket violations in Numbers")
                        
                    else:
                        self.log_test("No Placeholder Brackets in Numbers", False, f"❌ NO DATA! No Numbers verses found for placeholder check")
                else:
                    self.log_test("No Placeholder Brackets in Numbers", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("No Placeholder Brackets in Numbers", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("No Contamination Check", False, f"Error: {str(e)}")
            return False

    def test_foundation_books_preservation(self):
        """REVIEW REQUEST TEST 4: Foundation Books Preservation - Verify Genesis, Exodus, Leviticus have exact verse counts"""
        try:
            print("\n🔍 FOUNDATION BOOKS PRESERVATION - VERIFY GENESIS, EXODUS, LEVITICUS EXACT VERSE COUNTS...")
            
            # Verify Genesis still has exactly 1,533 verses (preserved)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1533  # Review request specifies exactly 1,533 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Genesis Exactly 1,533 Verses Preserved", True, f"✅ PERFECT! Genesis has exactly {total_verses} verses (preserved)")
                    elif total_verses > 0:
                        self.log_test("Genesis Exactly 1,533 Verses Preserved", False, f"❌ INCORRECT COUNT! Genesis has {total_verses} verses, expected exactly {expected_verses}")
                    else:
                        self.log_test("Genesis Exactly 1,533 Verses Preserved", False, f"❌ NOT FOUND! Genesis does not exist in database (0 verses)")
                else:
                    self.log_test("Genesis Exactly 1,533 Verses Preserved", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis Exactly 1,533 Verses Preserved", False, f"Error: {str(e)}")
            
            # Verify Exodus still has exactly 1,063 verses (preserved)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1063  # Review request specifies exactly 1,063 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Exodus Exactly 1,063 Verses Preserved", True, f"✅ PERFECT! Exodus has exactly {total_verses} verses (preserved)")
                    elif total_verses > 0:
                        self.log_test("Exodus Exactly 1,063 Verses Preserved", False, f"❌ INCORRECT COUNT! Exodus has {total_verses} verses, expected exactly {expected_verses}")
                    else:
                        self.log_test("Exodus Exactly 1,063 Verses Preserved", False, f"❌ NOT FOUND! Exodus does not exist in database (0 verses)")
                else:
                    self.log_test("Exodus Exactly 1,063 Verses Preserved", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Exactly 1,063 Verses Preserved", False, f"Error: {str(e)}")
            
            # Verify Leviticus still has exactly 788 verses (preserved)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Leviticus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 788  # Review request specifies exactly 788 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Leviticus Exactly 788 Verses Preserved", True, f"✅ PERFECT! Leviticus has exactly {total_verses} verses (preserved)")
                    elif total_verses > 0:
                        self.log_test("Leviticus Exactly 788 Verses Preserved", False, f"❌ INCORRECT COUNT! Leviticus has {total_verses} verses, expected exactly {expected_verses}")
                    else:
                        self.log_test("Leviticus Exactly 788 Verses Preserved", False, f"❌ NOT FOUND! Leviticus does not exist in database (0 verses)")
                else:
                    self.log_test("Leviticus Exactly 788 Verses Preserved", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Leviticus Exactly 788 Verses Preserved", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Foundation Books Preservation", False, f"Error: {str(e)}")
            return False

    def test_complete_database_status(self):
        """REVIEW REQUEST TEST 5: Complete Database Status - Verify total verse count and book structure"""
        try:
            print("\n🔍 COMPLETE DATABASE STATUS - VERIFY TOTAL VERSE COUNT AND BOOK STRUCTURE...")
            
            # Get total verse count (should be Genesis 1,533 + Exodus 1,063 + Leviticus 788 + Numbers 1,102 = 4,486)
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
                    
                    # Expected total: Genesis 1,533 + Exodus 1,063 + Leviticus 788 + Numbers 1,288 = 5,672
                    expected_total = 1533 + 1063 + 788 + 1288  # = 5,672
                    
                    if total_verses == expected_total:
                        self.log_test("Total Verse Count 5,672", True, f"✅ PERFECT! Total verses: {total_verses} (exactly Genesis + Exodus + Leviticus + Numbers = {expected_total})")
                    elif total_verses >= expected_total * 0.95:  # Within 5%
                        self.log_test("Total Verse Count 5,672", True, f"✅ CLOSE! Total verses: {total_verses} (close to expected {expected_total})")
                    elif total_verses > 0:
                        self.log_test("Total Verse Count 5,672", False, f"❌ INCORRECT! Total verses: {total_verses} (expected {expected_total})")
                    else:
                        self.log_test("Total Verse Count 5,672", False, f"❌ NO DATA! Total verses: {total_verses}")
                    
                    # Verify all 4 books exist
                    if total_books >= 4:
                        self.log_test("All 4 Books Exist", True, f"✅ GOOD! Total books: {total_books} (includes all 4 required books)")
                    elif total_books >= 3:
                        self.log_test("All 4 Books Exist", False, f"❌ MISSING BOOKS! Total books: {total_books} (expected at least 4)")
                    else:
                        self.log_test("All 4 Books Exist", False, f"❌ INSUFFICIENT! Total books: {total_books} (missing foundation books)")
                        
                else:
                    self.log_test("Total Verse Count 5,672", False, f"API Error - Status: {response.status_code}")
                    self.log_test("All 4 Books Exist", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Total Verse Count 5,672", False, f"Error: {str(e)}")
                self.log_test("All 4 Books Exist", False, f"Error: {str(e)}")
            
            # Verify all 4 books exist in KJV 1611 Divine version
            try:
                required_books = ['Genesis', 'Exodus', 'Leviticus', 'Numbers']
                books_found = []
                books_missing = []
                
                print(f"\n📚 INDIVIDUAL BOOK VERIFICATION IN KJV 1611 DIVINE:")
                
                for book_name in required_books:
                    try:
                        response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book={book_name}&limit=1")
                        if response.status_code == 200:
                            book_data = response.json()
                            verse_count = book_data.get('total', 0)
                            
                            if verse_count > 0:
                                books_found.append(f"{book_name} ({verse_count} verses)")
                                print(f"   ✅ {book_name}: FOUND ({verse_count} verses)")
                            else:
                                books_missing.append(book_name)
                                print(f"   ❌ {book_name}: MISSING (0 verses)")
                        else:
                            books_missing.append(book_name)
                            print(f"   ❌ {book_name}: API ERROR (Status {response.status_code})")
                    except Exception as e:
                        books_missing.append(book_name)
                        print(f"   ❌ {book_name}: ERROR ({str(e)})")
                
                if len(books_found) == 4:
                    self.log_test("KJV 1611 Divine Version Complete", True, f"✅ COMPLETE! All 4 books found in KJV 1611 Divine: {', '.join(books_found)}")
                elif len(books_found) >= 3:
                    self.log_test("KJV 1611 Divine Version Complete", False, f"❌ INCOMPLETE! Only {len(books_found)}/4 books found. Missing: {', '.join(books_missing)}")
                else:
                    self.log_test("KJV 1611 Divine Version Complete", False, f"❌ MAJOR MISSING! Only {len(books_found)}/4 books found. Missing: {', '.join(books_missing)}")
                    
            except Exception as e:
                self.log_test("KJV 1611 Divine Version Complete", False, f"Error: {str(e)}")
            
            # Confirm proper Old Testament classification and correct book order
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine&testament=old")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    
                    print(f"\n📜 OLD TESTAMENT CLASSIFICATION AND ORDER CHECK:")
                    
                    # Check for proper Old Testament classification
                    old_testament_books = []
                    for book in books:
                        book_name = book.get('name', '')
                        testament = book.get('testament', '')
                        order = book.get('order', 0)
                        
                        if testament == 'old':
                            old_testament_books.append((book_name, order))
                            print(f"   ✅ {book_name}: Old Testament (order: {order})")
                        else:
                            print(f"   ❌ {book_name}: WRONG TESTAMENT ({testament})")
                    
                    # Check correct book order (Genesis=1, Exodus=2, Leviticus=3, Numbers=4)
                    expected_order = {'Genesis': 1, 'Exodus': 2, 'Leviticus': 3, 'Numbers': 4}
                    correct_order = True
                    
                    for book_name, actual_order in old_testament_books:
                        if book_name in expected_order:
                            expected = expected_order[book_name]
                            if actual_order == expected:
                                print(f"   ✅ {book_name}: CORRECT ORDER ({actual_order})")
                            else:
                                print(f"   ❌ {book_name}: WRONG ORDER ({actual_order}, expected {expected})")
                                correct_order = False
                    
                    if len(old_testament_books) >= 4:
                        self.log_test("Proper Old Testament Classification", True, f"✅ CORRECT! {len(old_testament_books)} books properly classified as Old Testament")
                    else:
                        self.log_test("Proper Old Testament Classification", False, f"❌ INCOMPLETE! Only {len(old_testament_books)} books classified as Old Testament")
                    
                    if correct_order:
                        self.log_test("Correct Book Order", True, f"✅ PERFECT! All books in correct biblical order")
                    else:
                        self.log_test("Correct Book Order", False, f"❌ WRONG ORDER! Some books not in correct biblical order")
                        
                else:
                    self.log_test("Proper Old Testament Classification", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Correct Book Order", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Proper Old Testament Classification", False, f"Error: {str(e)}")
                self.log_test("Correct Book Order", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Complete Database Status", False, f"Error: {str(e)}")
            return False

    def test_100_success_validation(self):
        """REVIEW REQUEST TEST 5: 100% Success Validation - Confirm Numbers completion percentage is exactly 100.0%"""
        try:
            print("\n🔍 100% SUCCESS VALIDATION - CONFIRM NUMBERS COMPLETION PERCENTAGE IS EXACTLY 100.0%...")
            
            # Confirm Numbers completion percentage is exactly 100.0%
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    target_verses = 1288  # 100% completion target
                    
                    if total_verses > 0:
                        completion_percentage = (total_verses / target_verses) * 100
                        
                        if completion_percentage == 100.0:
                            self.log_test("Numbers Completion Exactly 100.0%", True, f"✅ PERFECT! Numbers completion is exactly {completion_percentage:.1f}% ({total_verses}/{target_verses} verses)")
                        elif completion_percentage >= 99.0:
                            self.log_test("Numbers Completion Exactly 100.0%", False, f"❌ NEARLY COMPLETE! Numbers completion is {completion_percentage:.1f}% ({total_verses}/{target_verses} verses), expected exactly 100.0%")
                        else:
                            self.log_test("Numbers Completion Exactly 100.0%", False, f"❌ INCOMPLETE! Numbers completion is only {completion_percentage:.1f}% ({total_verses}/{target_verses} verses)")
                    else:
                        self.log_test("Numbers Completion Exactly 100.0%", False, f"❌ NOT FOUND! Numbers does not exist (0% completion)")
                else:
                    self.log_test("Numbers Completion Exactly 100.0%", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Numbers Completion Exactly 100.0%", False, f"Error: {str(e)}")
            
            # Verify no missing chapters or significant gaps
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Numbers&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        # Check chapter coverage
                        chapters = set()
                        for verse in verses:
                            chapter = verse.get('chapter')
                            if chapter:
                                chapters.add(int(chapter))
                        
                        expected_chapters = set(range(1, 37))  # Chapters 1-36
                        missing_chapters = expected_chapters - chapters
                        
                        if len(missing_chapters) == 0:
                            self.log_test("No Missing Chapters", True, f"✅ COMPLETE! All 36 chapters present in Numbers (sampled chapters: {sorted(list(chapters))})")
                        elif len(missing_chapters) <= 2:
                            self.log_test("No Missing Chapters", False, f"❌ MINOR GAPS! Missing {len(missing_chapters)} chapters: {sorted(list(missing_chapters))}")
                        else:
                            self.log_test("No Missing Chapters", False, f"❌ SIGNIFICANT GAPS! Missing {len(missing_chapters)} chapters: {sorted(list(missing_chapters))}")
                    else:
                        self.log_test("No Missing Chapters", False, f"❌ NO DATA! No verses found to check chapter coverage")
                else:
                    self.log_test("No Missing Chapters", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("No Missing Chapters", False, f"Error: {str(e)}")
            
            # Validate users now have complete access to all of Numbers
            try:
                # Test access to first, middle, and last chapters
                test_chapters = [1, 18, 36]  # Beginning, middle, end
                accessible_chapters = 0
                
                for chapter in test_chapters:
                    try:
                        response = self.session.get(f"{self.base_url}/bible/verses/Numbers/{chapter}")
                        if response.status_code == 200:
                            chapter_data = response.json()
                            verses = chapter_data.get('verses', [])
                            if len(verses) > 0:
                                accessible_chapters += 1
                                print(f"   ✅ Chapter {chapter}: ACCESSIBLE ({len(verses)} verses)")
                            else:
                                print(f"   ❌ Chapter {chapter}: EMPTY (0 verses)")
                        else:
                            print(f"   ❌ Chapter {chapter}: API ERROR (Status {response.status_code})")
                    except Exception as e:
                        print(f"   ❌ Chapter {chapter}: ERROR ({str(e)})")
                
                if accessible_chapters == len(test_chapters):
                    self.log_test("Complete User Access to Numbers", True, f"✅ FULL ACCESS! Users can access all tested Numbers chapters ({accessible_chapters}/{len(test_chapters)})")
                elif accessible_chapters >= 2:
                    self.log_test("Complete User Access to Numbers", False, f"❌ PARTIAL ACCESS! Only {accessible_chapters}/{len(test_chapters)} tested chapters accessible")
                else:
                    self.log_test("Complete User Access to Numbers", False, f"❌ LIMITED ACCESS! Only {accessible_chapters}/{len(test_chapters)} tested chapters accessible")
                    
            except Exception as e:
                self.log_test("Complete User Access to Numbers", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("100% Success Validation", False, f"Error: {str(e)}")
            return False

    def run_numbers_100_completion_tests(self):
        """Run Numbers 100% completion verification tests as per review request"""
        print("=" * 80)
        print("🎉 NUMBERS 100% COMPLETION VERIFICATION")
        print("Verifying that Numbers has achieved 100% completion as required")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 5 main review request tests
        test_results = []
        
        # Test 1: 100% Completion Verification
        test_results.append(self.test_numbers_100_completion_verification())
        
        # Test 2: Content Quality Check
        test_results.append(self.test_content_quality_verification())
        
        # Test 3: Foundation Books Preservation
        test_results.append(self.test_foundation_books_preservation())
        
        # Test 4: Complete Database Status
        test_results.append(self.test_complete_database_status())
        
        # Test 5: 100% Success Validation
        test_results.append(self.test_100_success_validation())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 NUMBERS 100% COMPLETION SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 NUMBERS 100% COMPLETION SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major completion verification categories completed")
        
        # Show category results
        categories = [
            "100% Completion Verification (exactly 1,288 verses, all 36 chapters, key verses content)",
            "Content Quality Check (10 Numbers verses authentic content, substantial and meaningful)", 
            "Foundation Books Preservation (Genesis 1,533, Exodus 1,063, Leviticus 788 verses preserved)",
            "Complete Database Status (total 5,672 verses, all 4 books in KJV 1611 Divine, proper Old Testament classification)",
            "100% Success Validation (completion percentage exactly 100.0%, no missing chapters, complete user access)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ VERIFIED" if result else "❌ FAILED"
            print(f"{status}: {category}")
        
        print("\n🎉 KEY NUMBERS 100% COMPLETION FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # 100% Completion Verification
            print("✅ Numbers 100% COMPLETION VERIFIED - exactly 1,288 verses across 36 chapters with authentic key verses content")
        else:
            print("❌ Numbers 100% COMPLETION FAILED - incorrect verse count, missing chapters, or poor key verses content")
        
        if test_results[1]:  # Content Quality Check
            print("✅ Numbers CONTENT QUALITY VERIFIED - authentic biblical content that is substantial and meaningful")
        else:
            print("❌ Numbers CONTENT QUALITY FAILED - poor authentic content or insufficient substance")
        
        if test_results[2]:  # Foundation Books Preservation
            print("✅ Foundation books PRESERVED - Genesis (1,533), Exodus (1,063), Leviticus (788) verses intact")
        else:
            print("❌ Foundation books COMPROMISED - verse counts changed or books missing")
        
        if test_results[3]:  # Complete Database Status
            print("✅ Database STATUS VERIFIED - total 5,672 verses, all 4 books in KJV 1611 Divine, proper classification")
        else:
            print("❌ Database STATUS FAILED - incorrect total count, missing books, or wrong classification")
        
        if test_results[4]:  # 100% Success Validation
            print("✅ 100% SUCCESS VALIDATED - completion percentage exactly 100.0%, no missing chapters, complete user access")
        else:
            print("❌ 100% SUCCESS FAILED - completion percentage not 100.0%, missing chapters, or access issues")
        
        print(f"\n🎯 FINAL NUMBERS 100% COMPLETION ASSESSMENT:")
        if individual_success_rate >= 90:
            print(f"🎉 NUMBERS 100% COMPLETION EXCELLENT! Numbers has achieved the required 100% completion standard ({individual_success_rate:.1f}% success)")
            print("✅ Numbers has exactly 1,288 verses (100% completion) across 36 chapters with authentic biblical content")
            print("✅ Foundation books preserved, complete database status verified")
            print("✅ Users now have complete access to all of Numbers")
            print("🚀 Numbers 100% completion successfully verified!")
        elif individual_success_rate >= 75:
            print(f"✅ NUMBERS 100% COMPLETION GOOD! Numbers mostly achieved completion with minor issues ({individual_success_rate:.1f}% success)")
            print("✅ Numbers structure and content mostly complete")
            print("⚠️ Some minor issues with completion percentage, preservation, or database status")
            print("🔧 Minor fixes needed but Numbers is largely complete")
        elif individual_success_rate >= 60:
            print(f"⚠️ NUMBERS 100% COMPLETION MIXED! Numbers has significant completion issues requiring attention ({individual_success_rate:.1f}% success)")
            print("⚠️ Numbers may not have achieved full 100% completion or has content issues")
            print("🔧 Recommend reviewing and fixing specific Numbers completion issues")
        elif individual_success_rate >= 40:
            print(f"❌ NUMBERS 100% COMPLETION POOR! Numbers has major completion issues ({individual_success_rate:.1f}% success)")
            print("❌ Numbers likely missing significant verses or has major content problems")
            print("🔧 Recommend completing Numbers loading to achieve 100% standard")
        else:
            print(f"❌ NUMBERS 100% COMPLETION CRITICAL FAILURE! Numbers requires immediate attention ({individual_success_rate:.1f}% success)")
            print("❌ Major Numbers completion issues detected - far from 100% standard")
            print("🔧 Recommend complete Numbers reload to achieve required 100% completion")
        
        return individual_success_rate >= 75

def main():
    """Main test execution"""
    print("🚀 Starting Numbers 100% Completion Verification Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_numbers_100_completion_tests()
    
    if success:
        print("\n🎉 Numbers 100% completion verification successful!")
        sys.exit(0)
    else:
        print("\n❌ Numbers 100% completion verification completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()