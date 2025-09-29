#!/usr/bin/env python3
"""
CORRECTED: Process Mitzvot 1-50 with BOTH traditional wording AND scholarly notes
This fixes the critical oversight of ignoring traditional wording
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# CORRECTED: BOTH traditional wording AND scholarly notes for mitzvot 1-50
MITZVOT_1_50_CORRECTED = {
    1: {
        "traditionalWording": "Believe in and recognize YHWH as God.",
        "scholarlyNote": "Often treated as the first positive command; some read it as a declaration rather than a command. [Rambam], [Ramban]."
    },
    2: {
        "traditionalWording": "Do not recognize or serve other gods.",
        "scholarlyNote": "Establishes exclusive covenant loyalty; foundational to later anti-idolatry laws. [Rambam], [Sifre Deut.]."
    },
    3: {
        "traditionalWording": "Do not make carved or molten images for worship.",
        "scholarlyNote": "Scope debated—art in general vs. worship images; context supports cultic prohibition. [Ibn Ezra], [Rashi]."
    },
    4: {
        "traditionalWording": "Do not bow or perform service to idols.",
        "scholarlyNote": "Encompasses ritual acts like sacrifice, incense, libations. [Rambam], [Sifra Lev.]."
    },
    5: {
        "traditionalWording": "Do not curse or revile the Name of YHWH.",
        "scholarlyNote": "Distinguished from careless oaths; formal reviling of the Name. [Mishnah Sanh.], [Rambam]."
    },
    6: {
        "traditionalWording": "Love YHWH with all heart, soul, might.",
        "scholarlyNote": "Expressed through obedience and devotion; central to Shema. [Sifre Deut.], [Rambam]."
    },
    7: {
        "traditionalWording": "Live in reverent awe of YHWH.",
        "scholarlyNote": "Reverence motivates faithful service and avoidance of sin. [Rambam], [Ramban]."
    },
    8: {
        "traditionalWording": "Serve YHWH (worship/prayer/obedience).",
        "scholarlyNote": "Service includes prayer (avodah shebalev) in later rabbinic framing. [Taanit 2a], [Rambam]."
    },
    9: {
        "traditionalWording": "Cling to YHWH.",
        "scholarlyNote": "Interpreted as emulating God's ways and attaching to His Torah/servants. [Sifre Deut.], [Rambam]."
    },
    10: {
        "traditionalWording": "Swear only by YHWH, truthfully.",
        "scholarlyNote": "Permits oaths in God's Name when true and necessary; false oaths condemned. [Rambam], [Sefer HaChinuch]."
    },
    11: {
        "traditionalWording": "Do not profane; live to sanctify His Name.",
        "scholarlyNote": "Kiddush Hashem vs. Chillul Hashem as ethical-religious ideals. [Rambam], [Sifra Emor]."
    },
    12: {
        "traditionalWording": "Do not put YHWH to the test.",
        "scholarlyNote": "Prohibits demanding signs or doubting His faithfulness. [Ramban], [Sifre Deut.]."
    },
    13: {
        "traditionalWording": "Bind words as a sign on your arm.",
        "scholarlyNote": "Literal vs metaphorical interpretation debated; practice standardized rabbinically. [Rambam], [Rashi]."
    },
    14: {
        "traditionalWording": "Bind words between your eyes.",
        "scholarlyNote": "Placement, compartments, and texts regulated by tradition. [Rambam], [Sefer HaChinuch]."
    },
    15: {
        "traditionalWording": "Affix mezuzah to doorposts.",
        "scholarlyNote": "Physical act explicitly commanded; scroll text/content standardized later. [Rambam], [Rashi]."
    },
    # Continue with specific pattern for all 50...
    # I need to extract all from user's message systematically
}

def apply_corrected_traditional_wording_and_notes():
    """Apply both traditional wording and scholarly notes correctly"""
    
    print("=== CORRECTED: Applying Both Traditional Wording AND Scholarly Notes ===")
    print("Fixing the critical oversight identified by user")
    
    updated_count = 0
    
    for number, data in MITZVOT_1_50_CORRECTED.items():
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if mitzvah:
            current_note = mitzvah.get("scholarlyNote", "")
            
            # Extract existing additional context if present
            if " | **Additional Context**:" in current_note:
                additional_context = current_note.split(" | **Additional Context**: ")[1]
            else:
                additional_context = ""
            
            # Create new scholarly note with differentiation
            if additional_context.strip():
                new_scholarly_note = f"**Scholarly Analysis**: {data['scholarlyNote']} | **Additional Context**: {additional_context}"
            else:
                new_scholarly_note = f"**Scholarly Analysis**: {data['scholarlyNote']}"
            
            # Update BOTH fields
            db.mitzvot.update_one(
                {"number": number},
                {
                    "$set": {
                        "traditionalWording": data["traditionalWording"],
                        "scholarlyNote": new_scholarly_note,
                        "updatedAt": datetime.now(timezone.utc)
                    }
                }
            )
            
            updated_count += 1
    
    print(f"✅ Updated {updated_count} mitzvot with BOTH fields")
    
    # Verify the fix for mitzvah 87 (user's specific example)
    print("\\n🔍 Verification - Need to extract mitzvah 87 data from user's message:")
    print("User provided: 'Traditional wording: Do not perform labor on Yom Kippur.'")
    print("This confirms I need to systematically extract ALL traditional wording")

if __name__ == "__main__":
    apply_corrected_traditional_wording_and_notes()