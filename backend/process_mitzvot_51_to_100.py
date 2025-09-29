#!/usr/bin/env python3
"""
Process Mitzvot 51-100 with user's exact scholarly notes
Batch 2 of 13 total batches
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 51-100 - Exact scholarly notes from user's message
MITZVOT_51_TO_100 = {
    51: "Central symbol of redemption; linked to haste of Exodus. [Rambam], [Philo].",
    52: "Root of the Passover Seder narrative. [Mekhilta], [Rambam].",
    53: "Distinct from possession prohibition; eating is punishable by karet. [Rambam], [Pesachim].",
    54: "Holiday parallels Sabbath rest but with limited exceptions. [Rambam], [Sifra].",
    55: "Completes the festival cycle; recalls crossing of the Sea. [Rambam], [Rashbam].",
    56: "Agricultural and spiritual anticipation; debated if still biblical today. [Rambam], [Sefer HaChinuch].",
    57: "Marks Torah giving; agricultural firstfruits. [Philo], [Rambam].",
    58: "Symbol of covenant renewal. [Rambam], [Sifra].",
    59: "Known as \"Yom Teruah\"; rabbis emphasized shofar command. [Rambam], [Sifre].",
    60: "Tradition specifies ram's horn and ritual patterns. [Rambam], [Rosh Hashanah].",
    61: "Only fast-day among festivals; unique solemnity. [Rambam], [Sifra].",
    62: "Includes fasting and abstentions; scope debated. [Rambam], [Mishnah Yoma].",
    63: "Primary form of affliction; penalty severe. [Rambam], [Sifra].",
    64: "Parallels Passover's opening festival rest. [Rambam], [Sifra].",
    65: "Symbolizes wilderness sojourn; scope of \"dwell\" debated. [Rambam], [Sukkah].",
    66: "Rabbinic tradition identifies four species. [Rambam], [Sifra].",
    67: "Includes family, Levite, stranger, widow, orphan. [Rambam], [Sifre Deut.].",
    68: "Separate festival yet tied to Sukkot. [Rambam], [Rashbam].",
    69: "Defined schedule for daily, Sabbath, and festival offerings. [Rambam], [Sifra].",
    70: "Pilgrimage centered on Temple; linked to covenant loyalty. [Philo], [Rambam].",
    71: "Ensures honor in worship; offering scaled by ability. [Rambam], [Sifre].",
    72: "Extends joy theme beyond Sukkot. [Rambam], [Sefer HaChinuch].",
    73: "Covenant renewal through public reading. [Rambam], [Sifre Deut.].",
    74: "Cyclical tithe system reinforced Jerusalem pilgrimage. [Rambam], [Rashi].",
    75: "Underscores social equity in covenant economy. [Rambam], [Sefer HaChinuch].",
    76: "Public confession of faithful tithing; tied to covenant blessings. [Rambam], [Sifre Deut.].",
    77: "Act of gratitude and recognition of God's provision. [Rambam], [Philo].",
    78: "Confession links personal offering to national story of redemption. [Rambam], [Sifre Deut.].",
    79: "Funding for communal offerings; symbol of equality. [Rambam], [Josephus].",
    80: "Initially observational; later fixed calendar. [Rambam], [Philo].",
    81: "Central covenant sign; scope of \"work\" defined in tradition. [Rambam], [Mekhilta].",
    82: "Rabbinic interpretation made this verbal sanctification at meals. [Rambam], [Sifre].",
    83: "Thirty-nine categories of work derived later from Mishkan tasks. [Mishnah Shabbat], [Rambam].",
    84: "Explicit prohibition; debated if it stands apart or as an example of work. [Rambam], [Rashbam].",
    85: "One of the festival rest commands; associated with shofar. [Rambam], [Sifra].",
    86: "Combines rest with fasting; distinct from other festivals. [Rambam], [Mishnah Yoma].",
    87: "Multiple verses repeat this; emphasizes gravity of the day. [Rambam], [Sifra].",
    88: "Affliction primarily understood as fasting. [Rambam], [Sifra].",
    89: "Sets apart festival start; mirrors Passover. [Rambam], [Rashi].",
    90: "Treated as distinct yet tied to Sukkot. [Rambam], [Philo].",
    91: "Symbolizes dependence on God in wilderness; debated if literal or symbolic. [Rambam], [Sukkah].",
    92: "Identified by rabbinic tradition; not explicit in text. [Rambam], [Sifra].",
    93: "Includes all groups; tied to agricultural bounty. [Rambam], [Sifre Deut.].",
    94: "Post-exilic ordinance, later treated as binding. [Rambam], [Talmud Taanit].",
    95: "Basis for mikveh practice; expanded rabbinically. [Rambam], [Sifra].",
    96: "Only priests restricted; Nazirite included. [Rambam], [Sifre Num.].",
    97: "Rare ritual; central to corpse defilement laws. [Rambam], [Philo].",
    98: "Protects holiness of offerings. [Rambam], [Sifra].",
    99: "Purity required for sacred spaces. [Rambam], [Rashi].",
    100: "Ensures sanctity of worship and offerings. [Rambam], [Sifra]."
}

def process_mitzvot_51_to_100():
    """Process mitzvot 51-100 with exact user-provided notes"""
    
    print("=== Processing Mitzvot 51-100 (Batch 2/13) ===")
    
    processed_count = 0
    
    for number in range(51, 101):
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found")
            continue
        
        user_note = MITZVOT_51_TO_100.get(number)
        
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
    
    print(f"\n✅ Batch 2 Complete: {processed_count} mitzvot (51-100)")
    
    # Verification
    verification_numbers = [51, 75, 100]
    print(f"\n🔍 Verification Check:")
    
    for num in verification_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            note = mitzvah["scholarlyNote"]
            expected_note = MITZVOT_51_TO_100.get(num, "")
            
            if expected_note in note:
                print(f"✅ Mitzvah {num}: {expected_note[:50]}... - APPLIED")
            else:
                print(f"❌ Mitzvah {num}: Needs review")

if __name__ == "__main__":
    process_mitzvot_51_to_100()