#!/usr/bin/env python3
"""
Process Mitzvot 101-150 with user's exact scholarly notes
Batch 3 of 13 total batches
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 101-150 - Exact scholarly notes from user's message
MITZVOT_101_TO_150 = {
    101: "Symbolic act of purity before sacred duty. [Rambam], [Philo].",
    102: "Vestments confer sanctity; linked to priestly identity. [Rambam], [Josephus].",
    103: "Priesthood requires dignity; no mourning in service. [Rambam], [Sifra].",
    104: "Regulation for temple service appearance. [Rambam], [Philo].",
    105: "Ensures continuous sanctity during worship. [Rambam], [Sifra].",
    106: "Symbol of purity for the nation's intercessor. [Rambam], [Josephus].",
    107: "Reinforces distinction of High Priest's role. [Rambam], [Sifra].",
    108: "Preserves priestly holiness through marriage. [Rambam], [Rashi].",
    109: "Limits union to women of unbroken marital state. [Rambam], [Sifra].",
    110: "Restricts mourning to preserve holiness. [Rambam], [Philo].",
    111: "Highlights separation of High Priest. [Rambam], [Josephus].",
    112: "Prevents degradation of priestly seed. [Rambam], [Rashi].",
    113: "Formula preserved; still recited in synagogues. [Rambam], [Sifre Num.].",
    114: "Symbolizes prayers rising; integral to service. [Rambam], [Philo].",
    115: "Continuous flame symbolized divine presence. [Rambam], [Sifra].",
    116: "Ritual maintenance of sacred fire. [Rambam], [Rashi].",
    117: "Daily menorah lighting signified divine illumination. [Rambam], [Philo].",
    118: "Represents continual fellowship between God and Israel. [Rambam], [Josephus].",
    119: "Morning and evening service centerpiece. [Rambam], [Philo].",
    120: "Adds to daily offering; shows Sabbath honor. [Rambam], [Sifre Num.].",
    121: "Connects heavenly calendar with earthly worship. [Rambam], [Philo].",
    122: "Supplement to paschal lamb; communal. [Rambam], [Sifre Num.].",
    123: "Marks harvest and Torah giving. [Rambam], [Philo].",
    124: "Festival-specific offering; links with shofar. [Rambam], [Sifra].",
    125: "Atonement-focused communal worship. [Rambam], [Mishnah Yoma].",
    126: "Unique diminishing bull pattern over seven days. [Rambam], [Philo].",
    127: "Distinct day following Sukkot; symbolic of intimate fellowship. [Rambam], [Rashi].",
    128: "Centralization of worship in Jerusalem. [Rambam], [Sifre Deut.].",
    129: "Countered local high places; enforced unity. [Rambam], [Philo].",
    130: "Equated with bloodshed; emphasizes central altar. [Rambam], [Sifra].",
    131: "Commemoration of Egypt deliverance. [Rambam], [Philo].",
    132: "Exception among unclean beasts; symbolic of service. [Rambam], [Sifre].",
    133: "Avoids misuse of consecrated animal. [Rambam], [Philo].",
    134: "Belongs to God as deliverer. [Rambam], [Josephus].",
    135: "Priesthood supported through offerings. [Rambam], [Sifre Deut.].",
    136: "Fulfilled in priestly service dedication. [Rambam], [Philo].",
    137: "Sacrificed at altar; meat for priests. [Rambam], [Sifre Num.].",
    138: "Part of priestly portion system. [Rambam], [Rashi].",
    139: "Sustains Levites who serve without land. [Rambam], [Philo].",
    140: "Ensures priests share in Levitical support. [Rambam], [Sifre Num.].",
    141: "Combines worship with agricultural bounty. [Rambam], [Philo].",
    142: "Embeds social care into agriculture; part of the cyclical tithe system. [Rambam], [Sifre Deut.].",
    143: "Distinct from terumah/tithes; part of priestly support. [Rambam], [Sefer HaChinuch].",
    144: "Agricultural gift paralleling firstfruits; emphasizes priestly provision. [Rambam], [Rashi].",
    145: "Leaven/honey symbolize fermentation/sweetening; reserved for firstfruits loaves (not on the altar fire). [Rambam], [Sifra].",
    146: "\"Covenant of salt\" signifies permanence and loyalty. [Rambam], [Philo].",
    147: "Preserves honor of worship; extensive lists of blemishes follow. [Rambam], [Sifra Emor].",
    148: "Distinguishes between consecration and offering—blemished animals are invalid from the start. [Rambam], [Rashi].",
    149: "The obligation to \"inspect\" is implied by the requirement of perfection; procedures detailed in tradition. [Rambam], [Sifra].",
    150: "Protects integrity of offerings; also linked to later bans on castration. [Rambam], [Sefer HaChinuch]."
}

def process_mitzvot_101_to_150():
    """Process mitzvot 101-150 with exact user-provided notes"""
    
    print("=== Processing Mitzvot 101-150 (Batch 3/13) ===")
    
    processed_count = 0
    
    for number in range(101, 151):
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found")
            continue
        
        user_note = MITZVOT_101_TO_150.get(number)
        
        if not user_note:
            print(f"⚠️  No user note for Mitzvah {number}")
            continue
        
        # Get existing additional context
        current_note = mitzvah.get("scholarlyNote", "")
        
        if " | **Additional Context**:" in current_note:
            additional_context = current_note.split(" | **Additional Context**: ")[1]
        else:
            additional_context = current_note.strip() if not current_note.startswith("**Scholarly Analysis**:") else ""
        
        # Create differentiated note
        if additional_context.strip():
            new_note = f"**Scholarly Analysis**: {user_note} | **Additional Context**: {additional_context}"
        else:
            new_note = f"**Scholarly Analysis**: {user_note}"
        
        # Update database
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
        
        if processed_count % 10 == 0:
            print(f"   Processed {processed_count}/50...")
    
    print(f"\n✅ Batch 3 Complete: {processed_count} mitzvot (101-150)")
    
    # Verification
    verification_numbers = [101, 125, 150]
    print(f"\n🔍 Verification Check:")
    
    for num in verification_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            note = mitzvah["scholarlyNote"]
            expected_note = MITZVOT_101_TO_150.get(num, "")
            
            if expected_note in note:
                print(f"✅ Mitzvah {num}: {expected_note[:50]}... - APPLIED")
            else:
                print(f"❌ Mitzvah {num}: Needs review")
    
    # Overall progress update
    total_processed = 150
    total_mitzvot = 613
    progress_percent = (total_processed / total_mitzvot) * 100
    
    print(f"\n📊 Overall Progress: {total_processed}/{total_mitzvot} ({progress_percent:.1f}%) complete")
    print(f"Remaining: {total_mitzvot - total_processed} mitzvot in ~{(total_mitzvot - total_processed) // 50} batches")

if __name__ == "__main__":
    process_mitzvot_101_to_150()