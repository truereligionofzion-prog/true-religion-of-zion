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