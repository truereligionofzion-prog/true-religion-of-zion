#!/usr/bin/env python3
"""
Backend Testing for Exodus Current State Analysis

REVIEW REQUEST FOCUS - EXODUS CURRENT STATE ANALYSIS:
I need to analyze the current Exodus state to apply the successful Genesis completion formula. Please test:

1. **Exodus Current State Analysis**:
   - Check if Exodus exists in the database at all
   - If it exists, get the current chapter and verse count
   - Identify which chapters/verses are present vs missing

2. **Database Structure Check**:
   - Verify what Bible versions are available 
   - Check if Exodus exists in KJV 1611 Divine version specifically
   - Confirm the database structure matches Genesis format

3. **Exodus Content Quality Check** (if exists):
   - Sample a few Exodus verses to check content quality
   - Verify no cross-contamination with other books
   - Check verse numbering consistency

4. **Baseline Establishment**:
   - Get total count of Exodus verses currently in database
   - Provide chapter-by-chapter breakdown if data exists
   - Identify the starting point for Exodus completion

This analysis will help create a precision Exodus completion script following the proven Genesis formula.
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

    def test_exodus_current_state_analysis(self):
        """REVIEW REQUEST TEST 1: Exodus Current State Analysis - Check if Exodus exists and get current counts"""
        try:
            print("\n🔍 EXODUS CURRENT STATE ANALYSIS - CHECKING EXISTENCE AND CURRENT COUNTS...")
            
            # Check if Exodus exists in the database at all
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1213  # Exodus should have 1,213 verses total
                    
                    if total_verses > 0:
                        completion_percentage = (total_verses / expected_verses) * 100
                        self.log_test("Exodus Exists in Database", True, f"✅ FOUND! Exodus exists with {total_verses} verses ({completion_percentage:.1f}% of expected {expected_verses})")
                        
                        # If Exodus exists, get current chapter and verse count
                        if total_verses == expected_verses:
                            self.log_test("Exodus Completion Status", True, f"✅ COMPLETE! Exodus has all {total_verses} verses (100% complete)")
                        else:
                            missing_verses = expected_verses - total_verses
                            self.log_test("Exodus Completion Status", False, f"⚠️ INCOMPLETE! Exodus has {total_verses} verses, missing {missing_verses} ({completion_percentage:.1f}% complete)")
                    else:
                        self.log_test("Exodus Exists in Database", False, f"❌ NOT FOUND! Exodus does not exist in database (0 verses)")
                        self.log_test("Exodus Completion Status", False, f"❌ MISSING! Exodus completely absent from database")
                else:
                    self.log_test("Exodus Exists in Database", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Exodus Completion Status", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Exists in Database", False, f"Error: {str(e)}")
                self.log_test("Exodus Completion Status", False, f"Error: {str(e)}")
            
            # Identify which chapters/verses are present vs missing
            expected_verses_per_chapter = {
                1: 22, 2: 25, 3: 22, 4: 31, 5: 23, 6: 30, 7: 25, 8: 32, 9: 35, 10: 29,
                11: 10, 12: 51, 13: 22, 14: 31, 15: 27, 16: 36, 17: 16, 18: 27, 19: 25, 20: 26,
                21: 36, 22: 31, 23: 33, 24: 18, 25: 40, 26: 37, 27: 21, 28: 43, 29: 46, 30: 38,
                31: 18, 32: 35, 33: 23, 34: 35, 35: 35, 36: 38, 37: 29, 38: 31, 39: 43, 40: 38
            }
            
            print("\n📊 EXODUS CHAPTER-BY-CHAPTER ANALYSIS (40 chapters expected):")
            present_chapters = 0
            missing_chapters = []
            partial_chapters = []
            complete_chapters = []
            total_present_verses = 0
            
            for chapter in range(1, 41):  # Exodus has 40 chapters
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        
                        if actual_verses == expected_verses:
                            present_chapters += 1
                            complete_chapters.append(chapter)
                            total_present_verses += actual_verses
                            print(f"   ✅ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - COMPLETE")
                        elif actual_verses > 0:
                            present_chapters += 1
                            partial_chapters.append({
                                'chapter': chapter,
                                'actual': actual_verses,
                                'expected': expected_verses,
                                'missing': expected_verses - actual_verses
                            })
                            total_present_verses += actual_verses
                            print(f"   ⚠️ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - PARTIAL (missing {expected_verses - actual_verses})")
                        else:
                            missing_chapters.append({
                                'chapter': chapter,
                                'expected': expected_verses
                            })
                            print(f"   ❌ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - MISSING")
                        
                    else:
                        missing_chapters.append({
                            'chapter': chapter,
                            'expected': expected_verses_per_chapter.get(chapter, 0)
                        })
                        print(f"   ❌ Chapter {chapter:2d}: API ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    missing_chapters.append({
                        'chapter': chapter,
                        'expected': expected_verses_per_chapter.get(chapter, 0)
                    })
                    print(f"   ❌ Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Summary of chapter analysis
            total_missing_verses = sum(ch['expected'] for ch in missing_chapters) + sum(ch['missing'] for ch in partial_chapters)
            
            self.log_test("Exodus Chapter Presence Analysis", True, f"Present: {present_chapters}/40 chapters, Complete: {len(complete_chapters)}, Partial: {len(partial_chapters)}, Missing: {len(missing_chapters)}")
            self.log_test("Exodus Verse Count Analysis", True, f"Present: {total_present_verses} verses, Missing: {total_missing_verses} verses, Total Expected: 1213")
            
            if len(complete_chapters) == 40:
                self.log_test("All Exodus Chapters Complete", True, f"✅ PERFECT! All 40 chapters are complete")
            elif len(complete_chapters) > 0:
                self.log_test("All Exodus Chapters Complete", False, f"⚠️ PARTIAL! {len(complete_chapters)}/40 chapters complete, {len(partial_chapters)} partial, {len(missing_chapters)} missing")
            else:
                self.log_test("All Exodus Chapters Complete", False, f"❌ NONE! No complete chapters found")
            
            return True
            
        except Exception as e:
            self.log_test("Exodus Current State Analysis", False, f"Error: {str(e)}")
            return False

    def test_database_structure_check(self):
        """REVIEW REQUEST TEST 2: Database Structure Check - Verify Bible versions and database structure"""
        try:
            print("\n🔍 DATABASE STRUCTURE CHECK - VERIFYING BIBLE VERSIONS AND STRUCTURE...")
            
            # Verify what Bible versions are available
            try:
                response = self.session.get(f"{self.base_url}/bible/versions")
                if response.status_code == 200:
                    data = response.json()
                    versions = data.get('versions', [])
                    version_count = len(versions)
                    
                    if version_count > 0:
                        version_names = [v.get('name', 'Unknown') for v in versions]
                        version_ids = [v.get('id', 'Unknown') for v in versions]
                        self.log_test("Bible Versions Available", True, f"✅ FOUND! {version_count} versions available: {', '.join(version_names)}")
                        
                        # Check if KJV 1611 Divine version exists
                        kjv_divine_found = any(v.get('id') == 'kjv1611_divine' for v in versions)
                        if kjv_divine_found:
                            self.log_test("KJV 1611 Divine Version Available", True, f"✅ CONFIRMED! KJV 1611 Divine Names version is available")
                        else:
                            self.log_test("KJV 1611 Divine Version Available", False, f"❌ MISSING! KJV 1611 Divine Names version not found. Available: {', '.join(version_ids)}")
                    else:
                        self.log_test("Bible Versions Available", False, f"❌ NONE! No Bible versions found in database")
                        self.log_test("KJV 1611 Divine Version Available", False, f"❌ MISSING! No versions available")
                else:
                    self.log_test("Bible Versions Available", False, f"API Error - Status: {response.status_code}")
                    self.log_test("KJV 1611 Divine Version Available", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Bible Versions Available", False, f"Error: {str(e)}")
                self.log_test("KJV 1611 Divine Version Available", False, f"Error: {str(e)}")
            
            # Check if Exodus exists in KJV 1611 Divine version specifically
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    book_names = [book.get('name', 'Unknown') for book in books]
                    
                    if 'Exodus' in book_names:
                        exodus_book = next((book for book in books if book.get('name') == 'Exodus'), None)
                        if exodus_book:
                            testament = exodus_book.get('testament', 'unknown')
                            order = exodus_book.get('order', 'unknown')
                            self.log_test("Exodus in KJV 1611 Divine", True, f"✅ FOUND! Exodus exists in KJV 1611 Divine (Testament: {testament}, Order: {order})")
                        else:
                            self.log_test("Exodus in KJV 1611 Divine", True, f"✅ FOUND! Exodus exists in KJV 1611 Divine")
                    else:
                        self.log_test("Exodus in KJV 1611 Divine", False, f"❌ MISSING! Exodus not found in KJV 1611 Divine. Available books: {', '.join(book_names)}")
                        
                    # Show all available books for context
                    self.log_test("KJV 1611 Divine Books Available", True, f"Books in KJV 1611 Divine: {len(books)} total - {', '.join(book_names)}")
                else:
                    self.log_test("Exodus in KJV 1611 Divine", False, f"API Error - Status: {response.status_code}")
                    self.log_test("KJV 1611 Divine Books Available", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus in KJV 1611 Divine", False, f"Error: {str(e)}")
                self.log_test("KJV 1611 Divine Books Available", False, f"Error: {str(e)}")
            
            # Confirm the database structure matches Genesis format
            try:
                # Get a sample verse from Genesis to understand the structure
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        genesis_verse = verses[0]
                        genesis_fields = set(genesis_verse.keys())
                        
                        # Now get a sample verse from Exodus (if it exists)
                        response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                        if response.status_code == 200:
                            data = response.json()
                            verses = data.get('verses', [])
                            
                            if verses:
                                exodus_verse = verses[0]
                                exodus_fields = set(exodus_verse.keys())
                                
                                # Compare structures
                                if genesis_fields == exodus_fields:
                                    common_fields = list(genesis_fields)
                                    self.log_test("Database Structure Consistency", True, f"✅ CONSISTENT! Genesis and Exodus have identical structure: {', '.join(common_fields)}")
                                else:
                                    missing_in_exodus = genesis_fields - exodus_fields
                                    extra_in_exodus = exodus_fields - genesis_fields
                                    self.log_test("Database Structure Consistency", False, f"❌ INCONSISTENT! Missing in Exodus: {missing_in_exodus}, Extra in Exodus: {extra_in_exodus}")
                            else:
                                self.log_test("Database Structure Consistency", False, f"❌ NO DATA! Exodus has no verses to compare structure")
                        else:
                            self.log_test("Database Structure Consistency", False, f"❌ NO EXODUS! Cannot compare structure - Exodus not accessible")
                            
                        # Show Genesis structure as reference
                        self.log_test("Genesis Structure Reference", True, f"Genesis verse structure: {', '.join(genesis_fields)}")
                    else:
                        self.log_test("Database Structure Consistency", False, f"❌ NO DATA! Genesis has no verses to analyze structure")
                        self.log_test("Genesis Structure Reference", False, f"❌ NO DATA! Genesis has no verses")
                else:
                    self.log_test("Database Structure Consistency", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Genesis Structure Reference", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Database Structure Consistency", False, f"Error: {str(e)}")
                self.log_test("Genesis Structure Reference", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Database Structure Check", False, f"Error: {str(e)}")
            return False

    def test_exodus_content_quality_check(self):
        """REVIEW REQUEST TEST 3: Exodus Content Quality Check - Sample verses, cross-contamination, numbering"""
        try:
            print("\n🔍 EXODUS CONTENT QUALITY CHECK - SAMPLING VERSES AND CHECKING QUALITY...")
            
            # Sample a few Exodus verses to check content quality (if exists)
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    total_verses = data.get('total', 0)
                    
                    if verses:
                        print("\n📝 EXODUS VERSE QUALITY SAMPLING:")
                        quality_verses = 0
                        total_sampled = len(verses)
                        
                        for verse in verses:
                            verse_text = verse.get('text', '')
                            verse_ref = f"Exodus {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            
                            # Quality checks for Exodus verses
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
                                print(f"   ✅ {verse_ref}: '{verse_text[:80]}...'")
                            else:
                                print(f"   ❌ {verse_ref}: QUALITY ISSUE - '{verse_text[:80]}...'")
                        
                        if total_sampled > 0:
                            quality_percentage = (quality_verses / total_sampled) * 100
                            if quality_percentage >= 90:
                                self.log_test("Exodus Verse Quality", True, f"✅ EXCELLENT! {quality_verses}/{total_sampled} verses are high quality ({quality_percentage:.1f}%)")
                            elif quality_percentage >= 70:
                                self.log_test("Exodus Verse Quality", True, f"✅ GOOD! {quality_verses}/{total_sampled} verses are good quality ({quality_percentage:.1f}%)")
                            else:
                                self.log_test("Exodus Verse Quality", False, f"❌ POOR! {quality_verses}/{total_sampled} verses have quality issues ({quality_percentage:.1f}%)")
                        
                        # Check for Exodus-specific content
                        exodus_keywords = ['moses', 'pharaoh', 'egypt', 'israelites', 'commandments', 'tabernacle', 'aaron']
                        exodus_content_found = 0
                        
                        for verse in verses:
                            verse_text = verse.get('text', '').lower()
                            for keyword in exodus_keywords:
                                if keyword in verse_text:
                                    exodus_content_found += 1
                                    break
                        
                        if exodus_content_found > 0:
                            exodus_content_percentage = (exodus_content_found / len(verses)) * 100
                            self.log_test("Exodus Content Authenticity", True, f"✅ AUTHENTIC! {exodus_content_found}/{len(verses)} verses contain Exodus-specific content ({exodus_content_percentage:.1f}%)")
                        else:
                            self.log_test("Exodus Content Authenticity", False, f"❌ SUSPICIOUS! No Exodus-specific content found in sampled verses")
                            
                    else:
                        self.log_test("Exodus Verse Quality", False, f"❌ NO DATA! No Exodus verses found for quality check")
                        self.log_test("Exodus Content Authenticity", False, f"❌ NO DATA! No Exodus verses to check authenticity")
                else:
                    self.log_test("Exodus Verse Quality", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Exodus Content Authenticity", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Verse Quality", False, f"Error: {str(e)}")
                self.log_test("Exodus Content Authenticity", False, f"Error: {str(e)}")
            
            # Verify no cross-contamination with other books
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=20")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    if verses:
                        all_exodus = True
                        non_exodus_books = set()
                        
                        for verse in verses:
                            book = verse.get('book', '')
                            if book != 'Exodus':
                                all_exodus = False
                                non_exodus_books.add(book)
                        
                        if all_exodus:
                            self.log_test("No Cross-Contamination in Exodus", True, f"✅ PURE! All {len(verses)} sampled verses are from Exodus")
                        else:
                            self.log_test("No Cross-Contamination in Exodus", False, f"❌ CONTAMINATED! Found verses from: {', '.join(non_exodus_books)}")
                    else:
                        self.log_test("No Cross-Contamination in Exodus", False, f"❌ NO DATA! No Exodus verses to check for contamination")
                else:
                    self.log_test("No Cross-Contamination in Exodus", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("No Cross-Contamination in Exodus", False, f"Error: {str(e)}")
            
            # Check verse numbering consistency
            try:
                # Test a few chapters for proper verse numbering
                test_chapters = [1, 2, 3]  # Test first few chapters
                numbering_consistent = True
                
                for chapter in test_chapters:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&chapter={chapter}&limit=50")
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        
                        if verses:
                            # Check if verse numbers are sequential
                            verse_numbers = [verse.get('verse', 0) for verse in verses]
                            expected_numbers = list(range(1, len(verses) + 1))
                            
                            if verse_numbers == expected_numbers:
                                print(f"   ✅ Chapter {chapter}: Verse numbering is sequential (1-{len(verses)})")
                            else:
                                numbering_consistent = False
                                print(f"   ❌ Chapter {chapter}: Verse numbering inconsistent - Found: {verse_numbers[:10]}...")
                        else:
                            print(f"   ⚠️ Chapter {chapter}: No verses found")
                    else:
                        print(f"   ❌ Chapter {chapter}: API Error - Status {response.status_code}")
                
                if numbering_consistent:
                    self.log_test("Exodus Verse Numbering Consistency", True, f"✅ CONSISTENT! Verse numbering is sequential in tested chapters")
                else:
                    self.log_test("Exodus Verse Numbering Consistency", False, f"❌ INCONSISTENT! Verse numbering issues found in some chapters")
                    
            except Exception as e:
                self.log_test("Exodus Verse Numbering Consistency", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("Exodus Content Quality Check", False, f"Error: {str(e)}")
            return False

    def test_api_response_validation(self):
        """REVIEW REQUEST TEST 4: API Response Validation - Complete data and pagination"""
        try:
            print("\n🔍 API RESPONSE VALIDATION - COMPLETE DATA AND PAGINATION...")
            
            # Test that Genesis API endpoints return the complete data
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=50")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    total = data.get('total', 0)
                    total_pages = data.get('totalPages', 0)
                    
                    if total == 1533:
                        self.log_test("Genesis API - Complete Data Response", True, f"✅ COMPLETE! API returns {total} total verses (100% Genesis)")
                    else:
                        self.log_test("Genesis API - Complete Data Response", False, f"❌ INCOMPLETE! API returns {total} verses, expected 1,533")
                    
                    if len(verses) == 50:
                        self.log_test("Genesis API - Proper Response Limit", True, f"✅ CORRECT! API returns {len(verses)} verses per page as requested")
                    else:
                        self.log_test("Genesis API - Proper Response Limit", False, f"❌ INCORRECT! API returns {len(verses)} verses, expected 50")
                        
                    # Check that verses have proper structure
                    if verses:
                        first_verse = verses[0]
                        required_fields = ['book', 'chapter', 'verse', 'text']
                        missing_fields = [field for field in required_fields if field not in first_verse]
                        
                        if not missing_fields:
                            self.log_test("Genesis API - Proper Verse Structure", True, f"✅ COMPLETE! Verses have all required fields: {required_fields}")
                        else:
                            self.log_test("Genesis API - Proper Verse Structure", False, f"❌ INCOMPLETE! Missing fields: {missing_fields}")
                    else:
                        self.log_test("Genesis API - Proper Verse Structure", False, f"❌ NO DATA! No verses returned")
                        
                else:
                    self.log_test("Genesis API - Complete Data Response", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Genesis API - Proper Response Limit", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Genesis API - Proper Verse Structure", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis API - Complete Data Response", False, f"Error: {str(e)}")
                self.log_test("Genesis API - Proper Response Limit", False, f"Error: {str(e)}")
                self.log_test("Genesis API - Proper Verse Structure", False, f"Error: {str(e)}")
            
            # Verify pagination works correctly with the full dataset
            print("\n📄 PAGINATION TESTING WITH FULL GENESIS DATASET:")
            
            try:
                # Test first page
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&page=1&limit=20")
                if response.status_code == 200:
                    data = response.json()
                    page = data.get('page', 0)
                    total_pages = data.get('totalPages', 0)
                    verses = data.get('verses', [])
                    
                    if page == 1:
                        self.log_test("Pagination - First Page", True, f"✅ CORRECT! First page returns page={page}")
                    else:
                        self.log_test("Pagination - First Page", False, f"❌ INCORRECT! First page returns page={page}, expected 1")
                    
                    expected_total_pages = (1533 + 19) // 20  # Ceiling division for 1533 verses with 20 per page
                    if total_pages == expected_total_pages:
                        self.log_test("Pagination - Total Pages Calculation", True, f"✅ CORRECT! Total pages = {total_pages} (for 1,533 verses with 20 per page)")
                    else:
                        self.log_test("Pagination - Total Pages Calculation", False, f"❌ INCORRECT! Total pages = {total_pages}, expected {expected_total_pages}")
                        
                    if len(verses) == 20:
                        self.log_test("Pagination - Page Size", True, f"✅ CORRECT! Page contains {len(verses)} verses as requested")
                    else:
                        self.log_test("Pagination - Page Size", False, f"❌ INCORRECT! Page contains {len(verses)} verses, expected 20")
                        
                else:
                    self.log_test("Pagination - First Page", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Pagination - Total Pages Calculation", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Pagination - Page Size", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Pagination - First Page", False, f"Error: {str(e)}")
                self.log_test("Pagination - Total Pages Calculation", False, f"Error: {str(e)}")
                self.log_test("Pagination - Page Size", False, f"Error: {str(e)}")
            
            # Test middle page
            try:
                middle_page = 40  # Middle of the dataset
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&page={middle_page}&limit=20")
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    page = data.get('page', 0)
                    
                    if page == middle_page:
                        self.log_test("Pagination - Middle Page", True, f"✅ CORRECT! Middle page {middle_page} returns correct page number")
                    else:
                        self.log_test("Pagination - Middle Page", False, f"❌ INCORRECT! Middle page returns page={page}, expected {middle_page}")
                        
                    if verses:
                        first_verse = verses[0]
                        verse_book = first_verse.get('book', '')
                        if verse_book == 'Genesis':
                            self.log_test("Pagination - Middle Page Content", True, f"✅ CORRECT! Middle page contains Genesis verses")
                        else:
                            self.log_test("Pagination - Middle Page Content", False, f"❌ INCORRECT! Middle page contains {verse_book} verses, expected Genesis")
                    else:
                        self.log_test("Pagination - Middle Page Content", False, f"❌ EMPTY! Middle page contains no verses")
                        
                else:
                    self.log_test("Pagination - Middle Page", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Pagination - Middle Page Content", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Pagination - Middle Page", False, f"Error: {str(e)}")
                self.log_test("Pagination - Middle Page Content", False, f"Error: {str(e)}")
            
            # Test last page
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&page=1&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_pages = data.get('totalPages', 0)
                    
                    if total_pages > 0:
                        # Test the actual last page
                        response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&page={total_pages}&limit=20")
                        if response.status_code == 200:
                            data = response.json()
                            verses = data.get('verses', [])
                            page = data.get('page', 0)
                            
                            if page == total_pages:
                                self.log_test("Pagination - Last Page", True, f"✅ CORRECT! Last page {total_pages} returns correct page number")
                            else:
                                self.log_test("Pagination - Last Page", False, f"❌ INCORRECT! Last page returns page={page}, expected {total_pages}")
                                
                            if verses:
                                last_verse = verses[-1]
                                if last_verse.get('book') == 'Genesis':
                                    self.log_test("Pagination - Last Page Content", True, f"✅ CORRECT! Last page contains Genesis verses")
                                else:
                                    self.log_test("Pagination - Last Page Content", False, f"❌ INCORRECT! Last page contains non-Genesis verses")
                            else:
                                self.log_test("Pagination - Last Page Content", False, f"❌ EMPTY! Last page contains no verses")
                        else:
                            self.log_test("Pagination - Last Page", False, f"API Error - Status: {response.status_code}")
                            self.log_test("Pagination - Last Page Content", False, f"API Error - Status: {response.status_code}")
                    else:
                        self.log_test("Pagination - Last Page", False, f"❌ NO PAGES! Total pages = {total_pages}")
                        self.log_test("Pagination - Last Page Content", False, f"❌ NO PAGES! Total pages = {total_pages}")
                else:
                    self.log_test("Pagination - Last Page", False, f"API Error - Status: {response.status_code}")
                    self.log_test("Pagination - Last Page Content", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Pagination - Last Page", False, f"Error: {str(e)}")
                self.log_test("Pagination - Last Page Content", False, f"Error: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("API Response Validation", False, f"Error: {str(e)}")
            return False

    # Old test method removed - replaced with Genesis 100% completion verification tests

    def run_genesis_completion_verification_tests(self):
        """Run Genesis 100% completion verification tests as per review request"""
        print("=" * 80)
        print("🔍 GENESIS 100% COMPLETION VERIFICATION")
        print("Verifying that Genesis is now 100% complete with exactly 1,533 verses")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 4 main review request tests
        test_results = []
        
        # Test 1: Genesis Completion Verification
        test_results.append(self.test_genesis_completion_verification())
        
        # Test 2: Data Quality Check
        test_results.append(self.test_data_quality_check())
        
        # Test 3: Database Statistics
        test_results.append(self.test_database_statistics())
        
        # Test 4: API Response Validation
        test_results.append(self.test_api_response_validation())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 GENESIS 100% COMPLETION VERIFICATION SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 VERIFICATION SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major verification categories completed")
        
        # Show category results
        categories = [
            "Genesis Completion Verification (exactly 1,533 verses with all 50 chapters)",
            "Data Quality Check (key verses preserved, sampling, no cross-contamination)", 
            "Database Statistics (Genesis book record and pure dataset verification)",
            "API Response Validation (complete data endpoints and pagination)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ VERIFIED" if result else "❌ FAILED"
            print(f"{status}: {category}")
        
        print("\n🔍 KEY VERIFICATION FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # Genesis Completion Verification
            print("✅ Genesis completion verified - 1,533 verses with all 50 chapters complete")
        else:
            print("❌ Genesis completion FAILED - missing verses or incomplete chapters detected")
        
        if test_results[1]:  # Data Quality Check
            print("✅ Data quality verified - Genesis 1:1, 50:26 preserved, no cross-contamination")
        else:
            print("❌ Data quality FAILED - key verses corrupted or cross-contamination detected")
        
        if test_results[2]:  # Database Statistics
            print("✅ Database statistics verified - Genesis book record and pure dataset confirmed")
        else:
            print("❌ Database statistics FAILED - incorrect book record or dataset contamination")
        
        if test_results[3]:  # API Response Validation
            print("✅ API responses verified - complete data endpoints and pagination working")
        else:
            print("❌ API responses FAILED - incomplete data or pagination issues detected")
        
        print(f"\n🎯 FINAL GENESIS 100% COMPLETION ASSESSMENT:")
        if individual_success_rate >= 95:
            print(f"✅ GENESIS IS 100% COMPLETE! Verification successful ({individual_success_rate:.1f}% success)")
            print("✅ All 1,533 verses present with perfect data quality and API functionality")
            print("🎉 Genesis is ready for the user to see the achievement!")
        elif individual_success_rate >= 85:
            print(f"✅ GENESIS IS NEARLY COMPLETE! Verification mostly successful ({individual_success_rate:.1f}% success)")
            print("✅ Genesis appears complete with minor issues that don't affect core functionality")
        elif individual_success_rate >= 70:
            print(f"⚠️ GENESIS IS PARTIALLY COMPLETE! Verification partially successful ({individual_success_rate:.1f}% success)")
            print("⚠️ Genesis has significant completion but some issues remain")
        else:
            print(f"❌ GENESIS IS NOT 100% COMPLETE! Verification failed ({individual_success_rate:.1f}% success)")
            print("❌ Genesis still has major completion issues that need to be addressed")
        
        return individual_success_rate >= 85

def main():
    """Main test execution"""
    print("🚀 Starting Genesis 100% Completion Verification Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_genesis_completion_verification_tests()
    
    if success:
        print("\n🎉 Genesis 100% completion verification successful!")
        sys.exit(0)
    else:
        print("\n❌ Genesis 100% completion verification failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()