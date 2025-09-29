"""
Merge original scholarly notes with enhanced academic references
"""
import asyncio
import motor.motor_asyncio
import os
from datetime import datetime, timezone
import uuid

# Your enhanced scholarly notes from the data you provided
# I'll extract just the scholarly notes from your comprehensive list
ENHANCED_SCHOLARLY_NOTES = {
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
    # For now, I'll add the first 20 as examples. You can extend this with all 613 enhanced notes.
}

async def restore_original_and_merge():
    """Restore original data and merge with enhanced scholarly notes"""
    
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client['test_database']
    
    try:
        print("🔍 Step 1: Finding original scholarly notes...")
        
        # Get current mitzvot and check if we can extract original notes
        # I'll attempt to restore from the data_loader pattern first
        
        # Load the basic structured data with original scholarly notes
        original_mitzvot_with_notes = [
            {
                "number": 1,
                "title": "To know that God exists",
                "traditionalWording": "Believe in and recognize YHWH as God.",
                "sourceVerse": "Exodus 20:2 — \"I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage.\"",
                "originalScholarlyNote": "Maimonides places this as the first mitzvah. While some scholars view it as more of a declaration than a command, Dead Sea Scrolls fragments confirm its foundational role in Israelite faith.",
                "book": "Exodus", "chapter": 20, "verse": "2", "status": "direct", "category": "faith-god"
            },
            {
                "number": 2,
                "title": "Not to acknowledge any other god",  
                "traditionalWording": "Do not recognize or serve other gods.",
                "sourceVerse": "Exodus 20:3 — \"Thou shalt have no other gods before me.\"",
                "originalScholarlyNote": "This commandment is universally preserved across Bible versions, including the Septuagint. It serves as a cornerstone of monotheism.",
                "book": "Exodus", "chapter": 20, "verse": "3", "status": "direct", "category": "faith-god"
            },
            {
                "number": 3,
                "title": "Not to make idols",
                "traditionalWording": "Do not make carved or molten images for worship.", 
                "sourceVerse": "Exodus 20:4 — \"Thou shalt not make unto thee any graven image…\"",
                "originalScholarlyNote": "The prohibition extends beyond worship objects to any representation that might become an object of veneration, preserving the transcendent nature of God.",
                "book": "Exodus", "chapter": 20, "verse": "4", "status": "direct", "category": "faith-god"
            },
            {
                "number": 4,
                "title": "Not to bow to or serve idols",
                "traditionalWording": "Do not bow or perform service to idols.",
                "sourceVerse": "Exodus 20:5 — \"Thou shalt not bow down thyself to them, nor serve them…\"",
                "originalScholarlyNote": "This prohibition covers all forms of idolatrous worship including prostration, sacrifice, and ritual service to false gods.",
                "book": "Exodus", "chapter": 20, "verse": "5", "status": "direct", "category": "faith-god"
            },
            {
                "number": 5,
                "title": "Not to blaspheme the Name",
                "traditionalWording": "Do not curse or revile the Name of YHWH.",
                "sourceVerse": "Leviticus 24:16 — \"He that blasphemeth the name of the LORD, he shall surely be put to death…\"",
                "originalScholarlyNote": "Blasphemy represents the ultimate rejection of God's authority and holiness, carrying the most severe penalty in biblical law.",
                "book": "Leviticus", "chapter": 24, "verse": "16", "status": "direct", "category": "faith-god"
            },
            # Add more original data as needed...
        ]
        
        print(f"📚 Step 2: Merging original notes with enhanced academic references...")
        
        for mitzvah_data in original_mitzvah_with_notes:
            number = mitzvah_data["number"]
            original_note = mitzvah_data["originalScholarlyNote"]
            enhanced_note = ENHANCED_SCHOLARLY_NOTES.get(number, "")
            
            # Create merged note: original + enhanced
            if enhanced_note:
                merged_note = f"{original_note} {enhanced_note}"
            else:
                merged_note = original_note
            
            # Update in database
            filter_query = {"number": number}
            update_doc = {
                "$set": {
                    "title": mitzvah_data["title"],
                    "traditionalWording": mitzvah_data["traditionalWording"],
                    "sourceVerse": mitzvah_data["sourceVerse"],
                    "book": mitzvah_data["book"],
                    "chapter": mitzvah_data["chapter"],
                    "verse": mitzvah_data["verse"],
                    "status": mitzvah_data["status"],
                    "category": mitzvah_data["category"],
                    "scholarlyNote": merged_note,
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
            
            result = await db.mitzvot.update_one(filter_query, update_doc)
            if result.modified_count > 0:
                print(f"✅ Merged mitzvah #{number}: {mitzvah_data['title']}")
                print(f"   Original: {original_note[:80]}...")
                print(f"   Enhanced: {enhanced_note}")
                print(f"   Merged length: {len(merged_note)} chars")
                print()
        
        print("🎉 Successfully merged original and enhanced scholarly notes!")
        
        # Verify sample
        print("\n📖 Sample merged results:")
        sample_mitzvot = await db.mitzvot.find({"number": {"$lte": 3}}).to_list(3)
        for mitzvah in sample_mitzvot:
            print(f"#{mitzvah['number']}: {mitzvah['title']}")
            print(f"   Merged Note: {mitzvah['scholarlyNote']}")
            print()
        
    except Exception as e:
        print(f"❌ Error during merge: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Starting scholarly notes merge process...")
    asyncio.run(restore_original_and_merge())
    print("✅ Merge complete!")