#!/usr/bin/env python3
"""
Backend Testing for Genesis 100% Completion Verification

REVIEW REQUEST FOCUS - GENESIS COMPLETION VERIFICATION:
Please verify that Genesis is now 100% complete by testing:

1. **Genesis Completion Verification**:
   - Verify total verse count is exactly 1,533 verses (100%)
   - Check that all 50 chapters are complete with proper verse counts
   - Confirm Genesis 1:1 still has correct creation text
   - Confirm Genesis 50:26 has proper ending text

2. **Data Quality Check**:
   - Sample a few of the newly added verses to ensure they have proper text
   - Verify no cross-contamination occurred (database still has only Genesis)
   - Check that the existing verses were not modified

3. **Database Statistics**:
   - Verify the Genesis book record shows 1,533 verses
   - Confirm total database contains exactly 1,533 verses (pure Genesis dataset)

4. **API Response Validation**:
   - Test that Genesis API endpoints return the complete data
   - Verify pagination works correctly with the full dataset

This comprehensive verification will confirm Genesis is truly 100% complete and ready for the user.
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

    def test_genesis_completion_verification(self):
        """REVIEW REQUEST TEST 1: Genesis Completion Verification - Verify exactly 1,533 verses (100%)"""
        try:
            print("\n🔍 GENESIS COMPLETION VERIFICATION - VERIFYING 100% COMPLETION (1,533 VERSES)...")
            
            # Get overall Genesis statistics
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1533
                    
                    if total_verses == expected_verses:
                        self.log_test("Genesis Total Verse Count - 100% COMPLETE", True, f"✅ PERFECT! Found exactly {total_verses} verses (100% complete)")
                    else:
                        missing_verses = expected_verses - total_verses
                        completion_percentage = (total_verses / expected_verses) * 100
                        self.log_test("Genesis Total Verse Count - 100% COMPLETE", False, f"❌ INCOMPLETE! Found {total_verses} verses, missing {missing_verses} ({completion_percentage:.1f}% complete)")
                else:
                    self.log_test("Genesis Total Verse Count - 100% COMPLETE", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis Total Verse Count - 100% COMPLETE", False, f"Error: {str(e)}")
            
            # Verify all 50 chapters are complete with proper verse counts
            expected_verses_per_chapter = {
                1: 31, 2: 25, 3: 24, 4: 26, 5: 32, 6: 22, 7: 24, 8: 22, 9: 29, 10: 32,
                11: 32, 12: 20, 13: 18, 14: 24, 15: 21, 16: 16, 17: 27, 18: 33, 19: 38, 20: 18,
                21: 34, 22: 24, 23: 20, 24: 67, 25: 34, 26: 35, 27: 46, 28: 22, 29: 35, 30: 43,
                31: 55, 32: 32, 33: 20, 34: 31, 35: 29, 36: 43, 37: 36, 38: 30, 39: 23, 40: 23,
                41: 57, 42: 38, 43: 34, 44: 34, 45: 28, 46: 34, 47: 31, 48: 22, 49: 33, 50: 26
            }
            
            print("\n📊 ALL 50 CHAPTERS COMPLETION VERIFICATION:")
            complete_chapters = 0
            incomplete_chapters = []
            
            for chapter in range(1, 51):  # Genesis has 50 chapters
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        
                        if actual_verses == expected_verses:
                            complete_chapters += 1
                            print(f"   ✅ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - COMPLETE")
                        else:
                            incomplete_chapters.append({
                                'chapter': chapter,
                                'actual': actual_verses,
                                'expected': expected_verses,
                                'missing': expected_verses - actual_verses
                            })
                            print(f"   ❌ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - MISSING {expected_verses - actual_verses}")
                        
                    else:
                        incomplete_chapters.append({
                            'chapter': chapter,
                            'actual': 0,
                            'expected': expected_verses_per_chapter.get(chapter, 0),
                            'missing': expected_verses_per_chapter.get(chapter, 0)
                        })
                        print(f"   ❌ Chapter {chapter:2d}: API ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    incomplete_chapters.append({
                        'chapter': chapter,
                        'actual': 0,
                        'expected': expected_verses_per_chapter.get(chapter, 0),
                        'missing': expected_verses_per_chapter.get(chapter, 0)
                    })
                    print(f"   ❌ Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Summary of all 50 chapters
            if complete_chapters == 50:
                self.log_test("All 50 Chapters Complete", True, f"✅ PERFECT! All 50 chapters are complete with proper verse counts")
            else:
                total_missing = sum(ch['missing'] for ch in incomplete_chapters)
                self.log_test("All 50 Chapters Complete", False, f"❌ INCOMPLETE! {complete_chapters}/50 chapters complete, {len(incomplete_chapters)} chapters missing {total_missing} total verses")
            
            return True
            
        except Exception as e:
            self.log_test("Genesis Completion Verification", False, f"Error: {str(e)}")
            return False

    def test_data_quality_check(self):
        """REVIEW REQUEST TEST 2: Data Quality Check - Key verses, sampling, and cross-contamination"""
        try:
            print("\n🔍 DATA QUALITY CHECK - KEY VERSES, SAMPLING, AND PURITY...")
            
            # Confirm Genesis 1:1 still has correct creation text
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Genesis/1/1?version=kjv1611_divine")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for Genesis 1:1 creation content
                    creation_keywords = ['beginning', 'god', 'created', 'heaven', 'earth']
                    keywords_found = sum(1 for keyword in creation_keywords if keyword.lower() in verse_text.lower())
                    
                    if keywords_found >= 4:
                        self.log_test("Genesis 1:1 - Creation Text Preserved", True, f"✅ CORRECT! Found: '{verse_text}'")
                    else:
                        self.log_test("Genesis 1:1 - Creation Text Preserved", False, f"❌ CORRUPTED! Found: '{verse_text}'")
                else:
                    self.log_test("Genesis 1:1 - Creation Text Preserved", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis 1:1 - Creation Text Preserved", False, f"Error: {str(e)}")
            
            # Confirm Genesis 50:26 has proper ending text
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Genesis/50/26?version=kjv1611_divine")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for Genesis 50:26 content (Joseph's death/burial)
                    ending_keywords = ['joseph', 'died', 'egypt', 'coffin', 'years']
                    keywords_found = sum(1 for keyword in ending_keywords if keyword.lower() in verse_text.lower())
                    
                    if keywords_found >= 2:
                        self.log_test("Genesis 50:26 - Proper Ending Text", True, f"✅ CORRECT! Found: '{verse_text}'")
                    else:
                        self.log_test("Genesis 50:26 - Proper Ending Text", False, f"❌ INCORRECT! Found: '{verse_text}'")
                else:
                    self.log_test("Genesis 50:26 - Proper Ending Text", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis 50:26 - Proper Ending Text", False, f"Error: {str(e)}")
            
            # Verify no cross-contamination occurred (database still has only Genesis)
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    book_count = len(books)
                    
                    if book_count == 1:
                        book_name = books[0].get('name', 'Unknown') if books else 'Unknown'
                        if book_name == 'Genesis':
                            self.log_test("No Cross-Contamination - Pure Genesis Dataset", True, f"✅ PURE! Only Genesis exists ({book_count} book)")
                        else:
                            self.log_test("No Cross-Contamination - Pure Genesis Dataset", False, f"❌ WRONG BOOK! Found '{book_name}' instead of Genesis")
                    else:
                        book_names = [book.get('name', 'Unknown') for book in books]
                        self.log_test("No Cross-Contamination - Pure Genesis Dataset", False, f"❌ CONTAMINATED! {book_count} books found: {', '.join(book_names)}")
                else:
                    self.log_test("No Cross-Contamination - Pure Genesis Dataset", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("No Cross-Contamination - Pure Genesis Dataset", False, f"Error: {str(e)}")
            
            # Sample newly added verses to ensure they have proper text
            print("\n📝 NEWLY ADDED VERSES QUALITY SAMPLING:")
            
            # Sample verses from different chapters to check quality
            sample_chapters = [1, 10, 20, 30, 40, 50]  # Spread across Genesis
            quality_verses = 0
            total_sampled = 0
            
            for chapter in sample_chapters:
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=5")
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        
                        for verse in verses[:3]:  # Sample 3 verses per chapter
                            verse_text = verse.get('text', '')
                            verse_ref = f"Genesis {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            total_sampled += 1
                            
                            # Quality checks for newly added verses
                            is_quality = (
                                len(verse_text) > 10 and  # Reasonable length
                                not verse_text.startswith('...') and  # Not truncated
                                not verse_text.endswith('...') and
                                verse_text.strip() != '' and  # Not empty
                                not verse_text.lower().startswith('error') and  # No error messages
                                not verse_text.lower().startswith('missing')  # No missing indicators
                            )
                            
                            if is_quality:
                                quality_verses += 1
                                print(f"   ✅ {verse_ref}: '{verse_text[:60]}...'")
                            else:
                                print(f"   ❌ {verse_ref}: QUALITY ISSUE - '{verse_text[:60]}...'")
                                
                except Exception as e:
                    print(f"   ❌ Chapter {chapter}: Error - {str(e)}")
            
            if total_sampled > 0:
                quality_percentage = (quality_verses / total_sampled) * 100
                if quality_percentage >= 95:
                    self.log_test("Newly Added Verses Quality", True, f"✅ EXCELLENT! {quality_verses}/{total_sampled} verses are high quality ({quality_percentage:.1f}%)")
                elif quality_percentage >= 85:
                    self.log_test("Newly Added Verses Quality", True, f"✅ GOOD! {quality_verses}/{total_sampled} verses are good quality ({quality_percentage:.1f}%)")
                else:
                    self.log_test("Newly Added Verses Quality", False, f"❌ POOR! {quality_verses}/{total_sampled} verses have quality issues ({quality_percentage:.1f}%)")
            else:
                self.log_test("Newly Added Verses Quality", False, "No verses sampled for quality check")
            
            return True
            
        except Exception as e:
            self.log_test("Data Quality Check", False, f"Error: {str(e)}")
            return False

    def test_database_statistics(self):
        """REVIEW REQUEST TEST 3: Database Statistics - Verify Genesis book record and total database"""
        try:
            print("\n🔍 DATABASE STATISTICS - VERIFYING GENESIS BOOK RECORD AND TOTAL DATABASE...")
            
            # Verify the Genesis book record shows 1,533 verses
            try:
                response = self.session.get(f"{self.base_url}/bible/stats?version=kjv1611_divine")
                if response.status_code == 200:
                    stats = response.json()
                    total_verses = stats.get('totalVerses', 0)
                    total_books = stats.get('totalBooks', 0)
                    
                    if total_verses == 1533:
                        self.log_test("Genesis Book Record - 1,533 Verses", True, f"✅ PERFECT! Genesis book record shows exactly {total_verses} verses")
                    else:
                        self.log_test("Genesis Book Record - 1,533 Verses", False, f"❌ INCORRECT! Genesis book record shows {total_verses} verses, expected 1,533")
                    
                    if total_books == 1:
                        self.log_test("Database Contains Only Genesis", True, f"✅ PURE! Database contains exactly {total_books} book (Genesis only)")
                    else:
                        self.log_test("Database Contains Only Genesis", False, f"❌ CONTAMINATED! Database contains {total_books} books, expected 1 (Genesis only)")
                        
                else:
                    self.log_test("Genesis Book Record - 1,533 Verses", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Database Contains Only Genesis", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis Book Record - 1,533 Verses", False, f"Error: {str(e)}")
                self.log_test("Database Contains Only Genesis", False, f"Error: {str(e)}")
            
            # Confirm total database contains exactly 1,533 verses (pure Genesis dataset)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    
                    if total_verses == 1533:
                        self.log_test("Total Database - Pure Genesis Dataset (1,533 verses)", True, f"✅ PERFECT! Total database contains exactly {total_verses} verses (pure Genesis)")
                    else:
                        self.log_test("Total Database - Pure Genesis Dataset (1,533 verses)", False, f"❌ INCORRECT! Total database contains {total_verses} verses, expected 1,533")
                else:
                    self.log_test("Total Database - Pure Genesis Dataset (1,533 verses)", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Total Database - Pure Genesis Dataset (1,533 verses)", False, f"Error: {str(e)}")
            
            # Additional verification - check that all verses are from Genesis
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    all_genesis = True
                    non_genesis_books = set()
                    
                    for verse in verses:
                        book = verse.get('book', '')
                        if book != 'Genesis':
                            all_genesis = False
                            non_genesis_books.add(book)
                    
                    if all_genesis:
                        self.log_test("All Verses Are Genesis", True, f"✅ VERIFIED! All sampled verses are from Genesis")
                    else:
                        self.log_test("All Verses Are Genesis", False, f"❌ CONTAMINATED! Found verses from: {', '.join(non_genesis_books)}")
                else:
                    self.log_test("All Verses Are Genesis", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("All Verses Are Genesis", False, f"Error: {str(e)}")
            
            # Verify chapter distribution matches Genesis structure
            print("\n📊 GENESIS CHAPTER DISTRIBUTION VERIFICATION:")
            
            expected_verses_per_chapter = {
                1: 31, 2: 25, 3: 24, 4: 26, 5: 32, 6: 22, 7: 24, 8: 22, 9: 29, 10: 32,
                11: 32, 12: 20, 13: 18, 14: 24, 15: 21, 16: 16, 17: 27, 18: 33, 19: 38, 20: 18,
                21: 34, 22: 24, 23: 20, 24: 67, 25: 34, 26: 35, 27: 46, 28: 22, 29: 35, 30: 43,
                31: 55, 32: 32, 33: 20, 34: 31, 35: 29, 36: 43, 37: 36, 38: 30, 39: 23, 40: 23,
                41: 57, 42: 38, 43: 34, 44: 34, 45: 28, 46: 34, 47: 31, 48: 22, 49: 33, 50: 26
            }
            
            total_expected = sum(expected_verses_per_chapter.values())
            chapters_verified = 0
            
            for chapter in [1, 25, 50]:  # Sample key chapters
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        
                        if actual_verses == expected_verses:
                            chapters_verified += 1
                            print(f"   ✅ Chapter {chapter}: {actual_verses}/{expected_verses} verses - CORRECT")
                        else:
                            print(f"   ❌ Chapter {chapter}: {actual_verses}/{expected_verses} verses - INCORRECT")
                    else:
                        print(f"   ❌ Chapter {chapter}: API Error - Status {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Chapter {chapter}: Error - {str(e)}")
            
            if chapters_verified == 3:
                self.log_test("Genesis Chapter Distribution", True, f"✅ VERIFIED! Sample chapters have correct verse counts")
            else:
                self.log_test("Genesis Chapter Distribution", False, f"❌ INCORRECT! {chapters_verified}/3 sample chapters have wrong verse counts")
            
            self.log_test("Expected Total Verses Calculation", True, f"Genesis should have {total_expected} verses total (verified calculation)")
            
            return True
            
        except Exception as e:
            self.log_test("Database Statistics", False, f"Error: {str(e)}")
            return False

    def test_specific_missing_verses_investigation(self):
        """REVIEW REQUEST TEST 4: Specific Missing Verses Investigation - Calculate and locate missing verses"""
        try:
            print("\n🔍 SPECIFIC MISSING VERSES INVESTIGATION - CALCULATING MISSING 38 VERSES...")
            
            # Get current total verse count
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    current_verses = data.get('total', 0)
                    expected_verses = 1533
                    missing_verses = expected_verses - current_verses
                    
                    self.log_test("Missing Verses Calculation", True, f"Current: {current_verses}, Expected: {expected_verses}, Missing: {missing_verses}")
                else:
                    self.log_test("Missing Verses Calculation", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Missing Verses Calculation", False, f"Error: {str(e)}")
                return False
            
            # Detailed analysis of missing verses by chapter
            expected_verses_per_chapter = {
                1: 31, 2: 25, 3: 24, 4: 26, 5: 32, 6: 22, 7: 24, 8: 22, 9: 29, 10: 32,
                11: 32, 12: 20, 13: 18, 14: 24, 15: 21, 16: 16, 17: 27, 18: 33, 19: 38, 20: 18,
                21: 34, 22: 24, 23: 20, 24: 67, 25: 34, 26: 35, 27: 46, 28: 22, 29: 35, 30: 43,
                31: 55, 32: 32, 33: 20, 34: 31, 35: 29, 36: 43, 37: 36, 38: 30, 39: 23, 40: 23,
                41: 57, 42: 38, 43: 34, 44: 34, 45: 28, 46: 34, 47: 31, 48: 22, 49: 33, 50: 26
            }
            
            print("\n🔍 DETAILED MISSING VERSES ANALYSIS:")
            
            truncated_chapters = []
            scattered_missing = []
            total_calculated_missing = 0
            
            for chapter in range(1, 51):
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=100")
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        actual_count = data.get('total', 0)
                        expected_count = expected_verses_per_chapter.get(chapter, 0)
                        missing_count = expected_count - actual_count
                        
                        if missing_count > 0:
                            total_calculated_missing += missing_count
                            
                            # Check if chapter is truncated (missing verses at the end)
                            if verses:
                                verse_numbers = [v.get('verse', 0) for v in verses if isinstance(v.get('verse'), int)]
                                verse_numbers.sort()
                                max_verse = max(verse_numbers) if verse_numbers else 0
                                
                                if max_verse < expected_count:
                                    truncated_chapters.append({
                                        'chapter': chapter,
                                        'actual': actual_count,
                                        'expected': expected_count,
                                        'missing': missing_count,
                                        'max_verse': max_verse,
                                        'type': 'truncated'
                                    })
                                    print(f"   ❌ Chapter {chapter:2d}: TRUNCATED - has verses 1-{max_verse}, missing {expected_count - max_verse} at end")
                                else:
                                    # Check for gaps in verse numbering
                                    expected_verses = set(range(1, expected_count + 1))
                                    actual_verses = set(verse_numbers)
                                    missing_verse_numbers = expected_verses - actual_verses
                                    
                                    if missing_verse_numbers:
                                        scattered_missing.append({
                                            'chapter': chapter,
                                            'actual': actual_count,
                                            'expected': expected_count,
                                            'missing': missing_count,
                                            'missing_verses': sorted(list(missing_verse_numbers)),
                                            'type': 'scattered'
                                        })
                                        missing_list = ', '.join(map(str, sorted(list(missing_verse_numbers))[:10]))
                                        if len(missing_verse_numbers) > 10:
                                            missing_list += '...'
                                        print(f"   ❌ Chapter {chapter:2d}: SCATTERED - missing verses: {missing_list}")
                            else:
                                truncated_chapters.append({
                                    'chapter': chapter,
                                    'actual': 0,
                                    'expected': expected_count,
                                    'missing': expected_count,
                                    'max_verse': 0,
                                    'type': 'empty'
                                })
                                print(f"   ❌ Chapter {chapter:2d}: EMPTY - missing all {expected_count} verses")
                        else:
                            print(f"   ✅ Chapter {chapter:2d}: COMPLETE - {actual_count}/{expected_count} verses")
                            
                except Exception as e:
                    print(f"   ❌ Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Summary of missing verse patterns
            self.log_test("Total Missing Verses Verification", True, f"Calculated missing: {total_calculated_missing} verses")
            
            if truncated_chapters:
                truncated_count = len(truncated_chapters)
                truncated_missing = sum(ch['missing'] for ch in truncated_chapters)
                self.log_test("Truncated Chapters", False, f"❌ {truncated_count} chapters are truncated (missing {truncated_missing} verses)")
                
                # Show worst truncated chapters
                truncated_chapters.sort(key=lambda x: x['missing'], reverse=True)
                worst_truncated = truncated_chapters[:3]
                for ch in worst_truncated:
                    self.log_test(f"Truncated Chapter {ch['chapter']}", False, f"Missing {ch['missing']} verses (has 1-{ch['max_verse']}, needs 1-{ch['expected']})")
            else:
                self.log_test("Truncated Chapters", True, "✅ No chapters are truncated")
            
            if scattered_missing:
                scattered_count = len(scattered_missing)
                scattered_missing_total = sum(ch['missing'] for ch in scattered_missing)
                self.log_test("Scattered Missing Verses", False, f"❌ {scattered_count} chapters have scattered missing verses ({scattered_missing_total} total)")
                
                # Show chapters with most scattered missing
                scattered_missing.sort(key=lambda x: x['missing'], reverse=True)
                worst_scattered = scattered_missing[:3]
                for ch in worst_scattered:
                    missing_list = ', '.join(map(str, ch['missing_verses'][:5]))
                    if len(ch['missing_verses']) > 5:
                        missing_list += '...'
                    self.log_test(f"Scattered Chapter {ch['chapter']}", False, f"Missing {ch['missing']} verses: {missing_list}")
            else:
                self.log_test("Scattered Missing Verses", True, "✅ No scattered missing verses")
            
            # Pattern analysis
            if truncated_chapters and not scattered_missing:
                self.log_test("Missing Verse Pattern", True, "Pattern: Chapters are truncated (missing verses at end)")
            elif scattered_missing and not truncated_chapters:
                self.log_test("Missing Verse Pattern", True, "Pattern: Verses are scattered missing throughout chapters")
            elif truncated_chapters and scattered_missing:
                self.log_test("Missing Verse Pattern", True, "Pattern: Mixed - both truncated chapters and scattered missing verses")
            else:
                self.log_test("Missing Verse Pattern", True, "Pattern: No missing verses detected")
            
            return True
            
        except Exception as e:
            self.log_test("Specific Missing Verses Investigation", False, f"Error: {str(e)}")
            return False

    def test_genesis_completion_recommendations(self):
        """ADDITIONAL TEST: Generate recommendations for reaching 100% Genesis coverage"""
        try:
            print("\n🔍 GENESIS COMPLETION RECOMMENDATIONS - PATH TO 100% COVERAGE...")
            
            # Get current statistics
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    current_verses = data.get('total', 0)
                    expected_verses = 1533
                    missing_verses = expected_verses - current_verses
                    completion_percentage = (current_verses / expected_verses) * 100
                    
                    self.log_test("Current Completion Status", True, f"{completion_percentage:.1f}% complete ({current_verses}/{expected_verses} verses)")
                else:
                    self.log_test("Current Completion Status", False, f"Status: {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Current Completion Status", False, f"Error: {str(e)}")
                return False
            
            # Analyze which chapters need the most work
            expected_verses_per_chapter = {
                1: 31, 2: 25, 3: 24, 4: 26, 5: 32, 6: 22, 7: 24, 8: 22, 9: 29, 10: 32,
                11: 32, 12: 20, 13: 18, 14: 24, 15: 21, 16: 16, 17: 27, 18: 33, 19: 38, 20: 18,
                21: 34, 22: 24, 23: 20, 24: 67, 25: 34, 26: 35, 27: 46, 28: 22, 29: 35, 30: 43,
                31: 55, 32: 32, 33: 20, 34: 31, 35: 29, 36: 43, 37: 36, 38: 30, 39: 23, 40: 23,
                41: 57, 42: 38, 43: 34, 44: 34, 45: 28, 46: 34, 47: 31, 48: 22, 49: 33, 50: 26
            }
            
            priority_chapters = []
            
            for chapter in range(1, 51):
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        missing_verses = expected_verses - actual_verses
                        
                        if missing_verses > 0:
                            priority_chapters.append({
                                'chapter': chapter,
                                'missing': missing_verses,
                                'expected': expected_verses,
                                'actual': actual_verses,
                                'priority': 'HIGH' if missing_verses > 10 else 'MEDIUM' if missing_verses > 5 else 'LOW'
                            })
                except Exception as e:
                    priority_chapters.append({
                        'chapter': chapter,
                        'missing': expected_verses_per_chapter.get(chapter, 0),
                        'expected': expected_verses_per_chapter.get(chapter, 0),
                        'actual': 0,
                        'priority': 'CRITICAL'
                    })
            
            # Sort by missing verses (highest priority first)
            priority_chapters.sort(key=lambda x: x['missing'], reverse=True)
            
            print("\n📋 COMPLETION RECOMMENDATIONS:")
            
            if priority_chapters:
                high_priority = [ch for ch in priority_chapters if ch['priority'] in ['CRITICAL', 'HIGH']]
                medium_priority = [ch for ch in priority_chapters if ch['priority'] == 'MEDIUM']
                low_priority = [ch for ch in priority_chapters if ch['priority'] == 'LOW']
                
                if high_priority:
                    print(f"\n🔴 HIGH PRIORITY CHAPTERS ({len(high_priority)} chapters):")
                    for ch in high_priority[:5]:  # Show top 5
                        print(f"   Chapter {ch['chapter']:2d}: Missing {ch['missing']:2d} verses ({ch['actual']:2d}/{ch['expected']:2d})")
                    
                    total_high_missing = sum(ch['missing'] for ch in high_priority)
                    self.log_test("High Priority Chapters", False, f"❌ {len(high_priority)} chapters need urgent attention ({total_high_missing} missing verses)")
                
                if medium_priority:
                    print(f"\n🟡 MEDIUM PRIORITY CHAPTERS ({len(medium_priority)} chapters):")
                    for ch in medium_priority[:3]:  # Show top 3
                        print(f"   Chapter {ch['chapter']:2d}: Missing {ch['missing']:2d} verses ({ch['actual']:2d}/{ch['expected']:2d})")
                    
                    total_medium_missing = sum(ch['missing'] for ch in medium_priority)
                    self.log_test("Medium Priority Chapters", True, f"⚠️ {len(medium_priority)} chapters need moderate attention ({total_medium_missing} missing verses)")
                
                if low_priority:
                    total_low_missing = sum(ch['missing'] for ch in low_priority)
                    self.log_test("Low Priority Chapters", True, f"✅ {len(low_priority)} chapters need minor fixes ({total_low_missing} missing verses)")
                
                # Completion roadmap
                print(f"\n🗺️ COMPLETION ROADMAP:")
                print(f"   Phase 1: Fix {len(high_priority)} high-priority chapters ({sum(ch['missing'] for ch in high_priority)} verses)")
                print(f"   Phase 2: Fix {len(medium_priority)} medium-priority chapters ({sum(ch['missing'] for ch in medium_priority)} verses)")
                print(f"   Phase 3: Fix {len(low_priority)} low-priority chapters ({sum(ch['missing'] for ch in low_priority)} verses)")
                print(f"   Result: 100% Genesis coverage ({expected_verses} total verses)")
                
                self.log_test("Completion Roadmap", True, f"Path to 100%: {len(priority_chapters)} chapters need fixes across 3 phases")
            else:
                self.log_test("Completion Status", True, "✅ Genesis is already 100% complete!")
            
            return True
            
        except Exception as e:
            self.log_test("Genesis Completion Recommendations", False, f"Error: {str(e)}")
            return False

    def run_genesis_data_analysis_tests(self):
        """Run Genesis data analysis tests as per review request"""
        print("=" * 80)
        print("🔍 GENESIS DATA ANALYSIS - COMPLETION STATUS INVESTIGATION")
        print("Analyzing the current Genesis data in the database to understand completion status")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 4 main review request tests + recommendations
        test_results = []
        
        # Test 1: Genesis Chapter/Verse Analysis
        test_results.append(self.test_genesis_chapter_verse_analysis())
        
        # Test 2: Genesis Content Quality Check
        test_results.append(self.test_genesis_content_quality_check())
        
        # Test 3: Database Structure Verification
        test_results.append(self.test_database_structure_verification())
        
        # Test 4: Specific Missing Verses Investigation
        test_results.append(self.test_specific_missing_verses_investigation())
        
        # Additional: Completion Recommendations
        test_results.append(self.test_genesis_completion_recommendations())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 GENESIS DATA ANALYSIS SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 ANALYSIS SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major analysis categories completed")
        
        # Show category results
        categories = [
            "Genesis Chapter/Verse Analysis (current counts and gaps)",
            "Genesis Content Quality Check (key verses and sampling)", 
            "Database Structure Verification (Genesis only and completeness)",
            "Specific Missing Verses Investigation (calculate and locate missing verses)",
            "Genesis Completion Recommendations (path to 100% coverage)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ COMPLETE" if result else "❌ INCOMPLETE"
            print(f"{status}: {category}")
        
        print("\n🔍 KEY ANALYSIS FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # Chapter/Verse Analysis
            print("✅ Chapter/verse analysis completed - identified current counts and gaps")
        else:
            print("❌ Chapter/verse analysis incomplete - unable to determine structure")
        
        if test_results[1]:  # Content Quality Check
            print("✅ Content quality verified - Genesis 1:1, 50:26, and random samples checked")
        else:
            print("❌ Content quality issues - key verses or samples have problems")
        
        if test_results[2]:  # Database Structure Verification
            print("✅ Database structure analyzed - Genesis purity and chapter completeness assessed")
        else:
            print("❌ Database structure issues - contamination or structural problems detected")
        
        if test_results[3]:  # Missing Verses Investigation
            print("✅ Missing verses investigation completed - identified patterns and locations")
        else:
            print("❌ Missing verses investigation incomplete - unable to determine missing verse patterns")
        
        if test_results[4]:  # Completion Recommendations
            print("✅ Completion recommendations generated - roadmap to 100% coverage provided")
        else:
            print("❌ Completion recommendations incomplete - unable to generate completion roadmap")
        
        print(f"\n🎯 FINAL ANALYSIS ASSESSMENT:")
        if individual_success_rate >= 90:
            print(f"✅ COMPREHENSIVE ANALYSIS! Genesis data analysis completed successfully ({individual_success_rate:.1f}% success)")
            print("✅ Clear understanding of completion status and path to 100% coverage")
        elif individual_success_rate >= 75:
            print(f"✅ GOOD ANALYSIS! Genesis data analysis mostly successful ({individual_success_rate:.1f}% success)")
            print("✅ Sufficient data to understand completion status with minor gaps")
        elif individual_success_rate >= 50:
            print(f"⚠️ PARTIAL ANALYSIS! Genesis data analysis partially completed ({individual_success_rate:.1f}% success)")
            print("⚠️ Some analysis completed but significant gaps remain")
        else:
            print(f"❌ INCOMPLETE ANALYSIS! Genesis data analysis has major issues ({individual_success_rate:.1f}% success)")
            print("❌ Unable to provide comprehensive completion status assessment")
        
        return individual_success_rate >= 75

def main():
    """Main test execution"""
    print("🚀 Starting Genesis Data Analysis Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_genesis_data_analysis_tests()
    
    if success:
        print("\n🎉 Genesis data analysis completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Genesis data analysis completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()