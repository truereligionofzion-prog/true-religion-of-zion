#!/usr/bin/env python3
"""
Comprehensive Backend Testing for 613 Biblical Laws API - NEW BIBLICAL STRUCTURE
Tests the new biblical mitzvot structure implementation with:
- No more origin-based filtering (status field removed)
- New categories based on user's list (34 categories)
- Sample mitzvot with proper structure (sourceVerse, book, chapter, verse)
- YHWH/YHUH replacements applied correctly
- Updated quiz system with new question types
- Updated API endpoints
"""

import requests
import json
import sys
import os
from typing import Dict, List, Any

# Get backend URL from environment
BACKEND_URL = "https://torah-data-fix.preview.emergentagent.com/api"

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

    def test_new_biblical_structure_verification(self):
        """Test that the new biblical structure is working correctly"""
        try:
            # Test 1: Verify no more status-based filtering
            response = self.session.get(f"{self.base_url}/mitzvot?status=direct&limit=10")
            if response.status_code == 400:
                self.log_test("New Structure - No Status Filtering", True, "Status parameter properly rejected")
            else:
                self.log_test("New Structure - No Status Filtering", False, f"Status parameter still accepted: {response.status_code}")
                return False
            
            # Test 2: Get sample mitzvot to verify new structure
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=20")
            if response.status_code != 200:
                self.log_test("New Structure - Data Retrieval", False, f"Status: {response.status_code}")
                return False
                
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            if not mitzvot:
                self.log_test("New Structure - Data Retrieval", False, "No mitzvot returned")
                return False
            
            # Test 3: Verify new structure fields
            structure_tests_passed = 0
            yhwh_replacements_found = 0
            proper_verse_structure = 0
            
            for mitzvah in mitzvot:
                # Check for required new fields
                required_fields = ['sourceVerse', 'book', 'chapter', 'verse']
                has_all_fields = all(field in mitzvah for field in required_fields)
                
                # Check that old fields are removed
                old_fields = ['traditionalWording', 'scholarlyNote', 'status']
                has_old_fields = any(field in mitzvah for field in old_fields)
                
                if has_all_fields and not has_old_fields:
                    structure_tests_passed += 1
                
                # Check for YHWH/YHUH replacements
                source_verse = mitzvah.get('sourceVerse', '')
                title = mitzvah.get('title', '')
                if 'YHWH' in source_verse or 'YHUH' in source_verse or 'YHWH' in title or 'YHUH' in title:
                    yhwh_replacements_found += 1
                
                # Check proper verse structure (should have book, chapter, verse)
                book = mitzvah.get('book', '')
                chapter = mitzvah.get('chapter')
                verse = mitzvah.get('verse')
                if book and chapter and verse and isinstance(chapter, int) and isinstance(verse, int):
                    proper_verse_structure += 1
            
            # Test results
            total_mitzvot = len(mitzvot)
            if structure_tests_passed == total_mitzvot:
                self.log_test("New Structure - Field Structure", True, f"All {total_mitzvot} mitzvot have new structure")
            else:
                self.log_test("New Structure - Field Structure", False, f"Only {structure_tests_passed}/{total_mitzvot} have new structure")
            
            if yhwh_replacements_found > 0:
                self.log_test("New Structure - YHWH Replacements", True, f"Found {yhwh_replacements_found} mitzvot with YHWH/YHUH")
            else:
                self.log_test("New Structure - YHWH Replacements", False, "No YHWH/YHUH replacements found")
            
            if proper_verse_structure >= total_mitzvot * 0.9:
                self.log_test("New Structure - Verse Structure", True, f"{proper_verse_structure}/{total_mitzvot} have proper verse structure")
            else:
                self.log_test("New Structure - Verse Structure", False, f"Only {proper_verse_structure}/{total_mitzvot} have proper verse structure")
            
            return structure_tests_passed >= total_mitzvot * 0.9
            
        except Exception as e:
            self.log_test("New Biblical Structure Verification", False, f"Error: {str(e)}")
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
    
    def test_enhanced_data_structure(self):
        """Test that mitzvot have all new enhanced fields (traditionalWording, sourceVerse, enhanced scholarlyNote)"""
        try:
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=20")
            if response.status_code != 200:
                self.log_test("Enhanced Data Structure", False, f"Status: {response.status_code}")
                return False
                
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            if not mitzvot:
                self.log_test("Enhanced Data Structure", False, "No mitzvot returned")
                return False
            
            # Test each mitzvah for enhanced fields
            enhanced_fields_count = 0
            traditional_wording_count = 0
            source_verse_count = 0
            scholarly_note_count = 0
            
            for mitzvah in mitzvot:
                # Check for traditionalWording field
                traditional_wording = mitzvah.get('traditionalWording', '')
                if traditional_wording and len(traditional_wording) > 10:
                    traditional_wording_count += 1
                
                # Check for sourceVerse field
                source_verse = mitzvah.get('sourceVerse', '')
                if source_verse and len(source_verse) > 10:
                    source_verse_count += 1
                
                # Check for enhanced scholarlyNote field
                scholarly_note = mitzvah.get('scholarlyNote', '')
                if scholarly_note and len(scholarly_note) > 20:
                    scholarly_note_count += 1
                
                # Count mitzvot with all enhanced fields
                if traditional_wording and source_verse and scholarly_note:
                    enhanced_fields_count += 1
            
            # Test results
            total_mitzvot = len(mitzvot)
            if enhanced_fields_count == total_mitzvot:
                self.log_test("Enhanced Data - All Fields Present", True, f"All {total_mitzvot} mitzvot have enhanced fields")
            else:
                self.log_test("Enhanced Data - All Fields Present", False, f"Only {enhanced_fields_count}/{total_mitzvot} have all enhanced fields")
            
            if traditional_wording_count >= total_mitzvot * 0.9:
                self.log_test("Enhanced Data - Traditional Wording", True, f"{traditional_wording_count}/{total_mitzvot} have traditional wording")
            else:
                self.log_test("Enhanced Data - Traditional Wording", False, f"Only {traditional_wording_count}/{total_mitzvot} have traditional wording")
            
            if source_verse_count >= total_mitzvot * 0.9:
                self.log_test("Enhanced Data - Source Verses", True, f"{source_verse_count}/{total_mitzvot} have source verses")
            else:
                self.log_test("Enhanced Data - Source Verses", False, f"Only {source_verse_count}/{total_mitzvot} have source verses")
            
            if scholarly_note_count >= total_mitzvot * 0.9:
                self.log_test("Enhanced Data - Scholarly Notes", True, f"{scholarly_note_count}/{total_mitzvot} have scholarly notes")
            else:
                self.log_test("Enhanced Data - Scholarly Notes", False, f"Only {scholarly_note_count}/{total_mitzvot} have scholarly notes")
            
            return enhanced_fields_count >= total_mitzvot * 0.9
            
        except Exception as e:
            self.log_test("Enhanced Data Structure", False, f"Error: {str(e)}")
            return False

    def test_simplified_status_filtering(self):
        """Test filtering by simplified status types: 'direct' and 'indirect' only"""
        try:
            # Test direct status filtering - should return 421 mitzvot (based on current stats)
            response = self.session.get(f"{self.base_url}/mitzvot?status=direct&limit=100")
            if response.status_code == 200:
                data = response.json()
                direct_count = data.get('total', 0)
                
                if 420 <= direct_count <= 425:  # Allow some variance
                    self.log_test("Status Filter - Direct", True, f"Found {direct_count} direct mitzvot (expected ~421)")
                else:
                    self.log_test("Status Filter - Direct", False, f"Found {direct_count} direct mitzvot (expected ~421)")
            else:
                self.log_test("Status Filter - Direct", False, f"Status: {response.status_code}")
                return False
            
            # Test indirect status filtering - should return 94 mitzvot (based on current stats)
            response = self.session.get(f"{self.base_url}/mitzvot?status=indirect&limit=100")
            if response.status_code == 200:
                data = response.json()
                indirect_count = data.get('total', 0)
                
                if 90 <= indirect_count <= 100:  # Allow some variance
                    self.log_test("Status Filter - Indirect", True, f"Found {indirect_count} indirect mitzvot (expected ~94)")
                else:
                    self.log_test("Status Filter - Indirect", False, f"Found {indirect_count} indirect mitzvot (expected ~94)")
            else:
                self.log_test("Status Filter - Indirect", False, f"Status: {response.status_code}")
                return False
            
            # Test that direct + indirect adds up correctly (should be 515 total)
            total_filtered = direct_count + indirect_count
            if 510 <= total_filtered <= 520:  # Allow some variance
                self.log_test("Status Filter - Biblical Total", True, f"Direct + Indirect = {total_filtered} (biblical mitzvot)")
            else:
                self.log_test("Status Filter - Biblical Total", False, f"Direct + Indirect = {total_filtered} (unexpected total)")
            
            # Test status filter options in API response
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=1")
            if response.status_code == 200:
                data = response.json()
                filters = data.get('filters', {})
                status_types = filters.get('statusTypes', [])
                
                # Should only have 2 status types
                if len(status_types) == 2:
                    status_values = [st.get('value') for st in status_types]
                    if 'direct' in status_values and 'indirect' in status_values:
                        self.log_test("Status Filter - Options", True, "Only 'direct' and 'indirect' status options available")
                    else:
                        self.log_test("Status Filter - Options", False, f"Unexpected status values: {status_values}")
                else:
                    self.log_test("Status Filter - Options", False, f"Expected 2 status types, found {len(status_types)}")
            
            return True
            
        except Exception as e:
            self.log_test("Simplified Status Filtering", False, f"Error: {str(e)}")
            return False

    def test_enhanced_search_functionality(self):
        """Test enhanced search across title, traditionalWording, sourceVerse, scholarlyNote, and keywords"""
        try:
            # Test search for "God" - should return results from multiple fields
            response = self.session.get(f"{self.base_url}/mitzvot?search=God&limit=50")
            if response.status_code == 200:
                data = response.json()
                results = data.get('mitzvot', [])
                
                if results:
                    # Check which fields contain the search term
                    fields_found = set()
                    for mitzvah in results:
                        if 'God' in mitzvah.get('title', ''):
                            fields_found.add('title')
                        if 'God' in mitzvah.get('traditionalWording', ''):
                            fields_found.add('traditionalWording')
                        if 'God' in mitzvah.get('sourceVerse', ''):
                            fields_found.add('sourceVerse')
                        if 'God' in mitzvah.get('scholarlyNote', ''):
                            fields_found.add('scholarlyNote')
                        keywords = mitzvah.get('keywords', [])
                        if any('God' in keyword for keyword in keywords):
                            fields_found.add('keywords')
                    
                    if len(fields_found) >= 3:
                        self.log_test("Enhanced Search - Multiple Fields", True, f"Found 'God' in fields: {list(fields_found)}")
                    else:
                        self.log_test("Enhanced Search - Multiple Fields", False, f"Only found in fields: {list(fields_found)}")
                    
                    self.log_test("Enhanced Search - God Results", True, f"Found {len(results)} results for 'God'")
                else:
                    self.log_test("Enhanced Search - God Results", False, "No results found for 'God'")
            else:
                self.log_test("Enhanced Search - God Results", False, f"Status: {response.status_code}")
                return False
            
            # Test other search terms
            search_terms = [
                ("Torah", "Should find Torah-related mitzvot"),
                ("commandment", "Should find commandment references"),
                ("Exodus", "Should find Exodus references"),
                ("sacrifice", "Should find sacrifice-related mitzvot")
            ]
            
            search_passed = 0
            for term, description in search_terms:
                try:
                    response = self.session.get(f"{self.base_url}/mitzvot?search={term}&limit=20")
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('mitzvot', [])
                        if results:
                            self.log_test(f"Enhanced Search - '{term}'", True, f"Found {len(results)} results")
                            search_passed += 1
                        else:
                            self.log_test(f"Enhanced Search - '{term}'", False, "No results found")
                    else:
                        self.log_test(f"Enhanced Search - '{term}'", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"Enhanced Search - '{term}'", False, f"Error: {str(e)}")
            
            return search_passed >= len(search_terms) * 0.75  # At least 75% should work
            
        except Exception as e:
            self.log_test("Enhanced Search Functionality", False, f"Error: {str(e)}")
            return False

    def test_categories_validation(self):
        """Test that all 13 categories exist and have appropriate mitzvot assigned"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            if response.status_code == 200:
                categories = response.json()
                
                if len(categories) == 13:
                    self.log_test("Categories - Count", True, f"Found exactly 13 categories")
                else:
                    self.log_test("Categories - Count", False, f"Found {len(categories)} categories (expected 13)")
                
                # Check that each category has mitzvot assigned
                categories_with_mitzvot = 0
                total_mitzvot_in_categories = 0
                
                for category in categories:
                    count = category.get('count', 0)
                    name = category.get('name', 'Unknown')
                    if count > 0:
                        categories_with_mitzvot += 1
                        total_mitzvot_in_categories += count
                        self.log_test(f"Category - {name}", True, f"{count} mitzvot assigned")
                    else:
                        self.log_test(f"Category - {name}", False, "No mitzvot assigned")
                
                # Check that total mitzvot in categories equals 613
                if total_mitzvot_in_categories == 613:
                    self.log_test("Categories - Total Assignment", True, f"All 613 mitzvot properly categorized")
                else:
                    self.log_test("Categories - Total Assignment", False, f"Only {total_mitzvot_in_categories}/613 mitzvot categorized")
                
                # Check that all categories have mitzvot
                if categories_with_mitzvot == 13:
                    self.log_test("Categories - All Have Mitzvot", True, "All 13 categories have mitzvot assigned")
                else:
                    self.log_test("Categories - All Have Mitzvot", False, f"Only {categories_with_mitzvot}/13 categories have mitzvot")
                
                return len(categories) == 13 and categories_with_mitzvot == 13 and total_mitzvot_in_categories == 613
            else:
                self.log_test("Categories Validation", False, f"Status: {response.status_code}")
                return False
            
        except Exception as e:
            self.log_test("Categories Validation", False, f"Error: {str(e)}")
            return False

    def test_individual_mitzvah_data_structure(self):
        """Test individual mitzvah endpoint to verify complete enhanced data structure"""
        try:
            # First get a list of mitzvot to get valid IDs
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=5")
            if response.status_code != 200:
                self.log_test("Individual Mitzvah - Get IDs", False, f"Status: {response.status_code}")
                return False
            
            data = response.json()
            mitzvot = data.get('mitzvot', [])
            
            if not mitzvot:
                self.log_test("Individual Mitzvah - Get IDs", False, "No mitzvot available")
                return False
            
            # Test individual mitzvah endpoints
            tests_passed = 0
            for mitzvah in mitzvot[:3]:  # Test first 3
                mitzvah_id = mitzvah.get('id')
                if not mitzvah_id:
                    continue
                
                try:
                    response = self.session.get(f"{self.base_url}/mitzvot/{mitzvah_id}")
                    if response.status_code == 200:
                        individual_mitzvah = response.json()
                        
                        # Check for all enhanced fields
                        required_fields = [
                            'id', 'number', 'title', 'traditionalWording', 
                            'sourceVerse', 'scholarlyNote', 'category', 'status', 
                            'book', 'keywords'
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in individual_mitzvah]
                        
                        if not missing_fields:
                            # Check field quality
                            traditional_wording = individual_mitzvah.get('traditionalWording', '')
                            source_verse = individual_mitzvah.get('sourceVerse', '')
                            scholarly_note = individual_mitzvah.get('scholarlyNote', '')
                            
                            if (len(traditional_wording) > 10 and 
                                len(source_verse) > 10 and 
                                len(scholarly_note) > 20):
                                self.log_test(f"Individual Mitzvah - {mitzvah_id[:8]}", True, "Complete enhanced data structure")
                                tests_passed += 1
                            else:
                                self.log_test(f"Individual Mitzvah - {mitzvah_id[:8]}", False, "Enhanced fields too short")
                        else:
                            self.log_test(f"Individual Mitzvah - {mitzvah_id[:8]}", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test(f"Individual Mitzvah - {mitzvah_id[:8]}", False, f"Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"Individual Mitzvah - {mitzvah_id[:8]}", False, f"Error: {str(e)}")
            
            return tests_passed >= 2  # At least 2 out of 3 should pass
            
        except Exception as e:
            self.log_test("Individual Mitzvah Data Structure", False, f"Error: {str(e)}")
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
                        status_questions_found = 0
                        
                        for question in questions:
                            # Check required fields
                            required_fields = ['id', 'type', 'question', 'correct_answer', 'options', 'explanation']
                            if all(field in question for field in required_fields):
                                question_text = question.get('question', '').lower()
                                
                                # Check question type diversity
                                if 'traditional wording' in question_text and 'which mitzvah' in question_text:
                                    question_types_found.add('title_from_traditional')
                                elif 'traditional wording for' in question_text:
                                    question_types_found.add('traditional_from_title')
                                elif 'category' in question_text:
                                    question_types_found.add('category_from_title')
                                elif 'biblical status' in question_text:
                                    question_types_found.add('status_from_title')
                                    status_questions_found += 1
                                    
                                    # Test enhanced status questions - should only have 2 biblical status options
                                    options = question.get('options', [])
                                    biblical_status_options = [opt for opt in options if 'Direct in Bible' in opt or 'Indirect in Bible' in opt]
                                    if len(biblical_status_options) >= 1:
                                        self.log_test(f"Quiz - {category} Status Question Format", True, f"Found biblical status options: {biblical_status_options}")
                                    else:
                                        self.log_test(f"Quiz - {category} Status Question Format", False, f"No biblical status options found in: {options}")
                                
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
                        
                        if status_questions_found > 0:
                            self.log_test(f"Quiz - {category} Status Questions", True, f"Found {status_questions_found} status-based questions")
                        else:
                            self.log_test(f"Quiz - {category} Status Questions", False, "No status-based questions found")
                        
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
                
                # The flashcard system may return empty if no cards are due for review
                # This is expected behavior for spaced repetition
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
                    # Empty flashcards is expected behavior for spaced repetition when no cards are due
                    self.log_test("Flashcards - GET Endpoint", True, "No flashcards due for review (expected for spaced repetition)")
                    
                    # Test that the endpoint structure is correct even with empty results
                    if 'flashcards' in data and 'total' in data:
                        self.log_test("Flashcards - Response Structure", True, "Proper response structure with empty results")
                    else:
                        self.log_test("Flashcards - Response Structure", False, "Invalid response structure")
                    
                    # Test invalid flashcard ID handling
                    invalid_review = self.session.post(f"{self.base_url}/flashcards/invalid-id/review?difficulty=3&correct=true")
                    if invalid_review.status_code == 404:
                        self.log_test("Flashcards - Invalid ID Handling", True, "Properly handled invalid flashcard ID")
                    else:
                        self.log_test("Flashcards - Invalid ID Handling", False, f"Status: {invalid_review.status_code}")
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

    def test_batch_7_data_correction(self):
        """Test Batch 7 data correction for Mitzvot 137-186 - traditional wording and scholarly notes"""
        try:
            print("\n🔍 Testing Batch 7 Data Correction (Mitzvot 137-186)...")
            
            # Get all mitzvot using pagination (API limit is 100 per page)
            all_mitzvot = []
            page = 1
            while True:
                response = self.session.get(f"{self.base_url}/mitzvot?page={page}&limit=100")
                if response.status_code != 200:
                    self.log_test("Batch 7 - Data Retrieval", False, f"Status: {response.status_code} on page {page}")
                    return False
                
                data = response.json()
                mitzvot = data.get('mitzvot', [])
                if not mitzvot:
                    break
                    
                all_mitzvot.extend(mitzvot)
                
                if page >= data.get('totalPages', 1):
                    break
                page += 1
            
            if not all_mitzvot:
                self.log_test("Batch 7 - Data Retrieval", False, "No mitzvot returned")
                return False
            
            self.log_test("Batch 7 - Data Retrieval", True, f"Retrieved {len(all_mitzvot)} total mitzvot")
            
            # Filter mitzvot 137-186 (Batch 7)
            batch_7_mitzvot = [m for m in all_mitzvot if 137 <= m.get('number', 0) <= 186]
            
            if len(batch_7_mitzvot) != 50:
                self.log_test("Batch 7 - Range Verification", False, f"Expected 50 mitzvot (137-186), found {len(batch_7_mitzvot)}")
                return False
            
            self.log_test("Batch 7 - Range Verification", True, f"Found all 50 mitzvot in range 137-186")
            
            # Test specific mitzvot mentioned in the review request
            specific_tests = [
                (137, "firstborn", "Should contain firstborn-related content"),
                (186, "shelamim", "Should contain shelamim-related content")
            ]
            
            corrected_count = 0
            traditional_wording_count = 0
            scholarly_notes_count = 0
            proper_format_count = 0
            
            # Sample a few mitzvot to check their content
            sample_mitzvot = [m for m in batch_7_mitzvot if m.get('number') in [137, 150, 170, 186]]
            
            for mitzvah in batch_7_mitzvot:
                number = mitzvah.get('number')
                traditional_wording = mitzvah.get('traditionalWording', '')
                scholarly_note = mitzvah.get('scholarlyNote', '')
                
                # Check traditional wording quality (should not be generic "To do X")
                if traditional_wording and len(traditional_wording) > 10:
                    # Check if it's not just a generic "To" statement
                    if not traditional_wording.strip().startswith('To '):
                        traditional_wording_count += 1
                    elif len(traditional_wording) > 30:  # Even "To" statements can be detailed
                        traditional_wording_count += 1
                
                # Check scholarly notes format and quality
                if scholarly_note:
                    if '**Scholarly Analysis**:' in scholarly_note and '**Additional Context**:' in scholarly_note:
                        proper_format_count += 1
                    elif len(scholarly_note) > 50:  # At least substantial content
                        scholarly_notes_count += 1
                
                # Test specific mitzvot content
                for test_number, keyword, description in specific_tests:
                    if number == test_number:
                        # Check if content contains expected keywords (case insensitive)
                        full_content = f"{traditional_wording} {scholarly_note}".lower()
                        if keyword.lower() in full_content:
                            self.log_test(f"Batch 7 - Mitzvah {number} Content", True, f"Contains expected keyword '{keyword}'")
                            corrected_count += 1
                        else:
                            # Log what we actually found for debugging
                            content_preview = traditional_wording[:100] if traditional_wording else "No traditional wording"
                            self.log_test(f"Batch 7 - Mitzvah {number} Content", False, f"Missing '{keyword}' in: {content_preview}...")
            
            # Log sample mitzvot for verification
            for mitzvah in sample_mitzvot:
                number = mitzvah.get('number')
                traditional_wording = mitzvah.get('traditionalWording', '')[:100]
                scholarly_note = mitzvah.get('scholarlyNote', '')[:100]
                self.log_test(f"Batch 7 - Sample {number}", True, f"Traditional: {traditional_wording}... | Scholarly: {scholarly_note}...")
            
            # Test overall correction quality
            if traditional_wording_count >= 40:  # At least 80% should have proper traditional wording
                self.log_test("Batch 7 - Traditional Wording Quality", True, f"{traditional_wording_count}/50 have quality traditional wording")
            else:
                self.log_test("Batch 7 - Traditional Wording Quality", False, f"Only {traditional_wording_count}/50 have quality traditional wording")
            
            if proper_format_count >= 30:  # At least 60% should have the new format
                self.log_test("Batch 7 - Scholarly Notes Format", True, f"{proper_format_count}/50 have proper scholarly analysis format")
            elif scholarly_notes_count >= 40:  # Or at least enhanced scholarly notes
                self.log_test("Batch 7 - Scholarly Notes Enhanced", True, f"{scholarly_notes_count}/50 have enhanced scholarly notes")
            else:
                self.log_test("Batch 7 - Scholarly Notes", False, f"Only {proper_format_count} have proper format, {scholarly_notes_count} have enhanced notes")
            
            # Test data differentiation (traditional wording vs scholarly notes should be different)
            differentiated_count = 0
            for mitzvah in batch_7_mitzvot:
                traditional_wording = mitzvah.get('traditionalWording', '').lower()
                scholarly_note = mitzvah.get('scholarlyNote', '').lower()
                
                # They should be different content
                if traditional_wording and scholarly_note and traditional_wording != scholarly_note:
                    # Check they're not too similar (basic differentiation test)
                    if len(traditional_wording) > 10 and len(scholarly_note) > 10:
                        differentiated_count += 1
            
            if differentiated_count >= 40:
                self.log_test("Batch 7 - Content Differentiation", True, f"{differentiated_count}/50 have properly differentiated content")
            else:
                self.log_test("Batch 7 - Content Differentiation", False, f"Only {differentiated_count}/50 have properly differentiated content")
            
            return (traditional_wording_count >= 40 and 
                   (proper_format_count >= 30 or scholarly_notes_count >= 40) and 
                   differentiated_count >= 40)
            
        except Exception as e:
            self.log_test("Batch 7 Data Correction", False, f"Error: {str(e)}")
            return False

    def test_search_filter_with_corrected_data(self):
        """Test search and filter functionality with the corrected Batch 7 data"""
        try:
            # Test search functionality with terms that should be in corrected data
            search_terms = [
                ("firstborn", "Should find mitzvah 137 and related"),
                ("shelamim", "Should find mitzvah 186 and related"),
                ("sacrifice", "Should find sacrifice-related mitzvot"),
                ("offering", "Should find offering-related mitzvot")
            ]
            
            search_passed = 0
            for term, description in search_terms:
                try:
                    response = self.session.get(f"{self.base_url}/mitzvot?search={term}&limit=50")
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('mitzvot', [])
                        
                        # Check if any results are from Batch 7 (137-186)
                        batch_7_results = [r for r in results if 137 <= r.get('number', 0) <= 186]
                        
                        if batch_7_results:
                            self.log_test(f"Search Corrected Data - '{term}'", True, f"Found {len(batch_7_results)} Batch 7 results out of {len(results)} total")
                            search_passed += 1
                        elif results:
                            self.log_test(f"Search Corrected Data - '{term}'", True, f"Found {len(results)} results (no Batch 7 matches)")
                            search_passed += 0.5  # Partial credit
                        else:
                            self.log_test(f"Search Corrected Data - '{term}'", False, "No results found")
                    else:
                        self.log_test(f"Search Corrected Data - '{term}'", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"Search Corrected Data - '{term}'", False, f"Error: {str(e)}")
            
            # Test category filtering for categories that might contain Batch 7 mitzvot
            categories_to_test = ["temple-worship", "tithes-offerings", "festivals"]
            filter_passed = 0
            
            for category in categories_to_test:
                try:
                    response = self.session.get(f"{self.base_url}/mitzvot?category={category}&limit=100")
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('mitzvot', [])
                        
                        # Check if any results are from Batch 7
                        batch_7_results = [r for r in results if 137 <= r.get('number', 0) <= 186]
                        
                        if batch_7_results:
                            self.log_test(f"Filter Corrected Data - {category}", True, f"Found {len(batch_7_results)} Batch 7 mitzvot in category")
                            filter_passed += 1
                        elif results:
                            self.log_test(f"Filter Corrected Data - {category}", True, f"Category has {len(results)} mitzvot (no Batch 7)")
                            filter_passed += 0.5
                        else:
                            self.log_test(f"Filter Corrected Data - {category}", False, "No results in category")
                    else:
                        self.log_test(f"Filter Corrected Data - {category}", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"Filter Corrected Data - {category}", False, f"Error: {str(e)}")
            
            return search_passed >= 3 and filter_passed >= 2
            
        except Exception as e:
            self.log_test("Search Filter Corrected Data", False, f"Error: {str(e)}")
            return False

    def test_quiz_flashcard_with_corrected_data(self):
        """Test quiz and flashcard systems can access corrected Batch 7 data"""
        try:
            # Test quiz generation - should be able to use corrected data
            response = self.session.get(f"{self.base_url}/quiz/all?limit=10")
            if response.status_code == 200:
                data = response.json()
                questions = data.get('questions', [])
                
                if questions:
                    # Check if any questions use Batch 7 mitzvot
                    batch_7_questions = 0
                    for question in questions:
                        question_text = question.get('question', '')
                        explanation = question.get('explanation', '')
                        
                        # Look for mitzvah numbers in explanation
                        import re
                        numbers = re.findall(r'#(\d+)', explanation)
                        for num_str in numbers:
                            num = int(num_str)
                            if 137 <= num <= 186:
                                batch_7_questions += 1
                                break
                    
                    if batch_7_questions > 0:
                        self.log_test("Quiz Corrected Data Access", True, f"Found {batch_7_questions} questions using Batch 7 mitzvot")
                    else:
                        self.log_test("Quiz Corrected Data Access", True, f"Quiz system working (generated {len(questions)} questions)")
                else:
                    self.log_test("Quiz Corrected Data Access", False, "No questions generated")
            else:
                self.log_test("Quiz Corrected Data Access", False, f"Status: {response.status_code}")
                return False
            
            # Test flashcard system
            response = self.session.get(f"{self.base_url}/flashcards?limit=10")
            if response.status_code == 200:
                data = response.json()
                flashcards = data.get('flashcards', [])
                
                if flashcards:
                    # Check if any flashcards use Batch 7 mitzvot
                    batch_7_flashcards = 0
                    for flashcard_data in flashcards:
                        mitzvah = flashcard_data.get('mitzvah', {})
                        number = mitzvah.get('number', 0)
                        if 137 <= number <= 186:
                            batch_7_flashcards += 1
                    
                    if batch_7_flashcards > 0:
                        self.log_test("Flashcard Corrected Data Access", True, f"Found {batch_7_flashcards} flashcards using Batch 7 mitzvot")
                    else:
                        self.log_test("Flashcard Corrected Data Access", True, f"Flashcard system working (found {len(flashcards)} flashcards)")
                else:
                    # Empty flashcards is normal for spaced repetition
                    self.log_test("Flashcard Corrected Data Access", True, "Flashcard system accessible (no cards due for review)")
            else:
                self.log_test("Flashcard Corrected Data Access", False, f"Status: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Quiz Flashcard Corrected Data", False, f"Error: {str(e)}")
            return False
    
    def test_specific_batch_7_verification(self):
        """Test specific Batch 7 data correction as requested in review"""
        try:
            print("\n🎯 SPECIFIC BATCH 7 VERIFICATION - Testing Review Request Requirements")
            print("=" * 70)
            
            # Get all mitzvot to find specific ones
            all_mitzvot = []
            page = 1
            while True:
                response = self.session.get(f"{self.base_url}/mitzvot?page={page}&limit=100")
                if response.status_code != 200:
                    self.log_test("Batch 7 Verification - Data Retrieval", False, f"Status: {response.status_code}")
                    return False
                
                data = response.json()
                mitzvot = data.get('mitzvot', [])
                if not mitzvot:
                    break
                    
                all_mitzvot.extend(mitzvot)
                
                if page >= data.get('totalPages', 1):
                    break
                page += 1
            
            # Find specific mitzvot mentioned in review request
            mitzvah_137 = None
            mitzvah_186 = None
            
            for mitzvah in all_mitzvot:
                if mitzvah.get('number') == 137:
                    mitzvah_137 = mitzvah
                elif mitzvah.get('number') == 186:
                    mitzvah_186 = mitzvah
            
            # Test Mitzvah 137 - Should be "Offer firstborn ox, sheep, goat."
            if mitzvah_137:
                traditional_wording = mitzvah_137.get('traditionalWording', '')
                scholarly_note = mitzvah_137.get('scholarlyNote', '')
                full_content = f"{traditional_wording} {scholarly_note}".lower()
                
                print(f"\n📋 MITZVAH 137 ANALYSIS:")
                print(f"Traditional Wording: {traditional_wording}")
                print(f"Scholarly Note: {scholarly_note[:200]}...")
                
                # Check for expected content
                expected_terms = ['firstborn', 'ox', 'sheep', 'goat', 'offer']
                found_terms = [term for term in expected_terms if term in full_content]
                
                if len(found_terms) >= 3:  # Should find at least 3 of the 5 terms
                    self.log_test("Mitzvah 137 - Expected Content", True, f"Found terms: {found_terms}")
                else:
                    self.log_test("Mitzvah 137 - Expected Content", False, f"Only found: {found_terms}, expected: {expected_terms}")
                
                # Check if traditional wording matches expected format
                if 'firstborn' in traditional_wording.lower() and any(animal in traditional_wording.lower() for animal in ['ox', 'sheep', 'goat']):
                    self.log_test("Mitzvah 137 - Traditional Wording Format", True, "Contains firstborn and animals")
                else:
                    self.log_test("Mitzvah 137 - Traditional Wording Format", False, "Missing expected firstborn/animals format")
            else:
                self.log_test("Mitzvah 137 - Existence", False, "Mitzvah 137 not found")
            
            # Test Mitzvah 186 - Should be "Offer shelamim sacrifices."
            if mitzvah_186:
                traditional_wording = mitzvah_186.get('traditionalWording', '')
                scholarly_note = mitzvah_186.get('scholarlyNote', '')
                full_content = f"{traditional_wording} {scholarly_note}".lower()
                
                print(f"\n📋 MITZVAH 186 ANALYSIS:")
                print(f"Traditional Wording: {traditional_wording}")
                print(f"Scholarly Note: {scholarly_note[:200]}...")
                
                # Check for expected content
                expected_terms = ['shelamim', 'sacrifice', 'offer', 'peace']
                found_terms = [term for term in expected_terms if term in full_content]
                
                if len(found_terms) >= 2:  # Should find at least 2 of the 4 terms
                    self.log_test("Mitzvah 186 - Expected Content", True, f"Found terms: {found_terms}")
                else:
                    self.log_test("Mitzvah 186 - Expected Content", False, f"Only found: {found_terms}, expected: {expected_terms}")
                
                # Check if traditional wording matches expected format
                if 'shelamim' in traditional_wording.lower() or ('peace' in traditional_wording.lower() and 'sacrifice' in traditional_wording.lower()):
                    self.log_test("Mitzvah 186 - Traditional Wording Format", True, "Contains shelamim or peace sacrifice")
                else:
                    self.log_test("Mitzvah 186 - Traditional Wording Format", False, "Missing expected shelamim/peace sacrifice format")
            else:
                self.log_test("Mitzvah 186 - Existence", False, "Mitzvah 186 not found")
            
            # Test search functionality for specific terms
            search_tests = [
                ("shelamim", "Should return mitzvah 186 and related"),
                ("firstborn", "Should return mitzvah 137 and related")
            ]
            
            search_success = 0
            for term, description in search_tests:
                response = self.session.get(f"{self.base_url}/mitzvot?search={term}&limit=50")
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('mitzvot', [])
                    
                    if results:
                        # Check if we found the specific mitzvot
                        found_numbers = [r.get('number') for r in results]
                        if term == "shelamim" and 186 in found_numbers:
                            self.log_test(f"Search - {term} (Mitzvah 186)", True, f"Found mitzvah 186 in {len(results)} results")
                            search_success += 1
                        elif term == "firstborn" and 137 in found_numbers:
                            self.log_test(f"Search - {term} (Mitzvah 137)", True, f"Found mitzvah 137 in {len(results)} results")
                            search_success += 1
                        else:
                            self.log_test(f"Search - {term}", True, f"Found {len(results)} results (target mitzvah not in results)")
                            search_success += 0.5
                    else:
                        self.log_test(f"Search - {term}", False, "No results found")
                else:
                    self.log_test(f"Search - {term}", False, f"Status: {response.status_code}")
            
            # Test quiz system can access corrected data
            quiz_response = self.session.get(f"{self.base_url}/quiz/all?limit=20")
            if quiz_response.status_code == 200:
                quiz_data = quiz_response.json()
                questions = quiz_data.get('questions', [])
                
                # Check if any questions reference mitzvot 137 or 186
                batch_7_questions = 0
                for question in questions:
                    explanation = question.get('explanation', '')
                    if '#137' in explanation or '#186' in explanation:
                        batch_7_questions += 1
                
                if questions:
                    self.log_test("Quiz - Corrected Data Access", True, f"Generated {len(questions)} questions, {batch_7_questions} from target mitzvot")
                else:
                    self.log_test("Quiz - Corrected Data Access", False, "No quiz questions generated")
            else:
                self.log_test("Quiz - Corrected Data Access", False, f"Status: {quiz_response.status_code}")
            
            # Overall assessment
            mitzvah_137_ok = mitzvah_137 is not None
            mitzvah_186_ok = mitzvah_186 is not None
            search_ok = search_success >= 1.5
            
            overall_success = mitzvah_137_ok and mitzvah_186_ok and search_ok
            
            if overall_success:
                self.log_test("Batch 7 Verification - Overall", True, "Core requirements verified")
            else:
                self.log_test("Batch 7 Verification - Overall", False, "Some requirements not met")
            
            return overall_success
            
        except Exception as e:
            self.log_test("Batch 7 Verification", False, f"Error: {str(e)}")
            return False

    def test_new_categories_structure(self):
        """Test that new categories (34 categories) are created correctly"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            if response.status_code == 200:
                categories = response.json()
                
                # Test for 34 categories as mentioned in review request
                if len(categories) == 34:
                    self.log_test("New Categories - Count", True, f"Found exactly 34 categories")
                else:
                    self.log_test("New Categories - Count", False, f"Found {len(categories)} categories (expected 34)")
                
                # Check that each category has mitzvot assigned
                categories_with_mitzvot = 0
                total_mitzvot_in_categories = 0
                
                for category in categories:
                    count = category.get('count', 0)
                    name = category.get('name', 'Unknown')
                    if count > 0:
                        categories_with_mitzvot += 1
                        total_mitzvot_in_categories += count
                        self.log_test(f"New Category - {name}", True, f"{count} mitzvot assigned")
                    else:
                        self.log_test(f"New Category - {name}", False, "No mitzvot assigned")
                
                # Check that total mitzvot in categories equals 613
                if total_mitzvot_in_categories == 613:
                    self.log_test("New Categories - Total Assignment", True, f"All 613 mitzvot properly categorized")
                else:
                    self.log_test("New Categories - Total Assignment", False, f"Only {total_mitzvot_in_categories}/613 mitzvot categorized")
                
                return len(categories) == 34 and categories_with_mitzvot >= 30 and total_mitzvot_in_categories == 613
            else:
                self.log_test("New Categories Structure", False, f"Status: {response.status_code}")
                return False
            
        except Exception as e:
            self.log_test("New Categories Structure", False, f"Error: {str(e)}")
            return False

    def test_new_quiz_system(self):
        """Test the updated quiz system with new question types"""
        try:
            # Test quiz generation for different categories
            categories_to_test = ["all", "faith-god", "torah-study"]
            quiz_tests_passed = 0
            
            for category in categories_to_test:
                try:
                    response = self.session.get(f"{self.base_url}/quiz/{category}?limit=5")
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get('questions', [])
                        
                        if not questions:
                            self.log_test(f"New Quiz - {category} Generation", False, "No questions generated")
                            continue
                        
                        # Test for new question types
                        new_question_types_found = set()
                        
                        for question in questions:
                            question_text = question.get('question', '').lower()
                            
                            # Check for new question types
                            if 'which biblical verse corresponds to' in question_text:
                                new_question_types_found.add('verse_from_title')
                            elif 'which book of the bible' in question_text:
                                new_question_types_found.add('book_from_title')
                            elif 'which category does this commandment belong to' in question_text:
                                new_question_types_found.add('category_from_title')
                            elif 'which mitzvah is derived from this verse' in question_text:
                                new_question_types_found.add('title_from_verse')
                        
                        # Test results
                        if len(new_question_types_found) >= 2:
                            self.log_test(f"New Quiz - {category} Question Types", True, f"Found new question types: {list(new_question_types_found)}")
                            quiz_tests_passed += 1
                        else:
                            self.log_test(f"New Quiz - {category} Question Types", False, f"Only found: {list(new_question_types_found)}")
                        
                        self.log_test(f"New Quiz - {category} Generation", True, f"Generated {len(questions)} questions successfully")
                    else:
                        self.log_test(f"New Quiz - {category} Generation", False, f"Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_test(f"New Quiz - {category}", False, f"Error: {str(e)}")
            
            return quiz_tests_passed >= 2  # Should pass most tests
            
        except Exception as e:
            self.log_test("New Quiz System", False, f"Error: {str(e)}")
            return False

    def test_new_search_functionality(self):
        """Test search works across title, sourceVerse, book, and keywords"""
        try:
            # Test search across new fields
            search_terms = [
                ("YHWH", "Should find YHWH in sourceVerse or title"),
                ("Exodus", "Should find in book field"),
                ("commandment", "Should find in title or sourceVerse"),
                ("Torah", "Should find Torah-related content")
            ]
            
            search_passed = 0
            for term, description in search_terms:
                try:
                    response = self.session.get(f"{self.base_url}/mitzvot?search={term}&limit=20")
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('mitzvot', [])
                        
                        if results:
                            # Check which fields contain the search term
                            fields_found = set()
                            for mitzvah in results:
                                if term.lower() in mitzvah.get('title', '').lower():
                                    fields_found.add('title')
                                if term.lower() in mitzvah.get('sourceVerse', '').lower():
                                    fields_found.add('sourceVerse')
                                if term.lower() in mitzvah.get('book', '').lower():
                                    fields_found.add('book')
                                keywords = mitzvah.get('keywords', [])
                                if any(term.lower() in keyword.lower() for keyword in keywords):
                                    fields_found.add('keywords')
                            
                            if fields_found:
                                self.log_test(f"New Search - '{term}'", True, f"Found in fields: {list(fields_found)} ({len(results)} results)")
                                search_passed += 1
                            else:
                                self.log_test(f"New Search - '{term}'", False, f"Found {len(results)} results but no field matches")
                        else:
                            self.log_test(f"New Search - '{term}'", False, "No results found")
                    else:
                        self.log_test(f"New Search - '{term}'", False, f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"New Search - '{term}'", False, f"Error: {str(e)}")
            
            return search_passed >= len(search_terms) * 0.75  # At least 75% should work
            
        except Exception as e:
            self.log_test("New Search Functionality", False, f"Error: {str(e)}")
            return False

    def test_api_endpoints_new_structure(self):
        """Test that all API endpoints work with the new structure"""
        try:
            tests_passed = 0
            
            # Test 1: GET /api/mitzvot should work without status parameter
            response = self.session.get(f"{self.base_url}/mitzvot?page=1&limit=10")
            if response.status_code == 200:
                data = response.json()
                mitzvot = data.get('mitzvot', [])
                if mitzvot:
                    # Check that no old fields are present
                    sample_mitzvah = mitzvot[0]
                    old_fields = ['traditionalWording', 'scholarlyNote', 'status']
                    has_old_fields = any(field in sample_mitzvah for field in old_fields)
                    
                    if not has_old_fields:
                        self.log_test("API Endpoints - GET mitzvot", True, "Returns new structure without old fields")
                        tests_passed += 1
                    else:
                        self.log_test("API Endpoints - GET mitzvot", False, "Still contains old fields")
                else:
                    self.log_test("API Endpoints - GET mitzvot", False, "No mitzvot returned")
            else:
                self.log_test("API Endpoints - GET mitzvot", False, f"Status: {response.status_code}")
            
            # Test 2: Categories endpoint should return new biblical categories
            response = self.session.get(f"{self.base_url}/categories")
            if response.status_code == 200:
                categories = response.json()
                if len(categories) == 34:  # Expected 34 categories
                    self.log_test("API Endpoints - Categories", True, f"Returns {len(categories)} new biblical categories")
                    tests_passed += 1
                else:
                    self.log_test("API Endpoints - Categories", False, f"Returns {len(categories)} categories (expected 34)")
            else:
                self.log_test("API Endpoints - Categories", False, f"Status: {response.status_code}")
            
            # Test 3: Individual mitzvah endpoints should return new structure
            if mitzvot:
                test_mitzvah_id = mitzvot[0].get('id')
                response = self.session.get(f"{self.base_url}/mitzvot/{test_mitzvah_id}")
                if response.status_code == 200:
                    individual_mitzvah = response.json()
                    
                    # Check for new required fields
                    new_fields = ['sourceVerse', 'book', 'chapter', 'verse']
                    has_new_fields = all(field in individual_mitzvah for field in new_fields)
                    
                    # Check that old fields are not present
                    old_fields = ['traditionalWording', 'scholarlyNote', 'status']
                    has_old_fields = any(field in individual_mitzvah for field in old_fields)
                    
                    if has_new_fields and not has_old_fields:
                        self.log_test("API Endpoints - Individual Mitzvah", True, "Returns new structure with required fields")
                        tests_passed += 1
                    else:
                        self.log_test("API Endpoints - Individual Mitzvah", False, "Missing new fields or contains old fields")
                else:
                    self.log_test("API Endpoints - Individual Mitzvah", False, f"Status: {response.status_code}")
            
            return tests_passed >= 2
            
        except Exception as e:
            self.log_test("API Endpoints New Structure", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🔍 Starting Comprehensive Backend Testing for NEW BIBLICAL STRUCTURE")
        print("=" * 70)
        
        # Initialize database first
        print("\n📊 Initializing Database...")
        init_success = self.test_initialize_endpoint()
        
        if not init_success:
            print("❌ Database initialization failed. Stopping tests.")
            return False
        
        print("\n🔗 Testing API Connectivity...")
        self.test_api_root()
        
        print("\n🆕 Testing New Biblical Structure Verification...")
        self.test_new_biblical_structure_verification()
        
        print("\n📂 Testing New Categories Structure (34 categories)...")
        self.test_new_categories_structure()
        
        print("\n🧠 Testing New Quiz System (verse_from_title, book_from_title, etc.)...")
        self.test_new_quiz_system()
        
        print("\n🔍 Testing New Search Functionality (title, sourceVerse, book, keywords)...")
        self.test_new_search_functionality()
        
        print("\n🔌 Testing API Endpoints with New Structure...")
        self.test_api_endpoints_new_structure()
        
        print("\n🃏 Testing Flashcard System with New Structure...")
        self.test_flashcard_system()
        
        print("\n📈 Testing Statistics Validation...")
        self.test_stats_validation()
        
        print("\n📄 Testing Individual Mitzvah Data Structure...")
        self.test_individual_mitzvah_data_structure()
        
        print("\n🔄 Testing Data Consistency...")
        self.test_data_consistency()
        
        print("\n📊 Testing Progress Tracking System...")
        self.test_progress_tracking_system()
        
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