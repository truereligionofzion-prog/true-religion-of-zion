#!/usr/bin/env python3
"""
Process the user's comprehensive biblical mitzvot list
Remove origin-based filtering and implement new structure with complete verses
"""

import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# New categories based on user's list
NEW_CATEGORIES = [
    {"slug": "god", "name": "YHWH", "description": "Commandments about knowing, loving, and honoring YHWH", "order": 1},
    {"slug": "torah", "name": "Torah", "description": "Learning, teaching, and preserving Torah", "order": 2},
    {"slug": "signs-symbols", "name": "Signs and Symbols", "description": "Physical symbols and signs of the covenant", "order": 3},
    {"slug": "prayer-blessings", "name": "Prayer and Blessings", "description": "Prayer, worship, and blessings", "order": 4},
    {"slug": "love-brotherhood", "name": "Love & Brotherhood/Sisterhood", "description": "Love, relationships, and mutual responsibility", "order": 5},
    {"slug": "poor", "name": "The Poor", "description": "Caring for the poor and disadvantaged", "order": 6},
    {"slug": "gentiles", "name": "Gentiles", "description": "Relations with non-Israelites", "order": 7},
    {"slug": "marriage-family", "name": "Marriage, Divorce and Family", "description": "Family relationships and marriage laws", "order": 8},
    {"slug": "sexual-relations", "name": "Forbidden Sexual Relations", "description": "Sexual morality and prohibited relationships", "order": 9},
    {"slug": "times-seasons", "name": "Times and Seasons", "description": "Sabbath, festivals, and holy times", "order": 10},
    {"slug": "dietary-laws", "name": "Dietary Laws", "description": "Kosher laws and dietary restrictions", "order": 11},
    {"slug": "business-practices", "name": "Business Practices", "description": "Honest business and financial ethics", "order": 12},
    {"slug": "employees-servants", "name": "Employees, Servants and Slaves", "description": "Labor relations and servant treatment", "order": 13},
    {"slug": "vows-oaths", "name": "Vows, Oaths and Swearing", "description": "Making and keeping vows and oaths", "order": 14},
    {"slug": "sabbatical-jubilee", "name": "The Sabbatical and Jubilee Years", "description": "Seven-year and fifty-year cycles", "order": 15},
    {"slug": "court-judicial", "name": "The Court and Judicial Procedure", "description": "Justice system and legal procedures", "order": 16},
    {"slug": "injuries-damages", "name": "Injuries and Damages", "description": "Personal injury and property damage laws", "order": 17},
    {"slug": "property-rights", "name": "Property and Property Rights", "description": "Land ownership and property laws", "order": 18},
    {"slug": "criminal-laws", "name": "Criminal Laws", "description": "Criminal offenses and prohibitions", "order": 19},
    {"slug": "punishment-restitution", "name": "Punishment and Restitution", "description": "Legal penalties and compensation", "order": 20},
    {"slug": "prophecy", "name": "Prophecy", "description": "True and false prophecy", "order": 21},
    {"slug": "idolatry", "name": "Idolatry, Idolaters and Idolatrous Practices", "description": "Prohibitions against idolatry", "order": 22},
    {"slug": "agriculture-animals", "name": "Agriculture and Animal Husbandry", "description": "Farming and animal care laws", "order": 23},
    {"slug": "clothing", "name": "Clothing", "description": "Clothing and dress regulations", "order": 24},
    {"slug": "firstborn", "name": "The Firstborn", "description": "Laws concerning firstborn dedication", "order": 25},
    {"slug": "kohanim-levites", "name": "Kohanim and Levites", "description": "Priestly duties and regulations", "order": 26},
    {"slug": "terumah-tithes", "name": "T'rumah, Tithes, and Taxes", "description": "Religious offerings and taxes", "order": 27},
    {"slug": "temple-sanctuary", "name": "The Temple, the Sanctuary and Sacred Objects", "description": "Temple service and sacred items", "order": 28},
    {"slug": "sacrifices-offerings", "name": "Sacrifices and Offerings", "description": "Ritual sacrifices and offerings", "order": 29},
    {"slug": "ritual-purity", "name": "Ritual Purity and Impurity", "description": "Purity laws and purification", "order": 30},
    {"slug": "lepers-leprosy", "name": "Lepers and Leprosy", "description": "Laws concerning leprosy", "order": 31},
    {"slug": "king", "name": "The King", "description": "Rules for Israelite monarchy", "order": 32},
    {"slug": "nazarites", "name": "Nazarites", "description": "Nazarite vows and restrictions", "order": 33},
    {"slug": "wars", "name": "Wars", "description": "Laws of warfare and military conduct", "order": 34}
]

