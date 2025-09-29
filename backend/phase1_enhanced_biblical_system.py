#!/usr/bin/env python3
"""
Phase 1: 80-Book Bible + Precepts Database with Contextual Hermeneutics
Foundation: Everything ties back to 613 Mitzvot with proper biblical context
"""

import os
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# Enhanced data models for contextual biblical study
def create_enhanced_collections():
    """Create enhanced collections for integrated biblical study with hermeneutical context"""
    
    print("=== PHASE 1: ENHANCED BIBLICAL STUDY SYSTEM ===")
    print("Building 80-book Bible + Precepts + Contextual Analysis")
    
    # 1. Enhanced Bible Books Collection (80 books)
    bible_books_80 = [
        # OLD TESTAMENT (39 books)
        {"name": "Genesis", "testament": "old", "order": 1, "canonical": True, "hebrew_name": "Bereshit"},
        {"name": "Exodus", "testament": "old", "order": 2, "canonical": True, "hebrew_name": "Shemot"},
        {"name": "Leviticus", "testament": "old", "order": 3, "canonical": True, "hebrew_name": "Vayikra"},
        {"name": "Numbers", "testament": "old", "order": 4, "canonical": True, "hebrew_name": "Bamidbar"},
        {"name": "Deuteronomy", "testament": "old", "order": 5, "canonical": True, "hebrew_name": "Devarim"},
        {"name": "Joshua", "testament": "old", "order": 6, "canonical": True, "hebrew_name": "Yehoshua"},
        {"name": "Judges", "testament": "old", "order": 7, "canonical": True, "hebrew_name": "Shoftim"},
        {"name": "Ruth", "testament": "old", "order": 8, "canonical": True, "hebrew_name": "Rut"},
        {"name": "1Samuel", "testament": "old", "order": 9, "canonical": True, "hebrew_name": "Shmuel Aleph"},
        {"name": "2Samuel", "testament": "old", "order": 10, "canonical": True, "hebrew_name": "Shmuel Bet"},
        {"name": "1Kings", "testament": "old", "order": 11, "canonical": True, "hebrew_name": "Melachim Aleph"},
        {"name": "2Kings", "testament": "old", "order": 12, "canonical": True, "hebrew_name": "Melachim Bet"},
        {"name": "1Chronicles", "testament": "old", "order": 13, "canonical": True, "hebrew_name": "Divrei HaYamim Aleph"},
        {"name": "2Chronicles", "testament": "old", "order": 14, "canonical": True, "hebrew_name": "Divrei HaYamim Bet"},
        {"name": "Ezra", "testament": "old", "order": 15, "canonical": True, "hebrew_name": "Ezra"},
        {"name": "Nehemiah", "testament": "old", "order": 16, "canonical": True, "hebrew_name": "Nehemiah"},
        {"name": "Esther", "testament": "old", "order": 17, "canonical": True, "hebrew_name": "Esther"},
        {"name": "Job", "testament": "old", "order": 18, "canonical": True, "hebrew_name": "Iyov"},
        {"name": "Psalms", "testament": "old", "order": 19, "canonical": True, "hebrew_name": "Tehillim"},
        {"name": "Proverbs", "testament": "old", "order": 20, "canonical": True, "hebrew_name": "Mishlei"},
        {"name": "Ecclesiastes", "testament": "old", "order": 21, "canonical": True, "hebrew_name": "Kohelet"},
        {"name": "Songs of Solomon", "testament": "old", "order": 22, "canonical": True, "hebrew_name": "Shir HaShirim"},
        {"name": "Isaiah", "testament": "old", "order": 23, "canonical": True, "hebrew_name": "Yeshayahu"},
        {"name": "Jeremiah", "testament": "old", "order": 24, "canonical": True, "hebrew_name": "Yirmeyahu"},
        {"name": "Lamentations", "testament": "old", "order": 25, "canonical": True, "hebrew_name": "Eicha"},
        {"name": "Ezekiel", "testament": "old", "order": 26, "canonical": True, "hebrew_name": "Yechezkel"},
        {"name": "Daniel", "testament": "old", "order": 27, "canonical": True, "hebrew_name": "Daniel"},
        {"name": "Hosea", "testament": "old", "order": 28, "canonical": True, "hebrew_name": "Hoshea"},
        {"name": "Joel", "testament": "old", "order": 29, "canonical": True, "hebrew_name": "Yoel"},
        {"name": "Amos", "testament": "old", "order": 30, "canonical": True, "hebrew_name": "Amos"},
        {"name": "Obadiah", "testament": "old", "order": 31, "canonical": True, "hebrew_name": "Ovadiah"},
        {"name": "Jonah", "testament": "old", "order": 32, "canonical": True, "hebrew_name": "Yonah"},
        {"name": "Micah", "testament": "old", "order": 33, "canonical": True, "hebrew_name": "Micah"},
        {"name": "Nahum", "testament": "old", "order": 34, "canonical": True, "hebrew_name": "Nachum"},
        {"name": "Habakkuk", "testament": "old", "order": 35, "canonical": True, "hebrew_name": "Chavakuk"},
        {"name": "Zephaniah", "testament": "old", "order": 36, "canonical": True, "hebrew_name": "Tzefaniah"},
        {"name": "Haggai", "testament": "old", "order": 37, "canonical": True, "hebrew_name": "Chaggai"},
        {"name": "Zechariah", "testament": "old", "order": 38, "canonical": True, "hebrew_name": "Zechariah"},
        {"name": "Malachi", "testament": "old", "order": 39, "canonical": True, "hebrew_name": "Malachi"},
        
        # NEW TESTAMENT (27 books)
        {"name": "Matthew", "testament": "new", "order": 40, "canonical": True, "hebrew_name": None},
        {"name": "Mark", "testament": "new", "order": 41, "canonical": True, "hebrew_name": None},
        {"name": "Luke", "testament": "new", "order": 42, "canonical": True, "hebrew_name": None},
        {"name": "John", "testament": "new", "order": 43, "canonical": True, "hebrew_name": None},
        {"name": "Acts", "testament": "new", "order": 44, "canonical": True, "hebrew_name": None},
        {"name": "Romans", "testament": "new", "order": 45, "canonical": True, "hebrew_name": None},
        {"name": "1Corinthians", "testament": "new", "order": 46, "canonical": True, "hebrew_name": None},
        {"name": "2Corinthians", "testament": "new", "order": 47, "canonical": True, "hebrew_name": None},
        {"name": "Galatians", "testament": "new", "order": 48, "canonical": True, "hebrew_name": None},
        {"name": "Ephesians", "testament": "new", "order": 49, "canonical": True, "hebrew_name": None},
        {"name": "Philippians", "testament": "new", "order": 50, "canonical": True, "hebrew_name": None},
        {"name": "Colossians", "testament": "new", "order": 51, "canonical": True, "hebrew_name": None},
        {"name": "1Thessalonians", "testament": "new", "order": 52, "canonical": True, "hebrew_name": None},
        {"name": "2Thessalonians", "testament": "new", "order": 53, "canonical": True, "hebrew_name": None},
        {"name": "1Timothy", "testament": "new", "order": 54, "canonical": True, "hebrew_name": None},
        {"name": "2Timothy", "testament": "new", "order": 55, "canonical": True, "hebrew_name": None},
        {"name": "Titus", "testament": "new", "order": 56, "canonical": True, "hebrew_name": None},
        {"name": "Philemon", "testament": "new", "order": 57, "canonical": True, "hebrew_name": None},
        {"name": "Hebrews", "testament": "new", "order": 58, "canonical": True, "hebrew_name": None},
        {"name": "James", "testament": "new", "order": 59, "canonical": True, "hebrew_name": None},
        {"name": "1Peter", "testament": "new", "order": 60, "canonical": True, "hebrew_name": None},
        {"name": "2Peter", "testament": "new", "order": 61, "canonical": True, "hebrew_name": None},
        {"name": "1John", "testament": "new", "order": 62, "canonical": True, "hebrew_name": None},
        {"name": "2John", "testament": "new", "order": 63, "canonical": True, "hebrew_name": None},
        {"name": "3John", "testament": "new", "order": 64, "canonical": True, "hebrew_name": None},
        {"name": "Jude", "testament": "new", "order": 65, "canonical": True, "hebrew_name": None},
        {"name": "Revelations", "testament": "new", "order": 66, "canonical": True, "hebrew_name": None},
        
        # APOCRYPHAL/DEUTEROCANONICAL (14 books)
        {"name": "1Esdras", "testament": "apocrypha", "order": 67, "canonical": False, "hebrew_name": None},
        {"name": "2Esdras", "testament": "apocrypha", "order": 68, "canonical": False, "hebrew_name": None},
        {"name": "Tobit", "testament": "apocrypha", "order": 69, "canonical": False, "hebrew_name": None},
        {"name": "Judith", "testament": "apocrypha", "order": 70, "canonical": False, "hebrew_name": None},
        {"name": "Esther (Greek)", "testament": "apocrypha", "order": 71, "canonical": False, "hebrew_name": None},
        {"name": "Wisdom of Solomon", "testament": "apocrypha", "order": 72, "canonical": False, "hebrew_name": None},
        {"name": "Ecclesiasticus (Sirach)", "testament": "apocrypha", "order": 73, "canonical": False, "hebrew_name": None},
        {"name": "Baruch", "testament": "apocrypha", "order": 74, "canonical": False, "hebrew_name": None},
        {"name": "Epistle of Jeremiah", "testament": "apocrypha", "order": 75, "canonical": False, "hebrew_name": None},
        {"name": "Prayer of Azariah", "testament": "apocrypha", "order": 76, "canonical": False, "hebrew_name": None},
        {"name": "Susanna", "testament": "apocrypha", "order": 77, "canonical": False, "hebrew_name": None},
        {"name": "Bel and the Dragon", "testament": "apocrypha", "order": 78, "canonical": False, "hebrew_name": None},
        {"name": "Prayer of Manasseh", "testament": "apocrypha", "order": 79, "canonical": False, "hebrew_name": None},
        {"name": "1Maccabees", "testament": "apocrypha", "order": 80, "canonical": False, "hebrew_name": None},
        {"name": "2Maccabees", "testament": "apocrypha", "order": 81, "canonical": False, "hebrew_name": None}
    ]
    
    # Create/update collections
    print("Creating enhanced collections...")
    
    # Clear and recreate bible_books collection
    db.bible_books.delete_many({})
    for book_data in bible_books_80:
        book = {
            "id": str(uuid.uuid4()),
            "name": book_data["name"],
            "testament": book_data["testament"],
            "order": book_data["order"],
            "canonical": book_data["canonical"],
            "hebrew_name": book_data["hebrew_name"],
            "createdAt": datetime.now(timezone.utc)
        }
        db.bible_books.insert_one(book)
    
    print(f"✅ Created {len(bible_books_80)} books in bible_books collection")
    
    # Create precepts collection structure
    db.precepts.delete_many({})  # Clear existing
    print("✅ Prepared precepts collection")
    
    # Create contextual analysis collection
    db.contextual_analysis.delete_many({})
    print("✅ Prepared contextual_analysis collection")
    
    # Create cross_references collection (mitzvot ↔ precepts ↔ verses)
    db.cross_references.delete_many({})
    print("✅ Prepared cross_references collection")
    
    return len(bible_books_80)

