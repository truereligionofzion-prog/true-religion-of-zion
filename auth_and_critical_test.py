#!/usr/bin/env python3
"""
Focused Testing for Authentication System and Critical Issues
Tests the specific issues mentioned in the review request
"""

import requests
import json
import sys
import os
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = "https://sacred-verse-hub.preview.emergentagent.com/api"

class CriticalTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        
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

    def test_authentication_system(self):
        """Test the complete authentication system"""
        print("\n🔐 Testing Authentication System...")
        
        # Test user registration
        try:
            register_data = {
                "email": "testuser@example.com",
                "password": "securepassword123",
                "name": "Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=register_data)
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.auth_token = data['token']
                    self.log_test("Auth - User Registration", True, f"User registered with token")
                else:
                    self.log_test("Auth - User Registration", False, "Missing token or user in response")
            elif response.status_code == 400 and "already registered" in response.text:
                self.log_test("Auth - User Registration", True, "User already exists (expected)")
                # Try login instead
                login_data = {
                    "email": "testuser@example.com",
                    "password": "securepassword123"
                }
                login_response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    login_data_resp = login_response.json()
                    self.auth_token = login_data_resp.get('token')
                    self.log_test("Auth - Fallback Login", True, "Successfully logged in existing user")
                else:
                    self.log_test("Auth - Fallback Login", False, f"Status: {login_response.status_code}")
            else:
                self.log_test("Auth - User Registration", False, f"Status: {response.status_code}, Response: {response.text[:200]}")
        except Exception as e:
            self.log_test("Auth - User Registration", False, f"Error: {str(e)}")

        # Test user login
        try:
            login_data = {
                "email": "testuser@example.com",
                "password": "securepassword123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    if not self.auth_token:  # Only set if we don't have one from registration
                        self.auth_token = data['token']
                    self.log_test("Auth - User Login", True, f"Login successful with JWT token")
                else:
                    self.log_test("Auth - User Login", False, "Missing token or user in response")
            else:
                self.log_test("Auth - User Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Auth - User Login", False, f"Error: {str(e)}")

        # Test invalid login
        try:
            invalid_login = {
                "email": "testuser@example.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=invalid_login)
            if response.status_code == 401:
                self.log_test("Auth - Invalid Login", True, "Properly rejected invalid credentials")
            else:
                self.log_test("Auth - Invalid Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Auth - Invalid Login", False, f"Error: {str(e)}")

        # Test get current user (requires auth token)
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['id', 'email', 'name']
                    if all(field in data for field in required_fields):
                        self.log_test("Auth - Get Current User", True, f"Retrieved user profile")
                    else:
                        self.log_test("Auth - Get Current User", False, "Missing required user fields")
                else:
                    self.log_test("Auth - Get Current User", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Auth - Get Current User", False, f"Error: {str(e)}")
        else:
            self.log_test("Auth - Get Current User", False, "No auth token available")

        # Test unauthorized access
        try:
            response = self.session.get(f"{self.base_url}/auth/me")
            if response.status_code == 401:
                self.log_test("Auth - Unauthorized Access", True, "Properly rejected request without token")
            else:
                self.log_test("Auth - Unauthorized Access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Auth - Unauthorized Access", False, f"Error: {str(e)}")

    def test_progress_tracking_critical_issue(self):
        """Test the critical ObjectId serialization issue in progress tracking"""
        print("\n📊 Testing Progress Tracking Critical Issue...")
        
        try:
            # First get a valid mitzvah ID
            mitzvot_response = self.session.get(f"{self.base_url}/mitzvot?limit=1")
            if mitzvot_response.status_code != 200:
                self.log_test("Progress Critical - Get Mitzvah", False, f"Status: {mitzvot_response.status_code}")
                return
            
            mitzvot_data = mitzvot_response.json()
            mitzvot = mitzvot_data.get('mitzvot', [])
            if not mitzvot:
                self.log_test("Progress Critical - Get Mitzvah", False, "No mitzvot available")
                return
            
            test_mitzvah_id = mitzvot[0].get('id')
            self.log_test("Progress Critical - Get Mitzvah", True, f"Using mitzvah ID: {test_mitzvah_id}")
            
            # Test the problematic POST endpoint
            progress_response = self.session.post(f"{self.base_url}/progress/{test_mitzvah_id}?correct=true")
            
            if progress_response.status_code == 200:
                try:
                    progress_data = progress_response.json()
                    self.log_test("Progress Critical - POST Endpoint", True, "ObjectId serialization issue FIXED")
                except json.JSONDecodeError:
                    self.log_test("Progress Critical - POST Endpoint", False, "Response not valid JSON")
            elif progress_response.status_code == 500:
                # Check if it's the ObjectId serialization error
                error_text = progress_response.text
                if "ObjectId" in error_text or "not JSON serializable" in error_text:
                    self.log_test("Progress Critical - POST Endpoint", False, "CONFIRMED: ObjectId serialization issue still exists")
                else:
                    self.log_test("Progress Critical - POST Endpoint", False, f"500 error but different cause: {error_text[:200]}")
            else:
                self.log_test("Progress Critical - POST Endpoint", False, f"Status: {progress_response.status_code}")
                
        except Exception as e:
            self.log_test("Progress Critical - POST Endpoint", False, f"Error: {str(e)}")

    def test_flashcard_generation_issue(self):
        """Test the flashcard generation issue"""
        print("\n🃏 Testing Flashcard Generation Issue...")
        
        try:
            # Test GET /api/flashcards
            response = self.session.get(f"{self.base_url}/flashcards?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                flashcards = data.get('flashcards', [])
                
                if flashcards and len(flashcards) > 0:
                    self.log_test("Flashcard Generation - GET Endpoint", True, f"Generated {len(flashcards)} flashcards")
                    
                    # Test flashcard structure
                    sample_flashcard = flashcards[0]
                    if 'flashcard' in sample_flashcard and 'mitzvah' in sample_flashcard:
                        self.log_test("Flashcard Generation - Structure", True, "Proper flashcard structure")
                        
                        # Test spaced repetition fields
                        flashcard_data = sample_flashcard['flashcard']
                        required_fields = ['difficulty', 'nextReview', 'reviewCount', 'correctStreak']
                        if all(field in flashcard_data for field in required_fields):
                            self.log_test("Flashcard Generation - Spaced Repetition", True, "All spaced repetition fields present")
                        else:
                            missing_fields = [f for f in required_fields if f not in flashcard_data]
                            self.log_test("Flashcard Generation - Spaced Repetition", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("Flashcard Generation - Structure", False, "Invalid flashcard structure")
                else:
                    self.log_test("Flashcard Generation - GET Endpoint", False, "CONFIRMED: No flashcards generated - generation logic not triggering")
            else:
                self.log_test("Flashcard Generation - GET Endpoint", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Flashcard Generation - GET Endpoint", False, f"Error: {str(e)}")

    def test_quiz_system_verification(self):
        """Verify the quiz system is working properly"""
        print("\n🧠 Testing Quiz System Verification...")
        
        categories_to_test = ['all', 'faith-god', 'torah-study']
        
        for category in categories_to_test:
            try:
                response = self.session.get(f"{self.base_url}/quiz/{category}?limit=3")
                
                if response.status_code == 200:
                    data = response.json()
                    questions = data.get('questions', [])
                    
                    if questions:
                        self.log_test(f"Quiz - {category} Category", True, f"Generated {len(questions)} questions")
                        
                        # Test question structure
                        sample_question = questions[0]
                        required_fields = ['id', 'type', 'question', 'correct_answer', 'options', 'explanation']
                        if all(field in sample_question for field in required_fields):
                            # Test answer uniqueness
                            options = sample_question.get('options', [])
                            if len(options) == len(set(options)):
                                self.log_test(f"Quiz - {category} Answer Uniqueness", True, "All answers unique")
                            else:
                                self.log_test(f"Quiz - {category} Answer Uniqueness", False, "Duplicate answers found")
                        else:
                            self.log_test(f"Quiz - {category} Structure", False, "Missing required fields")
                    else:
                        self.log_test(f"Quiz - {category} Category", False, "No questions generated")
                else:
                    self.log_test(f"Quiz - {category} Category", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Quiz - {category} Category", False, f"Error: {str(e)}")

    def test_database_verification(self):
        """Verify database has all 613 mitzvot with authentic content"""
        print("\n🗄️ Testing Database Verification...")
        
        try:
            # Test stats endpoint
            stats_response = self.session.get(f"{self.base_url}/stats")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                total_mitzvot = stats_data.get('totalMitzvot', 0)
                
                if total_mitzvot == 613:
                    self.log_test("Database - Total Count", True, "Exactly 613 mitzvot present")
                else:
                    self.log_test("Database - Total Count", False, f"Expected 613, found {total_mitzvot}")
                
                # Check distribution
                direct = stats_data.get('directBiblical', 0)
                if direct > 0:
                    self.log_test("Database - Authentic Content", True, f"Found {direct} direct biblical mitzvot")
                else:
                    self.log_test("Database - Authentic Content", False, "No direct biblical mitzvot found")
            else:
                self.log_test("Database - Stats", False, f"Status: {stats_response.status_code}")
                
            # Test categories
            categories_response = self.session.get(f"{self.base_url}/categories")
            if categories_response.status_code == 200:
                categories_data = categories_response.json()
                if len(categories_data) >= 10:  # Should have multiple categories
                    self.log_test("Database - Categories", True, f"Found {len(categories_data)} categories")
                else:
                    self.log_test("Database - Categories", False, f"Only {len(categories_data)} categories found")
            else:
                self.log_test("Database - Categories", False, f"Status: {categories_response.status_code}")
                
        except Exception as e:
            self.log_test("Database Verification", False, f"Error: {str(e)}")

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test invalid mitzvah ID
        try:
            response = self.session.get(f"{self.base_url}/mitzvot/invalid-id")
            if response.status_code == 404:
                self.log_test("Error Handling - Invalid Mitzvah ID", True, "Properly returned 404")
            else:
                self.log_test("Error Handling - Invalid Mitzvah ID", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Mitzvah ID", False, f"Error: {str(e)}")
        
        # Test invalid quiz category
        try:
            response = self.session.get(f"{self.base_url}/quiz/invalid-category")
            if response.status_code in [400, 404]:
                self.log_test("Error Handling - Invalid Quiz Category", True, f"Properly returned {response.status_code}")
            else:
                self.log_test("Error Handling - Invalid Quiz Category", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Quiz Category", False, f"Error: {str(e)}")
        
        # Test malformed JSON
        try:
            response = self.session.post(f"{self.base_url}/auth/register", data="invalid json")
            if response.status_code in [400, 422]:
                self.log_test("Error Handling - Malformed JSON", True, f"Properly returned {response.status_code}")
            else:
                self.log_test("Error Handling - Malformed JSON", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Malformed JSON", False, f"Error: {str(e)}")

    def run_critical_tests(self):
        """Run all critical tests"""
        print("🔍 Starting Critical Issues Testing for 613 Biblical Laws API")
        print("=" * 70)
        
        # Test authentication system
        self.test_authentication_system()
        
        # Test critical issues
        self.test_progress_tracking_critical_issue()
        self.test_flashcard_generation_issue()
        
        # Test existing systems
        self.test_quiz_system_verification()
        self.test_database_verification()
        
        # Test error handling
        self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 CRITICAL TESTS SUMMARY")
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
        
        return passed, total, failed_tests

def main():
    """Main test execution"""
    print("🚀 613 Biblical Laws API - Critical Issues Testing")
    print(f"Testing against: {BACKEND_URL}")
    print()
    
    tester = CriticalTester(BACKEND_URL)
    passed, total, failed_tests = tester.run_critical_tests()
    
    return passed, total, failed_tests

if __name__ == "__main__":
    main()