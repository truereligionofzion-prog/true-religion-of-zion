#!/usr/bin/env python3
"""
Debug specific API issues
"""

import requests
import json

BACKEND_URL = "https://precept-bible-app.preview.emergentagent.com/api"

def test_specific_issues():
    session = requests.Session()
    
    print("Testing specific issues...")
    
    # Test 1: Limit validation
    print("\n1. Testing limit validation:")
    response = session.get(f"{BACKEND_URL}/mitzvot?limit=613")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    # Test 2: Quiz with invalid category
    print("\n2. Testing quiz with invalid category:")
    response = session.get(f"{BACKEND_URL}/quiz/invalid-category")
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
    
    # Test 3: Progress POST with incorrect answer
    print("\n3. Testing progress POST:")
    # First get a valid mitzvah ID
    mitzvot_response = session.get(f"{BACKEND_URL}/mitzvot?limit=1")
    if mitzvot_response.status_code == 200:
        mitzvot_data = mitzvot_response.json()
        mitzvot = mitzvot_data.get('mitzvot', [])
        if mitzvot:
            test_mitzvah_id = mitzvot[0].get('id')
            print(f"   Using mitzvah ID: {test_mitzvah_id}")
            
            response = session.post(f"{BACKEND_URL}/progress/{test_mitzvah_id}?correct=false")
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.text}")
    
    # Test 4: Flashcards endpoint
    print("\n4. Testing flashcards:")
    response = session.get(f"{BACKEND_URL}/flashcards?limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        print(f"   Flashcards returned: {len(flashcards)}")
        if flashcards:
            print(f"   Sample flashcard keys: {list(flashcards[0].keys())}")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    test_specific_issues()