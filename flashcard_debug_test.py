#!/usr/bin/env python3
"""
Debug test for flashcard generation issue
"""

import requests
import json

BACKEND_URL = "https://covenant-app.preview.emergentagent.com/api"

def test_flashcard_debug():
    session = requests.Session()
    
    print("🔍 Debugging Flashcard Generation...")
    
    # Test multiple calls to see if flashcards are being created
    for i in range(3):
        print(f"\n--- Attempt {i+1} ---")
        response = session.get(f"{BACKEND_URL}/flashcards?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            flashcards = data.get('flashcards', [])
            total = data.get('total', 0)
            
            print(f"Status: 200 OK")
            print(f"Flashcards returned: {len(flashcards)}")
            print(f"Total: {total}")
            
            if flashcards:
                sample = flashcards[0]
                print(f"Sample flashcard structure: {list(sample.keys())}")
                if 'flashcard' in sample:
                    fc_data = sample['flashcard']
                    print(f"Flashcard fields: {list(fc_data.keys())}")
                    print(f"Difficulty: {fc_data.get('difficulty')}")
                    print(f"Review count: {fc_data.get('reviewCount')}")
            else:
                print("No flashcards in response")
        else:
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
    
    # Test with different user IDs to see if that affects generation
    print(f"\n--- Testing with different user ID ---")
    response = session.get(f"{BACKEND_URL}/flashcards?user_id=test_user_123&limit=5")
    
    if response.status_code == 200:
        data = response.json()
        flashcards = data.get('flashcards', [])
        print(f"With different user ID - Flashcards: {len(flashcards)}")
    else:
        print(f"With different user ID - Status: {response.status_code}")

if __name__ == "__main__":
    test_flashcard_debug()