#!/usr/bin/env python3
"""
Focused testing of new interactive features
"""

import requests
import json

BACKEND_URL = "https://biblestudysuite.preview.emergentagent.com/api"

def test_new_features():
    session = requests.Session()
    
    print("🔍 Testing New Interactive Features")
    print("=" * 50)
    
    # Test Enhanced Quiz System
    print("\n🧠 Enhanced Quiz System:")
    
    # Test valid categories
    for category in ["all", "faith-god", "torah-study"]:
        response = session.get(f"{BACKEND_URL}/quiz/{category}?limit=3")
        if response.status_code == 200:
            data = response.json()
            questions = data.get('questions', [])
            print(f"   ✅ {category}: {len(questions)} questions generated")
            
            if questions:
                # Check question diversity
                question_types = set()
                for q in questions:
                    question_text = q.get('question', '')
                    if 'traditional wording' in question_text:
                        question_types.add('title_from_traditional')
                    elif 'What is the traditional wording' in question_text:
                        question_types.add('traditional_from_title')
                    elif 'category' in question_text:
                        question_types.add('category_from_title')
                    elif 'origin status' in question_text:
                        question_types.add('status_from_title')
                
                print(f"      Question types: {len(question_types)}")
                
                # Check answer uniqueness
                for i, q in enumerate(questions):
                    options = q.get('options', [])
                    unique_options = len(set(options))
                    if unique_options == len(options):
                        print(f"      Q{i+1}: ✅ Unique answers ({len(options)})")
                    else:
                        print(f"      Q{i+1}: ❌ Duplicate answers")
        else:
            print(f"   ❌ {category}: Status {response.status_code}")
    
    # Test Progress Tracking
    print("\n📊 Progress Tracking System:")
    
    # Test GET progress
    response = session.get(f"{BACKEND_URL}/progress")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ GET /progress: Working")
        print(f"      Total mitzvot: {data.get('totalMitzvot', 0)}")
        print(f"      Learning: {data.get('learning', 0)}")
        print(f"      Reviewing: {data.get('reviewing', 0)}")
        print(f"      Mastered: {data.get('mastered', 0)}")
        print(f"      Categories tracked: {len(data.get('categoryProgress', {}))}")
    else:
        print(f"   ❌ GET /progress: Status {response.status_code}")
    
    # Test POST progress (get valid mitzvah first)
    mitzvot_response = session.get(f"{BACKEND_URL}/mitzvot?limit=1")
    if mitzvot_response.status_code == 200:
        mitzvot_data = mitzvot_response.json()
        mitzvot = mitzvot_data.get('mitzvot', [])
        if mitzvot:
            test_mitzvah_id = mitzvot[0].get('id')
            
            # Test correct answer
            response = session.post(f"{BACKEND_URL}/progress/{test_mitzvah_id}?correct=true")
            if response.status_code == 200:
                print(f"   ✅ POST /progress (correct): Working")
            else:
                print(f"   ❌ POST /progress (correct): Status {response.status_code}")
            
            # Test incorrect answer - this seems to have issues
            response = session.post(f"{BACKEND_URL}/progress/{test_mitzvah_id}?correct=false")
            if response.status_code == 200:
                print(f"   ✅ POST /progress (incorrect): Working")
            else:
                print(f"   ❌ POST /progress (incorrect): Status {response.status_code} - Known issue")
    
    # Test Flashcard System
    print("\n🃏 Flashcard System:")
    
    response = session.get(f"{BACKEND_URL}/flashcards?limit=5")
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        print(f"   ✅ GET /flashcards: {len(flashcards)} flashcards")
        
        if flashcards:
            # Test flashcard review
            sample_flashcard = flashcards[0]
            flashcard_id = sample_flashcard['flashcard']['id']
            
            response = session.post(f"{BACKEND_URL}/flashcards/{flashcard_id}/review?difficulty=3&correct=true")
            if response.status_code == 200:
                print(f"   ✅ POST /flashcards/review: Working")
            else:
                print(f"   ❌ POST /flashcards/review: Status {response.status_code}")
        else:
            print(f"   ⚠️  No flashcards available for testing")
    else:
        print(f"   ❌ GET /flashcards: Status {response.status_code}")
    
    # Test Mitzvah of the Day
    print("\n📅 Mitzvah of the Day:")
    response = session.get(f"{BACKEND_URL}/mitzvah-of-the-day")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Daily mitzvah #{data.get('number')}: {data.get('title', '')[:50]}...")
    else:
        print(f"   ❌ Status {response.status_code}")

if __name__ == "__main__":
    test_new_features()