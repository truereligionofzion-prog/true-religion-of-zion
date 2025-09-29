#!/usr/bin/env python3
"""
CORRECTED: Process Mitzvot 87-136 with BOTH traditional wording AND scholarly notes
Starting from where the issue was identified by user
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 87-136 - BOTH traditional wording AND scholarly notes from user's message
MITZVOT_87_TO_136_CORRECTED = {
    87: {
        "traditionalWording": "Do not perform labor on Yom Kippur.",
        "scholarlyNote": "Multiple verses repeat this; emphasizes gravity of the day. [Rambam], [Sifra]."
    },
    88: {
        "traditionalWording": "Fast and deny physical pleasures.",
        "scholarlyNote": "Affliction primarily understood as fasting. [Rambam], [Sifra]."
    },
    89: {
        "traditionalWording": "Cease from labor on the first day.",
        "scholarlyNote": "Sets apart festival start; mirrors Passover. [Rambam], [Rashi]."
    },
    90: {
        "traditionalWording": "Cease from labor on the eighth day.",
        "scholarlyNote": "Treated as distinct yet tied to Sukkot. [Rambam], [Philo]."
    },
    91: {
        "traditionalWording": "Live in booths during the feast.",
        "scholarlyNote": "Symbolizes dependence on God in wilderness; debated if literal or symbolic. [Rambam], [Sukkah]."
    },
    92: {
        "traditionalWording": "Take palm, citron, myrtle, willow.",
        "scholarlyNote": "Identified by rabbinic tradition; not explicit in text. [Rambam], [Sifra]."
    },
    93: {
        "traditionalWording": "Rejoice before YHWH on the feast.",
        "scholarlyNote": "Includes all groups; tied to agricultural bounty. [Rambam], [Sifre Deut.]."
    },
    94: {
        "traditionalWording": "Provide wood for the altar.",
        "scholarlyNote": "Post-exilic ordinance, later treated as binding. [Rambam], [Talmud Taanit]."
    },
    95: {
        "traditionalWording": "Purify oneself through water immersion.",
        "scholarlyNote": "Basis for mikveh practice; expanded rabbinically. [Rambam], [Sifra]."
    },
    96: {
        "traditionalWording": "Avoid corpse impurity unless permitted.",
        "scholarlyNote": "Only priests restricted; Nazirite included. [Rambam], [Sifre Num.]."
    },
    97: {
        "traditionalWording": "Use water of purification with ashes.",
        "scholarlyNote": "Rare ritual; central to corpse defilement laws. [Rambam], [Philo]."
    },
    98: {
        "traditionalWording": "Do not eat holy offerings in impurity.",
        "scholarlyNote": "Protects holiness of offerings. [Rambam], [Sifra]."
    },
    99: {
        "traditionalWording": "Do not enter God's sanctuary in a state of impurity.",
        "scholarlyNote": "Purity required for sacred spaces. [Rambam], [Rashi]."
    },
    100: {
        "traditionalWording": "Priests shall not minister when defiled.",
        "scholarlyNote": "Ensures sanctity of worship and offerings. [Rambam], [Sifra]."
    },
    101: {
        "traditionalWording": "Priests must wash hands and feet before ministering.",
        "scholarlyNote": "Symbolic act of purity before sacred duty. [Rambam], [Philo]."
    },
    102: {
        "traditionalWording": "Priests must wear holy vestments during service.",
        "scholarlyNote": "Vestments confer sanctity; linked to priestly identity. [Rambam], [Josephus]."
    },
    103: {
        "traditionalWording": "Do not serve with torn clothes.",
        "scholarlyNote": "Priesthood requires dignity; no mourning in service. [Rambam], [Sifra]."
    },
    104: {
        "traditionalWording": "Do not enter with unshorn hair.",
        "scholarlyNote": "Regulation for temple service appearance. [Rambam], [Philo]."
    },
    105: {
        "traditionalWording": "Stay in the sanctuary while serving.",
        "scholarlyNote": "Ensures continuous sanctity during worship. [Rambam], [Sifra]."
    },
    106: {
        "traditionalWording": "High Priest may only wed a virgin.",
        "scholarlyNote": "Symbol of purity for the nation's intercessor. [Rambam], [Josephus]."
    },
    107: {
        "traditionalWording": "Forbidden for High Priest to marry a widow.",
        "scholarlyNote": "Reinforces distinction of High Priest's role. [Rambam], [Sifra]."
    },
    108: {
        "traditionalWording": "Do not marry zonah or chalalah.",
        "scholarlyNote": "Preserves priestly holiness through marriage. [Rambam], [Rashi]."
    },
    109: {
        "traditionalWording": "Do not wed a divorced woman.",
        "scholarlyNote": "Limits union to women of unbroken marital state. [Rambam], [Sifra]."
    },
    110: {
        "traditionalWording": "Regular priests avoid corpse impurity except family.",
        "scholarlyNote": "Restricts mourning to preserve holiness. [Rambam], [Philo]."
    },
    111: {
        "traditionalWording": "High Priest cannot defile even for relatives.",
        "scholarlyNote": "Highlights separation of High Priest. [Rambam], [Josephus]."
    },
    112: {
        "traditionalWording": "Priests may not marry those desecrated from priestly lineage.",
        "scholarlyNote": "Prevents degradation of priestly seed. [Rambam], [Rashi]."
    },
    113: {
        "traditionalWording": "Priests bless Israel.",
        "scholarlyNote": "Formula preserved; still recited in synagogues. [Rambam], [Sifre Num.]."
    },
    114: {
        "traditionalWording": "Offer incense morning and evening.",
        "scholarlyNote": "Symbolizes prayers rising; integral to service. [Rambam], [Philo]."
    },
    115: {
        "traditionalWording": "Fire must never go out.",
        "scholarlyNote": "Continuous flame symbolized divine presence. [Rambam], [Sifra]."
    },
    116: {
        "traditionalWording": "Priests must clear altar ashes.",
        "scholarlyNote": "Ritual maintenance of sacred fire. [Rambam], [Rashi]."
    },
    117: {
        "traditionalWording": "Priests light the menorah daily.",
        "scholarlyNote": "Daily menorah lighting signified divine illumination. [Rambam], [Philo]."
    },
    118: {
        "traditionalWording": "Place twelve loaves weekly.",
        "scholarlyNote": "Represents continual fellowship between God and Israel. [Rambam], [Josephus]."
    },
    119: {
        "traditionalWording": "Bring two lambs every day.",
        "scholarlyNote": "Morning and evening service centerpiece. [Rambam], [Philo]."
    },
    120: {
        "traditionalWording": "Bring two lambs on Sabbath.",
        "scholarlyNote": "Adds to daily offering; shows Sabbath honor. [Rambam], [Sifre Num.]."
    },
    121: {
        "traditionalWording": "Sacrifices for each new month.",
        "scholarlyNote": "Connects heavenly calendar with earthly worship. [Rambam], [Philo]."
    },
    122: {
        "traditionalWording": "Musaf for Passover days.",
        "scholarlyNote": "Supplement to paschal lamb; communal. [Rambam], [Sifre Num.]."
    },
    123: {
        "traditionalWording": "Musaf offering on Feast of Weeks.",
        "scholarlyNote": "Marks harvest and Torah giving. [Rambam], [Philo]."
    },
    124: {
        "traditionalWording": "Musaf sacrifices on Day of Trumpets.",
        "scholarlyNote": "Festival-specific offering; links with shofar. [Rambam], [Sifra]."
    },
    125: {
        "traditionalWording": "Musaf sacrifices on Day of Atonement.",
        "scholarlyNote": "Atonement-focused communal worship. [Rambam], [Mishnah Yoma]."
    },
    126: {
        "traditionalWording": "Musaf offerings each day of Sukkot.",
        "scholarlyNote": "Unique diminishing bull pattern over seven days. [Rambam], [Philo]."
    },
    127: {
        "traditionalWording": "Musaf offering on the eighth day.",
        "scholarlyNote": "Distinct day following Sukkot; symbolic of intimate fellowship. [Rambam], [Rashi]."
    },
    128: {
        "traditionalWording": "Sacrifices only at the chosen place.",
        "scholarlyNote": "Centralization of worship in Jerusalem. [Rambam], [Sifre Deut.]."
    },
    129: {
        "traditionalWording": "No sacrifices outside the sanctuary.",
        "scholarlyNote": "Countered local high places; enforced unity. [Rambam], [Philo]."
    },
    130: {
        "traditionalWording": "Do not slaughter consecrated animals outside.",
        "scholarlyNote": "Equated with bloodshed; emphasizes central altar. [Rambam], [Sifra]."
    },
    131: {
        "traditionalWording": "Redeem firstborn with silver.",
        "scholarlyNote": "Commemoration of Egypt deliverance. [Rambam], [Philo]."
    },
    132: {
        "traditionalWording": "Redeem or break the neck of firstling ass.",
        "scholarlyNote": "Exception among unclean beasts; symbolic of service. [Rambam], [Sifre]."
    },
    133: {
        "traditionalWording": "Break the neck if not redeemed.",
        "scholarlyNote": "Avoids misuse of consecrated animal. [Rambam], [Philo]."
    },
    134: {
        "traditionalWording": "Consecrate firstborn ox, sheep, goat.",
        "scholarlyNote": "Belongs to God as deliverer. [Rambam], [Josephus]."
    },
    135: {
        "traditionalWording": "Give firstborn animals to priests.",
        "scholarlyNote": "Priesthood supported through offerings. [Rambam], [Sifre Deut.]."
    },
    136: {
        "traditionalWording": "Present firstborn at sanctuary.",
        "scholarlyNote": "Fulfilled in priestly service dedication. [Rambam], [Philo]."
    }
}

def process_mitzvot_87_to_136_corrected():
    """Process mitzvot 87-136 with BOTH traditional wording and scholarly notes"""
    
    print("=== CORRECTED: Processing Mitzvot 87-136 (Both Fields) ===")
    print("Fixing the issue identified by user starting from mitzvah 87")
    
    updated_count = 0
    
    for number in range(87, 137):
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found")
            continue
        
        correction_data = MITZVOT_87_TO_136_CORRECTED.get(number)
        
        if not correction_data:
            print(f"⚠️  No correction data for Mitzvah {number}")
            continue
        
        # Get existing additional context from scholarly note
        current_note = mitzvah.get("scholarlyNote", "")
        
        if " | **Additional Context**:" in current_note:
            additional_context = current_note.split(" | **Additional Context**: ")[1]
        else:
            additional_context = current_note.strip() if not current_note.startswith("**Scholarly Analysis**:") else ""
        
        # Create new scholarly note with differentiation
        if additional_context.strip():
            new_scholarly_note = f"**Scholarly Analysis**: {correction_data['scholarlyNote']} | **Additional Context**: {additional_context}"
        else:
            new_scholarly_note = f"**Scholarly Analysis**: {correction_data['scholarlyNote']}"
        
        # Update BOTH traditional wording AND scholarly note
        db.mitzvot.update_one(
            {"number": number},
            {
                "$set": {
                    "traditionalWording": correction_data["traditionalWording"],
                    "scholarlyNote": new_scholarly_note,
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
        )
        
        updated_count += 1
        
        if updated_count % 10 == 0:
            print(f"   Updated {updated_count}/50...")
    
    print(f"\n✅ CORRECTED Batch: {updated_count} mitzvot (87-136) with BOTH fields")
    
    # Verification of the specific issue user identified
    print(f"\n🔍 Verification Check (Mitzvah 87 - User's Example):")
    mitzvah_87 = db.mitzvot.find_one({"number": 87})
    if mitzvah_87:
        traditional = mitzvah_87["traditionalWording"]
        expected = "Do not perform labor on Yom Kippur."
        
        print(f"Traditional Wording: {traditional}")
        if expected in traditional:
            print("✅ FIXED: Mitzvah 87 now has correct traditional wording!")
        else:
            print("❌ Still needs fixing")
    
    # Check a few more
    verification_numbers = [100, 120, 136]
    for num in verification_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            traditional = mitzvah["traditionalWording"]
            expected_traditional = MITZVOT_87_TO_136_CORRECTED.get(num, {}).get("traditionalWording", "")
            
            if expected_traditional in traditional:
                print(f"✅ Mitzvah {num}: Traditional wording correct")
            else:
                print(f"❌ Mitzvah {num}: Needs review")

if __name__ == "__main__":
    process_mitzvot_87_to_136_corrected()