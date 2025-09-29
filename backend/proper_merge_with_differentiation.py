"""
Proper merge of original and enhanced scholarly notes with clear differentiation
"""
import asyncio
import motor.motor_asyncio
import os
from datetime import datetime, timezone
import uuid

# Original scholarly notes (from the working system before changes)
ORIGINAL_SCHOLARLY_NOTES = {
    1: "Maimonides places this as the first mitzvah. While some scholars view it as more of a declaration than a command, Dead Sea Scrolls fragments confirm its foundational role in Israelite faith.",
    2: "This commandment is universally preserved across Bible versions, including the Septuagint. It serves as a cornerstone of monotheism.",
    3: "The prohibition extends beyond worship objects to any representation that might become an object of veneration, preserving the transcendent nature of God.",
    4: "This prohibition covers all forms of idolatrous worship including prostration, sacrifice, and ritual service to false gods.",
    5: "Blasphemy represents the ultimate rejection of God's authority and holiness, carrying the most severe penalty in biblical law.",
    6: "This commandment encompasses both emotional love and practical obedience, forming the foundation of Jewish religious life.",
    7: "Fear of God represents reverent awe rather than terror, motivating ethical behavior and spiritual growth.",
    8: "Divine service encompasses both ritual worship and ethical living, extending beyond Temple sacrifices to daily conduct.",
    9: "Cleaving to God involves constant awareness of His presence and alignment with His will in all aspects of life.",
    10: "Sacred oaths in God's name were permitted for solemn occasions but carried serious responsibility for truthfulness.",
    11: "Sanctification of God's name encompasses both public behavior that honors God and willingness to sacrifice for faith.",
    12: "Testing God through demands for miraculous signs reflects lack of faith and proper reverence.",
    13: "Tefillin serve as physical reminders of God's commandments, worn during morning prayers as symbols of dedication.",
    14: "Head tefillin complement arm tefillin, symbolizing the binding of mind and heart to God's service.",
    15: "Mezuzah on doorposts serves as a constant reminder of God's presence and commandments in Jewish homes.",
    16: "Writing Torah scrolls preserves the sacred text and connects each generation to the divine revelation.",
    17: "Torah study is both a personal obligation and communal responsibility, ensuring transmission of Jewish knowledge.",
    18: "Prohibition against adding to Torah preserves the integrity and authenticity of divine revelation.",
    19: "Prohibition against subtracting from Torah maintains the completeness of God's commandments.",
    20: "Building a sanctuary provides a focal point for divine service and communal worship."
}

# Enhanced scholarly notes (your academic references)
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
    20: "Fulfilled in Tabernacle/Temple; later hopes for restoration. [Rambam], [Ramban]."
}

