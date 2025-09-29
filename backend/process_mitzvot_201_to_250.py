#!/usr/bin/env python3
"""
Process Mitzvot 201-250 with user's exact scholarly notes
Batch 5 of 13 total batches
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 201-250 - Exact scholarly notes from user's message
MITZVOT_201_TO_250 = {
    201: "Eating symbolizes bearing the people's sin. [Rambam], [Sifra].",
    202: "Preserves sacred boundary. [Rambam], [Rashi].",
    203: "Prevents desecration; invalid meat becomes piggul. [Rambam], [Sifra].",
    204: "Defines boundary of priestly privileges. [Rambam], [Sifre].",
    205: "Links marital status with access to terumah. [Rambam], [Rashi].",
    206: "Applies purity laws to priestly food. [Rambam], [Sifra].",
    207: "Institutionalizes priestly sustenance. [Rambam], [Philo].",
    208: "Repeated obligation for Levitical support. [Rambam], [Nehemiah 10].",
    209: "Creates fairness; priests share in Levitical tithe. [Rambam], [Sifre Num.].",
    210: "Binds agriculture to Jerusalem's sanctity. [Rambam], [Philo].",
    211: "Ensures social justice within covenant. [Rambam], [Sefer HaChinuch].",
    212: "Public accountability before God. [Rambam], [Sifre Deut.].",
    213: "Gratitude command; tied to land's bounty. [Rambam], [Philo].",
    214: "Links harvest with covenant history. [Rambam], [Sifre Deut.].",
    215: "System of compassion for poor. [Rambam], [Sifra].",
    216: "Includes widows, orphans, foreigners. [Rambam], [Sefer HaChinuch].",
    217: "Ensures provision for marginalized. [Rambam], [Rashi].",
    218: "Parallels gleanings for equity. [Rambam], [Sifra].",
    219: "Brings sanctity into daily bread. [Rambam], [Rashi].",
    220: "Agricultural rest for land and poor. [Rambam], [Philo].",
    221: "Land Sabbath reflects divine ownership. [Rambam], [Sifra].",
    222: "Produce treated as common property. [Rambam], [Sefer HaChinuch].",
    223: "Promotes rest and sharing. [Rambam], [Rashi].",
    224: "Reset of land and liberty; iconic in history. [Rambam], [Philo].",
    225: "Marks release of slaves and return of land. [Rambam], [Josephus].",
    226: "Ultimate liberation command. [Rambam], [Sifra].",
    227: "Prevents permanent poverty and loss. [Rambam], [Philo].",
    228: "Theology of God's ownership of land. [Rambam], [Sifra].",
    229: "Protects family inheritance. [Rambam], [Rashi].",
    230: "Prevents exploitation in sales. [Rambam], [Sifra].",
    231: "Fairness in trade tied to holiness. [Rambam], [Sefer HaChinuch].",
    232: "Model of social solidarity. [Rambam], [Philo].",
    233: "Encourages mercy-based lending. [Rambam], [Sifra].",
    234: "Builds communal trust and relief. [Rambam], [Rashi].",
    235: "Tradition frames it as forbidding harshness toward poor borrowers. [Rambam], [Sifra].",
    236: "Prevents permanent poverty cycles. [Rambam], [Philo].",
    237: "Encourages generosity despite release laws. [Rambam], [Sifre Deut.].",
    238: "Balances creditor rights and debtor dignity. [Rambam], [Rashi].",
    239: "Protects livelihood of poor. [Rambam], [Sefer HaChinuch].",
    240: "Extra compassion toward vulnerable. [Rambam], [Sifre Deut.].",
    241: "Core covenant ethic of protecting the weak. [Rambam], [Philo].",
    242: "Early labor-rights commandment. [Rambam], [Sefer HaChinuch].",
    243: "Links wage delay with oppression; ethical labor norm. [Rambam], [Sifra].",
    244: "Protects the vulnerable; applied broadly to all forms of abuse. [Rambam], [Sefer HaChinuch].",
    245: "Interpreted ethically as banning deceptive advice. [Rambam], [Sifra].",
    246: "Basis for due process and favorable presumption. [Rambam], [Rashi].",
    247: "Expands into bans on bribes, bias, and unequal measures. [Rambam], [Sifre].",
    248: "Justice must be impartial—neither wealth nor poverty sways law. [Rambam], [Rashi].",
    249: "Complements previous command; equity before law. [Rambam], [Sifra].",
    250: "Duty to rescue/endangerment prevention. [Rambam], [Sefer HaChinuch]."
}

def process_mitzvot_201_to_250():
    """Process mitzvot 201-250 with exact user-provided notes"""
    
    print("=== Processing Mitzvot 201-250 (Batch 5/13) ===")
    
    processed_count = 0
    
    for number in range(201, 251):
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found")
            continue
        
        user_note = MITZVOT_201_TO_250.get(number)
        
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
    
    print(f"\n✅ Batch 5 Complete: {processed_count} mitzvot (201-250)")
    
    # Verification
    verification_numbers = [201, 225, 250]
    print(f"\n🔍 Verification Check:")
    
    for num in verification_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            note = mitzvah["scholarlyNote"]
            expected_note = MITZVOT_201_TO_250.get(num, "")
            
            if expected_note in note:
                print(f"✅ Mitzvah {num}: {expected_note[:50]}... - APPLIED")
            else:
                print(f"❌ Mitzvah {num}: Needs review")
    
    # Overall progress update
    total_processed = 250
    total_mitzvot = 613
    progress_percent = (total_processed / total_mitzvot) * 100
    
    print(f"\n📊 Overall Progress: {total_processed}/{total_mitzvot} ({progress_percent:.1f}%) complete")
    print(f"Remaining: {total_mitzvot - total_processed} mitzvot in ~{(total_mitzvot - total_processed) // 50} batches")

if __name__ == "__main__":
    process_mitzvot_201_to_250()