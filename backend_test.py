#!/usr/bin/env python3
"""
Comprehensive Backend Testing for 613 Biblical Laws API
Tests the enhanced data with authentic traditional wording and biblical sources
"""

import requests
import json
import sys
import os
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = "https://biblaw-explorer.preview.emergentagent.com/api"

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
    
    def test_initialize_endpoint(self):
        """Test /api/initialize endpoint to verify 613 mitzvot are loaded correctly"""
        try:
            response = self.session.post(f"{self.base_url}/initialize")
            if response.status_code == 200:
                data = response.json()
                mitzvot_count = data.get('mitzvot_count', 0)
                categories_count = data.get('categories_count', 0)
                
                if mitzvot_count == 613:
                    self.log_test("Initialize - Mitzvot Count", True, f"Loaded exactly 613 mitzvot")
                else:
                    self.log_test("Initialize - Mitzvot Count", False, f"Expected 613, got {mitzvot_count}")
                
                if categories_count > 0:
                    self.log_test("Initialize - Categories", True, f"Loaded {categories_count} categories")
                else:
                    self.log_test("Initialize - Categories", False, "No categories loaded")
                    
                return mitzvot_count == 613
            else:
                self.log_test("Initialize Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Initialize Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_stats_validation(self):
        """Test /api/stats to confirm exactly 613 total mitzvot with proper distribution"""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            if response.status_code == 200:
                data = response.json()
                total_mitzvot = data.get('totalMitzvot', 0)
                direct = data.get('directBiblical', 0)
                indirect = data.get('indirectBiblical', 0)
                rabbinic = data.get('rabbinic', 0)
                traditional = data.get('traditional', 0)
                
                # Test total count
                if total_mitzvot == 613:
                    self.log_test("Stats - Total Count", True, "Exactly 613 mitzvot")
                else:
                    self.log_test("Stats - Total Count", False, f"Expected 613, got {total_mitzvot}")
                
                # Test distribution adds up
                sum_categories = direct + indirect + rabbinic + traditional
                if sum_categories == total_mitzvot:
                    self.log_test("Stats - Distribution Sum", True, f"Categories sum to {sum_categories}")
                else:
                    self.log_test("Stats - Distribution Sum", False, f"Categories sum to {sum_categories}, total is {total_mitzvot}")
                
                # Test reasonable distribution
                if direct > 0 and indirect > 0:
                    self.log_test("Stats - Distribution Variety", True, f"Direct: {direct}, Indirect: {indirect}, Rabbinic: {rabbinic}, Traditional: {traditional}")
                else:
                    self.log_test("Stats - Distribution Variety", False, "Missing direct or indirect mitzvot")
                
                return total_mitzvot == 613 and sum_categories == total_mitzvot
            else:
                self.log_test("Stats Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Stats Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_enhanced_data_quality(self):
        """Test /api/mitzvot endpoint to verify enhanced data quality"""
        try:
            # Test first page
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=50")
            if response.status_code != 200:
                self.log_test("Enhanced Data Quality", False, f"Status: {response.status_code}")
                return False
                
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            if not mitzvot:
                self.log_test("Enhanced Data Quality", False, "No mitzvot returned")
                return False
            
            # Test specific mitzvot for authentic content
            authentic_found = 0
            generic_found = 0
            full_verses_found = 0
            meaningful_notes_found = 0
            
            for mitzvah in mitzvot:
                traditional_wording = mitzvah.get('traditionalWording', '')
                source_verse = mitzvah.get('sourceVerse', '')
                scholarly_note = mitzvah.get('scholarlyNote', '')
                
                # Check for authentic traditional wording (not generic)
                if 'Traditional observance and practice of commandment' not in traditional_wording:
                    authentic_found += 1
                else:
                    generic_found += 1
                
                # Check for full biblical references with quoted text
                if '—' in source_verse and '"' in source_verse:
                    full_verses_found += 1
                
                # Check for meaningful scholarly notes
                if len(scholarly_note) > 50 and 'Maimonides' in scholarly_note or 'biblical' in scholarly_note.lower():
                    meaningful_notes_found += 1
            
            # Test results
            if authentic_found > generic_found:
                self.log_test("Enhanced Data - Authentic Wording", True, f"Found {authentic_found} authentic vs {generic_found} generic")
            else:
                self.log_test("Enhanced Data - Authentic Wording", False, f"Too many generic wordings: {generic_found} vs {authentic_found} authentic")
            
            if full_verses_found > len(mitzvot) * 0.8:  # At least 80% should have full verses
                self.log_test("Enhanced Data - Full Verses", True, f"{full_verses_found}/{len(mitzvot)} have full biblical references")
            else:
                self.log_test("Enhanced Data - Full Verses", False, f"Only {full_verses_found}/{len(mitzvot)} have full biblical references")
            
            if meaningful_notes_found > len(mitzvot) * 0.7:  # At least 70% should have meaningful notes
                self.log_test("Enhanced Data - Scholarly Notes", True, f"{meaningful_notes_found}/{len(mitzvot)} have meaningful notes")
            else:
                self.log_test("Enhanced Data - Scholarly Notes", False, f"Only {meaningful_notes_found}/{len(mitzvot)} have meaningful notes")
            
            # Test specific examples mentioned in the request
            specific_examples = [
                "Write on doorposts of thy house",
                "Every man should write Torah",
                "Bind words as a sign on your arm"
            ]
            
            examples_found = 0
            for mitzvah in mitzvot:
                for example in specific_examples:
                    if example in mitzvah.get('traditionalWording', ''):
                        examples_found += 1
                        break
            
            if examples_found > 0:
                self.log_test("Enhanced Data - Specific Examples", True, f"Found {examples_found} specific authentic examples")
            else:
                self.log_test("Enhanced Data - Specific Examples", False, "No specific authentic examples found in first 50")
            
            return authentic_found > generic_found and full_verses_found > len(mitzvot) * 0.8
            
        except Exception as e:
            self.log_test("Enhanced Data Quality", False, f"Error: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test search across enhanced traditional wording and source verses"""
        search_terms = [
            ("doorposts", "Should find mezuzah mitzvah"),
            ("tefillin", "Should find tefillin mitzvot"),
            ("Torah", "Should find Torah-related mitzvot"),
            ("Exodus", "Should find mitzvot from Exodus"),
            ("altar", "Should find altar-related mitzvot")
        ]
        
        search_passed = 0
        for term, description in search_terms:
            try:
                response = self.session.get(f"{self.base_url}/mitzvot?search={term}&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('mitzvot', [])
                    if results:
                        self.log_test(f"Search - '{term}'", True, f"Found {len(results)} results")
                        search_passed += 1
                    else:
                        self.log_test(f"Search - '{term}'", False, "No results found")
                else:
                    self.log_test(f"Search - '{term}'", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Search - '{term}'", False, f"Error: {str(e)}")
        
        return search_passed >= len(search_terms) * 0.8  # At least 80% should work
    
    def test_filtering(self):
        """Test category, status, and book filters work with enhanced data"""
        filters_to_test = [
            ("category", "faith-god", "Faith & God category"),
            ("category", "torah-study", "Torah Study category"),
            ("status", "direct", "Direct biblical status"),
            ("status", "indirect", "Indirect biblical status"),
            ("book", "Exodus", "Book of Exodus"),
            ("book", "Leviticus", "Book of Leviticus")
        ]
        
        filters_passed = 0
        for filter_type, filter_value, description in filters_to_test:
            try:
                response = self.session.get(f"{self.base_url}/mitzvot?{filter_type}={filter_value}&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('mitzvot', [])
                    if results:
                        # Verify filter actually worked
                        if filter_type == "category":
                            filtered_correctly = all(m.get('category') == filter_value for m in results)
                        elif filter_type == "status":
                            filtered_correctly = all(m.get('status') == filter_value for m in results)
                        elif filter_type == "book":
                            filtered_correctly = all(m.get('book') == filter_value for m in results)
                        else:
                            filtered_correctly = True
                        
                        if filtered_correctly:
                            self.log_test(f"Filter - {description}", True, f"Found {len(results)} correctly filtered results")
                            filters_passed += 1
                        else:
                            self.log_test(f"Filter - {description}", False, "Filter not applied correctly")
                    else:
                        self.log_test(f"Filter - {description}", False, "No results found")
                else:
                    self.log_test(f"Filter - {description}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Filter - {description}", False, f"Error: {str(e)}")
        
        return filters_passed >= len(filters_to_test) * 0.7  # At least 70% should work
    
    def test_pagination(self):
        """Verify all 613 mitzvot can be accessed through pagination"""
        try:
            # Test first page
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=50")
            if response.status_code != 200:
                self.log_test("Pagination", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            total = data.get('total', 0)
            total_pages = data.get('totalPages', 0)
            
            if total != 613:
                self.log_test("Pagination - Total Count", False, f"Expected 613, got {total}")
                return False
            
            self.log_test("Pagination - Total Count", True, f"Total: {total}")
            
            # Test accessing different pages
            pages_to_test = [1, 5, 10, total_pages]
            pages_passed = 0
            
            for page in pages_to_test:
                if page <= total_pages:
                    try:
                        response = self.session.get(f"{self.base_url}/mitzvot?page={page}&limit=20")
                        if response.status_code == 200:
                            page_data = response.json()
                            mitzvot = page_data.get('mitzvot', [])
                            if mitzvot:
                                self.log_test(f"Pagination - Page {page}", True, f"Retrieved {len(mitzvot)} mitzvot")
                                pages_passed += 1
                            else:
                                self.log_test(f"Pagination - Page {page}", False, "No mitzvot returned")
                        else:
                            self.log_test(f"Pagination - Page {page}", False, f"Status: {response.status_code}")
                    except Exception as e:
                        self.log_test(f"Pagination - Page {page}", False, f"Error: {str(e)}")
            
            return pages_passed == len([p for p in pages_to_test if p <= total_pages])
            
        except Exception as e:
            self.log_test("Pagination", False, f"Error: {str(e)}")
            return False
    
    def test_data_consistency(self):
        """Verify no duplicate mitzvot numbers (should be exactly 1-613)"""
        try:
            # Get all mitzvot in batches
            all_numbers = set()
            page = 1
            limit = 100
            
            while True:
                response = self.session.get(f"{self.base_url}/mitzvot?page={page}&limit={limit}")
                if response.status_code != 200:
                    self.log_test("Data Consistency", False, f"Failed to fetch page {page}")
                    return False
                
                data = response.json()
                mitzvot = data.get('mitzvot', [])
                
                if not mitzvot:
                    break
                
                # Collect numbers
                for mitzvah in mitzvot:
                    number = mitzvah.get('number')
                    if number in all_numbers:
                        self.log_test("Data Consistency - Duplicates", False, f"Duplicate number found: {number}")
                        return False
                    all_numbers.add(number)
                
                # Check if we've reached the end
                if page >= data.get('totalPages', 1):
                    break
                page += 1
            
            # Verify we have exactly numbers 1-613
            expected_numbers = set(range(1, 614))
            missing_numbers = expected_numbers - all_numbers
            extra_numbers = all_numbers - expected_numbers
            
            if missing_numbers:
                self.log_test("Data Consistency - Missing Numbers", False, f"Missing: {sorted(list(missing_numbers))[:10]}...")
                return False
            
            if extra_numbers:
                self.log_test("Data Consistency - Extra Numbers", False, f"Extra: {sorted(list(extra_numbers))[:10]}...")
                return False
            
            if len(all_numbers) == 613:
                self.log_test("Data Consistency - Complete Set", True, "All numbers 1-613 present, no duplicates")
                return True
            else:
                self.log_test("Data Consistency - Count", False, f"Expected 613 unique numbers, got {len(all_numbers)}")
                return False
                
        except Exception as e:
            self.log_test("Data Consistency", False, f"Error: {str(e)}")
            return False
    
    def test_specific_mitzvot_content(self):
        """Test specific mitzvot to verify authentic content"""
        # Test specific mitzvot mentioned in the enhancement
        specific_tests = [
            (15, "mezuzah", "doorposts"),  # Mezuzah mitzvah
            (16, "Torah", "write"),        # Writing Torah scroll
            (13, "tefillin", "arm"),       # Tefillin on arm
            (1, "God", "exists"),          # First mitzvah
        ]
        
        tests_passed = 0
        for number, keyword1, keyword2 in specific_tests:
            try:
                # Get specific mitzvah by searching for its number
                response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=613")
                if response.status_code == 200:
                    data = response.json()
                    mitzvot = data.get('mitzvot', [])
                    
                    # Find the specific mitzvah
                    target_mitzvah = None
                    for m in mitzvot:
                        if m.get('number') == number:
                            target_mitzvah = m
                            break
                    
                    if target_mitzvah:
                        traditional_wording = target_mitzvah.get('traditionalWording', '').lower()
                        source_verse = target_mitzvah.get('sourceVerse', '')
                        
                        # Check for authentic content
                        has_keyword1 = keyword1.lower() in traditional_wording
                        has_keyword2 = keyword2.lower() in traditional_wording
                        has_full_verse = '—' in source_verse and '"' in source_verse
                        
                        if has_keyword1 or has_keyword2:
                            if has_full_verse:
                                self.log_test(f"Specific Mitzvah {number}", True, f"Authentic content with full verse")
                                tests_passed += 1
                            else:
                                self.log_test(f"Specific Mitzvah {number}", False, f"Missing full verse format")
                        else:
                            self.log_test(f"Specific Mitzvah {number}", False, f"Missing expected keywords")
                    else:
                        self.log_test(f"Specific Mitzvah {number}", False, f"Mitzvah not found")
                else:
                    self.log_test(f"Specific Mitzvah {number}", False, f"API error: {response.status_code}")
            except Exception as e:
                self.log_test(f"Specific Mitzvah {number}", False, f"Error: {str(e)}")
        
        return tests_passed >= len(specific_tests) * 0.75  # At least 75% should pass

    def test_enhanced_quiz_system(self):
        """Test the enhanced quiz system with diverse answer choices and question types"""
        try:
            # Test quiz generation for different categories
            categories_to_test = ["all", "faith-god", "torah-study", "invalid-category"]
            quiz_tests_passed = 0
            
            for category in categories_to_test:
                try:
                    response = self.session.get(f"{self.base_url}/quiz/{category}?limit=5")
                    
                    if category == "invalid-category":
                        # Should handle invalid category gracefully
                        if response.status_code in [400, 404]:
                            self.log_test(f"Quiz - Invalid Category Handling", True, f"Properly handled invalid category")
                            quiz_tests_passed += 1
                        else:
                            self.log_test(f"Quiz - Invalid Category Handling", False, f"Status: {response.status_code}")
                        continue
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get('questions', [])
                        
                        if not questions:
                            self.log_test(f"Quiz - {category} Generation", False, "No questions generated")
                            continue
                        
                        # Test question structure and diversity
                        question_types_found = set()
                        unique_answers_per_question = []
                        
                        for question in questions:
                            # Check required fields
                            required_fields = ['id', 'type', 'question', 'correct_answer', 'options', 'explanation']
                            if all(field in question for field in required_fields):
                                # Check question type diversity
                                if 'title_from_traditional' in question.get('question', ''):
                                    question_types_found.add('title_from_traditional')
                                elif 'traditional wording' in question.get('question', ''):
                                    question_types_found.add('traditional_from_title')
                                elif 'category' in question.get('question', ''):
                                    question_types_found.add('category_from_title')
                                elif 'origin status' in question.get('question', ''):
                                    question_types_found.add('status_from_title')
                                
                                # Check answer diversity (no duplicates)
                                options = question.get('options', [])
                                unique_options = len(set(options))
                                unique_answers_per_question.append(unique_options == len(options))
                                
                                # Verify correct answer is in options
                                correct_answer = question.get('correct_answer')
                                if correct_answer not in options:
                                    self.log_test(f"Quiz - {category} Answer Validity", False, "Correct answer not in options")
                                    continue
                        
                        # Test results
                        if len(question_types_found) >= 2:
                            self.log_test(f"Quiz - {category} Question Diversity", True, f"Found {len(question_types_found)} question types")
                        else:
                            self.log_test(f"Quiz - {category} Question Diversity", False, f"Only {len(question_types_found)} question types")
                        
                        if all(unique_answers_per_question):
                            self.log_test(f"Quiz - {category} Answer Uniqueness", True, "All questions have unique answer options")
                            quiz_tests_passed += 1
                        else:
                            self.log_test(f"Quiz - {category} Answer Uniqueness", False, "Found duplicate answers in some questions")
                        
                        self.log_test(f"Quiz - {category} Generation", True, f"Generated {len(questions)} questions successfully")
                        quiz_tests_passed += 1
                    else:
                        self.log_test(f"Quiz - {category} Generation", False, f"Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Quiz - {category}", False, f"Error: {str(e)}")
            
            return quiz_tests_passed >= 4  # Should pass most tests
            
        except Exception as e:
            self.log_test("Enhanced Quiz System", False, f"Error: {str(e)}")
            return False

    def test_progress_tracking_system(self):
        """Test the progress tracking system"""
        try:
            # Test GET /api/progress
            response = self.session.get(f"{self.base_url}/progress")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['userId', 'totalMitzvot', 'learning', 'reviewing', 'mastered', 'overallProgress', 'categoryProgress']
                
                if all(field in data for field in required_fields):
                    self.log_test("Progress - GET Endpoint Structure", True, "All required fields present")
                    
                    # Test category progress structure
                    category_progress = data.get('categoryProgress', {})
                    if category_progress and isinstance(category_progress, dict):
                        # Check if categories have proper structure
                        sample_category = next(iter(category_progress.values()), {})
                        if 'total' in sample_category and 'mastered' in sample_category and 'percentage' in sample_category:
                            self.log_test("Progress - Category Progress Structure", True, f"Found {len(category_progress)} categories")
                        else:
                            self.log_test("Progress - Category Progress Structure", False, "Missing category progress fields")
                    else:
                        self.log_test("Progress - Category Progress Structure", False, "No category progress data")
                else:
                    self.log_test("Progress - GET Endpoint Structure", False, f"Missing fields: {[f for f in required_fields if f not in data]}")
            else:
                self.log_test("Progress - GET Endpoint", False, f"Status: {response.status_code}")
                return False
            
            # Test POST /api/progress/{mitzvah_id} - need to get a valid mitzvah ID first
            mitzvot_response = self.session.get(f"{self.base_url}/mitzvot?limit=1")
            if mitzvot_response.status_code == 200:
                mitzvot_data = mitzvot_response.json()
                mitzvot = mitzvot_data.get('mitzvot', [])
                if mitzvot:
                    test_mitzvah_id = mitzvot[0].get('id')
                    
                    # Test updating progress with correct answer
                    progress_response = self.session.post(f"{self.base_url}/progress/{test_mitzvah_id}?correct=true")
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        if 'status' in progress_data and 'progress' in progress_data:
                            self.log_test("Progress - POST Update Correct", True, "Successfully updated progress")
                        else:
                            self.log_test("Progress - POST Update Correct", False, "Invalid response structure")
                    else:
                        self.log_test("Progress - POST Update Correct", False, f"Status: {progress_response.status_code}")
                    
                    # Test updating progress with incorrect answer
                    progress_response = self.session.post(f"{self.base_url}/progress/{test_mitzvah_id}?correct=false")
                    if progress_response.status_code == 200:
                        self.log_test("Progress - POST Update Incorrect", True, "Successfully updated progress")
                    else:
                        self.log_test("Progress - POST Update Incorrect", False, f"Status: {progress_response.status_code}")
                    
                    # Test invalid mitzvah ID
                    invalid_response = self.session.post(f"{self.base_url}/progress/invalid-id?correct=true")
                    if invalid_response.status_code == 404:
                        self.log_test("Progress - Invalid Mitzvah ID", True, "Properly handled invalid ID")
                    else:
                        self.log_test("Progress - Invalid Mitzvah ID", False, f"Status: {invalid_response.status_code}")
                else:
                    self.log_test("Progress - POST Tests", False, "No mitzvot available for testing")
            else:
                self.log_test("Progress - POST Tests", False, "Could not get mitzvot for testing")
            
            return True
            
        except Exception as e:
            self.log_test("Progress Tracking System", False, f"Error: {str(e)}")
            return False

    def test_flashcard_system(self):
        """Test the flashcard system with spaced repetition"""
        try:
            # Test GET /api/flashcards
            response = self.session.get(f"{self.base_url}/flashcards?limit=5")
            if response.status_code == 200:
                data = response.json()
                flashcards = data.get('flashcards', [])
                
                if flashcards:
                    self.log_test("Flashcards - GET Endpoint", True, f"Retrieved {len(flashcards)} flashcards")
                    
                    # Test flashcard structure
                    sample_flashcard = flashcards[0]
                    if 'flashcard' in sample_flashcard and 'mitzvah' in sample_flashcard:
                        flashcard_data = sample_flashcard['flashcard']
                        mitzvah_data = sample_flashcard['mitzvah']
                        
                        # Check flashcard fields
                        required_flashcard_fields = ['id', 'userId', 'mitzvahId', 'difficulty', 'nextReview', 'reviewCount']
                        if all(field in flashcard_data for field in required_flashcard_fields):
                            self.log_test("Flashcards - Structure", True, "Proper flashcard structure")
                        else:
                            self.log_test("Flashcards - Structure", False, "Missing flashcard fields")
                        
                        # Check mitzvah fields
                        required_mitzvah_fields = ['id', 'title', 'traditionalWording', 'sourceVerse']
                        if all(field in mitzvah_data for field in required_mitzvah_fields):
                            self.log_test("Flashcards - Mitzvah Data", True, "Complete mitzvah data included")
                        else:
                            self.log_test("Flashcards - Mitzvah Data", False, "Missing mitzvah fields")
                        
                        # Test POST /api/flashcards/{id}/review
                        flashcard_id = flashcard_data.get('id')
                        if flashcard_id:
                            # Test correct review
                            review_response = self.session.post(f"{self.base_url}/flashcards/{flashcard_id}/review?difficulty=3&correct=true")
                            if review_response.status_code == 200:
                                review_data = review_response.json()
                                if 'status' in review_data and 'nextReview' in review_data:
                                    self.log_test("Flashcards - Review Correct", True, "Successfully processed correct review")
                                else:
                                    self.log_test("Flashcards - Review Correct", False, "Invalid review response")
                            else:
                                self.log_test("Flashcards - Review Correct", False, f"Status: {review_response.status_code}")
                            
                            # Test incorrect review
                            review_response = self.session.post(f"{self.base_url}/flashcards/{flashcard_id}/review?difficulty=2&correct=false")
                            if review_response.status_code == 200:
                                self.log_test("Flashcards - Review Incorrect", True, "Successfully processed incorrect review")
                            else:
                                self.log_test("Flashcards - Review Incorrect", False, f"Status: {review_response.status_code}")
                            
                            # Test invalid flashcard ID
                            invalid_review = self.session.post(f"{self.base_url}/flashcards/invalid-id/review?difficulty=3&correct=true")
                            if invalid_review.status_code == 404:
                                self.log_test("Flashcards - Invalid ID", True, "Properly handled invalid flashcard ID")
                            else:
                                self.log_test("Flashcards - Invalid ID", False, f"Status: {invalid_review.status_code}")
                        else:
                            self.log_test("Flashcards - Review Tests", False, "No flashcard ID available")
                    else:
                        self.log_test("Flashcards - Structure", False, "Invalid flashcard structure")
                else:
                    self.log_test("Flashcards - GET Endpoint", False, "No flashcards returned")
            else:
                self.log_test("Flashcards - GET Endpoint", False, f"Status: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Flashcard System", False, f"Error: {str(e)}")
            return False

    def test_mitzvah_of_the_day(self):
        """Test the mitzvah of the day endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/mitzvah-of-the-day")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'number', 'title', 'traditionalWording', 'sourceVerse', 'category', 'status']
                
                if all(field in data for field in required_fields):
                    mitzvah_number = data.get('number')
                    if 1 <= mitzvah_number <= 613:
                        self.log_test("Mitzvah of the Day", True, f"Valid daily mitzvah #{mitzvah_number}")
                        return True
                    else:
                        self.log_test("Mitzvah of the Day", False, f"Invalid mitzvah number: {mitzvah_number}")
                else:
                    self.log_test("Mitzvah of the Day", False, "Missing required fields")
            else:
                self.log_test("Mitzvah of the Day", False, f"Status: {response.status_code}")
            
            return False
            
        except Exception as e:
            self.log_test("Mitzvah of the Day", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🔍 Starting Comprehensive Backend Testing for 613 Biblical Laws API")
        print("=" * 70)
        
        # Initialize database first
        print("\n📊 Initializing Database...")
        init_success = self.test_initialize_endpoint()
        
        if not init_success:
            print("❌ Database initialization failed. Stopping tests.")
            return False
        
        print("\n🔗 Testing API Connectivity...")
        self.test_api_root()
        
        print("\n📈 Testing Statistics Validation...")
        self.test_stats_validation()
        
        print("\n✨ Testing Enhanced Data Quality...")
        self.test_enhanced_data_quality()
        
        print("\n🔍 Testing Search Functionality...")
        self.test_search_functionality()
        
        print("\n🔧 Testing Filtering...")
        self.test_filtering()
        
        print("\n📄 Testing Pagination...")
        self.test_pagination()
        
        print("\n🔄 Testing Data Consistency...")
        self.test_data_consistency()
        
        print("\n🎯 Testing Specific Mitzvot Content...")
        self.test_specific_mitzvot_content()
        
        print("\n🧠 Testing Enhanced Quiz System...")
        self.test_enhanced_quiz_system()
        
        print("\n📊 Testing Progress Tracking System...")
        self.test_progress_tracking_system()
        
        print("\n🃏 Testing Flashcard System...")
        self.test_flashcard_system()
        
        print("\n📅 Testing Mitzvah of the Day...")
        self.test_mitzvah_of_the_day()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['passed']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        return passed == total

def main():
    """Main test execution"""
    print("🚀 613 Biblical Laws API - Backend Testing")
    print(f"Testing against: {BACKEND_URL}")
    print()
    
    tester = APITester(BACKEND_URL)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! The 613 Biblical Laws API is working correctly with enhanced data.")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()