# Complete mitzvah data with proper structure
COMPLETE_MITZVOT_DATA = [
    {"number": 1, "title": "To know that God exists", "traditionalWording": "Believe in and recognize YHWH as God.", "sourceVerse": "Exodus 20:2 — \"I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage.\"", "book": "Exodus", "chapter": 20, "verse": "2", "status": "direct", "category": "faith-god"},
    {"number": 2, "title": "Not to acknowledge any other god", "traditionalWording": "Do not recognize or serve other gods.", "sourceVerse": "Exodus 20:3 — \"Thou shalt have no other gods before me.\"", "book": "Exodus", "chapter": 20, "verse": "3", "status": "direct", "category": "faith-god"},
    {"number": 3, "title": "Not to make idols", "traditionalWording": "Do not make carved or molten images for worship.", "sourceVerse": "Exodus 20:4 — \"Thou shalt not make unto thee any graven image…\"", "book": "Exodus", "chapter": 20, "verse": "4", "status": "direct", "category": "faith-god"},
    {"number": 4, "title": "Not to bow to or serve idols", "traditionalWording": "Do not bow or perform service to idols.", "sourceVerse": "Exodus 20:5 — \"Thou shalt not bow down thyself to them, nor serve them…\"", "book": "Exodus", "chapter": 20, "verse": "5", "status": "direct", "category": "faith-god"},
    {"number": 5, "title": "Not to blaspheme the Name", "traditionalWording": "Do not curse or revile the Name of YHWH.", "sourceVerse": "Leviticus 24:16 — \"He that blasphemeth the name of the LORD, he shall surely be put to death…\"", "book": "Leviticus", "chapter": 24, "verse": "16", "status": "direct", "category": "faith-god"},
    {"number": 6, "title": "To love God", "traditionalWording": "Love YHWH with all heart, soul, might.", "sourceVerse": "Deuteronomy 6:5 — \"And thou shalt love the LORD thy God…\"", "book": "Deuteronomy", "chapter": 6, "verse": "5", "status": "direct", "category": "faith-god"},
    {"number": 7, "title": "To fear (revere) God", "traditionalWording": "Live in reverent awe of YHWH.", "sourceVerse": "Deuteronomy 6:13 — \"Thou shalt fear the LORD thy God, and serve him…\"", "book": "Deuteronomy", "chapter": 6, "verse": "13", "status": "direct", "category": "faith-god"},
    {"number": 8, "title": "To serve God", "traditionalWording": "Serve YHWH (worship/prayer/obedience).", "sourceVerse": "Exodus 23:25 — \"And ye shall serve the LORD your God…\"", "book": "Exodus", "chapter": 23, "verse": "25", "status": "direct", "category": "faith-god"},
    {"number": 9, "title": "To cleave to God", "traditionalWording": "Cling to YHWH.", "sourceVerse": "Deuteronomy 10:20 — \"…him shalt thou serve, and to him shalt thou cleave…\"", "book": "Deuteronomy", "chapter": 10, "verse": "20", "status": "direct", "category": "faith-god"},
    {"number": 10, "title": "To swear by His Name truthfully", "traditionalWording": "Swear only by YHWH, truthfully.", "sourceVerse": "Deuteronomy 10:20 — \"…and swear by his name.\"", "book": "Deuteronomy", "chapter": 10, "verse": "20", "status": "direct", "category": "faith-god"},
    {"number": 11, "title": "Not to profane the Name; to sanctify it", "traditionalWording": "Do not profane; live to sanctify His Name.", "sourceVerse": "Leviticus 22:32 — \"Neither shall ye profane my holy name; but I will be hallowed among the children of Israel.\"", "book": "Leviticus", "chapter": 22, "verse": "32", "status": "direct", "category": "faith-god"},
    {"number": 12, "title": "Not to test God", "traditionalWording": "Do not put YHWH to the test.", "sourceVerse": "Deuteronomy 6:16 — \"Ye shall not tempt the LORD your God, as ye tempted him in Massah.\"", "book": "Deuteronomy", "chapter": 6, "verse": "16", "status": "direct", "category": "faith-god"},
    {"number": 13, "title": "To bind tefillin on the arm", "traditionalWording": "Bind words as a sign on your arm.", "sourceVerse": "Deuteronomy 6:8 — \"And thou shalt bind them for a sign upon thine hand…\"", "book": "Deuteronomy", "chapter": 6, "verse": "8", "status": "direct", "category": "torah-study"},
    {"number": 14, "title": "To place tefillin on the head", "traditionalWording": "Bind words between your eyes.", "sourceVerse": "Deuteronomy 6:8 — \"…and they shall be as frontlets between thine eyes.\"", "book": "Deuteronomy", "chapter": 6, "verse": "8", "status": "direct", "category": "torah-study"},
    {"number": 15, "title": "To affix a mezuzah", "traditionalWording": "Affix mezuzah to doorposts.", "sourceVerse": "Deuteronomy 6:9 — \"And thou shalt write them upon the posts of thy house, and on thy gates.\"", "book": "Deuteronomy", "chapter": 6, "verse": "9", "status": "direct", "category": "torah-study"},
    {"number": 16, "title": "To write a Torah scroll", "traditionalWording": "Every man should write a Sefer Torah.", "sourceVerse": "Deuteronomy 31:19 — \"Now therefore write ye this song for you…\"", "book": "Deuteronomy", "chapter": 31, "verse": "19", "status": "indirect", "category": "torah-study"},
    {"number": 17, "title": "To study and teach Torah", "traditionalWording": "Teach these words diligently to your children.", "sourceVerse": "Deuteronomy 6:7 — \"And thou shalt teach them diligently unto thy children…\"", "book": "Deuteronomy", "chapter": 6, "verse": "7", "status": "direct", "category": "torah-study"},
    {"number": 18, "title": "Not to add to the commandments", "traditionalWording": "Do not add to the Torah.", "sourceVerse": "Deuteronomy 4:2 — \"Ye shall not add unto the word which I command you…\"", "book": "Deuteronomy", "chapter": 4, "verse": "2", "status": "direct", "category": "torah-study"},
    {"number": 19, "title": "Not to subtract from the commandments", "traditionalWording": "Do not diminish any command.", "sourceVerse": "Deuteronomy 4:2 — \"…neither shall ye diminish ought from it.\"", "book": "Deuteronomy", "chapter": 4, "verse": "2", "status": "direct", "category": "torah-study"},
    {"number": 20, "title": "To build a sanctuary for God", "traditionalWording": "Make a sanctuary for YHWH.", "sourceVerse": "Exodus 25:8 — \"And let them make me a sanctuary; that I may dwell among them.\"", "book": "Exodus", "chapter": 25, "verse": "8", "status": "direct", "category": "temple-worship"}
]

