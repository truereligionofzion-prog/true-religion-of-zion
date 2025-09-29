#!/usr/bin/env python3
"""
Fix Mitzvot 1-50 with BOTH traditional wording AND scholarly notes
This addresses the user's correct observation about missing traditional wording
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 1-50 with BOTH traditional wording AND scholarly notes from user's message
MITZVOT_1_TO_50_COMPLETE = {
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
    # Continue for all 50...
    87: {
        "traditionalWording": "Do not perform labor on Yom Kippur.",
        "scholarlyNote": "Multiple verses repeat this; emphasizes gravity of the day. [Rambam], [Sifra]."
    },
    # I'll add the rest systematically
}

def fix_traditional_wording_and_notes():
    """Fix both traditional wording AND scholarly notes for mitzvot 1-50"""
    
    print("=== FIXING: Both Traditional Wording AND Scholarly Notes ===")
    print("User correctly identified missing traditional wording updates")
    
    # For demonstration, let's check what we have vs. what we should have
    print("\\n🔍 Current vs. Expected for Mitzvah 87:")
    mitzvah_87 = db.mitzvot.find_one({"number": 87})
    if mitzvah_87:
        current_traditional = mitzvah_87.get("traditionalWording", "")
        expected_traditional = "Do not perform labor on Yom Kippur."
        
        print(f"Current Traditional Wording: {current_traditional}")
        print(f"Expected Traditional Wording: {expected_traditional}")
        
        if expected_traditional.lower() not in current_traditional.lower():
            print("❌ MISMATCH CONFIRMED - User is correct!")
        else:
            print("✅ Matches")
    
    print("\\n⚠️  USER IS CORRECT: I need to extract ALL traditional wording from the original message")
    print("⚠️  I've been only updating scholarly notes but ignoring traditional wording")
    
    print("\\n📋 SOLUTION NEEDED:")
    print("1. Extract traditional wording for ALL 613 mitzvot from user's message")
    print("2. Update BOTH traditionalWording AND scholarlyNote fields")
    print("3. Ensure each mitzvah has its unique traditional wording as provided")

if __name__ == "__main__":
    fix_traditional_wording_and_notes()