def create_contextual_framework():
    """Create framework for proper biblical hermeneutics and audience analysis"""
    
    print("\n=== CONTEXTUAL HERMENEUTICS FRAMEWORK ===")
    
    # Audience context categories
    audience_contexts = [
        {
            "id": str(uuid.uuid4()),
            "type": "ethnic_israelites",
            "name": "Ethnic Israelites Only",
            "description": "Prophecies, commandments, and promises specifically for ethnic/biological descendants of Israel",
            "hermeneutical_key": "Exclusive to Israel",
            "examples": ["Land promises", "Specific prophecies about Israel's future", "Certain mitzvot"],
            "color": "blue"
        },
        {
            "id": str(uuid.uuid4()),
            "type": "universal",
            "name": "Universal Principles", 
            "description": "Moral and spiritual principles applicable to all peoples",
            "hermeneutical_key": "Universal application",
            "examples": ["Do not murder", "Love your neighbor", "Moral precepts"],
            "color": "green"
        },
        {
            "id": str(uuid.uuid4()),
            "type": "conditional",
            "name": "Conditional/Contextual",
            "description": "Context-dependent teachings that may apply differently based on circumstances",
            "hermeneutical_key": "Conditional application",
            "examples": ["Cultural practices", "Temporal commands", "Situational guidance"],
            "color": "orange"
        },
        {
            "id": str(uuid.uuid4()),
            "type": "prophetic_specific",
            "name": "Prophetic - Israel Specific",
            "description": "Prophetic messages specifically about Israel's destiny and role",
            "hermeneutical_key": "Prophetic exclusivity",
            "examples": ["End-times role of Israel", "Restoration prophecies", "National promises"],
            "color": "purple"
        }
    ]
    
    for context in audience_contexts:
        context["createdAt"] = datetime.now(timezone.utc)
        db.audience_contexts.insert_one(context)
    
    print(f"✅ Created {len(audience_contexts)} audience context categories")
    
    # Hermeneutical principles
    hermeneutical_principles = [
        {
            "id": str(uuid.uuid4()),
            "principle": "Historical Context",
            "description": "Who was the original audience? What was their situation?",
            "questions": [
                "Who was this written to originally?",
                "What was the historical situation?", 
                "What cultural context is important?"
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "principle": "Literary Context", 
            "description": "What comes before and after this passage?",
            "questions": [
                "What is the broader context of this passage?",
                "How does this fit with surrounding verses?",
                "What is the literary genre?"
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "principle": "Audience Analysis",
            "description": "Is this for ethnic Israelites specifically or universal?",
            "questions": [
                "Is this exclusive to ethnic Israelites?",
                "Does this apply universally?",
                "Are there conditional aspects?"
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "principle": "Cross-Reference Analysis",
            "description": "How do other passages illuminate this text?",
            "questions": [
                "What do related mitzvot teach?",
                "What do relevant precepts show?",
                "How do parallel passages help?"
            ]
        }
    ]
    
    for principle in hermeneutical_principles:
        principle["createdAt"] = datetime.now(timezone.utc)
        db.hermeneutical_principles.insert_one(principle)
    
    print(f"✅ Created {len(hermeneutical_principles)} hermeneutical principles")

def main():
    """Phase 1 initialization"""
    
    print("🚀 PHASE 1: COMPREHENSIVE BIBLICAL STUDY SYSTEM")
    print("Foundation: 613 Mitzvot + 80-Book Bible + Precepts + Contextual Analysis")
    
    # Create enhanced collections
    books_count = create_enhanced_collections()
    
    # Create contextual framework
    create_contextual_framework()
    
    # Summary
    print(f"\n📊 PHASE 1 SETUP COMPLETE:")
    print(f"✅ 80-book Bible structure: {books_count} books")
    print(f"✅ Contextual hermeneutics framework")
    print(f"✅ Cross-reference system prepared")
    print(f"✅ Audience analysis tools ready")
    
    print(f"\n🔄 NEXT STEPS:")
    print(f"1. Scrape and populate Bible text from thepreceptbible.com")
    print(f"2. Extract and structure precepts with biblical references")  
    print(f"3. Build cross-reference system linking mitzvot ↔ precepts ↔ verses")
    print(f"4. Implement contextual analysis tools")
    print(f"5. Update UI for integrated experience")
    
    print(f"\n🎯 FOUNDATION MAINTAINED:")
    print(f"Everything will tie back to the 613 mitzvot as the foundational system")
    print(f"Contextual analysis prevents taking verses out of context")
    print(f"Proper hermeneutics and exegesis tools integrated")

if __name__ == "__main__":
    main()