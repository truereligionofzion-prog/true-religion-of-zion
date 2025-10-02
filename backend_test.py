#!/usr/bin/env python3
"""
Backend Testing for Genesis Data Analysis - COMPLETION STATUS INVESTIGATION

REVIEW REQUEST FOCUS - GENESIS DATA ANALYSIS:
Analyze the current Genesis data in the database to understand the completion status:

1. **Genesis Chapter/Verse Analysis**: 
   - Get the current chapter count and verse count for Genesis
   - Check which chapters might have fewer verses than expected
   - Identify any gaps in verse numbering within chapters

2. **Genesis Content Quality Check**:
   - Verify that Genesis 1:1 contains the expected creation text
   - Check Genesis 50:26 (last verse) to ensure we have the complete book
   - Sample a few random verses to ensure content quality

3. **Database Structure Verification**:
   - Confirm we only have Genesis data (no cross-contamination)
   - Check the verse count per chapter to identify any incomplete chapters

4. **Specific Missing Verses Investigation**:
   - Calculate which 38 verses are missing (1533 - 1495 = 38)
   - Check if certain chapters are truncated or if verses are scattered missing

This analysis will provide detailed insights into what needs to be completed to reach 100% Genesis coverage.
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

    def test_genesis_chapter_verse_analysis(self):
        """REVIEW REQUEST TEST 1: Genesis Chapter/Verse Analysis - Current counts and gaps"""
        try:
            print("\n🔍 GENESIS CHAPTER/VERSE ANALYSIS - CURRENT COUNTS AND GAPS...")
            
            # Get overall Genesis statistics
            try:
                response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&limit=1")
                if response.status_code == 200:
                    data = response.json()
                    total_verses = data.get('total', 0)
                    expected_verses = 1533
                    missing_verses = expected_verses - total_verses
                    
                    self.log_test("Genesis Total Verse Count", True, f"Current: {total_verses} verses, Expected: {expected_verses}, Missing: {missing_verses}")
                else:
                    self.log_test("Genesis Total Verse Count", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis Total Verse Count", False, f"Error: {str(e)}")
            
            # Analyze chapter structure - get all chapters
            chapter_analysis = {}
            expected_verses_per_chapter = {
                1: 31, 2: 25, 3: 24, 4: 26, 5: 32, 6: 22, 7: 24, 8: 22, 9: 29, 10: 32,
                11: 32, 12: 20, 13: 18, 14: 24, 15: 21, 16: 16, 17: 27, 18: 33, 19: 38, 20: 18,
                21: 34, 22: 24, 23: 20, 24: 67, 25: 34, 26: 35, 27: 46, 28: 22, 29: 35, 30: 43,
                31: 55, 32: 32, 33: 20, 34: 31, 35: 29, 36: 43, 37: 36, 38: 30, 39: 23, 40: 23,
                41: 57, 42: 38, 43: 34, 44: 34, 45: 28, 46: 34, 47: 31, 48: 22, 49: 33, 50: 26
            }
            
            print("\n📊 CHAPTER-BY-CHAPTER ANALYSIS:")
            chapters_with_issues = []
            
            for chapter in range(1, 51):  # Genesis has 50 chapters
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        
                        chapter_analysis[chapter] = {
                            'actual': actual_verses,
                            'expected': expected_verses,
                            'missing': expected_verses - actual_verses
                        }
                        
                        if actual_verses < expected_verses:
                            chapters_with_issues.append(chapter)
                            status = "❌ INCOMPLETE"
                        elif actual_verses == expected_verses:
                            status = "✅ COMPLETE"
                        else:
                            status = "⚠️ EXTRA"
                        
                        print(f"   Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses {status}")
                        
                    else:
                        chapter_analysis[chapter] = {'actual': 0, 'expected': expected_verses_per_chapter.get(chapter, 0), 'missing': expected_verses_per_chapter.get(chapter, 0)}
                        chapters_with_issues.append(chapter)
                        print(f"   Chapter {chapter:2d}: ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    chapter_analysis[chapter] = {'actual': 0, 'expected': expected_verses_per_chapter.get(chapter, 0), 'missing': expected_verses_per_chapter.get(chapter, 0)}
                    chapters_with_issues.append(chapter)
                    print(f"   Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Summary of chapter analysis
            complete_chapters = sum(1 for ch in chapter_analysis.values() if ch['actual'] == ch['expected'])
            incomplete_chapters = sum(1 for ch in chapter_analysis.values() if ch['actual'] < ch['expected'])
            
            self.log_test("Chapter Completeness Analysis", True, f"Complete: {complete_chapters}/50 chapters, Incomplete: {incomplete_chapters}/50 chapters")
            
            if chapters_with_issues:
                self.log_test("Chapters with Missing Verses", False, f"Chapters with issues: {chapters_with_issues[:10]}{'...' if len(chapters_with_issues) > 10 else ''}")
            else:
                self.log_test("Chapters with Missing Verses", True, "All chapters have expected verse counts")
            
            return True
            
        except Exception as e:
            self.log_test("Genesis Chapter/Verse Analysis", False, f"Error: {str(e)}")
            return False

    def test_genesis_content_quality_check(self):
        """REVIEW REQUEST TEST 2: Genesis Content Quality Check - Key verses and random sampling"""
        try:
            print("\n🔍 GENESIS CONTENT QUALITY CHECK - KEY VERSES AND SAMPLING...")
            
            # Test Genesis 1:1 - Expected creation text
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Genesis/1/1?version=kjv1611_divine")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for Genesis 1:1 creation content
                    creation_keywords = ['beginning', 'god', 'created', 'heaven', 'earth']
                    keywords_found = sum(1 for keyword in creation_keywords if keyword.lower() in verse_text.lower())
                    
                    if keywords_found >= 4:
                        self.log_test("Genesis 1:1 - Creation Text", True, f"✅ CORRECT! Found: '{verse_text[:100]}...'")
                    else:
                        self.log_test("Genesis 1:1 - Creation Text", False, f"Missing creation content. Found: '{verse_text[:100]}...'")
                else:
                    self.log_test("Genesis 1:1 - Creation Text", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Genesis 1:1 - Creation Text", False, f"Error: {str(e)}")
            
            # Test Genesis 50:26 - Last verse to ensure complete book
            try:
                response = self.session.get(f"{self.base_url}/bible/verse/Genesis/50/26?version=kjv1611_divine")
                if response.status_code == 200:
                    verse_data = response.json()
                    verse_text = verse_data.get('text', '')
                    
                    # Check for Genesis 50:26 content (Joseph's death/burial)
                    ending_keywords = ['joseph', 'died', 'egypt', 'coffin', 'years']
                    keywords_found = sum(1 for keyword in ending_keywords if keyword.lower() in verse_text.lower())
                    
                    if keywords_found >= 2:
                        self.log_test("Genesis 50:26 - Last Verse", True, f"✅ COMPLETE BOOK! Found: '{verse_text[:100]}...'")
                    else:
                        self.log_test("Genesis 50:26 - Last Verse", False, f"Unexpected ending content. Found: '{verse_text[:100]}...'")
                else:
                    self.log_test("Genesis 50:26 - Last Verse", False, f"Status: {response.status_code} - Book may be incomplete")
            except Exception as e:
                self.log_test("Genesis 50:26 - Last Verse", False, f"Error: {str(e)}")
            
            # Sample random verses for content quality
            sample_chapters = [5, 12, 18, 25, 32, 39, 45]  # Spread across Genesis
            quality_verses = 0
            total_sampled = 0
            
            print("\n📝 RANDOM VERSE QUALITY SAMPLING:")
            
            for chapter in sample_chapters:
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=3")
                    if response.status_code == 200:
                        data = response.json()
                        verses = data.get('verses', [])
                        
                        for verse in verses[:2]:  # Sample 2 verses per chapter
                            verse_text = verse.get('text', '')
                            verse_ref = f"Genesis {verse.get('chapter', '?')}:{verse.get('verse', '?')}"
                            total_sampled += 1
                            
                            # Quality checks
                            is_quality = (
                                len(verse_text) > 15 and  # Reasonable length
                                not verse_text.startswith('...') and  # Not truncated
                                not verse_text.endswith('...') and
                                any(char in verse_text for char in ['.', ';', ':', '!', '?']) and  # Has punctuation
                                verse_text.strip() != ''  # Not empty
                            )
                            
                            if is_quality:
                                quality_verses += 1
                                print(f"   ✅ {verse_ref}: '{verse_text[:80]}...'")
                            else:
                                print(f"   ❌ {verse_ref}: QUALITY ISSUE - '{verse_text[:80]}...'")
                                
                except Exception as e:
                    print(f"   ❌ Chapter {chapter}: Error - {str(e)}")
            
            if total_sampled > 0:
                quality_percentage = (quality_verses / total_sampled) * 100
                if quality_percentage >= 90:
                    self.log_test("Random Verse Quality", True, f"✅ EXCELLENT! {quality_verses}/{total_sampled} verses are high quality ({quality_percentage:.1f}%)")
                elif quality_percentage >= 75:
                    self.log_test("Random Verse Quality", True, f"Good quality: {quality_verses}/{total_sampled} verses ({quality_percentage:.1f}%)")
                else:
                    self.log_test("Random Verse Quality", False, f"Poor quality: {quality_verses}/{total_sampled} verses ({quality_percentage:.1f}%)")
            else:
                self.log_test("Random Verse Quality", False, "No verses sampled for quality check")
            
            return True
            
        except Exception as e:
            self.log_test("Genesis Content Quality Check", False, f"Error: {str(e)}")
            return False

    def test_database_structure_verification(self):
        """REVIEW REQUEST TEST 3: Database Structure Verification - Genesis only and chapter completeness"""
        try:
            print("\n🔍 DATABASE STRUCTURE VERIFICATION - GENESIS ONLY AND COMPLETENESS...")
            
            # Confirm we only have Genesis data (no cross-contamination)
            try:
                response = self.session.get(f"{self.base_url}/bible/books?version=kjv1611_divine")
                if response.status_code == 200:
                    data = response.json()
                    books = data.get('books', [])
                    book_count = len(books)
                    
                    if book_count == 1:
                        book_name = books[0].get('name', 'Unknown') if books else 'Unknown'
                        if book_name == 'Genesis':
                            self.log_test("Database Purity - Genesis Only", True, f"✅ PURE! Only Genesis exists ({book_count} book)")
                        else:
                            self.log_test("Database Purity - Genesis Only", False, f"Wrong book: Found '{book_name}' instead of Genesis")
                    else:
                        book_names = [book.get('name', 'Unknown') for book in books]
                        self.log_test("Database Purity - Genesis Only", False, f"Cross-contamination: {book_count} books ({', '.join(book_names[:5])})")
                else:
                    self.log_test("Database Purity - Genesis Only", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Database Purity - Genesis Only", False, f"Error: {str(e)}")
            
            # Check verse count per chapter to identify incomplete chapters
            print("\n📊 VERSE COUNT PER CHAPTER ANALYSIS:")
            
            expected_verses_per_chapter = {
                1: 31, 2: 25, 3: 24, 4: 26, 5: 32, 6: 22, 7: 24, 8: 22, 9: 29, 10: 32,
                11: 32, 12: 20, 13: 18, 14: 24, 15: 21, 16: 16, 17: 27, 18: 33, 19: 38, 20: 18,
                21: 34, 22: 24, 23: 20, 24: 67, 25: 34, 26: 35, 27: 46, 28: 22, 29: 35, 30: 43,
                31: 55, 32: 32, 33: 20, 34: 31, 35: 29, 36: 43, 37: 36, 38: 30, 39: 23, 40: 23,
                41: 57, 42: 38, 43: 34, 44: 34, 45: 28, 46: 34, 47: 31, 48: 22, 49: 33, 50: 26
            }
            
            incomplete_chapters = []
            complete_chapters = []
            total_missing = 0
            
            for chapter in range(1, 51):
                try:
                    response = self.session.get(f"{self.base_url}/bible/verses?version=kjv1611_divine&book=Genesis&chapter={chapter}&limit=1")
                    if response.status_code == 200:
                        data = response.json()
                        actual_verses = data.get('total', 0)
                        expected_verses = expected_verses_per_chapter.get(chapter, 0)
                        missing = expected_verses - actual_verses
                        
                        if missing > 0:
                            incomplete_chapters.append({
                                'chapter': chapter,
                                'actual': actual_verses,
                                'expected': expected_verses,
                                'missing': missing
                            })
                            total_missing += missing
                            print(f"   ❌ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses (missing {missing})")
                        else:
                            complete_chapters.append(chapter)
                            if actual_verses == expected_verses:
                                print(f"   ✅ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses (complete)")
                            else:
                                print(f"   ⚠️ Chapter {chapter:2d}: {actual_verses:2d}/{expected_verses:2d} verses (extra verses)")
                    else:
                        incomplete_chapters.append({
                            'chapter': chapter,
                            'actual': 0,
                            'expected': expected_verses_per_chapter.get(chapter, 0),
                            'missing': expected_verses_per_chapter.get(chapter, 0)
                        })
                        total_missing += expected_verses_per_chapter.get(chapter, 0)
                        print(f"   ❌ Chapter {chapter:2d}: ERROR - Status {response.status_code}")
                        
                except Exception as e:
                    incomplete_chapters.append({
                        'chapter': chapter,
                        'actual': 0,
                        'expected': expected_verses_per_chapter.get(chapter, 0),
                        'missing': expected_verses_per_chapter.get(chapter, 0)
                    })
                    total_missing += expected_verses_per_chapter.get(chapter, 0)
                    print(f"   ❌ Chapter {chapter:2d}: ERROR - {str(e)}")
            
            # Summary
            self.log_test("Complete Chapters", True, f"✅ {len(complete_chapters)}/50 chapters are complete")
            
            if incomplete_chapters:
                self.log_test("Incomplete Chapters", False, f"❌ {len(incomplete_chapters)}/50 chapters are incomplete (missing {total_missing} total verses)")
                
                # Show top 5 chapters with most missing verses
                incomplete_chapters.sort(key=lambda x: x['missing'], reverse=True)
                top_incomplete = incomplete_chapters[:5]
                missing_summary = ", ".join([f"Ch{ch['chapter']}(-{ch['missing']})" for ch in top_incomplete])
                self.log_test("Most Incomplete Chapters", False, f"Top missing: {missing_summary}")
            else:
                self.log_test("Incomplete Chapters", True, "✅ All chapters are complete")
            
            return True
            
        except Exception as e:
            self.log_test("Database Structure Verification", False, f"Error: {str(e)}")
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

    def run_genesis_kjv_1611_tests(self):
        """Run Genesis KJV 1611 final implementation tests as per review request"""
        print("=" * 80)
        print("🔍 GENESIS KJV 1611 FINAL IMPLEMENTATION TESTING")
        print("Testing the final Genesis KJV 1611 implementation to verify it meets all criteria and reads correctly")
        print("=" * 80)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return False
        
        # Run the 5 main review request tests
        test_results = []
        
        # Test 1: Content Accuracy Verification (Genesis specific verses)
        test_results.append(self.test_genesis_content_accuracy_verification())
        
        # Test 2: Complete Structure Test (50 chapters, ~1,495 verses)
        test_results.append(self.test_genesis_complete_structure())
        
        # Test 3: Database Cleanup Verification (only Genesis exists)
        test_results.append(self.test_database_cleanup_verification())
        
        # Test 4: Reading Quality Test (verse readability)
        test_results.append(self.test_genesis_reading_quality())
        
        # Test 5: API Performance (search and navigation)
        test_results.append(self.test_genesis_api_performance())
        
        # Calculate overall results
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("📊 GENESIS KJV 1611 FINAL IMPLEMENTATION TESTING SUMMARY")
        print("=" * 80)
        
        # Count individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result["passed"])
        individual_success_rate = (passed_individual_tests / total_individual_tests) * 100 if total_individual_tests > 0 else 0
        
        print(f"📈 OVERALL SUCCESS RATE: {individual_success_rate:.1f}% ({passed_individual_tests}/{total_individual_tests} individual tests passed)")
        print(f"🎯 MAIN CATEGORIES: {passed_tests}/{total_tests} major test categories passed")
        
        # Show category results
        categories = [
            "Content Accuracy Verification (Genesis 1:1, 1:2, 1:28 specific verses)",
            "Complete Structure Test (50 chapters, ~1,495 verses)", 
            "Database Cleanup Verification (only Genesis exists)",
            "Reading Quality Test (verse readability and completeness)",
            "API Performance (search and navigation for Genesis)"
        ]
        
        for i, (category, result) in enumerate(zip(categories, test_results)):
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {category}")
        
        print("\n🔍 KEY FINDINGS:")
        
        # Analyze results for key findings
        if test_results[0]:  # Content Accuracy Verification
            print("✅ Genesis content accuracy verified - specific verses contain expected biblical text")
        else:
            print("❌ Genesis content accuracy issues - verses missing expected content")
        
        if test_results[1]:  # Complete Structure Test
            print("✅ Genesis structure verified - 50 chapters with ~1,495 verses approaching web standards")
        else:
            print("❌ Genesis structure issues - incorrect chapter/verse counts")
        
        if test_results[2]:  # Database Cleanup Verification
            print("✅ Database cleanup successful - only Genesis exists (no 104+ book contamination)")
        else:
            print("❌ Database cleanup incomplete - multiple books or contamination detected")
        
        if test_results[3]:  # Reading Quality Test
            print("✅ Genesis reading quality excellent - verses are complete and readable")
        else:
            print("❌ Genesis reading quality issues - verses fragmented or incomplete")
        
        if test_results[4]:  # API Performance
            print("✅ Genesis API performance excellent - search and navigation working correctly")
        else:
            print("❌ Genesis API performance issues - search or navigation problems")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if individual_success_rate >= 90:
            print(f"✅ EXCELLENT! Genesis KJV 1611 implementation meets all criteria ({individual_success_rate:.1f}% success)")
            print("✅ Ready for production use - Genesis reads correctly according to web-verified standards")
        elif individual_success_rate >= 75:
            print(f"✅ GOOD! Genesis KJV 1611 implementation mostly successful ({individual_success_rate:.1f}% success)")
            print("✅ Minor issues remain but core functionality working")
        elif individual_success_rate >= 50:
            print(f"⚠️ PARTIAL! Genesis KJV 1611 implementation partially working ({individual_success_rate:.1f}% success)")
            print("⚠️ Significant issues need addressing before production")
        else:
            print(f"❌ FAILED! Genesis KJV 1611 implementation has major issues ({individual_success_rate:.1f}% success)")
            print("❌ Requires substantial fixes before meeting review criteria")
        
        return individual_success_rate >= 75

def main():
    """Main test execution"""
    print("🚀 Starting Genesis KJV 1611 Final Implementation Testing...")
    
    tester = APITester(BACKEND_URL)
    success = tester.run_genesis_kjv_1611_tests()
    
    if success:
        print("\n🎉 Genesis KJV 1611 testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Genesis KJV 1611 testing completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()