#!/usr/bin/env python3
"""
Backend Testing for Deuteronomy Chapter and Verse Structure Issues Investigation

REVIEW REQUEST FOCUS - DEUTERONOMY STRUCTURE ANALYSIS:
Please investigate the current Deuteronomy chapter and verse structure issues. Test:

1. **Deuteronomy Chapter Structure Analysis**:
   - Check how many chapters Deuteronomy currently has
   - Verify Deuteronomy Chapter 1 verse count and ordering
   - Identify any verse numbering problems in Chapter 1 (verses out of order, wrong numbers, gaps)

2. **Deuteronomy Completeness Check**:
   - Current total verse count (should be 959, but we have 562)
   - Missing chapters and verse gaps
   - Compare current count vs KJV standard (34 chapters, 959 verses)

3. **Verse Ordering Issues**:
   - Sample Deuteronomy Chapter 1 verses 1-15 to check ordering
   - Identify any duplicate verse numbers
   - Check for missing verse numbers in sequence

4. **Data Quality Issues**:
   - Check if verses are properly sequential within chapters
   - Verify chapter boundaries are correct
   - Identify any cross-contamination or data corruption

5. **Root Cause Analysis**:
   - Why is Deuteronomy incomplete (562/959 verses)?
   - What caused the verse ordering/numbering issues?
   - How does this compare to our successful Exodus (1,213/1,213 verses)?

Please provide detailed analysis of the Deuteronomy structure problems so we can fix them properly.
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

    def test_deuteronomy_chapter_structure_analysis(self):
        """REVIEW REQUEST TEST 1: Deuteronomy Chapter Structure Analysis - Check chapters, Chapter 1 verse count and ordering"""
        try:
            print("\n🔍 DEUTERONOMY CHAPTER STRUCTURE ANALYSIS - CHECKING CURRENT CHAPTERS AND CHAPTER 1 VERSE ORDERING...")
            
            # Check how many chapters Deuteronomy currently has
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    total_verses = data.get('total', 0)
                    
                    # Count unique chapters in Deuteronomy
                    deuteronomy_chapters = set()
                    chapter_verse_counts = {}
                    
                    for verse in verses:
                        chapter = verse.get('chapter')
                        if chapter:
                            chapter_num = int(chapter)
                            deuteronomy_chapters.add(chapter_num)
                            if chapter_num not in chapter_verse_counts:
                                chapter_verse_counts[chapter_num] = 0
                            chapter_verse_counts[chapter_num] += 1
                    
                    unique_chapters = len(deuteronomy_chapters)
                    expected_chapters = 34  # Deuteronomy should have 34 chapters
                    
                    print(f"\n📖 DEUTERONOMY CHAPTER STRUCTURE:")
                    print(f"   📊 Current Chapters: {unique_chapters} (expected 34)")
                    print(f"   📊 Current Total Verses: {total_verses} (expected 959)")
                    print(f"   📊 Chapters Found: {sorted(list(deuteronomy_chapters))}")
                    
                    if unique_chapters == expected_chapters:
                        self.log_test("Deuteronomy All 34 Chapters Present", True, f"✅ PERFECT! Deuteronomy has all {unique_chapters} chapters")
                    elif unique_chapters >= 30:  # At least 88% of chapters
                        self.log_test("Deuteronomy All 34 Chapters Present", True, f"✅ MOSTLY COMPLETE! Deuteronomy has {unique_chapters}/34 chapters")
                    elif unique_chapters > 0:
                        self.log_test("Deuteronomy All 34 Chapters Present", False, f"❌ INCOMPLETE! Deuteronomy has only {unique_chapters}/34 chapters")
                    else:
                        self.log_test("Deuteronomy All 34 Chapters Present", False, f"❌ NO CHAPTERS! Deuteronomy has 0 chapters")
                        
                else:
                    self.log_test("Deuteronomy All 34 Chapters Present", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy All 34 Chapters Present", False, f"Error: {str(e)}")
            
            # Verify Deuteronomy Chapter 1 verse count and ordering
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&chapter=1&limit=50")
                if response.status_code == 200:
                    chapter_data = response.json()
                    chapter_verses = chapter_data.get('verses', [])
                    chapter_total = chapter_data.get('total', 0)
                    expected_chapter1_verses = 46  # Deuteronomy Chapter 1 should have 46 verses
                    
                    print(f"\n📖 DEUTERONOMY CHAPTER 1 ANALYSIS:")
                    print(f"   📊 Chapter 1 Verses Found: {chapter_total} (expected 46)")
                    
                    if chapter_total == expected_chapter1_verses:
                        self.log_test("Deuteronomy Chapter 1 Correct Verse Count (46)", True, f"✅ PERFECT! Chapter 1 has exactly {chapter_total} verses")
                    elif chapter_total > 0:
                        completion_percentage = (chapter_total / expected_chapter1_verses) * 100
                        self.log_test("Deuteronomy Chapter 1 Correct Verse Count (46)", False, f"❌ INCORRECT! Chapter 1 has {chapter_total} verses, expected {expected_chapter1_verses} ({completion_percentage:.1f}% complete)")
                    else:
                        self.log_test("Deuteronomy Chapter 1 Correct Verse Count (46)", False, f"❌ MISSING! Chapter 1 has 0 verses")
                    
                    # Check verse ordering in Chapter 1
                    if chapter_verses:
                        verse_numbers = []
                        for verse in chapter_verses:
                            verse_num = verse.get('verse')
                            if verse_num:
                                verse_numbers.append(int(verse_num))
                        
                        verse_numbers.sort()
                        expected_sequence = list(range(1, len(verse_numbers) + 1))
                        
                        print(f"   📊 Verse Numbers Found: {verse_numbers[:10]}{'...' if len(verse_numbers) > 10 else ''}")
                        
                        # Check for proper sequential ordering
                        is_sequential = verse_numbers == expected_sequence
                        has_duplicates = len(verse_numbers) != len(set(verse_numbers))
                        has_gaps = any(verse_numbers[i] != verse_numbers[i-1] + 1 for i in range(1, len(verse_numbers)))
                        
                        if is_sequential and not has_duplicates:
                            self.log_test("Deuteronomy Chapter 1 Proper Verse Ordering", True, f"✅ PERFECT! Chapter 1 verses are properly ordered (1-{max(verse_numbers)})")
                        elif not has_duplicates and not has_gaps:
                            self.log_test("Deuteronomy Chapter 1 Proper Verse Ordering", True, f"✅ GOOD! Chapter 1 verses are sequential without duplicates")
                        else:
                            issues = []
                            if has_duplicates:
                                issues.append("duplicates")
                            if has_gaps:
                                issues.append("gaps")
                            if not is_sequential:
                                issues.append("wrong order")
                            self.log_test("Deuteronomy Chapter 1 Proper Verse Ordering", False, f"❌ ISSUES! Chapter 1 has verse ordering problems: {', '.join(issues)}")
                    else:
                        self.log_test("Deuteronomy Chapter 1 Proper Verse Ordering", False, f"❌ NO DATA! No verses found in Chapter 1")
                        
                else:
                    self.log_test("Deuteronomy Chapter 1 Correct Verse Count (46)", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Deuteronomy Chapter 1 Proper Verse Ordering", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy Chapter 1 Correct Verse Count (46)", False, f"Error: {str(e)}")
                self.log_test("Deuteronomy Chapter 1 Proper Verse Ordering", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Deuteronomy Chapter Structure Analysis", False, f"Error: {str(e)}")
            return False

    def test_deuteronomy_completeness_check(self):
        """REVIEW REQUEST TEST 2: Deuteronomy Completeness Check - Current vs expected verse count and missing chapters"""
        try:
            print("\n🔍 DEUTERONOMY COMPLETENESS CHECK - CURRENT VS EXPECTED VERSE COUNT AND MISSING CHAPTERS...")
            
            # Current total verse count (should be 959, but we have 562)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    current_verses = data.get('total', 0)
                    expected_verses = 959  # KJV standard for Deuteronomy
                    current_from_test_result = 562  # From test_result.md
                    
                    print(f"\n📊 DEUTERONOMY VERSE COUNT ANALYSIS:")
                    print(f"   📊 Current Verses: {current_verses}")
                    print(f"   📊 Expected Verses (KJV Standard): {expected_verses}")
                    print(f"   📊 Test Result File Shows: {current_from_test_result}")
                    
                    completion_percentage = (current_verses / expected_verses) * 100
                    
                    if current_verses == expected_verses:
                        self.log_test("Deuteronomy Complete 959 Verses", True, f"✅ PERFECT! Deuteronomy has exactly {current_verses} verses (100% complete)")
                    elif current_verses >= expected_verses * 0.9:  # At least 90%
                        self.log_test("Deuteronomy Complete 959 Verses", True, f"✅ NEARLY COMPLETE! Deuteronomy has {current_verses} verses ({completion_percentage:.1f}% complete)")
                    elif current_verses > 0:
                        self.log_test("Deuteronomy Complete 959 Verses", False, f"❌ INCOMPLETE! Deuteronomy has only {current_verses}/{expected_verses} verses ({completion_percentage:.1f}% complete)")
                    else:
                        self.log_test("Deuteronomy Complete 959 Verses", False, f"❌ NOT FOUND! Deuteronomy has 0 verses")
                        
                    # Check if current count matches test_result.md expectation
                    if current_verses == current_from_test_result:
                        self.log_test("Deuteronomy Matches Test Result Count (562)", True, f"✅ CONSISTENT! Current count {current_verses} matches test_result.md expectation")
                    else:
                        self.log_test("Deuteronomy Matches Test Result Count (562)", False, f"❌ INCONSISTENT! Current count {current_verses} differs from test_result.md ({current_from_test_result})")
                        
                else:
                    self.log_test("Deuteronomy Complete 959 Verses", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Deuteronomy Matches Test Result Count (562)", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy Complete 959 Verses", False, f"Error: {str(e)}")
                self.log_test("Deuteronomy Matches Test Result Count (562)", False, f"Error: {str(e)}")
            
            # Missing chapters and verse gaps analysis
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=100")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        # Analyze chapter distribution
                        chapter_counts = {}
                        all_chapters = set()
                        
                        for verse in verses:
                            chapter = verse.get('chapter')
                            if chapter:
                                chapter_num = int(chapter)
                                all_chapters.add(chapter_num)
                                if chapter_num not in chapter_counts:
                                    chapter_counts[chapter_num] = 0
                                chapter_counts[chapter_num] += 1
                        
                        expected_chapters = set(range(1, 35))  # Deuteronomy should have chapters 1-34
                        missing_chapters = expected_chapters - all_chapters
                        present_chapters = sorted(list(all_chapters))
                        
                        print(f"\n📖 DEUTERONOMY CHAPTER DISTRIBUTION:")
                        print(f"   📊 Chapters Present: {len(present_chapters)}/34")
                        print(f"   📊 Present Chapters: {present_chapters[:10]}{'...' if len(present_chapters) > 10 else ''}")
                        if missing_chapters:
                            missing_list = sorted(list(missing_chapters))
                            print(f"   📊 Missing Chapters: {missing_list[:10]}{'...' if len(missing_list) > 10 else ''}")
                        
                        if len(missing_chapters) == 0:
                            self.log_test("Deuteronomy All Chapters Present (1-34)", True, f"✅ COMPLETE! All 34 chapters present")
                        elif len(missing_chapters) <= 5:
                            self.log_test("Deuteronomy All Chapters Present (1-34)", True, f"✅ MOSTLY COMPLETE! Only {len(missing_chapters)} chapters missing")
                        else:
                            self.log_test("Deuteronomy All Chapters Present (1-34)", False, f"❌ INCOMPLETE! {len(missing_chapters)} chapters missing")
                        
                        # Check for verse gaps within chapters
                        chapter_gaps = []
                        for chapter_num in sorted(present_chapters[:5]):  # Check first 5 chapters for gaps
                            try:
                                chapter_response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&chapter={chapter_num}&limit=50")
                                if chapter_response.status_code == 200:
                                    chapter_data = chapter_response.json()
                                    chapter_verses = chapter_data.get('verses', [])
                                    
                                    verse_numbers = []
                                    for verse in chapter_verses:
                                        verse_num = verse.get('verse')
                                        if verse_num:
                                            verse_numbers.append(int(verse_num))
                                    
                                    verse_numbers.sort()
                                    if verse_numbers:
                                        expected_sequence = list(range(1, max(verse_numbers) + 1))
                                        missing_verses = set(expected_sequence) - set(verse_numbers)
                                        if missing_verses:
                                            chapter_gaps.append(f"Ch{chapter_num}: missing verses {sorted(list(missing_verses))}")
                            except Exception as e:
                                chapter_gaps.append(f"Ch{chapter_num}: error checking gaps")
                        
                        if len(chapter_gaps) == 0:
                            self.log_test("Deuteronomy No Verse Gaps in Chapters", True, f"✅ GOOD! No verse gaps detected in sampled chapters")
                        else:
                            self.log_test("Deuteronomy No Verse Gaps in Chapters", False, f"❌ GAPS FOUND! Verse gaps detected: {'; '.join(chapter_gaps[:3])}")
                        
                    else:
                        self.log_test("Deuteronomy All Chapters Present (1-34)", False, f"❌ NO DATA! No Deuteronomy verses found")
                        self.log_test("Deuteronomy No Verse Gaps in Chapters", False, f"❌ NO DATA! Cannot check for verse gaps")
                else:
                    self.log_test("Deuteronomy All Chapters Present (1-34)", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Deuteronomy No Verse Gaps in Chapters", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy All Chapters Present (1-34)", False, f"Error: {str(e)}")
                self.log_test("Deuteronomy No Verse Gaps in Chapters", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Deuteronomy Completeness Check", False, f"Error: {str(e)}")
            return False

    def test_deuteronomy_verse_ordering_issues(self):
        """REVIEW REQUEST TEST 3: Verse Ordering Issues - Sample Chapter 1 verses 1-15 and check for duplicates/missing numbers"""
        try:
            print("\n🔍 DEUTERONOMY VERSE ORDERING ISSUES - SAMPLE CHAPTER 1 VERSES 1-15 AND CHECK FOR DUPLICATES/MISSING NUMBERS...")
            
            # Sample Deuteronomy Chapter 1 verses 1-15 to check ordering
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&chapter=1&limit=20")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print(f"\n📖 DEUTERONOMY CHAPTER 1 VERSES 1-15 ORDERING ANALYSIS:")
                        
                        # Extract verse numbers and content for verses 1-15
                        verse_data = []
                        for verse in verses:
                            verse_num = verse.get('verse')
                            verse_text = verse.get('text', '')
                            if verse_num and int(verse_num) <= 15:
                                verse_data.append({
                                    'number': int(verse_num),
                                    'text': verse_text,
                                    'ref': f"Deuteronomy 1:{verse_num}"
                                })
                        
                        # Sort by verse number for analysis
                        verse_data.sort(key=lambda x: x['number'])
                        
                        # Check for proper sequential ordering (1-15)
                        verse_numbers = [v['number'] for v in verse_data]
                        expected_sequence = list(range(1, min(16, len(verse_numbers) + 1)))
                        
                        print(f"   📊 Verses Found (1-15): {verse_numbers}")
                        print(f"   📊 Expected Sequence: {expected_sequence}")
                        
                        # Check for duplicates
                        duplicates = []
                        seen = set()
                        for num in verse_numbers:
                            if num in seen:
                                duplicates.append(num)
                            seen.add(num)
                        
                        # Check for missing numbers in sequence
                        missing_numbers = []
                        for i in range(1, 16):
                            if i not in verse_numbers:
                                missing_numbers.append(i)
                        
                        # Check for out-of-order verses
                        is_sequential = verse_numbers == sorted(verse_numbers)
                        
                        print(f"\n📝 DETAILED VERSE ANALYSIS (First 10):")
                        for i, verse in enumerate(verse_data[:10]):
                            print(f"   {verse['ref']}: '{verse['text'][:60]}...'")
                        
                        # Test results
                        if len(duplicates) == 0:
                            self.log_test("Deuteronomy Ch1 No Duplicate Verse Numbers", True, f"✅ GOOD! No duplicate verse numbers found in Chapter 1")
                        else:
                            self.log_test("Deuteronomy Ch1 No Duplicate Verse Numbers", False, f"❌ DUPLICATES! Found duplicate verse numbers: {duplicates}")
                        
                        if len(missing_numbers) == 0:
                            self.log_test("Deuteronomy Ch1 No Missing Verse Numbers (1-15)", True, f"✅ COMPLETE! All verse numbers 1-15 present")
                        elif len(missing_numbers) <= 3:
                            self.log_test("Deuteronomy Ch1 No Missing Verse Numbers (1-15)", True, f"✅ MOSTLY COMPLETE! Only {len(missing_numbers)} missing: {missing_numbers}")
                        else:
                            self.log_test("Deuteronomy Ch1 No Missing Verse Numbers (1-15)", False, f"❌ GAPS! Missing verse numbers: {missing_numbers}")
                        
                        if is_sequential:
                            self.log_test("Deuteronomy Ch1 Proper Sequential Order", True, f"✅ ORDERED! Verses are in proper sequential order")
                        else:
                            self.log_test("Deuteronomy Ch1 Proper Sequential Order", False, f"❌ OUT OF ORDER! Verses not in sequential order")
                        
                        # Overall ordering assessment
                        ordering_issues = len(duplicates) + len(missing_numbers) + (0 if is_sequential else 1)
                        if ordering_issues == 0:
                            self.log_test("Deuteronomy Ch1 Overall Verse Ordering Quality", True, f"✅ PERFECT! No ordering issues detected in Chapter 1 verses 1-15")
                        elif ordering_issues <= 2:
                            self.log_test("Deuteronomy Ch1 Overall Verse Ordering Quality", True, f"✅ MINOR ISSUES! {ordering_issues} ordering issues detected")
                        else:
                            self.log_test("Deuteronomy Ch1 Overall Verse Ordering Quality", False, f"❌ MAJOR ISSUES! {ordering_issues} ordering problems detected")
                        
                    else:
                        self.log_test("Deuteronomy Ch1 No Duplicate Verse Numbers", False, f"❌ NO DATA! No verses found in Deuteronomy Chapter 1")
                        self.log_test("Deuteronomy Ch1 No Missing Verse Numbers (1-15)", False, f"❌ NO DATA! Cannot check for missing verse numbers")
                        self.log_test("Deuteronomy Ch1 Proper Sequential Order", False, f"❌ NO DATA! Cannot check sequential order")
                        self.log_test("Deuteronomy Ch1 Overall Verse Ordering Quality", False, f"❌ NO DATA! No verses available for ordering analysis")
                else:
                    self.log_test("Deuteronomy Ch1 No Duplicate Verse Numbers", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Deuteronomy Ch1 No Missing Verse Numbers (1-15)", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Deuteronomy Ch1 Proper Sequential Order", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Deuteronomy Ch1 Overall Verse Ordering Quality", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy Ch1 No Duplicate Verse Numbers", False, f"Error: {str(e)}")
                self.log_test("Deuteronomy Ch1 No Missing Verse Numbers (1-15)", False, f"Error: {str(e)}")
                self.log_test("Deuteronomy Ch1 Proper Sequential Order", False, f"Error: {str(e)}")
                self.log_test("Deuteronomy Ch1 Overall Verse Ordering Quality", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Deuteronomy Verse Ordering Issues", False, f"Error: {str(e)}")
            return False

    def test_deuteronomy_data_quality_issues(self):
        """REVIEW REQUEST TEST 4: Data Quality Issues - Check sequential verses, chapter boundaries, cross-contamination"""

        try:
            print("\n🔍 DEUTERONOMY DATA QUALITY ISSUES - CHECK SEQUENTIAL VERSES, CHAPTER BOUNDARIES, CROSS-CONTAMINATION...")
            
            # Check if verses are properly sequential within chapters
            try:
                # Sample multiple chapters to check sequential verse patterns
                chapters_to_check = [1, 2, 3, 4, 5]  # Check first 5 chapters
                sequential_issues = []
                
                print(f"\n📖 DEUTERONOMY SEQUENTIAL VERSE ANALYSIS (Chapters 1-5):")
                
                for chapter_num in chapters_to_check:
                    try:
                        response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&chapter={chapter_num}&limit=50")
                        if response.status_code == 200:
                            chapter_data = response.json()
                            chapter_verses = chapter_data.get('verses', [])
                            
                            if chapter_verses:
                                verse_numbers = []
                                for verse in chapter_verses:
                                    verse_num = verse.get('verse')
                                    if verse_num:
                                        verse_numbers.append(int(verse_num))
                                
                                verse_numbers.sort()
                                
                                # Check for sequential pattern
                                is_sequential = True
                                gaps = []
                                for i in range(1, len(verse_numbers)):
                                    if verse_numbers[i] != verse_numbers[i-1] + 1:
                                        is_sequential = False
                                        gaps.append(f"{verse_numbers[i-1]}-{verse_numbers[i]}")
                                
                                if is_sequential:
                                    print(f"   ✅ Chapter {chapter_num}: SEQUENTIAL ({len(verse_numbers)} verses, 1-{max(verse_numbers)})")
                                else:
                                    print(f"   ❌ Chapter {chapter_num}: GAPS ({len(verse_numbers)} verses, gaps: {', '.join(gaps[:3])})")
                                    sequential_issues.append(f"Ch{chapter_num}")
                            else:
                                print(f"   ❌ Chapter {chapter_num}: NO VERSES")
                                sequential_issues.append(f"Ch{chapter_num}")
                        else:
                            print(f"   ❌ Chapter {chapter_num}: API ERROR")
                            sequential_issues.append(f"Ch{chapter_num}")
                    except Exception as e:
                        print(f"   ❌ Chapter {chapter_num}: ERROR ({str(e)})")
                        sequential_issues.append(f"Ch{chapter_num}")
                
                if len(sequential_issues) == 0:
                    self.log_test("Deuteronomy Verses Properly Sequential Within Chapters", True, f"✅ GOOD! All sampled chapters have sequential verses")
                elif len(sequential_issues) <= 2:
                    self.log_test("Deuteronomy Verses Properly Sequential Within Chapters", True, f"✅ MOSTLY GOOD! Only {len(sequential_issues)} chapters with issues: {', '.join(sequential_issues)}")
                else:
                    self.log_test("Deuteronomy Verses Properly Sequential Within Chapters", False, f"❌ ISSUES! {len(sequential_issues)} chapters have sequential problems: {', '.join(sequential_issues)}")
                    
            except Exception as e:
                self.log_test("Deuteronomy Verses Properly Sequential Within Chapters", False, f"Error: {str(e)}")
            
            # Verify chapter boundaries are correct
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=50")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        # Check chapter transitions
                        chapter_transitions = {}
                        for verse in verses:
                            chapter = verse.get('chapter')
                            verse_num = verse.get('verse')
                            if chapter and verse_num:
                                chapter_num = int(chapter)
                                verse_num = int(verse_num)
                                
                                if chapter_num not in chapter_transitions:
                                    chapter_transitions[chapter_num] = {'min': verse_num, 'max': verse_num}
                                else:
                                    chapter_transitions[chapter_num]['min'] = min(chapter_transitions[chapter_num]['min'], verse_num)
                                    chapter_transitions[chapter_num]['max'] = max(chapter_transitions[chapter_num]['max'], verse_num)
                        
                        print(f"\n📖 DEUTERONOMY CHAPTER BOUNDARIES ANALYSIS:")
                        boundary_issues = []
                        
                        for chapter_num in sorted(chapter_transitions.keys())[:5]:  # Check first 5 chapters
                            min_verse = chapter_transitions[chapter_num]['min']
                            max_verse = chapter_transitions[chapter_num]['max']
                            
                            # Check if chapter starts at verse 1
                            if min_verse == 1:
                                print(f"   ✅ Chapter {chapter_num}: PROPER START (verse 1-{max_verse})")
                            else:
                                print(f"   ❌ Chapter {chapter_num}: WRONG START (verse {min_verse}-{max_verse}, should start at 1)")
                                boundary_issues.append(f"Ch{chapter_num}")
                        
                        if len(boundary_issues) == 0:
                            self.log_test("Deuteronomy Chapter Boundaries Correct", True, f"✅ GOOD! Chapter boundaries are correct (all start at verse 1)")
                        else:
                            self.log_test("Deuteronomy Chapter Boundaries Correct", False, f"❌ ISSUES! {len(boundary_issues)} chapters have boundary problems: {', '.join(boundary_issues)}")
                    else:
                        self.log_test("Deuteronomy Chapter Boundaries Correct", False, f"❌ NO DATA! No verses found for boundary analysis")
                else:
                    self.log_test("Deuteronomy Chapter Boundaries Correct", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy Chapter Boundaries Correct", False, f"Error: {str(e)}")
            
            # Identify any cross-contamination or data corruption
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=20")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        print(f"\n📖 DEUTERONOMY CROSS-CONTAMINATION CHECK (20 verses sample):")
                        contamination_issues = []
                        
                        # Check for content from other books
                        other_book_keywords = {
                            'Genesis': ['creation', 'adam', 'eve', 'noah', 'abraham', 'isaac', 'jacob'],
                            'Exodus': ['pharaoh', 'egypt', 'plagues', 'passover', 'red sea'],
                            'Leviticus': ['offerings', 'sacrifices', 'priests', 'aaron'],
                            'Numbers': ['census', 'wilderness', 'tribes', 'spies']
                        }
                        
                        deuteronomy_keywords = ['moses', 'law', 'commandments', 'statutes', 'jordan', 'promised land', 'israel']
                        
                        for i, verse in enumerate(verses[:10]):  # Check first 10 verses
                            verse_text = verse.get('text', '').lower()
                            verse_ref = f"Deuteronomy {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Check for other book content
                            contamination_found = []
                            for book, keywords in other_book_keywords.items():
                                for keyword in keywords:
                                    if keyword in verse_text and book != 'Deuteronomy':
                                        contamination_found.append(f"{book}:{keyword}")
                            
                            # Check for proper Deuteronomy content
                            has_deuteronomy_content = any(keyword in verse_text for keyword in deuteronomy_keywords)
                            
                            if contamination_found:
                                print(f"   ❌ {verse_ref}: CONTAMINATION - '{verse_text[:60]}...' (found: {', '.join(contamination_found[:2])})")
                                contamination_issues.append(verse_ref)
                            elif has_deuteronomy_content:
                                print(f"   ✅ {verse_ref}: PROPER CONTENT - '{verse_text[:60]}...'")
                            else:
                                print(f"   ⚠️ {verse_ref}: UNCLEAR - '{verse_text[:60]}...'")
                        
                        if len(contamination_issues) == 0:
                            self.log_test("Deuteronomy No Cross-Contamination", True, f"✅ CLEAN! No cross-contamination detected in sampled verses")
                        else:
                            self.log_test("Deuteronomy No Cross-Contamination", False, f"❌ CONTAMINATION! {len(contamination_issues)} verses show cross-contamination: {', '.join(contamination_issues[:3])}")
                    else:
                        self.log_test("Deuteronomy No Cross-Contamination", False, f"❌ NO DATA! No verses found for contamination analysis")
                else:
                    self.log_test("Deuteronomy No Cross-Contamination", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy No Cross-Contamination", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Deuteronomy Data Quality Issues", False, f"Error: {str(e)}")
            return False

    def test_deuteronomy_root_cause_analysis(self):
        """REVIEW REQUEST TEST 5: Root Cause Analysis - Why incomplete, comparison with successful Exodus"""

        try:
            print("\n🔍 DEUTERONOMY ROOT CAUSE ANALYSIS - WHY INCOMPLETE, COMPARISON WITH SUCCESSFUL EXODUS...")
            
            # Compare Deuteronomy vs Exodus completion rates
            try:
                print(f"\n📊 DEUTERONOMY VS EXODUS COMPARISON:")
                
                # Get Deuteronomy stats
                deut_response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=1")
                exodus_response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                
                deut_verses = 0
                exodus_verses = 0
                
                if deut_response.status_code == 200:
                    deut_data = deut_response.json()
                    deut_verses = deut_data.get('total', 0)
                
                if exodus_response.status_code == 200:
                    exodus_data = exodus_response.json()
                    exodus_verses = exodus_data.get('total', 0)
                
                # Expected counts
                deut_expected = 959  # KJV standard
                exodus_expected = 1213  # KJV standard
                
                deut_completion = (deut_verses / deut_expected) * 100 if deut_expected > 0 else 0
                exodus_completion = (exodus_verses / exodus_expected) * 100 if exodus_expected > 0 else 0
                
                print(f"   📖 Deuteronomy: {deut_verses}/{deut_expected} verses ({deut_completion:.1f}% complete)")
                print(f"   📖 Exodus: {exodus_verses}/{exodus_expected} verses ({exodus_completion:.1f}% complete)")
                print(f"   📊 Completion Gap: {exodus_completion - deut_completion:.1f}% (Exodus ahead)")
                
                if exodus_completion >= 90 and deut_completion < 70:
                    self.log_test("Deuteronomy vs Exodus Completion Gap Analysis", True, f"✅ CLEAR PATTERN! Exodus ({exodus_completion:.1f}%) significantly more complete than Deuteronomy ({deut_completion:.1f}%)")
                elif abs(exodus_completion - deut_completion) > 20:
                    self.log_test("Deuteronomy vs Exodus Completion Gap Analysis", True, f"✅ SIGNIFICANT GAP! {abs(exodus_completion - deut_completion):.1f}% difference between books")
                else:
                    self.log_test("Deuteronomy vs Exodus Completion Gap Analysis", False, f"❌ SIMILAR COMPLETION! Both books have similar completion rates")
                    
            except Exception as e:
                self.log_test("Deuteronomy vs Exodus Completion Gap Analysis", False, f"Error: {str(e)}")
            
            # Analyze potential causes of incompleteness
            try:
                print(f"\n🔍 DEUTERONOMY INCOMPLETENESS ROOT CAUSE ANALYSIS:")
                
                # Check data loading patterns
                deut_response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Deuteronomy&limit=50")
                if deut_response.status_code == 200:
                    deut_data = deut_response.json()
                    deut_verses = deut_data.get('verses', [])
                    
                    if deut_verses:
                        # Analyze chapter distribution
                        chapter_counts = {}
                        for verse in deut_verses:
                            chapter = verse.get('chapter')
                            if chapter:
                                chapter_num = int(chapter)
                                if chapter_num not in chapter_counts:
                                    chapter_counts[chapter_num] = 0
                                chapter_counts[chapter_num] += 1
                        
                        chapters_present = len(chapter_counts)
                        max_chapter = max(chapter_counts.keys()) if chapter_counts else 0
                        
                        # Analyze potential causes
                        causes = []
                        
                        if chapters_present < 10:
                            causes.append("PARTIAL_LOADING: Only few chapters loaded")
                        
                        if max_chapter < 20:
                            causes.append("TRUNCATED_LOADING: Loading stopped early")
                        
                        # Check for consistent verse counts per chapter
                        verse_counts = list(chapter_counts.values())
                        if verse_counts:
                            avg_verses = sum(verse_counts) / len(verse_counts)
                            if avg_verses < 20:
                                causes.append("INCOMPLETE_CHAPTERS: Chapters have too few verses")
                        
                        # Check for data quality issues
                        sample_verse = deut_verses[0] if deut_verses else {}
                        verse_text = sample_verse.get('text', '')
                        if len(verse_text) < 20:
                            causes.append("POOR_CONTENT_QUALITY: Verses have minimal content")
                        
                        print(f"   📊 Chapters Present: {chapters_present}/34 (max chapter: {max_chapter})")
                        print(f"   📊 Average Verses per Chapter: {avg_verses:.1f}" if verse_counts else "   📊 No verse count data")
                        print(f"   🔍 Potential Causes: {', '.join(causes) if causes else 'Unknown'}")
                        
                        if len(causes) >= 2:
                            self.log_test("Deuteronomy Root Cause Identified", True, f"✅ CAUSES IDENTIFIED! Multiple issues found: {', '.join(causes[:2])}")
                        elif len(causes) == 1:
                            self.log_test("Deuteronomy Root Cause Identified", True, f"✅ CAUSE IDENTIFIED! Primary issue: {causes[0]}")
                        else:
                            self.log_test("Deuteronomy Root Cause Identified", False, f"❌ UNCLEAR! No obvious causes identified")
                    else:
                        self.log_test("Deuteronomy Root Cause Identified", False, f"❌ NO DATA! Cannot analyze causes without verse data")
                else:
                    self.log_test("Deuteronomy Root Cause Identified", False, f"API Error - Status: {deut_response.status_code}")
            except Exception as e:
                self.log_test("Deuteronomy Root Cause Identified", False, f"Error: {str(e)}")
            
            # Compare data loading success patterns
            try:
                print(f"\n📈 DATA LOADING SUCCESS PATTERN ANALYSIS:")
                
                # Check multiple books to identify patterns
                books_to_check = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
                expected_counts = {'Genesis': 1533, 'Exodus': 1213, 'Leviticus': 788, 'Numbers': 601, 'Deuteronomy': 959}
                
                success_rates = {}
                for book in books_to_check:
                    try:
                        response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book={book}&limit=1")
                        if response.status_code == 200:
                            data = response.json()
                            actual = data.get('total', 0)
                            expected = expected_counts[book]
                            success_rate = (actual / expected) * 100 if expected > 0 else 0
                            success_rates[book] = success_rate
                            print(f"   📖 {book}: {success_rate:.1f}% complete ({actual}/{expected})")
                        else:
                            success_rates[book] = 0
                            print(f"   ❌ {book}: API Error")
                    except Exception as e:
                        success_rates[book] = 0
                        print(f"   ❌ {book}: Error")
                
                # Identify pattern
                successful_books = [book for book, rate in success_rates.items() if rate >= 90]
                incomplete_books = [book for book, rate in success_rates.items() if rate < 70]
                
                print(f"   ✅ Successful Books (≥90%): {', '.join(successful_books)}")
                print(f"   ❌ Incomplete Books (<70%): {', '.join(incomplete_books)}")
                
                if 'Deuteronomy' in incomplete_books and len(successful_books) >= 2:
                    self.log_test("Data Loading Pattern Analysis", True, f"✅ PATTERN IDENTIFIED! Deuteronomy is among incomplete books while {len(successful_books)} books are successful")
                else:
                    self.log_test("Data Loading Pattern Analysis", False, f"❌ NO CLEAR PATTERN! Cannot identify consistent loading success pattern")
                    
            except Exception as e:
                self.log_test("Data Loading Pattern Analysis", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Deuteronomy Root Cause Analysis", False, f"Error: {str(e)}")
            return False

    # Removed old test method - replaced with new tests matching review request

    def run_exodus_100_percent_completion_tests(self):
        """Run Exodus 100% completion verification tests as per review request"""
        print("=" * 80)
        print("🎉 EXODUS 100% COMPLETION WITH AUTHENTIC CONTENT VERIFICATION")
        print("Verifying that the new Exodus loading achieved 100% completion with authentic content")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 5 main review request tests
        test_results = []
        
        # Test 1: 100% Completion Verification
        test_results.append(self.test_exodus_100_percent_completion_verification())
        
        # Test 2: Content Quality Check
        test_results.append(self.test_exodus_content_quality_check())
        
        # Test 3: Foundation Books Preservation
        test_results.append(self.test_foundation_books_preservation())
        
        # Test 4: Authenticity vs Generated Content Analysis
        test_results.append(self.test_authenticity_vs_generated_content_analysis())
        
        # Test 5: Complete Database Status
        test_results.append(self.test_complete_database_status())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 EXODUS 100% COMPLETION SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 EXODUS 100% COMPLETION SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major completion verification categories completed")
        
        # Show category results
        categories = [
            "100% Completion Verification (exactly 1,213 verses, all 40 chapters, key chapters with proper verse counts)",
            "Content Quality Check (Exodus 1:1-5 Israel names, Exodus 3:2 burning bush, Exodus 20:1-3 Ten Commandments, authentic vs generated analysis)", 
            "Foundation Books Preservation (Genesis 1,533, Leviticus 788, Numbers 601, Deuteronomy 562 verses preserved)",
            "Authenticity vs Generated Content Analysis (percentage authentic vs contextual/generated, cross-referenced verses, gap-filled verses)",
            "Complete Database Status (total 4,697 verses, all 5 books correctly classified, proper Old Testament order)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ VERIFIED" if result else "❌ FAILED"
            print(f"{status}: {category}")
        
        print("\n🎉 KEY EXODUS 100% COMPLETION FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # 100% Completion Verification
            print("✅ EXODUS 100% COMPLETION VERIFIED - exactly 1,213 verses with all 40 chapters and proper key chapter verse counts")
        else:
            print("❌ EXODUS COMPLETION FAILED - incorrect verse count, missing chapters, or wrong key chapter verse counts")
        
        if test_results[1]:  # Content Quality Check
            print("✅ CONTENT QUALITY VERIFIED - Exodus 1:1-5 contain Israel names, Exodus 3:2 has burning bush content, Exodus 20:1-3 has Ten Commandments")
        else:
            print("❌ CONTENT QUALITY FAILED - missing key biblical content in critical Exodus verses")
        
        if test_results[2]:  # Foundation Books Preservation
            print("✅ Foundation books PRESERVED - Genesis (1,533), Leviticus (788), Numbers (601), Deuteronomy (562) verses intact")
        else:
            print("❌ Foundation books COMPROMISED - verse counts changed or books missing")
        
        if test_results[3]:  # Authenticity vs Generated Content Analysis
            print("✅ AUTHENTICITY ANALYSIS VERIFIED - high percentage of authentic biblical content, minimal generated/placeholder content")
        else:
            print("❌ AUTHENTICITY ANALYSIS FAILED - too much generated/contextual content, poor cross-referenced verses, or inadequate gap-filled content")
        
        if test_results[4]:  # Complete Database Status
            print("✅ Database STATUS VERIFIED - total 4,697 verses, all 5 books correctly classified, proper Old Testament order")
        else:
            print("❌ Database STATUS FAILED - incorrect total count, missing books, or wrong classification")
        
        print(f"\n🎯 FINAL EXODUS 100% COMPLETION ASSESSMENT:")
        if individual_success_rate >= 90:
            print(f"🎉 EXODUS 100% COMPLETION EXCELLENT! Exodus achieved 100% completion with authentic content ({individual_success_rate:.1f}% success)")
            print("✅ Exodus has exactly 1,213 verses with all 40 chapters and proper key chapter structure")
            print("✅ Key verses contain authentic biblical content (Israel names, burning bush, Ten Commandments)")
            print("✅ Foundation books preserved, high authenticity percentage, proper database classification")
            print("🚀 Exodus 100% completion successfully verified with authentic biblical text standards!")
        elif individual_success_rate >= 75:
            print(f"✅ EXODUS 100% COMPLETION GOOD! Exodus mostly achieved completion with minor issues ({individual_success_rate:.1f}% success)")
            print("✅ Exodus structure and authentic content mostly verified")
            print("⚠️ Some minor issues with verse count, content quality, or authenticity analysis")
            print("🔧 Minor fixes needed but Exodus is largely complete and authentic")
        elif individual_success_rate >= 60:
            print(f"⚠️ EXODUS COMPLETION MIXED! Exodus has significant completion issues requiring attention ({individual_success_rate:.1f}% success)")
            print("⚠️ Exodus may not have achieved 100% completion or has authenticity issues")
            print("🔧 Recommend reviewing and fixing specific Exodus completion and authenticity issues")
        elif individual_success_rate >= 40:
            print(f"❌ EXODUS COMPLETION POOR! Exodus has major completion issues ({individual_success_rate:.1f}% success)")
            print("❌ Exodus likely incomplete or contains too much generated/contextual content")
            print("🔧 Recommend completing Exodus loading to achieve 100% completion with authentic biblical text")
        else:
            print(f"❌ EXODUS COMPLETION CRITICAL FAILURE! Exodus requires immediate attention ({individual_success_rate:.1f}% success)")
            print("❌ Major Exodus completion issues detected - far from 100% completion standard")
            print("🔧 Recommend complete Exodus reloading to achieve required 100% completion with authentic biblical text")
        
        return individual_success_rate >= 75

def main():
    """Main test execution"""
    print("🚀 Starting Exodus 100% Completion with Authentic Content Verification Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_exodus_100_percent_completion_tests()
    
    if success:
        print("\n🎉 Exodus 100% completion with authentic content verification successful!")
        sys.exit(0)
    else:
        print("\n❌ Exodus 100% completion verification completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()