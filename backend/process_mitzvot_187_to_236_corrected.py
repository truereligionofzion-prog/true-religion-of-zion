#!/usr/bin/env python3
"""
Process Mitzvot 187-236 with BOTH traditional wording AND scholarly notes
Continuing the systematic batch correction approach
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 187-236 - BOTH traditional wording AND scholarly notes from user's message
MITZVOT_187_TO_236_CORRECTED = {
    187: {
        "traditionalWording": "Present firstfruits at Temple and recite declaration.",
        "scholarlyNote": "Gratitude ceremony linking faith and agriculture. [Rambam], [Mishnah Bikkurim]."
    },
    188: {
        "traditionalWording": "Separate terumah (priestly portion) from crops.",
        "scholarlyNote": "First obligation before eating new produce. [Rambam], [Philo]."
    },
    189: {
        "traditionalWording": "Separate first tithe from remaining crops.",
        "scholarlyNote": "Given to Levites as their inheritance. [Rambam], [Josephus]."
    },
    190: {
        "traditionalWording": "Levites give tithe of their tithe to priests.",
        "scholarlyNote": "Maintains hierarchy within Temple service. [Rambam], [Sifre]."
    },
    191: {
        "traditionalWording": "Separate second tithe in years 1, 2, 4, 5 of sabbatical cycle.",
        "scholarlyNote": "Eaten in Jerusalem or redeemed with money. [Rambam], [Talmud]."
    },
    192: {
        "traditionalWording": "Separate poor tithe in years 3, 6 of sabbatical cycle.",
        "scholarlyNote": "Social welfare system commanded by Torah. [Rambam], [Philo]."
    },
    193: {
        "traditionalWording": "Give sheaves forgotten in field to poor.",
        "scholarlyNote": "Divine providence expressed through forgetfulness. [Rambam], [Rashi]."
    },
    194: {
        "traditionalWording": "Leave grape clusters for poor.",
        "scholarlyNote": "Incomplete harvest mandated for charity. [Rambam], [Sifra]."
    },
    195: {
        "traditionalWording": "Leave corners of field unharvested for poor.",
        "scholarlyNote": "Corner portion belongs to poor by divine right. [Rambam], [Philo]."
    },
    196: {
        "traditionalWording": "Return lost property to owner.",
        "scholarlyNote": "Active obligation to restore others' property. [Rambam], [Talmud]."
    },
    197: {
        "traditionalWording": "Help load burden on person or animal.",
        "scholarlyNote": "Prevents cruelty and shows human solidarity. [Rambam], [Rashi]."
    },
    198: {
        "traditionalWording": "Help unload burden from person or animal.",
        "scholarlyNote": "Overrides property rights when suffering involved. [Rambam], [Gemara]."
    },
    199: {
        "traditionalWording": "Give accurate weights and measures.",
        "scholarlyNote": "Foundation of honest commerce. [Rambam], [Philo]."
    },
    200: {
        "traditionalWording": "Honor father and mother.",
        "scholarlyNote": "Reciprocal divine honor; foundational to society. [Rambam], [Philo]."
    },
    201: {
        "traditionalWording": "Fear father and mother.",
        "scholarlyNote": "Reverence distinct from honor; inner attitude. [Rambam], [Talmud]."
    },
    202: {
        "traditionalWording": "Be fruitful and multiply.",
        "scholarlyNote": "First divine command; participation in creation. [Rambam], [Genesis Rabbah]."
    },
    203: {
        "traditionalWording": "Marry through kiddushin (betrothal).",
        "scholarlyNote": "Sanctification distinguishing marriage from other unions. [Rambam], [Talmud]."
    },
    204: {
        "traditionalWording": "Groom rejoice with bride one year.",
        "scholarlyNote": "Establishes strong marital foundation. [Rambam], [Rashi]."
    },
    205: {
        "traditionalWording": "Circumcise male children on eighth day.",
        "scholarlyNote": "Covenant sign linking individual to Abraham. [Rambam], [Philo]."
    },
    206: {
        "traditionalWording": "Perform levirate marriage or chalitzah.",
        "scholarlyNote": "Preserves deceased brother's name and lineage. [Rambam], [Talmud]."
    },
    207: {
        "traditionalWording": "Rapist must marry victim if she agrees.",
        "scholarlyNote": "Ancient provision for woman's protection and support. [Rambam], [Talmud]."
    },
    208: {
        "traditionalWording": "Seducer pay fine and marry if woman's father agrees.",
        "scholarlyNote": "Compensation for damaged reputation. [Rambam], [Exodus commentary]."
    },
    209: {
        "traditionalWording": "Beautiful captive must observe mourning month.",
        "scholarlyNote": "Humanizes war; allows psychological transition. [Rambam], [Sifre]."
    },
    210: {
        "traditionalWording": "Divorce by giving written get (bill of divorce).",
        "scholarlyNote": "Formalized process protecting both parties. [Rambam], [Talmud]."
    },
    211: {
        "traditionalWording": "Test suspected adulteress with bitter water.",
        "scholarlyNote": "Divine trial resolving marriage disputes. [Rambam], [Mishnah Sotah]."
    },
    212: {
        "traditionalWording": "Do not have relations with mother.",
        "scholarlyNote": "Fundamental incest prohibition. [Rambam], [Sifra]."
    },
    213: {
        "traditionalWording": "Do not have relations with father's wife.",
        "scholarlyNote": "Protects paternal authority structure. [Rambam], [Talmud]."
    },
    214: {
        "traditionalWording": "Do not have relations with sister.",
        "scholarlyNote": "Sibling boundary regardless of parentage. [Rambam], [Sifra]."
    },
    215: {
        "traditionalWording": "Do not have relations with father's sister.",
        "scholarlyNote": "Extends incest laws to paternal relatives. [Rambam], [Leviticus commentary]."
    },
    216: {
        "traditionalWording": "Do not have relations with mother's sister.",
        "scholarlyNote": "Extends incest laws to maternal relatives. [Rambam], [Sifra]."
    },
    217: {
        "traditionalWording": "Do not have relations with son's wife.",
        "scholarlyNote": "Protects generational boundaries. [Rambam], [Talmud]."
    },
    218: {
        "traditionalWording": "Do not have relations with brother's wife.",
        "scholarlyNote": "Exception only for levirate marriage. [Rambam], [Sifra]."
    },
    219: {
        "traditionalWording": "Do not have relations with wife and her daughter.",
        "scholarlyNote": "Prevents household conflict and corruption. [Rambam], [Leviticus commentary]."
    },
    220: {
        "traditionalWording": "Do not have relations with animals.",
        "scholarlyNote": "Maintains human dignity and natural order. [Rambam], [Philo]."
    },
    221: {
        "traditionalWording": "Men do not wear women's clothing.",
        "scholarlyNote": "Preserves gender distinctions in society. [Rambam], [Talmud]."
    },
    222: {
        "traditionalWording": "Women do not wear men's clothing.",
        "scholarlyNote": "Maintains social order through dress codes. [Rambam], [Sifre]."
    },
    223: {
        "traditionalWording": "Men do not shave with razor.",
        "scholarlyNote": "Distinguishes from pagan mourning practices. [Rambam], [Rashi]."
    },
    224: {
        "traditionalWording": "High priest marries virgin.",
        "scholarlyNote": "Highest purity standard for Temple leadership. [Rambam], [Sifra]."
    },
    225: {
        "traditionalWording": "High priest does not marry widow, divorcee, prostitute.",
        "scholarlyNote": "Maintains sanctity required for Temple service. [Rambam], [Leviticus commentary]."
    },
    226: {
        "traditionalWording": "Ordinary priest does not marry prostitute, divorcee.",
        "scholarlyNote": "Priestly purity extends to marriage choices. [Rambam], [Talmud]."
    },
    227: {
        "traditionalWording": "Priests do not become ritually impure from corpses.",
        "scholarlyNote": "Maintains priestly purity for Temple service. [Rambam], [Sifra]."
    },
    228: {
        "traditionalWording": "High priest never becomes ritually impure.",
        "scholarlyNote": "Absolute purity requirement for spiritual leadership. [Rambam], [Leviticus commentary]."
    },
    229: {
        "traditionalWording": "High priest does not enter place with corpse.",
        "scholarlyNote": "Highest level of ritual purity maintained. [Rambam], [Talmud]."
    },
    230: {
        "traditionalWording": "Tribe of Levi receives no territorial inheritance.",
        "scholarlyNote": "Spiritual service replaces material possession. [Rambam], [Deuteronomy commentary]."
    },
    231: {
        "traditionalWording": "Tribe of Levi takes no share in battle spoils.",
        "scholarlyNote": "Focus on spiritual rather than material rewards. [Rambam], [Sifre]."
    },
    232: {
        "traditionalWording": "Set aside cities of refuge for accidental killers.",
        "scholarlyNote": "Justice system protecting unintentional homicide. [Rambam], [Talmud]."
    },
    233: {
        "traditionalWording": "Establish courts in every city and region.",
        "scholarlyNote": "Local justice ensures accessible legal system. [Rambam], [Sifre]."
    },
    234: {
        "traditionalWording": "Appoint judges and officers.",
        "scholarlyNote": "Structured authority for maintaining social order. [Rambam], [Deuteronomy commentary]."
    },
    235: {
        "traditionalWording": "Equal justice for all people.",
        "scholarlyNote": "Fundamental principle of biblical jurisprudence. [Rambam], [Philo]."
    },
    236: {
        "traditionalWording": "Witnesses must testify truthfully in court.",
        "scholarlyNote": "Truth-seeking foundation of legal system. [Rambam], [Talmud]."
    }
}

def combine_scholarly_notes(new_note, existing_note):
    """Combine new scholarly note with existing note using differentiation markers."""
    if existing_note and existing_note.strip():
        return f"**Scholarly Analysis**: {new_note} | **Additional Context**: {existing_note}"
    else:
        return f"**Scholarly Analysis**: {new_note}"

def process_batch():
    """Process the batch of mitzvot with both traditional wording and scholarly notes."""
    print("=== Processing Mitzvot 187-236 (Both Fields) ===")
    
    updated_count = 0
    
    for number, data in MITZVOT_187_TO_236_CORRECTED.items():
        # Find existing mitzvah
        existing = db.mitzvot.find_one({"number": number})
        
        if not existing:
            print(f"⚠️  Mitzvah {number} not found in database")
            continue
        
        # Get existing scholarly note for combination
        existing_scholarly = existing.get("scholarlyNote", "")
        
        # Combine notes with differentiation
        combined_note = combine_scholarly_notes(data["scholarlyNote"], existing_scholarly)
        
        # Update both fields
        update_data = {
            "traditionalWording": data["traditionalWording"],
            "scholarlyNote": combined_note,
            "updated": datetime.now(timezone.utc)
        }
        
        # Perform update
        result = db.mitzvot.update_one(
            {"number": number},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"   Updated {updated_count}/50...")
    
    print(f"\n✅ Batch Complete: {updated_count} mitzvot (187-236) with BOTH fields")
    
    # Verification check
    print(f"\n🔍 Verification Check:")
    sample_numbers = [187, 200, 220, 236]
    
    for num in sample_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            traditional = mitzvah.get("traditionalWording", "")
            scholarly = mitzvah.get("scholarlyNote", "")
            
            # Check both fields exist and are properly formatted
            has_traditional = bool(traditional and traditional.strip())
            has_scholarly = bool(scholarly and "**Scholarly Analysis**" in scholarly)
            
            if has_traditional and has_scholarly:
                print(f"✅ Mitzvah {num}: Both fields correct")
            else:
                print(f"❌ Mitzvah {num}: Missing fields - Traditional: {has_traditional}, Scholarly: {has_scholarly}")
    
    # Progress summary
    print(f"\n📊 Overall Progress: 236/613 (38.5%) complete")
    print(f"Remaining: 377 mitzvot")

if __name__ == "__main__":
    process_batch()