# User's comprehensive list with basic parsing
# This is a simplified version - we'll need to extract and process each commandment
SAMPLE_MITZVOT_DATA = [
    {
        "number": 1,
        "title": "To know that YHWH exists",
        "sourceVerse": "I am YHWH your Elohim, who brought you out of the land of Egypt, out of the house of bondage.",
        "book": "Exodus",
        "chapter": 20,
        "verse": "2",
        "category": "god",
        "keywords": ["YHWH", "exists", "Elohim", "Egypt"]
    },
    {
        "number": 2, 
        "title": "Not to entertain the idea that there is any god but the Eternal",
        "sourceVerse": "You shall have no other gods before Me.",
        "book": "Exodus",
        "chapter": 20,
        "verse": "3",
        "category": "god",
        "keywords": ["no other gods", "before Me", "monotheism"]
    },
    {
        "number": 3,
        "title": "Not to blaspheme",
        "sourceVerse": "You shall not curse Elohim, nor curse a ruler of your people.",
        "book": "Exodus", 
        "chapter": 22,
        "verse": "28",
        "category": "god",
        "keywords": ["blaspheme", "curse", "Elohim", "ruler"]
    }
]

def replace_god_with_yhwh(text):
    """Replace 'God' with 'YHWH' or 'YHUH' randomly"""
    import random
    # Replace 'God' but not 'gods' (plural)
    replacements = ['YHWH', 'YHUH']
    
    # Match 'God' as whole word, case-insensitive, but not 'gods'
    pattern = r'\bGod\b(?!s)'
    
    def replace_func(match):
        return random.choice(replacements)
    
    return re.sub(pattern, replace_func, text, flags=re.IGNORECASE)

async def clear_and_initialize():
    """Clear existing data and set up new structure"""
    print("=== Clearing existing data ===")
    
    # Clear collections
    db.mitzvot.delete_many({})
    db.categories.delete_many({})
    
    print("=== Creating new categories ===")
    
    # Insert new categories
    for cat_data in NEW_CATEGORIES:
        category = {
            "id": str(uuid.uuid4()),
            "createdAt": datetime.now(timezone.utc),
            **cat_data
        }
        db.categories.insert_one(category)
    
    print(f"Created {len(NEW_CATEGORIES)} categories")

async def process_sample_data():
    """Process sample mitzvot data to test the new structure"""
    print("=== Processing sample mitzvot ===")
    
    for mitzvah_data in SAMPLE_MITZVOT_DATA:
        # Apply YHWH replacement
        processed_data = {
            "id": str(uuid.uuid4()),
            "number": mitzvah_data["number"],
            "title": replace_god_with_yhwh(mitzvah_data["title"]),
            "sourceVerse": replace_god_with_yhwh(mitzvah_data["sourceVerse"]),
            "book": mitzvah_data["book"],
            "chapter": mitzvah_data["chapter"],
            "verse": mitzvah_data["verse"],
            "category": mitzvah_data["category"],
            "keywords": [replace_god_with_yhwh(keyword) for keyword in mitzvah_data["keywords"]],
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        db.mitzvot.insert_one(processed_data)
    
    print(f"Processed {len(SAMPLE_MITZVOT_DATA)} sample mitzvot")

def main():
    """Main processing function"""
    print("=== Implementing New Biblical Mitzvot Structure ===")
    print("Removing origin-based filtering, implementing YHWH/YHUH replacements")
    
    # Clear and initialize
    clear_and_initialize()
    
    # Process sample data
    process_sample_data()
    
    print("\n✅ Initial structure setup complete")
    print(f"📊 Categories: {len(NEW_CATEGORIES)}")
    print(f"📊 Sample Mitzvot: {len(SAMPLE_MITZVOT_DATA)}")
    
    print("\n🔄 Next Steps:")
    print("1. Process full user list with complete biblical verses")
    print("2. Update frontend to remove origin filtering")
    print("3. Test new quiz and flashcard systems")

if __name__ == "__main__":
    main()