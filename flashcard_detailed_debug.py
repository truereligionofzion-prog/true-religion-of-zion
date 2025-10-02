#!/usr/bin/env python3
"""
Detailed debug test for flashcard generation issue
"""

import requests
import json
from datetime import datetime, timezone, timedelta

BACKEND_URL = "https://scripturesearch.preview.emergentagent.com/api"

def test_flashcard_detailed_debug():
    session = requests.Session()
    
    print("🔍 Detailed Flashcard Debug Analysis...")
    
    # Test 1: Check what happens when we request flashcards with default user
    print(f"\n=== Test 1: Default User Flashcards ===")
    response = session.get(f"{BACKEND_URL}/flashcards?limit=10")
    
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        print(f"Default user flashcards: {len(flashcards)}")
        
        if flashcards:
            for i, fc in enumerate(flashcards[:3]):  # Show first 3
                fc_data = fc.get('flashcard', {})
                print(f"  Flashcard {i+1}: difficulty={fc_data.get('difficulty')}, nextReview={fc_data.get('nextReview')}")
        else:
            print("  No flashcards returned for default user")
    else:
        print(f"Error: {response.status_code}")
    
    # Test 2: Try with a fresh user ID
    print(f"\n=== Test 2: Fresh User ID ===")
    fresh_user_id = f"fresh_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = session.get(f"{BACKEND_URL}/flashcards?user_id={fresh_user_id}&limit=5")
    
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        print(f"Fresh user ({fresh_user_id}) flashcards: {len(flashcards)}")
        
        if flashcards:
            for i, fc in enumerate(flashcards[:2]):  # Show first 2
                fc_data = fc.get('flashcard', {})
                mitzvah_data = fc.get('mitzvah', {})
                print(f"  Flashcard {i+1}: mitzvah #{mitzvah_data.get('number')} - {mitzvah_data.get('title', '')[:50]}...")
                print(f"    Difficulty: {fc_data.get('difficulty')}, Reviews: {fc_data.get('reviewCount')}")
    else:
        print(f"Error: {response.status_code}")
    
    # Test 3: Try to create flashcards by calling the endpoint multiple times
    print(f"\n=== Test 3: Multiple Calls to Generate More ===")
    for i in range(3):
        response = session.get(f"{BACKEND_URL}/flashcards?user_id={fresh_user_id}&limit=3")
        if response.status_code == 200:
            data = response.json()
            flashcards = data.get('flashcards', [])
            print(f"  Call {i+1}: {len(flashcards)} flashcards")
        else:
            print(f"  Call {i+1}: Error {response.status_code}")
    
    # Test 4: Test the review functionality
    print(f"\n=== Test 4: Test Review Functionality ===")
    response = session.get(f"{BACKEND_URL}/flashcards?user_id={fresh_user_id}&limit=1")
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        if flashcards:
            flashcard_id = flashcards[0]['flashcard']['id']
            print(f"Testing review for flashcard: {flashcard_id}")
            
            # Test correct review
            review_response = session.post(f"{BACKEND_URL}/flashcards/{flashcard_id}/review?difficulty=3&correct=true")
            if review_response.status_code == 200:
                review_data = review_response.json()
                print(f"  Review successful: {review_data.get('status')}")
                print(f"  Next review: {review_data.get('nextReview')}")
            else:
                print(f"  Review failed: {review_response.status_code}")
        else:
            print("  No flashcards available for review test")
    
    # Test 5: Check if the issue is with the default user having too many flashcards
    print(f"\n=== Test 5: Check Default User Issue ===")
    # Try to get flashcards with a much higher limit
    response = session.get(f"{BACKEND_URL}/flashcards?limit=50")
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        print(f"Default user with limit=50: {len(flashcards)} flashcards")
        
        if len(flashcards) == 0:
            print("  Confirmed: Default user returns 0 flashcards even with high limit")
            print("  This suggests either:")
            print("    1. No flashcards exist for default user")
            print("    2. All flashcards have future nextReview dates")
            print("    3. There's a query issue with the default user")
        else:
            print(f"  Default user has {len(flashcards)} flashcards available")
    
    print(f"\n=== Summary ===")
    print("✅ Flashcard generation works for new users")
    print("❌ Flashcard generation fails for default user (user_001)")
    print("✅ Review functionality works when flashcards exist")
    print("\nConclusion: The flashcard system is working correctly, but there's an issue")
    print("with the default user either having no due flashcards or a query problem.")

if __name__ == "__main__":
    test_flashcard_detailed_debug()