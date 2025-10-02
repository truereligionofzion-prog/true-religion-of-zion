#!/usr/bin/env python3
"""
Backend Testing for Exodus Completion Verification

REVIEW REQUEST FOCUS - EXODUS COMPLETION VERIFICATION:
Please verify that Exodus is now successfully completed following the Genesis success formula. Test:

1. **Exodus Completion Verification**:
   - Verify Exodus exists in the database with proper verse count
   - Check all 40 chapters are present  
   - Confirm key verses (1:1, 3:1, 12:1, 20:1, 40:1) have proper content

2. **Genesis Preservation Check**:
   - Verify Genesis still has exactly 1,533 verses (wasn't affected)
   - Confirm Genesis 1:1 and 50:26 are still intact
   - Ensure no cross-contamination between Genesis and Exodus

3. **Exodus Content Quality**:
   - Sample Exodus verses for content quality
   - Verify proper biblical content structure
   - Check verse numbering consistency within chapters

4. **Database Statistics**:
   - Get total Bible verse count (should be Genesis 1,533 + Exodus ~1,173)
   - Verify both books exist in KJV 1611 Divine version
   - Confirm proper testament classification (Old Testament)

5. **Key Chapter Verification**:
   - Test Exodus Chapter 1 (Israel in Egypt)
   - Test Exodus Chapter 12 (Passover) 
   - Test Exodus Chapter 20 (Ten Commandments)
   - Verify these critical chapters have proper verse counts

This verification confirms Exodus follows the successful Genesis formula and both books are working correctly together.
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

    def test_exodus_completion_verification(self):
        """REVIEW REQUEST TEST 1: Exodus Completion Verification - Verify Exodus exists with proper verse count and all 40 chapters"""
        try:
            print("\n🔍 EXODUS COMPLETION VERIFICATION - CHECKING FULL COMPLETION STATUS...")
            
            # Verify Exodus exists in the database with proper verse count
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1213  # Exodus should have 1,213 verses total
                    
                    if total_verses == expected_verses:
                        self.log_test("Exodus Complete Verse Count", True, f"✅ PERFECT! Exodus has exactly {total_verses} verses (100% complete)")
                    elif total_verses > 0:
                        completion_percentage = (total_verses / expected_verses) * 100
                        missing_verses = expected_verses - total_verses
                        self.log_test("Exodus Complete Verse Count", False, f"❌ INCOMPLETE! Exodus has {total_verses} verses, missing {missing_verses} ({completion_percentage:.1f}% complete)")
                    else:
                        self.log_test("Exodus Complete Verse Count", False, f"❌ NOT FOUND! Exodus does not exist in database (0 verses)")
                else:
                    self.log_test("Exodus Complete Verse Count", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Complete Verse Count", False, f"Error: {str(e)}")
            
            # Check all 40 chapters are present with correct verse counts
            expected_verses_per_chapter = {
                1: 22, 2: 25, 3: 22, 4: 31, 5: 23, 6: 30, 7: 25, 8: 32, 9: 35, 10: 29,
                11: 10, 12: 51, 13: 22, 14: 31, 15: 27, 16: 36, 17: 16, 18: 27, 19: 25, 20: 26,
                21: 36, 22: 31, 23: 33, 24: 18, 25: 40, 26: 37, 27: 21, 28: 43, 29: 46, 30: 38,
                31: 18, 32: 35, 33: 23, 34: 35, 35: 35, 36: 38, 37: 29, 38: 31, 39: 43, 40: 38
            }
            
            print("\n📊 EXODUS ALL 40 CHAPTERS VERIFICATION:")
            complete_chapters = 0
            incomplete_chapters = []
            total_verified_verses = 0
            
            for chapter in range(1, 41):  # Exodus has 40 chapters
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        
                        if actual_verses == expected_verses:
                            complete_chapters += 1
                            total_verified_verses += actual_verses
                            print(f"   ✅ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - COMPLETE")
                        else:
                            incomplete_chapters.append({
                                'chapter': chapter,
                                'actual': actual_verses,
                                'expected': expected_verses,
                                'status': 'MISSING' if actual_verses == 0 else 'PARTIAL'
                            })
                            total_verified_verses += actual_verses
                            status = 'MISSING' if actual_verses == 0 else 'PARTIAL'
                            print(f"   ❌ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - {status}")
                        
                    else:
                        incomplete_chapters.append({
                            'chapter': chapter,
                            'actual': 0,
                            'expected': expected_verses_per_chapter.get(chapter, 0),
                            'status': 'API_ERROR'
                        })
                        print(f"   ❌ Chapter {chapter:2d}: API ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    incomplete_chapters.append({
                        'chapter': chapter,
                        'actual': 0,
                        'expected': expected_verses_per_chapter.get(chapter, 0),
                        'status': 'ERROR'
                    })
                    print(f"   ❌ Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Verify all 40 chapters are complete
            if complete_chapters == 40:
                self.log_test("All 40 Exodus Chapters Present", True, f"✅ PERFECT! All 40 chapters are complete with correct verse counts")
            else:
                missing_count = len([ch for ch in incomplete_chapters if ch['status'] == 'MISSING'])
                partial_count = len([ch for ch in incomplete_chapters if ch['status'] == 'PARTIAL'])
                self.log_test("All 40 Exodus Chapters Present", False, f"❌ INCOMPLETE! {complete_chapters}/40 complete, {partial_count} partial, {missing_count} missing")
            
            # Confirm key verses have proper content
            key_verses = [
                {'chapter': 1, 'verse': 1, 'description': 'Israel in Egypt'},
                {'chapter': 3, 'verse': 1, 'description': 'Burning Bush'},
                {'chapter': 12, 'verse': 1, 'description': 'Passover'},
                {'chapter': 20, 'verse': 1, 'description': 'Ten Commandments'},
                {'chapter': 40, 'verse': 1, 'description': 'Tabernacle Completion'}
            ]
            
            print("\n📖 KEY EXODUS VERSES CONTENT VERIFICATION:")
            key_verses_verified = 0
            
            for key_verse in key_verses:
                try:
                    response = self.session.get(f"{self.base_url}/bible/verse/Exodus/{key_verse['chapter']}/{key_verse['verse']}")
                    if response.status_code == 200:
                        verse_data = response.json()
                        verse_text = verse_data.get('text', '')
                        
                        if len(verse_text) > 20 and not verse_text.startswith('...'):
                            key_verses_verified += 1
                            print(f"   ✅ Exodus {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): '{verse_text[:60]}...'")
                        else:
                            print(f"   ❌ Exodus {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): POOR CONTENT - '{verse_text}'")
                    else:
                        print(f"   ❌ Exodus {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): API ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Exodus {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): ERROR - {str(e)}")
            
            if key_verses_verified == len(key_verses):
                self.log_test("Key Exodus Verses Content", True, f"✅ EXCELLENT! All {key_verses_verified}/5 key verses have proper content")
            else:
                self.log_test("Key Exodus Verses Content", False, f"❌ ISSUES! Only {key_verses_verified}/5 key verses have proper content")
            
            return True
            
        except Exception as e:
            self.log_test("Exodus Completion Verification", False, f"Error: {str(e)}")
            return False

    def test_genesis_preservation_check(self):
        """REVIEW REQUEST TEST 2: Genesis Preservation Check - Verify Genesis still has exactly 1,533 verses and is intact"""
        try:
            print("\n🔍 GENESIS PRESERVATION CHECK - VERIFYING GENESIS WASN'T AFFECTED BY EXODUS COMPLETION...")
            
            # Verify Genesis still has exactly 1,533 verses
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1533  # Genesis should have exactly 1,533 verses
                    
                    if total_verses == expected_verses:
                        self.log_test("Genesis Exact Verse Count Preserved", True, f"✅ PERFECT! Genesis still has exactly {total_verses} verses (preserved)")
                    else:
                        self.log_test("Genesis Exact Verse Count Preserved", False, f"❌ CHANGED! Genesis now has {total_verses} verses, expected {expected_verses}")
                else:
                    self.log_test("Genesis Exact Verse Count Preserved", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis Exact Verse Count Preserved", False, f"Error: {str(e)}")
            
            # Confirm Genesis 1:1 and 50:26 are still intact
            key_genesis_verses = [
                {'chapter': 1, 'verse': 1, 'description': 'Creation Beginning', 'expected_content': 'In the beginning God created'},
                {'chapter': 50, 'verse': 26, 'description': 'Genesis Ending', 'expected_content': 'So Joseph died'}
            ]
            
            print("\n📖 GENESIS KEY VERSES INTEGRITY CHECK:")
            genesis_key_verses_intact = 0
            
            for key_verse in key_genesis_verses:
                try:
                    response = self.session.get(f"{self.base_url}/bible/verse/Genesis/{key_verse['chapter']}/{key_verse['verse']}")
                    if response.status_code == 200:
                        verse_data = response.json()
                        verse_text = verse_data.get('text', '')
                        
                        if key_verse['expected_content'].lower() in verse_text.lower():
                            genesis_key_verses_intact += 1
                            print(f"   ✅ Genesis {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): INTACT - '{verse_text[:60]}...'")
                        else:
                            print(f"   ❌ Genesis {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): CHANGED - '{verse_text[:60]}...'")
                    else:
                        print(f"   ❌ Genesis {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): API ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Genesis {key_verse['chapter']}:{key_verse['verse']} ({key_verse['description']}): ERROR - {str(e)}")
            
            if genesis_key_verses_intact == len(key_genesis_verses):
                self.log_test("Genesis Key Verses Intact", True, f"✅ PRESERVED! All {genesis_key_verses_intact}/2 key Genesis verses are intact")
            else:
                self.log_test("Genesis Key Verses Intact", False, f"❌ CORRUPTED! Only {genesis_key_verses_intact}/2 key Genesis verses are intact")
            
            # Ensure no cross-contamination between Genesis and Exodus
            try:
                # Check Genesis verses don't contain Exodus content
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    genesis_verses = data.get('verses', [])
                    
                    exodus_contamination = 0
                    exodus_keywords = ['moses', 'pharaoh', 'egypt', 'israelites', 'commandments', 'tabernacle', 'aaron']
                    
                    for verse in genesis_verses:
                        verse_text = verse.get('text', '').lower()
                        book = verse.get('book', '')
                        
                        # Check book field is correct
                        if book != 'Genesis':
                            exodus_contamination += 1
                            print(f"   ❌ BOOK CONTAMINATION: Verse labeled as '{book}' in Genesis query")
                            continue
                        
                        # Check for Exodus-specific content in Genesis verses
                        for keyword in exodus_keywords:
                            if keyword in verse_text:
                                # Some keywords like 'egypt' might legitimately appear in Genesis
                                if keyword in ['moses', 'pharaoh', 'commandments', 'tabernacle', 'aaron']:
                                    exodus_contamination += 1
                                    print(f"   ❌ CONTENT CONTAMINATION: Genesis verse contains '{keyword}': '{verse_text[:50]}...'")
                                    break
                    
                    if exodus_contamination == 0:
                        self.log_test("No Cross-Contamination Genesis", True, f"✅ PURE! No Exodus contamination found in {len(genesis_verses)} Genesis verses")
                    else:
                        self.log_test("No Cross-Contamination Genesis", False, f"❌ CONTAMINATED! Found {exodus_contamination} instances of Exodus contamination in Genesis")
                        
                    # Check Exodus verses don't contain Genesis-specific content
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=10")
                    if response.status_code == 200:
                        data = response.json()
                        exodus_verses = data.get('verses', [])
                        
                        genesis_contamination = 0
                        genesis_keywords = ['adam', 'eve', 'noah', 'abraham', 'isaac', 'jacob', 'joseph']
                        
                        for verse in exodus_verses:
                            verse_text = verse.get('text', '').lower()
                            book = verse.get('book', '')
                            
                            # Check book field is correct
                            if book != 'Exodus':
                                genesis_contamination += 1
                                print(f"   ❌ BOOK CONTAMINATION: Verse labeled as '{book}' in Exodus query")
                                continue
                            
                            # Check for Genesis-specific content in Exodus verses (some overlap is expected)
                            for keyword in genesis_keywords:
                                if keyword in verse_text:
                                    # Some names like 'abraham', 'isaac', 'jacob' might legitimately appear in Exodus
                                    if keyword in ['adam', 'eve', 'noah']:
                                        genesis_contamination += 1
                                        print(f"   ❌ CONTENT CONTAMINATION: Exodus verse contains '{keyword}': '{verse_text[:50]}...'")
                                        break
                        
                        if genesis_contamination == 0:
                            self.log_test("No Cross-Contamination Exodus", True, f"✅ PURE! No Genesis contamination found in {len(exodus_verses)} Exodus verses")
                        else:
                            self.log_test("No Cross-Contamination Exodus", False, f"❌ CONTAMINATED! Found {genesis_contamination} instances of Genesis contamination in Exodus")
                    else:
                        self.log_test("No Cross-Contamination Exodus", False, f"API Error getting Exodus verses - Status: {response.status_code}")
                else:
                    self.log_test("No Cross-Contamination Genesis", False, f"API Error getting Genesis verses - Status: {response.status_code}")
                    self.log_test("No Cross-Contamination Exodus", False, f"Cannot test Exodus contamination without Genesis data")
            except Exception as e:
                self.log_test("No Cross-Contamination Genesis", False, f"Error: {str(e)}")
                self.log_test("No Cross-Contamination Exodus", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Genesis Preservation Check", False, f"Error: {str(e)}")
            return False

    def test_exodus_content_quality(self):
        """REVIEW REQUEST TEST 3: Exodus Content Quality - Sample verses for quality, biblical structure, numbering consistency"""
        try:
            print("\n🔍 EXODUS CONTENT QUALITY - SAMPLING VERSES FOR QUALITY AND BIBLICAL STRUCTURE...")
            
            # Sample Exodus verses for content quality
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=20")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print("\n📝 EXODUS VERSE CONTENT QUALITY SAMPLING:")
                        high_quality_verses = 0
                        total_sampled = len(verses)
                        
                        for verse in verses:
                            verse_text = verse.get('text', '')
                            verse_ref = f"Exodus {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Enhanced quality checks for biblical content
                            is_high_quality = (
                                len(verse_text) > 15 and  # Reasonable length for biblical verse
                                not verse_text.startswith('...') and  # Not truncated
                                not verse_text.endswith('...') and
                                verse_text.strip() != '' and  # Not empty
                                not verse_text.lower().startswith('error') and  # No error messages
                                not verse_text.lower().startswith('missing') and  # No missing indicators
                                len(verse_text.split()) >= 3 and  # At least 3 words
                                verse_text[0].isupper()  # Starts with capital letter
                            )
                            
                            if is_high_quality:
                                high_quality_verses += 1
                                print(f"   ✅ {verse_ref}: '{verse_text[:70]}...'")
                            else:
                                print(f"   ❌ {verse_ref}: QUALITY ISSUE - '{verse_text}'")
                        
                        if total_sampled > 0:
                            quality_percentage = (high_quality_verses / total_sampled) * 100
                            if quality_percentage >= 95:
                                self.log_test("Exodus Verse Content Quality", True, f"✅ EXCELLENT! {high_quality_verses}/{total_sampled} verses are high quality ({quality_percentage:.1f}%)")
                            elif quality_percentage >= 85:
                                self.log_test("Exodus Verse Content Quality", True, f"✅ GOOD! {high_quality_verses}/{total_sampled} verses are good quality ({quality_percentage:.1f}%)")
                            else:
                                self.log_test("Exodus Verse Content Quality", False, f"❌ POOR! {high_quality_verses}/{total_sampled} verses have quality issues ({quality_percentage:.1f}%)")
                        
                    else:
                        self.log_test("Exodus Verse Content Quality", False, f"❌ NO DATA! No Exodus verses found for quality check")
                else:
                    self.log_test("Exodus Verse Content Quality", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Verse Content Quality", False, f"Error: {str(e)}")
            
            # Verify proper biblical content structure
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=15")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print("\n📖 EXODUS BIBLICAL CONTENT STRUCTURE VERIFICATION:")
                        biblical_structure_count = 0
                        
                        # Check for proper biblical content themes in Exodus
                        exodus_themes = {
                            'moses': 0, 'pharaoh': 0, 'egypt': 0, 'israelites': 0, 'israel': 0,
                            'lord': 0, 'god': 0, 'commandments': 0, 'tabernacle': 0, 'aaron': 0,
                            'plague': 0, 'passover': 0, 'wilderness': 0, 'mount': 0, 'covenant': 0
                        }
                        
                        for verse in verses:
                            verse_text = verse.get('text', '').lower()
                            verse_ref = f"Exodus {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Count biblical themes
                            themes_found = []
                            for theme in exodus_themes:
                                if theme in verse_text:
                                    exodus_themes[theme] += 1
                                    themes_found.append(theme)
                            
                            if themes_found:
                                biblical_structure_count += 1
                                print(f"   ✅ {verse_ref}: Biblical themes found: {', '.join(themes_found[:3])}")
                            else:
                                print(f"   ⚠️ {verse_ref}: No specific Exodus themes detected")
                        
                        # Summary of biblical themes
                        total_theme_occurrences = sum(exodus_themes.values())
                        themes_with_content = len([theme for theme, count in exodus_themes.items() if count > 0])
                        
                        if biblical_structure_count >= len(verses) * 0.6:  # At least 60% should have biblical themes
                            self.log_test("Proper Biblical Content Structure", True, f"✅ AUTHENTIC! {biblical_structure_count}/{len(verses)} verses contain biblical themes ({themes_with_content} different themes, {total_theme_occurrences} total occurrences)")
                        else:
                            self.log_test("Proper Biblical Content Structure", False, f"❌ QUESTIONABLE! Only {biblical_structure_count}/{len(verses)} verses contain biblical themes")
                        
                    else:
                        self.log_test("Proper Biblical Content Structure", False, f"❌ NO DATA! No Exodus verses found for structure check")
                else:
                    self.log_test("Proper Biblical Content Structure", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Proper Biblical Content Structure", False, f"Error: {str(e)}")
            
            # Check verse numbering consistency within chapters
            try:
                print("\n🔢 EXODUS VERSE NUMBERING CONSISTENCY CHECK:")
                test_chapters = [1, 12, 20, 40]  # Test key chapters
                numbering_consistent = True
                consistent_chapters = 0
                
                for chapter in test_chapters:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&chapter={chapter}&limit=100")
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        
                        if verses:
                            # Check if verse numbers are sequential starting from 1
                            verse_numbers = sorted([verse.get('verse', 0) for verse in verses])
                            expected_numbers = list(range(1, len(verses) + 1))
                            
                            if verse_numbers == expected_numbers:
                                consistent_chapters += 1
                                print(f"   ✅ Chapter {chapter}: Perfect numbering (1-{len(verses)})")
                            else:
                                numbering_consistent = False
                                missing_numbers = set(expected_numbers) - set(verse_numbers)
                                extra_numbers = set(verse_numbers) - set(expected_numbers)
                                print(f"   ❌ Chapter {chapter}: Numbering issues - Missing: {missing_numbers}, Extra: {extra_numbers}")
                        else:
                            numbering_consistent = False
                            print(f"   ❌ Chapter {chapter}: No verses found")
                    else:
                        numbering_consistent = False
                        print(f"   ❌ Chapter {chapter}: API Error - Status {response.status_code}")
                
                if consistent_chapters == len(test_chapters):
                    self.log_test("Verse Numbering Consistency", True, f"✅ PERFECT! All {consistent_chapters}/{len(test_chapters)} tested chapters have consistent numbering")
                elif consistent_chapters >= len(test_chapters) * 0.75:
                    self.log_test("Verse Numbering Consistency", True, f"✅ GOOD! {consistent_chapters}/{len(test_chapters)} tested chapters have consistent numbering")
                else:
                    self.log_test("Verse Numbering Consistency", False, f"❌ POOR! Only {consistent_chapters}/{len(test_chapters)} tested chapters have consistent numbering")
                    
            except Exception as e:
                self.log_test("Verse Numbering Consistency", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Exodus Content Quality", False, f"Error: {str(e)}")
            return False

    def test_database_statistics(self):
        """REVIEW REQUEST TEST 4: Database Statistics - Total Bible verse count, both books verification, testament classification"""
        try:
            print("\n🔍 DATABASE STATISTICS - TOTAL BIBLE VERSE COUNT AND BOOK VERIFICATION...")
            
            # Get total Bible verse count (should be Genesis 1,533 + Exodus ~1,173)
            try:
                response = self.session.get(f"{self.base_url}/bible/stats?version=kjv1611_divine")
                if response.status_code == 200:
                    stats = response.json()
                    total_verses = stats.get('totalVerses', 0)
                    total_books = stats.get('totalBooks', 0)
                    old_testament_verses = stats.get('oldTestamentVerses', 0)
                    
                    expected_total = 1533 + 1213  # Genesis + Exodus = 2,746 verses
                    
                    print(f"\n📊 BIBLE DATABASE STATISTICS:")
                    print(f"   📖 Total Books: {total_books}")
                    print(f"   📝 Total Verses: {total_verses}")
                    print(f"   📜 Old Testament Verses: {old_testament_verses}")
                    
                    if total_verses == expected_total:
                        self.log_test("Total Bible Verse Count", True, f"✅ PERFECT! Total verses: {total_verses} (Genesis 1,533 + Exodus 1,213 = {expected_total})")
                    elif total_verses >= expected_total * 0.95:  # Within 5% is acceptable
                        self.log_test("Total Bible Verse Count", True, f"✅ EXCELLENT! Total verses: {total_verses} (close to expected {expected_total})")
                    else:
                        self.log_test("Total Bible Verse Count", False, f"❌ INCOMPLETE! Total verses: {total_verses}, expected approximately {expected_total}")
                        
                else:
                    self.log_test("Total Bible Verse Count", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Total Bible Verse Count", False, f"Error: {str(e)}")
            
            # Verify both books exist in KJV 1611 Divine version
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    book_names = [book.get('name', '') for book in books]
                    
                    genesis_found = 'Genesis' in book_names
                    exodus_found = 'Exodus' in book_names
                    
                    print(f"\n📚 KJV 1611 DIVINE VERSION BOOKS:")
                    print(f"   📖 Total Books Available: {len(books)}")
                    print(f"   📜 Books: {', '.join(book_names)}")
                    
                    if genesis_found and exodus_found:
                        self.log_test("Both Genesis and Exodus Present", True, f"✅ CONFIRMED! Both Genesis and Exodus exist in KJV 1611 Divine version")
                        
                        # Get detailed info for both books
                        genesis_book = next((book for book in books if book.get('name') == 'Genesis'), None)
                        exodus_book = next((book for book in books if book.get('name') == 'Exodus'), None)
                        
                        if genesis_book and exodus_book:
                            genesis_testament = genesis_book.get('testament', 'unknown')
                            exodus_testament = exodus_book.get('testament', 'unknown')
                            genesis_order = genesis_book.get('order', 'unknown')
                            exodus_order = exodus_book.get('order', 'unknown')
                            
                            print(f"   ✅ Genesis: Testament={genesis_testament}, Order={genesis_order}")
                            print(f"   ✅ Exodus: Testament={exodus_testament}, Order={exodus_order}")
                            
                    elif genesis_found:
                        self.log_test("Both Genesis and Exodus Present", False, f"❌ PARTIAL! Genesis found but Exodus missing from KJV 1611 Divine")
                    elif exodus_found:
                        self.log_test("Both Genesis and Exodus Present", False, f"❌ PARTIAL! Exodus found but Genesis missing from KJV 1611 Divine")
                    else:
                        self.log_test("Both Genesis and Exodus Present", False, f"❌ MISSING! Neither Genesis nor Exodus found in KJV 1611 Divine")
                        
                else:
                    self.log_test("Both Genesis and Exodus Present", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Both Genesis and Exodus Present", False, f"Error: {str(e)}")
            
            # Confirm proper testament classification (Old Testament)
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
                
                print(f"\n📜 TESTAMENT CLASSIFICATION VERIFICATION:")
                print(f"   📖 Genesis Testament: {genesis_testament}")
                print(f"   📖 Exodus Testament: {exodus_testament}")
                
                if genesis_testament == 'old' and exodus_testament == 'old':
                    self.log_test("Proper Testament Classification", True, f"✅ CORRECT! Both Genesis and Exodus classified as Old Testament")
                elif genesis_testament == 'old' or exodus_testament == 'old':
                    self.log_test("Proper Testament Classification", False, f"❌ PARTIAL! Genesis: {genesis_testament}, Exodus: {exodus_testament} (both should be 'old')")
                else:
                    self.log_test("Proper Testament Classification", False, f"❌ INCORRECT! Genesis: {genesis_testament}, Exodus: {exodus_testament} (both should be 'old')")
                    
            except Exception as e:
                self.log_test("Proper Testament Classification", False, f"Error: {str(e)}")
            
            # Additional verification: Individual book verse counts
            try:
                print(f"\n🔢 INDIVIDUAL BOOK VERSE COUNT VERIFICATION:")
                
                # Genesis verse count
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    genesis_verses = data.get('total', 0)
                    print(f"   📖 Genesis: {genesis_verses} verses (expected: 1,533)")
                    
                    if genesis_verses == 1533:
                        self.log_test("Genesis Individual Count", True, f"✅ PERFECT! Genesis has exactly 1,533 verses")
                    else:
                        self.log_test("Genesis Individual Count", False, f"❌ INCORRECT! Genesis has {genesis_verses} verses, expected 1,533")
                else:
                    self.log_test("Genesis Individual Count", False, f"API Error - Status: {response.status_code}")
                
                # Exodus verse count
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    exodus_verses = data.get('total', 0)
                    print(f"   📖 Exodus: {exodus_verses} verses (expected: 1,213)")
                    
                    if exodus_verses == 1213:
                        self.log_test("Exodus Individual Count", True, f"✅ PERFECT! Exodus has exactly 1,213 verses")
                    elif exodus_verses >= 1173:  # Close to expected
                        self.log_test("Exodus Individual Count", True, f"✅ EXCELLENT! Exodus has {exodus_verses} verses (close to expected 1,213)")
                    else:
                        self.log_test("Exodus Individual Count", False, f"❌ INCOMPLETE! Exodus has {exodus_verses} verses, expected approximately 1,213")
                else:
                    self.log_test("Exodus Individual Count", False, f"API Error - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Genesis Individual Count", False, f"Error: {str(e)}")
                self.log_test("Exodus Individual Count", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Statistics", False, f"Error: {str(e)}")
            return False

    # Old test method removed - replaced with Genesis 100% completion verification tests

    def run_exodus_current_state_analysis_tests(self):
        """Run Exodus current state analysis tests as per review request"""
        print("=" * 80)
        print("🔍 EXODUS CURRENT STATE ANALYSIS")
        print("Analyzing current Exodus state to apply successful Genesis completion formula")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 4 main review request tests
        test_results = []
        
        # Test 1: Exodus Current State Analysis
        test_results.append(self.test_exodus_current_state_analysis())
        
        # Test 2: Database Structure Check
        test_results.append(self.test_database_structure_check())
        
        # Test 3: Exodus Content Quality Check
        test_results.append(self.test_exodus_content_quality_check())
        
        # Test 4: Baseline Establishment
        test_results.append(self.test_baseline_establishment())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 EXODUS CURRENT STATE ANALYSIS SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 ANALYSIS SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major analysis categories completed")
        
        # Show category results
        categories = [
            "Exodus Current State Analysis (existence check, chapter/verse counts, present vs missing)",
            "Database Structure Check (Bible versions available, KJV 1611 Divine, structure consistency)", 
            "Exodus Content Quality Check (verse sampling, cross-contamination, numbering consistency)",
            "Baseline Establishment (total counts, chapter breakdown, completion starting point)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ ANALYZED" if result else "❌ FAILED"
            print(f"{status}: {category}")
        
        print("\n🔍 KEY ANALYSIS FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # Exodus Current State Analysis
            print("✅ Exodus state analyzed - existence, chapter/verse counts, and gaps identified")
        else:
            print("❌ Exodus state analysis FAILED - unable to determine current state")
        
        if test_results[1]:  # Database Structure Check
            print("✅ Database structure verified - Bible versions and structure consistency confirmed")
        else:
            print("❌ Database structure FAILED - version or structure issues detected")
        
        if test_results[2]:  # Exodus Content Quality Check
            print("✅ Content quality assessed - verse sampling and contamination check completed")
        else:
            print("❌ Content quality FAILED - quality or contamination issues detected")
        
        if test_results[3]:  # Baseline Establishment
            print("✅ Baseline established - total counts, chapter breakdown, and starting point identified")
        else:
            print("❌ Baseline establishment FAILED - unable to establish completion starting point")
        
        print(f"\n🎯 FINAL EXODUS COMPLETION READINESS ASSESSMENT:")
        if individual_success_rate >= 90:
            print(f"✅ EXODUS ANALYSIS COMPLETE! Ready to apply Genesis formula ({individual_success_rate:.1f}% success)")
            print("✅ All baseline data collected - can proceed with precision Exodus completion")
            print("🚀 Ready to implement Exodus completion script following proven Genesis approach!")
        elif individual_success_rate >= 75:
            print(f"✅ EXODUS ANALYSIS MOSTLY COMPLETE! Can proceed with caution ({individual_success_rate:.1f}% success)")
            print("✅ Sufficient baseline data collected - minor gaps won't prevent completion")
        elif individual_success_rate >= 60:
            print(f"⚠️ EXODUS ANALYSIS PARTIAL! Some gaps in baseline data ({individual_success_rate:.1f}% success)")
            print("⚠️ Can proceed but may need additional investigation during completion")
        else:
            print(f"❌ EXODUS ANALYSIS INSUFFICIENT! Major gaps in baseline data ({individual_success_rate:.1f}% success)")
            print("❌ Need to resolve analysis issues before attempting Exodus completion")
        
        return individual_success_rate >= 75

def main():
    """Main test execution"""
    print("🚀 Starting Exodus Current State Analysis Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_exodus_current_state_analysis_tests()
    
    if success:
        print("\n🎉 Exodus current state analysis successful!")
        sys.exit(0)
    else:
        print("\n❌ Exodus current state analysis failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()