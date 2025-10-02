#!/usr/bin/env python3
"""
Enhanced Data Testing for 613 Biblical Laws API
Specifically tests the enhanced scholarly content for mitzvot 1-20
"""

import requests
import json
import sys

# Get backend URL from environment
BACKEND_URL = "https://scripturesearch.preview.emergentagent.com/api"

class EnhancedDataTester:
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
    
    def test_enhanced_mitzvot_1_20(self):
        """Test that mitzvot 1-20 have authentic enhanced content"""
        try:
            # Get first 20 mitzvot
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=20")
            if response.status_code != 200:
                self.log_test("Enhanced Mitzvot 1-20", False, f"API Error: {response.status_code}")
                return False
            
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            if len(mitzvot) < 20:
                self.log_test("Enhanced Mitzvot 1-20", False, f"Only got {len(mitzvot)} mitzvot, expected 20")
                return False
            
            # Test specific enhanced content for first 20 mitzvot
            enhanced_content_tests = []
            
            for mitzvah in mitzvot[:20]:
                number = mitzvah.get('number', 0)
                title = mitzvah.get('title', '')
                traditional_wording = mitzvah.get('traditionalWording', '')
                source_verse = mitzvah.get('sourceVerse', '')
                scholarly_note = mitzvah.get('scholarlyNote', '')
                
                # Test for authentic traditional wording (not generic placeholders)
                has_authentic_wording = (
                    'Traditional observance and practice' not in traditional_wording and
                    len(traditional_wording) > 20 and
                    traditional_wording != title
                )
                
                # Test for proper source verses with full citations
                has_full_verse = (
                    '—' in source_verse and
                    '"' in source_verse and
                    any(book in source_verse for book in ['Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Genesis'])
                )
                
                # Test for scholarly notes with proper academic references
                has_scholarly_references = (
                    len(scholarly_note) > 50 and
                    any(ref in scholarly_note for ref in ['Maimonides', 'Rambam', 'Ramban', 'biblical', 'Torah', 'rabbinic', 'tradition'])
                )
                
                enhanced_content_tests.append({
                    'number': number,
                    'title': title,
                    'has_authentic_wording': has_authentic_wording,
                    'has_full_verse': has_full_verse,
                    'has_scholarly_references': has_scholarly_references,
                    'traditional_wording': traditional_wording[:100] + '...' if len(traditional_wording) > 100 else traditional_wording,
                    'source_verse': source_verse[:100] + '...' if len(source_verse) > 100 else source_verse
                })
            
            # Analyze results
            authentic_wording_count = sum(1 for test in enhanced_content_tests if test['has_authentic_wording'])
            full_verse_count = sum(1 for test in enhanced_content_tests if test['has_full_verse'])
            scholarly_ref_count = sum(1 for test in enhanced_content_tests if test['has_scholarly_references'])
            
            # Test authentic traditional wording
            if authentic_wording_count >= 18:  # At least 90% should have authentic wording
                self.log_test("Enhanced Content - Authentic Wording", True, f"{authentic_wording_count}/20 have authentic traditional wording")
            else:
                self.log_test("Enhanced Content - Authentic Wording", False, f"Only {authentic_wording_count}/20 have authentic wording")
                # Show examples of non-authentic wording
                for test in enhanced_content_tests:
                    if not test['has_authentic_wording']:
                        print(f"  Mitzvah {test['number']}: {test['traditional_wording']}")
            
            # Test full biblical verses
            if full_verse_count >= 18:  # At least 90% should have full verses
                self.log_test("Enhanced Content - Full Biblical Verses", True, f"{full_verse_count}/20 have full verse citations")
            else:
                self.log_test("Enhanced Content - Full Biblical Verses", False, f"Only {full_verse_count}/20 have full verses")
                # Show examples of incomplete verses
                for test in enhanced_content_tests:
                    if not test['has_full_verse']:
                        print(f"  Mitzvah {test['number']}: {test['source_verse']}")
            
            # Test scholarly references
            if scholarly_ref_count >= 15:  # At least 75% should have scholarly references
                self.log_test("Enhanced Content - Scholarly References", True, f"{scholarly_ref_count}/20 have proper scholarly notes")
            else:
                self.log_test("Enhanced Content - Scholarly References", False, f"Only {scholarly_ref_count}/20 have scholarly references")
            
            return authentic_wording_count >= 18 and full_verse_count >= 18 and scholarly_ref_count >= 15
            
        except Exception as e:
            self.log_test("Enhanced Mitzvot 1-20", False, f"Error: {str(e)}")
            return False
    
    def test_specific_enhanced_examples(self):
        """Test specific examples mentioned in the review request"""
        try:
            # Get all mitzvot to search through
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=50")
            if response.status_code != 200:
                self.log_test("Specific Enhanced Examples", False, f"API Error: {response.status_code}")
                return False
            
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            # Look for specific enhanced examples
            specific_examples = [
                {
                    'search_term': 'know that God exists',
                    'expected_wording': 'believe in the existence',
                    'description': 'First mitzvah - To know that God exists'
                },
                {
                    'search_term': 'doorposts',
                    'expected_wording': 'mezuzah',
                    'description': 'Mezuzah mitzvah with proper traditional wording'
                },
                {
                    'search_term': 'write',
                    'expected_wording': 'Torah',
                    'description': 'Writing Torah scroll mitzvah'
                },
                {
                    'search_term': 'tefillin',
                    'expected_wording': 'bind',
                    'description': 'Tefillin mitzvot with proper wording'
                }
            ]
            
            examples_found = 0
            for example in specific_examples:
                found = False
                for mitzvah in mitzvot:
                    title = mitzvah.get('title', '').lower()
                    traditional_wording = mitzvah.get('traditionalWording', '').lower()
                    
                    if (example['search_term'].lower() in title or 
                        example['search_term'].lower() in traditional_wording):
                        if example['expected_wording'].lower() in traditional_wording:
                            self.log_test(f"Enhanced Example - {example['description']}", True, 
                                        f"Found proper wording: {mitzvah.get('traditionalWording', '')[:80]}...")
                            examples_found += 1
                            found = True
                            break
                
                if not found:
                    self.log_test(f"Enhanced Example - {example['description']}", False, 
                                f"Could not find proper enhanced wording")
            
            return examples_found >= len(specific_examples) * 0.75  # At least 75% should be found
            
        except Exception as e:
            self.log_test("Specific Enhanced Examples", False, f"Error: {str(e)}")
            return False
    
    def test_quiz_with_enhanced_data(self):
        """Test that quiz system uses enhanced content"""
        try:
            # Test quiz generation
            response = self.session.get(f"{self.base_url}/quiz/all?limit=10")
            if response.status_code != 200:
                self.log_test("Quiz Enhanced Data", False, f"API Error: {response.status_code}")
                return False
            
            data = response.json()
            questions = data.get('questions', [])
            
            if not questions:
                self.log_test("Quiz Enhanced Data", False, "No quiz questions generated")
                return False
            
            # Check if quiz questions use enhanced traditional wording
            enhanced_questions = 0
            for question in questions:
                question_text = question.get('question', '')
                correct_answer = question.get('correct_answer', '')
                explanation = question.get('explanation', '')
                
                # Look for signs of enhanced content in questions
                if ('traditional wording' in question_text.lower() and 
                    len(correct_answer) > 20 and
                    'Traditional observance' not in correct_answer):
                    enhanced_questions += 1
                elif ('mitzvah' in explanation.lower() and 
                      any(ref in explanation for ref in ['Source:', 'biblical', 'Torah'])):
                    enhanced_questions += 1
            
            if enhanced_questions >= len(questions) * 0.5:  # At least 50% should use enhanced data
                self.log_test("Quiz Enhanced Data", True, f"{enhanced_questions}/{len(questions)} questions use enhanced content")
                return True
            else:
                self.log_test("Quiz Enhanced Data", False, f"Only {enhanced_questions}/{len(questions)} questions use enhanced content")
                return False
            
        except Exception as e:
            self.log_test("Quiz Enhanced Data", False, f"Error: {str(e)}")
            return False
    
    def test_flashcard_enhanced_data(self):
        """Test that flashcard system uses enhanced content"""
        try:
            # Test flashcard generation
            response = self.session.get(f"{self.base_url}/flashcards?limit=10")
            if response.status_code != 200:
                self.log_test("Flashcard Enhanced Data", False, f"API Error: {response.status_code}")
                return False
            
            data = response.json()
            flashcards = data.get('flashcards', [])
            
            if not flashcards:
                self.log_test("Flashcard Enhanced Data", False, "No flashcards returned")
                return False
            
            # Check if flashcards display enhanced mitzvah content
            enhanced_flashcards = 0
            for flashcard_item in flashcards:
                mitzvah = flashcard_item.get('mitzvah', {})
                traditional_wording = mitzvah.get('traditionalWording', '')
                source_verse = mitzvah.get('sourceVerse', '')
                
                # Check for enhanced content
                if (len(traditional_wording) > 20 and 
                    'Traditional observance' not in traditional_wording and
                    '—' in source_verse and '"' in source_verse):
                    enhanced_flashcards += 1
            
            if enhanced_flashcards >= len(flashcards) * 0.8:  # At least 80% should have enhanced data
                self.log_test("Flashcard Enhanced Data", True, f"{enhanced_flashcards}/{len(flashcards)} flashcards use enhanced content")
                return True
            else:
                self.log_test("Flashcard Enhanced Data", False, f"Only {enhanced_flashcards}/{len(flashcards)} flashcards use enhanced content")
                return False
            
        except Exception as e:
            self.log_test("Flashcard Enhanced Data", False, f"Error: {str(e)}")
            return False
    
    def test_search_enhanced_keywords(self):
        """Test search functionality with enhanced keywords"""
        try:
            # Test searches that should work with enhanced content
            enhanced_searches = [
                ('Maimonides', 'Should find mitzvot with Maimonides references'),
                ('biblical', 'Should find mitzvot with biblical references'),
                ('covenant', 'Should find covenant-related mitzvot'),
                ('rabbinic', 'Should find rabbinic interpretations'),
                ('tradition', 'Should find traditional observances')
            ]
            
            successful_searches = 0
            for search_term, description in enhanced_searches:
                response = self.session.get(f"{self.base_url}/mitzvot?search={search_term}&limit=10")
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('mitzvot', [])
                    if results:
                        # Verify results actually contain the search term
                        relevant_results = 0
                        for mitzvah in results:
                            text_to_search = (
                                mitzvah.get('title', '') + ' ' +
                                mitzvah.get('traditionalWording', '') + ' ' +
                                mitzvah.get('scholarlyNote', '') + ' ' +
                                mitzvah.get('sourceVerse', '')
                            ).lower()
                            
                            if search_term.lower() in text_to_search:
                                relevant_results += 1
                        
                        if relevant_results > 0:
                            self.log_test(f"Enhanced Search - {search_term}", True, 
                                        f"Found {relevant_results} relevant results out of {len(results)}")
                            successful_searches += 1
                        else:
                            self.log_test(f"Enhanced Search - {search_term}", False, 
                                        f"Found {len(results)} results but none contain '{search_term}'")
                    else:
                        self.log_test(f"Enhanced Search - {search_term}", False, "No results found")
                else:
                    self.log_test(f"Enhanced Search - {search_term}", False, f"API Error: {response.status_code}")
            
            return successful_searches >= len(enhanced_searches) * 0.6  # At least 60% should work
            
        except Exception as e:
            self.log_test("Search Enhanced Keywords", False, f"Error: {str(e)}")
            return False
    
    def test_data_integrity_enhanced(self):
        """Test data integrity with enhanced content"""
        try:
            # Get all mitzvot to check for data integrity issues
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=613")
            if response.status_code != 200:
                self.log_test("Data Integrity Enhanced", False, f"API Error: {response.status_code}")
                return False
            
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            if len(mitzvot) != 613:
                self.log_test("Data Integrity Enhanced", False, f"Expected 613 mitzvot, got {len(mitzvot)}")
                return False
            
            # Check for data integrity issues
            issues = []
            
            # Check for missing required fields
            for mitzvah in mitzvot:
                number = mitzvah.get('number', 0)
                if not mitzvah.get('title'):
                    issues.append(f"Mitzvah {number}: Missing title")
                if not mitzvah.get('traditionalWording'):
                    issues.append(f"Mitzvah {number}: Missing traditional wording")
                if not mitzvah.get('sourceVerse'):
                    issues.append(f"Mitzvah {number}: Missing source verse")
                if not mitzvah.get('category'):
                    issues.append(f"Mitzvah {number}: Missing category")
            
            # Check for duplicate numbers
            numbers = [m.get('number') for m in mitzvot]
            duplicates = [n for n in numbers if numbers.count(n) > 1]
            if duplicates:
                issues.append(f"Duplicate mitzvah numbers: {list(set(duplicates))}")
            
            # Check for proper categorization
            categories = set(m.get('category') for m in mitzvot)
            expected_categories = {
                'faith-god', 'torah-study', 'temple-worship', 'dietary-laws',
                'tithes-offerings', 'festivals', 'family-marriage', 'civil-criminal',
                'purity-laws', 'business-society', 'leadership', 'land-agriculture', 'other'
            }
            
            invalid_categories = categories - expected_categories
            if invalid_categories:
                issues.append(f"Invalid categories found: {invalid_categories}")
            
            if not issues:
                self.log_test("Data Integrity Enhanced", True, "All 613 mitzvot have proper structure and categorization")
                return True
            else:
                self.log_test("Data Integrity Enhanced", False, f"Found {len(issues)} integrity issues")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"  • {issue}")
                if len(issues) > 5:
                    print(f"  • ... and {len(issues) - 5} more issues")
                return False
            
        except Exception as e:
            self.log_test("Data Integrity Enhanced", False, f"Error: {str(e)}")
            return False
    
    def run_enhanced_tests(self):
        """Run all enhanced data tests"""
        print("🔍 Testing Enhanced 613 Mitzvot System")
        print("=" * 50)
        
        print("\n✨ Testing Enhanced Data Quality (Mitzvot 1-20)...")
        self.test_enhanced_mitzvot_1_20()
        
        print("\n🎯 Testing Specific Enhanced Examples...")
        self.test_specific_enhanced_examples()
        
        print("\n🧠 Testing Quiz System with Enhanced Data...")
        self.test_quiz_with_enhanced_data()
        
        print("\n🃏 Testing Flashcard System with Enhanced Data...")
        self.test_flashcard_enhanced_data()
        
        print("\n🔍 Testing Search with Enhanced Keywords...")
        self.test_search_enhanced_keywords()
        
        print("\n🔄 Testing Data Integrity with Enhanced Content...")
        self.test_data_integrity_enhanced()
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 ENHANCED DATA TEST SUMMARY")
        print("=" * 50)
        
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
    print("🚀 Enhanced 613 Biblical Laws API Testing")
    print(f"Testing against: {BACKEND_URL}")
    print()
    
    tester = EnhancedDataTester(BACKEND_URL)
    success = tester.run_enhanced_tests()
    
    if success:
        print("\n🎉 ALL ENHANCED DATA TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME ENHANCED DATA TESTS FAILED. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()