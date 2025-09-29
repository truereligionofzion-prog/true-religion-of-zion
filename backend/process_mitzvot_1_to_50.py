#!/usr/bin/env python3
"""
Process Mitzvot 1-50 with user's exact scholarly notes
Extracted directly from user's provided list
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 1-50 - Exact scholarly notes from user's message
MITZVOT_1_TO_50 = {
    1: "Often treated as the first positive command; some read it as a declaration rather than a command. [Rambam], [Ramban].",
    2: "Establishes exclusive covenant loyalty; foundational to later anti-idolatry laws. [Rambam], [Sifre Deut.].",
    3: "Scope debated—art in general vs. worship images; context supports cultic prohibition. [Ibn Ezra], [Rashi].",
    4: "Encompasses ritual acts like sacrifice, incense, libations. [Rambam], [Sifra Lev.].",
    5: "Distinguished from careless oaths; formal reviling of the Name. [Mishnah Sanh.], [Rambam].",
    6: "Expressed through obedience and devotion; central to Shema. [Sifre Deut.], [Rambam].",
    7: "Reverence motivates faithful service and avoidance of sin. [Rambam], [Ramban].",
    8: "Service includes prayer (avodah shebalev) in later rabbinic framing. [Taanit 2a], [Rambam].",
    9: "Interpreted as emulating God's ways and attaching to His Torah/servants. [Sifre Deut.], [Rambam].",
    10: "Permits oaths in God's Name when true and necessary; false oaths condemned. [Rambam], [Sefer HaChinuch].",
    11: "Kiddush Hashem vs. Chillul Hashem as ethical-religious ideals. [Rambam], [Sifra Emor].",
    12: "Prohibits demanding signs or doubting His faithfulness. [Ramban], [Sifre Deut.].",
    13: "Literal vs metaphorical interpretation debated; practice standardized rabbinically. [Rambam], [Rashi].",
    14: "Placement, compartments, and texts regulated by tradition. [Rambam], [Sefer HaChinuch].",
    15: "Physical act explicitly commanded; scroll text/content standardized later. [Rambam], [Rashi].",
    16: "Verse addresses the \"Song of Moses\"; rabbinic law expands to a full Torah scroll. [Rambam], [Ramban].",
    17: "Lifelong obligation of learning/transmission; basis of communal education. [Sifre Deut.], [Rambam].",
    18: "Guards integrity of Torah; debated vis-à-vis protective \"fences.\" [Rambam], [Ramban].",
    19: "Forbids erasing or loosening Torah law. [Rambam], [Sefer HaChinuch].",
    20: "Fulfilled in Tabernacle/Temple; later hopes for restoration. [Rambam], [Ramban].",
    21: "Repeated prohibition; tied to life being \"in the blood.\" [Lev. 17:11], [Sifra].",
    22: "Rabbinic law specifies which fats are chelev vs. permissible shuman. [Rambam], [Hullin].",
    23: "May give/sell to a resident alien; reflects ritual/ethical boundary. [Ramban], [Sefer HaChinuch].",
    24: "Later laws define injury types rendering meat terefah. [Hullin], [Rambam].",
    25: "Tradition broadens to a general meat-dairy separation; scope debated. [Rambam], [Rashbam].",
    26: "Classification of insects and vermin debated. [Rambam], [Sifra].",
    27: "Expands dietary separation and ritual purity. [Ramban], [Hullin].",
    28: "Locusts partly excepted; tradition diverges. [Rambam], [Sifra].",
    29: "General prohibition covering multiple categories. [Ramban], [Sefer HaChinuch].",
    30: "Torah assumes prior instruction; method defined in tradition (shechita). [Hullin], [Rambam].",
    31: "Rooted in Jacob's wrestling story; ritualized later. [Rambam], [Sifra].",
    32: "Reverence for life, especially in wild game. [Ramban], [Hullin].",
    33: "A law of compassion and preservation. [Rambam], [Sefer HaChinuch].",
    34: "Blessing attached: \"that it may be well with thee.\" [Ramban], [Sifre Deut.].",
    35: "Reinforces sanctity of life cycles. [Rambam], [Sifra Emor].",
    36: "Forms basis of kosher laws. [Rambam], [Sifra].",
    37: "Simple test, repeated in Deut. 14:9. [Rambam], [Rashbam].",
    38: "Torah lists forbidden birds; rabbis develop criteria. [Ramban], [Sifra].",
    39: "Practiced in some Jewish traditions, lost in others. [Rambam], [Mishnah Hullin].",
    40: "Torah forbids misuse of sacred things; rabbis codified \"tevel.\" [Rambam], [Hullin].",
    41: "Sustains priestly class; echoes Levitical inheritance. [Rambam], [Rashi].",
    42: "Central to support of Levites. [Nehemiah 10], [Rambam].",
    43: "Models accountability; leaders tithe too. [Rambam], [Rashi].",
    44: "Strengthened Jerusalem's centrality. [Ramban], [Sifre].",
    45: "Prioritizes social justice and care. [Rambam], [Sefer HaChinuch].",
    46: "Infuses daily bread with sanctity. [Rambam], [Rashi].",
    47: "Remembrance of Israel's redemption in Egypt. [Rambam], [Rashi].",
    48: "Unique command; donkey symbolically tied to service/slavery. [Rambam], [Philo].",
    49: "Root of Passover ritual; expanded into detailed practices. [Rambam], [Mishnah Pesachim].",
    50: "Complements mitzvah to remove chametz; ensures total removal. [Rambam], [Pesachim]."
}

def process_mitzvot_1_to_50():
    """Process first 50 mitzvot with exact user-provided notes"""
    
    print("=== Processing Mitzvot 1-50 with User's Exact Scholarly Notes ===")
    
    processed_count = 0
    verification_results = []
    
    for number in range(1, 51):
        # Get the mitzvah from database
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found in database")
            continue
        
        # Get user's specific note for this mitzvah
        user_note = MITZVOT_1_TO_50.get(number)
        
        if not user_note:
            print(f"⚠️  No user note found for Mitzvah {number}")
            continue
        
        # Get existing note and extract additional context
        current_note = mitzvah.get("scholarlyNote", "")
        
        if " | **Additional Context**:" in current_note:
            additional_context = current_note.split(" | **Additional Context**: ")[1]
        else:
            # Use the current note as additional context if no differentiation exists yet
            if current_note.startswith("**Scholarly Analysis**:"):
                additional_context = ""
            else:
                additional_context = current_note.strip()
        
        # Create the differentiated note
        if additional_context.strip():
            new_note = f"**Scholarly Analysis**: {user_note} | **Additional Context**: {additional_context}"
        else:
            new_note = f"**Scholarly Analysis**: {user_note}"
        
        # Update in database
        db.mitzvot.update_one(
            {"number": number},
            {
                "$set": {
                    "scholarlyNote": new_note,
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        )
        
        processed_count += 1
        
        # Store verification info
        verification_results.append({
            "number": number,
            "title": mitzvah.get("title", ""),
            "user_note": user_note,
            "has_additional": bool(additional_context.strip())
        })
        
        if processed_count % 10 == 0:
            print(f"   Processed {processed_count}/50 mitzvot...")
    
    print(f"\n✅ Processed {processed_count} mitzvot (1-50)")
    
    # Verification
    print("\n📝 Verification Sample (first 5):")
    for result in verification_results[:5]:
        print(f"\nMitzvah {result['number']}: {result['title']}")
        print(f"User note applied: {result['user_note'][:60]}...")
        print(f"Has additional context: {result['has_additional']}")
    
    # Final check
    print(f"\n🔍 Final Verification:")
    sample_numbers = [1, 25, 50]
    for num in sample_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            note = mitzvah["scholarlyNote"]
            expected_note = MITZVOT_1_TO_50.get(num, "")
            
            if expected_note in note:
                print(f"✅ Mitzvah {num}: Correctly applied")
            else:
                print(f"❌ Mitzvah {num}: May need review")

if __name__ == "__main__":
    process_mitzvot_1_to_50()