async def create_properly_differentiated_merge():
    """Create properly differentiated scholarly notes that preserve BOTH original and enhanced content"""
    
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client['test_database']
    
    try:
        print("🔄 Creating properly differentiated merge...")
        print("Format: [Original Analysis] + [Enhanced Academic References]")
        print("="*80)
        
        # Clear and reload with proper differentiated content
        await db.mitzvot.delete_many({})
        
        for mitzvah_data in COMPLETE_MITZVOT_DATA:
            number = mitzvah_data["number"]
            original_note = ORIGINAL_SCHOLARLY_NOTES.get(number, "")
            enhanced_note = ENHANCED_SCHOLARLY_NOTES.get(number, "")
            
            # Create DIFFERENTIATED scholarly note with clear separation
            if original_note and enhanced_note:
                # Format: Original content + separator + Enhanced academic analysis
                differentiated_note = f"{original_note} | Academic Analysis: {enhanced_note}"
            elif original_note:
                differentiated_note = original_note
            elif enhanced_note:
                differentiated_note = f"Academic Analysis: {enhanced_note}"
            else:
                differentiated_note = "Traditional observance and practice of this commandment."
            
            # Generate keywords
            keywords = [
                "mitzvah", str(number), mitzvah_data["category"].replace("-", " "),
                "biblical", "commandment", "Torah"
            ]
            
            # Create complete mitzvah document
            mitzvah_doc = {
                "id": str(uuid.uuid4()),
                "number": number,
                "title": mitzvah_data["title"],
                "traditionalWording": mitzvah_data["traditionalWording"],
                "sourceVerse": mitzvah_data["sourceVerse"],
                "book": mitzvah_data["book"],
                "chapter": mitzvah_data["chapter"], 
                "verse": mitzvah_data["verse"],
                "status": mitzvah_data["status"],
                "category": mitzvah_data["category"],
                "scholarlyNote": differentiated_note,
                "keywords": keywords,
                "createdAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
            
            await db.mitzvot.insert_one(mitzvah_doc)
            
            print(f"✅ MITZVAH #{number}: {mitzvah_data['title']}")
            print(f"📖 Original: {original_note[:60]}...")
            print(f"🎓 Enhanced: {enhanced_note}")
            print(f"🔗 Differentiated: {differentiated_note[:100]}...")
            print("-"*60)
        
        print(f"\n🎉 Successfully created {len(COMPLETE_MITZVOT_DATA)} properly differentiated mitzvot!")
        
        # Verify the differentiated format
        print("\n📖 Sample differentiated scholarly notes:")
        sample_mitzvot = await db.mitzvot.find({"number": {"$lte": 3}}).to_list(3)
        for mitzvah in sample_mitzvot:
            print(f"\n#{mitzvah['number']}: {mitzvah['title']}")
            print(f"Differentiated Note: {mitzvah['scholarlyNote']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Creating properly differentiated scholarly notes merge...")
    asyncio.run(create_properly_differentiated_merge())
    print("✅ Differentiated merge complete!")