#!/usr/bin/env python3
"""
Process Mitzvot 151-200 with user's exact scholarly notes
Batch 4 of 13 total batches
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 151-200 - Exact scholarly notes from user's message
MITZVOT_151_TO_200 = {
    151: "Castration itself later prohibited; offering such animals profanes the altar. [Rambam], [Sifra].",
    152: "Protects sanctity of the sanctuary; tied to moral purity. [Rambam], [Philo].",
    153: "Exceptions for firstfruits bread; general fire-offerings excluded. [Rambam], [Sifra].",
    154: "Symbol of covenant permanence. [Rambam], [Philo].",
    155: "Upholds God's honor in worship. [Rambam], [Sifra].",
    156: "Distinction made between ownership and consecration. [Rambam], [Rashi].",
    157: "Derived prohibition to protect sacred property. [Rambam], [Sifra].",
    158: "Ensures sanctity even when animal is unfit. [Rambam], [Sifra].",
    159: "Honors natural development before use in worship. [Rambam], [Rashbam].",
    160: "Reinforces purity in worship. [Rambam], [Sefer HaChinuch].",
    161: "Prevents dishonoring God by substitutions. [Rambam], [Sifra].",
    162: "Creates deterrence against substitution. [Rambam], [Rashi].",
    163: "They are inherently sanctified for sacrifice. [Rambam], [Sifre Num.].",
    164: "Memorial of the Exodus. [Rambam], [Philo].",
    165: "Centralizes worship; rejects local high places. [Rambam], [Sifre Deut.].",
    166: "Restricts sacred consumption to holy place. [Rambam], [Rashbam].",
    167: "Redeemed via pidyon haben ceremony. [Rambam], [Sifre Exod.].",
    168: "Ongoing mitzvah in Jewish practice. [Rambam], [Sefer HaChinuch].",
    169: "Derived from the requirement \"from a month old.\" [Rambam], [Rashi].",
    170: "Unique case among unclean animals. [Rambam], [Philo].",
    171: "Prevents misuse of consecrated property. [Rambam], [Sifra].",
    172: "Gratitude practice; accompanied by declaration. [Rambam], [Philo].",
    173: "Links agricultural blessing to covenant story. [Rambam], [Sifre Deut.].",
    174: "Agricultural system sustaining Levites and poor. [Rambam], [Philo].",
    175: "Performed by passing animals under the rod. [Rambam], [Mishnah Bekhorot].",
    176: "Ensures fairness in offering. [Rambam], [Rashi].",
    177: "Early social welfare institution. [Rambam], [Sifra].",
    178: "Institutionalizes care for marginalized. [Rambam], [Sefer HaChinuch].",
    179: "Ensures poor partake in harvest bounty. [Rambam], [Rashi].",
    180: "Parallels field gleanings; compassion command. [Rambam], [Sifra].",
    181: "Extends sanctity into daily bread-making. [Rambam], [Rashi].",
    182: "Practical adaptation for long journeys. [Rambam], [Sifre Deut.].",
    183: "Ensures tithe strengthens Jerusalem's role. [Rambam], [Philo].",
    184: "Public accountability reinforces covenant. [Rambam], [Sifre Deut.].",
    185: "Symbol of gratitude for deliverance. [Rambam], [Philo].",
    186: "Fellowship meals symbolizing covenant harmony. [Rambam], [Sifra].",
    187: "Total dedication; no part eaten. [Rambam], [Philo].",
    188: "Restores purity and atonement. [Rambam], [Sifra].",
    189: "Includes cases of misuse of holy things. [Rambam], [Sifra].",
    190: "Symbolic act of presentation and sanctity. [Rambam], [Rashi].",
    191: "Set apart as holy portion for priests. [Rambam], [Sifre Num.].",
    192: "Leftovers become piggul (invalid). [Rambam], [Sifra].",
    193: "Restricts consumption to sanctified grounds; ties holiness to location. [Rambam], [Sifre Deut.].",
    194: "Reinforces Jerusalem's centrality in worship. [Rambam], [Philo].",
    195: "Blood rites essential for atonement; eating prior profanes the ritual. [Rambam], [Sifra].",
    196: "Protects holiness of offerings and purity system. [Rambam], [Sifra].",
    197: "Linked to requirement of unblemished offerings; ensures integrity. [Rambam], [Rashi].",
    198: "Prevents desecration through spoilage; sanctifies remains by fire. [Rambam], [Sifra].",
    199: "Overlaps with burning mitzvah; focuses on intentional neglect. [Rambam], [Sifre Lev.].",
    200: "Priestly eating seen as completing atonement process. [Rambam], [Sifra]."
}

def process_mitzvot_151_to_200():
    """Process mitzvot 151-200 with exact user-provided notes"""
    
    print("=== Processing Mitzvot 151-200 (Batch 4/13) ===")
    
    processed_count = 0
    
    for number in range(151, 201):
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found")
            continue
        
        user_note = MITZVOT_151_TO_200.get(number)
        
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
    
    print(f"\n✅ Batch 4 Complete: {processed_count} mitzvot (151-200)")
    
    # Verification
    verification_numbers = [151, 175, 200]
    print(f"\n🔍 Verification Check:")
    
    for num in verification_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            note = mitzvah["scholarlyNote"]
            expected_note = MITZVOT_151_TO_200.get(num, "")
            
            if expected_note in note:
                print(f"✅ Mitzvah {num}: {expected_note[:50]}... - APPLIED")
            else:
                print(f"❌ Mitzvah {num}: Needs review")
    
    # Overall progress update
    total_processed = 200
    total_mitzvot = 613
    progress_percent = (total_processed / total_mitzvot) * 100
    
    print(f"\n📊 Overall Progress: {total_processed}/{total_mitzvot} ({progress_percent:.1f}%) complete")
    print(f"Remaining: {total_mitzvot - total_processed} mitzvot in ~{(total_mitzvot - total_processed) // 50} batches")

if __name__ == "__main__":
    process_mitzvot_151_to_200()