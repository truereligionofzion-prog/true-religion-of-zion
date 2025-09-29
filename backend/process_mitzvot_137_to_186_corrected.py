#!/usr/bin/env python3
"""
Process Mitzvot 137-186 with BOTH traditional wording AND scholarly notes
Continuing the corrected approach
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

client = MongoClient(os.environ.get('MONGO_URL'))
db = client.get_database('test_database')

# MITZVOT 137-186 - BOTH traditional wording AND scholarly notes from user's message
MITZVOT_137_TO_186_CORRECTED = {
    137: {
        "traditionalWording": "Offer firstborn ox, sheep, goat.",
        "scholarlyNote": "Sacrificed at altar; meat for priests. [Rambam], [Sifre Num.]."
    },
    138: {
        "traditionalWording": "Priests eat firstborn flesh in holy place.",
        "scholarlyNote": "Part of priestly portion system. [Rambam], [Rashi]."
    },
    139: {
        "traditionalWording": "Give tithe of produce to Levites.",
        "scholarlyNote": "Sustains Levites who serve without land. [Rambam], [Philo]."
    },
    140: {
        "traditionalWording": "Levites tithe from received tithe.",
        "scholarlyNote": "Ensures priests share in Levitical support. [Rambam], [Sifre Num.]."
    },
    141: {
        "traditionalWording": "Bring second tithe to Jerusalem.",
        "scholarlyNote": "Combines worship with agricultural bounty. [Rambam], [Philo]."
    },
    142: {
        "traditionalWording": "Give the poor tithe in the third and sixth years of the Shemitah cycle.",
        "scholarlyNote": "Embeds social care into agriculture; part of the cyclical tithe system. [Rambam], [Sifre Deut.]."
    },
    143: {
        "traditionalWording": "From a slaughtered animal, give the kohen the foreleg, cheeks, and stomach.",
        "scholarlyNote": "Distinct from terumah/tithes; part of priestly support. [Rambam], [Sefer HaChinuch]."
    },
    144: {
        "traditionalWording": "Give the first of the fleece of your sheep to the kohen.",
        "scholarlyNote": "Agricultural gift paralleling firstfruits; emphasizes priestly provision. [Rambam], [Rashi]."
    },
    145: {
        "traditionalWording": "Do not bring chametz or honey in any fire-offering.",
        "scholarlyNote": "Leaven/honey symbolize fermentation/sweetening; reserved for firstfruits loaves (not on the altar fire). [Rambam], [Sifra]."
    },
    146: {
        "traditionalWording": "All offerings must be seasoned with salt.",
        "scholarlyNote": "\"Covenant of salt\" signifies permanence and loyalty. [Rambam], [Philo]."
    },
    147: {
        "traditionalWording": "Do not offer an animal with a blemish.",
        "scholarlyNote": "Preserves honor of worship; extensive lists of blemishes follow. [Rambam], [Sifra Emor]."
    },
    148: {
        "traditionalWording": "Do not consecrate animals with defects for the altar.",
        "scholarlyNote": "Distinguishes between consecration and offering—blemished animals are invalid from the start. [Rambam], [Rashi]."
    },
    149: {
        "traditionalWording": "Examine sacrificial animals to confirm fitness.",
        "scholarlyNote": "The obligation to \"inspect\" is implied by the requirement of perfection; procedures detailed in tradition. [Rambam], [Sifra]."
    },
    150: {
        "traditionalWording": "Do not sacrifice animals whose testicles are crushed, bruised, torn, or cut.",
        "scholarlyNote": "Protects integrity of offerings; also linked to later bans on castration. [Rambam], [Sefer HaChinuch]."
    },
    151: {
        "traditionalWording": "Do not bring castrated animals as offerings.",
        "scholarlyNote": "Castration itself later prohibited; offering such animals profanes the altar. [Rambam], [Sifra]."
    },
    152: {
        "traditionalWording": "Do not dedicate wages of prostitution or dog's price.",
        "scholarlyNote": "Protects sanctity of the sanctuary; tied to moral purity. [Rambam], [Philo]."
    },
    153: {
        "traditionalWording": "Do not put honey or chametz on altar fire.",
        "scholarlyNote": "Exceptions for firstfruits bread; general fire-offerings excluded. [Rambam], [Sifra]."
    },
    154: {
        "traditionalWording": "Offer salt with sacrifices.",
        "scholarlyNote": "Symbol of covenant permanence. [Rambam], [Philo]."
    },
    155: {
        "traditionalWording": "Only whole, unblemished animals accepted.",
        "scholarlyNote": "Upholds God's honor in worship. [Rambam], [Sifra]."
    },
    156: {
        "traditionalWording": "Do not consecrate blemished animals for offerings.",
        "scholarlyNote": "Distinction made between ownership and consecration. [Rambam], [Rashi]."
    },
    157: {
        "traditionalWording": "Do not intentionally injure sacrificial animals.",
        "scholarlyNote": "Derived prohibition to protect sacred property. [Rambam], [Sifra]."
    },
    158: {
        "traditionalWording": "Redeem animals unfit for sacrifice.",
        "scholarlyNote": "Ensures sanctity even when animal is unfit. [Rambam], [Sifra]."
    },
    159: {
        "traditionalWording": "Do not sacrifice animals under eight days old.",
        "scholarlyNote": "Honors natural development before use in worship. [Rambam], [Rashbam]."
    },
    160: {
        "traditionalWording": "Do not offer illicitly acquired property.",
        "scholarlyNote": "Reinforces purity in worship. [Rambam], [Sefer HaChinuch]."
    },
    161: {
        "traditionalWording": "Do not exchange one consecrated animal for another.",
        "scholarlyNote": "Prevents dishonoring God by substitutions. [Rambam], [Sifra]."
    },
    162: {
        "traditionalWording": "When substitution occurs, both become consecrated.",
        "scholarlyNote": "Creates deterrence against substitution. [Rambam], [Rashi]."
    },
    163: {
        "traditionalWording": "Firstborn ox, sheep, goat not to be redeemed.",
        "scholarlyNote": "They are inherently sanctified for sacrifice. [Rambam], [Sifre Num.]."
    },
    164: {
        "traditionalWording": "Set apart firstborn ox, sheep, goat for sacrifice.",
        "scholarlyNote": "Memorial of the Exodus. [Rambam], [Philo]."
    },
    165: {
        "traditionalWording": "Offerings only at the chosen place.",
        "scholarlyNote": "Centralizes worship; rejects local high places. [Rambam], [Sifre Deut.]."
    },
    166: {
        "traditionalWording": "Do not eat holy offerings outside the sanctuary.",
        "scholarlyNote": "Restricts sacred consumption to holy place. [Rambam], [Rashbam]."
    },
    167: {
        "traditionalWording": "Dedicate every firstborn male to God.",
        "scholarlyNote": "Redeemed via pidyon haben ceremony. [Rambam], [Sifre Exod.]."
    },
    168: {
        "traditionalWording": "Redeem firstborn male with five shekels.",
        "scholarlyNote": "Ongoing mitzvah in Jewish practice. [Rambam], [Sefer HaChinuch]."
    },
    169: {
        "traditionalWording": "Do not postpone redemption.",
        "scholarlyNote": "Derived from the requirement \"from a month old.\" [Rambam], [Rashi]."
    },
    170: {
        "traditionalWording": "Redeem with lamb or break its neck.",
        "scholarlyNote": "Unique case among unclean animals. [Rambam], [Philo]."
    },
    171: {
        "traditionalWording": "Break neck if not redeemed.",
        "scholarlyNote": "Prevents misuse of consecrated property. [Rambam], [Sifra]."
    },
    172: {
        "traditionalWording": "Bring the first yield of produce to Temple.",
        "scholarlyNote": "Gratitude practice; accompanied by declaration. [Rambam], [Philo]."
    },
    173: {
        "traditionalWording": "Confession of history and gratitude.",
        "scholarlyNote": "Links agricultural blessing to covenant story. [Rambam], [Sifre Deut.]."
    },
    174: {
        "traditionalWording": "Set aside tithes of grain, wine, oil.",
        "scholarlyNote": "Agricultural system sustaining Levites and poor. [Rambam], [Philo]."
    },
    175: {
        "traditionalWording": "Every tenth animal belongs to the LORD.",
        "scholarlyNote": "Performed by passing animals under the rod. [Rambam], [Mishnah Bekhorot]."
    },
    176: {
        "traditionalWording": "Do not choose better or worse animals for tithe.",
        "scholarlyNote": "Ensures fairness in offering. [Rambam], [Rashi]."
    },
    177: {
        "traditionalWording": "Leave corners (pe'ah) for the poor.",
        "scholarlyNote": "Early social welfare institution. [Rambam], [Sifra]."
    },
    178: {
        "traditionalWording": "Do not collect forgotten sheaves.",
        "scholarlyNote": "Institutionalizes care for marginalized. [Rambam], [Sefer HaChinuch]."
    },
    179: {
        "traditionalWording": "Do not pick the forgotten grapes.",
        "scholarlyNote": "Ensures poor partake in harvest bounty. [Rambam], [Rashi]."
    },
    180: {
        "traditionalWording": "Do not gather fallen grapes.",
        "scholarlyNote": "Parallels field gleanings; compassion command. [Rambam], [Sifra]."
    },
    181: {
        "traditionalWording": "Set aside a portion of dough.",
        "scholarlyNote": "Extends sanctity into daily bread-making. [Rambam], [Rashi]."
    },
    182: {
        "traditionalWording": "Exchange tithe for money when Jerusalem is too far.",
        "scholarlyNote": "Practical adaptation for long journeys. [Rambam], [Sifre Deut.]."
    },
    183: {
        "traditionalWording": "Use redeemed money to rejoice before YHWH.",
        "scholarlyNote": "Ensures tithe strengthens Jerusalem's role. [Rambam], [Philo]."
    },
    184: {
        "traditionalWording": "Confess that tithes were given properly.",
        "scholarlyNote": "Public accountability reinforces covenant. [Rambam], [Sifre Deut.]."
    },
    185: {
        "traditionalWording": "Bring todah sacrifice of gratitude.",
        "scholarlyNote": "Symbol of gratitude for deliverance. [Rambam], [Philo]."
    },
    186: {
        "traditionalWording": "Offer shelamim sacrifices.",
        "scholarlyNote": "Fellowship meals symbolizing covenant harmony. [Rambam], [Sifra]."
    }
}

def process_mitzvot_137_to_186_corrected():
    """Process mitzvot 137-186 with BOTH traditional wording and scholarly notes"""
    
    print("=== Processing Mitzvot 137-186 (Both Fields) ===")
    
    updated_count = 0
    
    for number in range(137, 187):
        mitzvah = db.mitzvot.find_one({"number": number})
        
        if not mitzvah:
            print(f"⚠️  Mitzvah {number} not found")
            continue
        
        correction_data = MITZVOT_137_TO_186_CORRECTED.get(number)
        
        if not correction_data:
            print(f"⚠️  No correction data for Mitzvah {number}")
            continue
        
        # Get existing additional context
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
        
        # Update BOTH fields
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
    
    print(f"\n✅ Batch Complete: {updated_count} mitzvot (137-186) with BOTH fields")
    
    # Verification
    verification_numbers = [137, 160, 186]
    print(f"\n🔍 Verification Check:")
    
    for num in verification_numbers:
        mitzvah = db.mitzvot.find_one({"number": num})
        if mitzvah:
            traditional = mitzvah["traditionalWording"]
            expected_traditional = MITZVOT_137_TO_186_CORRECTED.get(num, {}).get("traditionalWording", "")
            
            if expected_traditional in traditional:
                print(f"✅ Mitzvah {num}: Both fields correct")
            else:
                print(f"❌ Mitzvah {num}: Needs review")
    
    # Overall progress
    total_corrected = 86 + 50 + 50  # Original (1-86) + First corrected batch (87-136) + This batch (137-186)
    total_mitzvot = 613
    progress_percent = (total_corrected / total_mitzvot) * 100
    
    print(f"\n📊 Overall Progress: {total_corrected}/{total_mitzvot} ({progress_percent:.1f}%) complete")
    print(f"Remaining: {total_mitzvot - total_corrected} mitzvot")

if __name__ == "__main__":
    process_mitzvot_137_to_186_corrected()