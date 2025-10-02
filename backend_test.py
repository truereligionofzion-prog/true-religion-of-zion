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

    def test_baseline_establishment(self):
        """REVIEW REQUEST TEST 4: Baseline Establishment - Total counts, chapter breakdown, starting point"""
        try:
            print("\n🔍 BASELINE ESTABLISHMENT - TOTAL COUNTS, CHAPTER BREAKDOWN, STARTING POINT...")
            
            # Get total count of Exodus verses currently in database
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1213  # Exodus should have 1,213 verses total
                    
                    if total_verses > 0:
                        completion_percentage = (total_verses / expected_verses) * 100
                        self.log_test("Exodus Total Verse Count Baseline", True, f"BASELINE: {total_verses} verses currently in database ({completion_percentage:.1f}% of expected {expected_verses})")
                    else:
                        self.log_test("Exodus Total Verse Count Baseline", True, f"BASELINE: 0 verses in database - Starting from scratch (0% of expected {expected_verses})")
                else:
                    self.log_test("Exodus Total Verse Count Baseline", False, f"API Error - Status: {response.status_code}")
            except Exception as e:
                self.log_test("Exodus Total Verse Count Baseline", False, f"Error: {str(e)}")
            
            # Provide chapter-by-chapter breakdown if data exists
            expected_verses_per_chapter = {
                1: 22, 2: 25, 3: 22, 4: 31, 5: 23, 6: 30, 7: 25, 8: 32, 9: 35, 10: 29,
                11: 10, 12: 51, 13: 22, 14: 31, 15: 27, 16: 36, 17: 16, 18: 27, 19: 25, 20: 26,
                21: 36, 22: 31, 23: 33, 24: 18, 25: 40, 26: 37, 27: 21, 28: 43, 29: 46, 30: 38,
                31: 18, 32: 35, 33: 23, 34: 35, 35: 35, 36: 38, 37: 29, 38: 31, 39: 43, 40: 38
            }
            
            print("\n📊 DETAILED CHAPTER-BY-CHAPTER BASELINE BREAKDOWN:")
            
            chapter_status = {
                'complete': [],
                'partial': [],
                'missing': [],
                'total_present': 0,
                'total_missing': 0
            }
            
            for chapter in range(1, 41):  # Exodus has 40 chapters
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Exodus&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        
                        if actual_verses == expected_verses:
                            chapter_status['complete'].append(chapter)
                            chapter_status['total_present'] += actual_verses
                            print(f"   ✅ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - COMPLETE")
                        elif actual_verses > 0:
                            chapter_status['partial'].append({
                                'chapter': chapter,
                                'actual': actual_verses,
                                'expected': expected_verses,
                                'missing': expected_verses - actual_verses
                            })
                            chapter_status['total_present'] += actual_verses
                            chapter_status['total_missing'] += (expected_verses - actual_verses)
                            print(f"   ⚠️ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - PARTIAL (need {expected_verses - actual_verses} more)")
                        else:
                            chapter_status['missing'].append({
                                'chapter': chapter,
                                'expected': expected_verses
                            })
                            chapter_status['total_missing'] += expected_verses
                            print(f"   ❌ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses - MISSING (need all {expected_verses})")
                        
                    else:
                        chapter_status['missing'].append({
                            'chapter': chapter,
                            'expected': expected_verses_per_chapter.get(chapter, 0)
                        })
                        chapter_status['total_missing'] += expected_verses_per_chapter.get(chapter, 0)
                        print(f"   ❌ Chapter {chapter:2d}: API ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    chapter_status['missing'].append({
                        'chapter': chapter,
                        'expected': expected_verses_per_chapter.get(chapter, 0)
                    })
                    chapter_status['total_missing'] += expected_verses_per_chapter.get(chapter, 0)
                    print(f"   ❌ Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Summary of chapter breakdown
            complete_count = len(chapter_status['complete'])
            partial_count = len(chapter_status['partial'])
            missing_count = len(chapter_status['missing'])
            
            self.log_test("Chapter Breakdown Summary", True, f"Complete: {complete_count}/40, Partial: {partial_count}/40, Missing: {missing_count}/40")
            self.log_test("Verse Count Summary", True, f"Present: {chapter_status['total_present']}, Missing: {chapter_status['total_missing']}, Total Expected: 1213")
            
            # Identify the starting point for Exodus completion
            if complete_count == 40:
                starting_point = "Exodus is 100% complete - no work needed"
                self.log_test("Exodus Completion Starting Point", True, f"✅ COMPLETE! {starting_point}")
            elif complete_count == 0 and partial_count == 0:
                starting_point = "Start from scratch - no Exodus data exists"
                self.log_test("Exodus Completion Starting Point", True, f"🚀 FRESH START! {starting_point}")
            elif partial_count > 0:
                first_partial = chapter_status['partial'][0]
                starting_point = f"Continue from Chapter {first_partial['chapter']} (has {first_partial['actual']}/{first_partial['expected']} verses)"
                self.log_test("Exodus Completion Starting Point", True, f"⚠️ PARTIAL DATA! {starting_point}")
            else:
                first_missing = chapter_status['missing'][0]['chapter'] if chapter_status['missing'] else 1
                starting_point = f"Continue from Chapter {first_missing} (first missing chapter)"
                self.log_test("Exodus Completion Starting Point", True, f"📍 CONTINUE FROM! {starting_point}")
            
            # Provide completion strategy recommendation
            if chapter_status['total_missing'] > 0:
                completion_percentage = (chapter_status['total_present'] / 1213) * 100
                
                if completion_percentage == 0:
                    strategy = "Apply Genesis completion formula from the beginning - load all 1,213 verses across 40 chapters"
                elif completion_percentage < 50:
                    strategy = f"Apply Genesis completion formula to fill {chapter_status['total_missing']} missing verses - focus on missing chapters first"
                else:
                    strategy = f"Apply targeted completion to fill remaining {chapter_status['total_missing']} verses - focus on partial chapters"
                
                self.log_test("Completion Strategy Recommendation", True, f"STRATEGY: {strategy}")
            else:
                self.log_test("Completion Strategy Recommendation", True, f"STRATEGY: Exodus is complete - no action needed")
            
            return True
            
        except Exception as e:
            self.log_test("Baseline Establishment", False, f"Error: {str(e)}")
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