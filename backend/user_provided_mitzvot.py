"""
User-provided enhanced mitzvot data with complete scholarly content
This contains the actual enhanced scholarly data provided by the user
"""
import asyncio
import motor.motor_asyncio
import os
from datetime import datetime, timezone
import uuid

# The actual enhanced mitzvot data provided by the user - first 50 as examples
USER_ENHANCED_MITZVOT = [
    {
        "number": 1,
        "title": "To know that God exists",
        "traditionalWording": "Believe in and recognize YHWH as God.",
        "sourceVerse": "Exodus 20:2 — \"I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage.\"",
        "book": "Exodus", "chapter": 20, "verse": "2",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Often treated as the first positive command; some read it as a declaration rather than a command. [Rambam], [Ramban].",
        "keywords": ["God", "believe", "recognize", "YHWH", "faith", "existence"]
    },
    {
        "number": 2,
        "title": "Not to acknowledge any other god",
        "traditionalWording": "Do not recognize or serve other gods.",
        "sourceVerse": "Exodus 20:3 — \"Thou shalt have no other gods before me.\"",
        "book": "Exodus", "chapter": 20, "verse": "3",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Establishes exclusive covenant loyalty; foundational to later anti-idolatry laws. [Rambam], [Sifre Deut.].",
        "keywords": ["gods", "idolatry", "worship", "exclusive", "loyalty"]
    },
    {
        "number": 3,
        "title": "Not to make idols",
        "traditionalWording": "Do not make carved or molten images for worship.",
        "sourceVerse": "Exodus 20:4 — \"Thou shalt not make unto thee any graven image…\"",
        "book": "Exodus", "chapter": 20, "verse": "4",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Scope debated—art in general vs. worship images; context supports cultic prohibition. [Ibn Ezra], [Rashi].",
        "keywords": ["idols", "images", "graven", "worship", "art"]
    },
    {
        "number": 4,
        "title": "Not to bow to or serve idols",
        "traditionalWording": "Do not bow or perform service to idols.",
        "sourceVerse": "Exodus 20:5 — \"Thou shalt not bow down thyself to them, nor serve them…\"",
        "book": "Exodus", "chapter": 20, "verse": "5",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Encompasses ritual acts like sacrifice, incense, libations. [Rambam], [Sifra Lev.].",
        "keywords": ["bow", "serve", "idols", "worship", "ritual", "sacrifice"]
    },
    {
        "number": 5,
        "title": "Not to blaspheme the Name",
        "traditionalWording": "Do not curse or revile the Name of YHWH.",
        "sourceVerse": "Leviticus 24:16 — \"He that blasphemeth the name of the LORD, he shall surely be put to death…\"",
        "book": "Leviticus", "chapter": 24, "verse": "16",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Distinguished from careless oaths; formal reviling of the Name. [Mishnah Sanh.], [Rambam].",
        "keywords": ["blaspheme", "curse", "Name", "YHWH", "revile"]
    },
    {
        "number": 6,
        "title": "To love God",
        "traditionalWording": "Love YHWH with all heart, soul, might.",
        "sourceVerse": "Deuteronomy 6:5 — \"And thou shalt love the LORD thy God…\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "5",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Expressed through obedience and devotion; central to Shema. [Sifre Deut.], [Rambam].",
        "keywords": ["love", "God", "heart", "soul", "devotion", "Shema"]
    },
    {
        "number": 7,
        "title": "To fear (revere) God",
        "traditionalWording": "Live in reverent awe of YHWH.",
        "sourceVerse": "Deuteronomy 6:13 — \"Thou shalt fear the LORD thy God, and serve him…\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "13",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Reverence motivates faithful service and avoidance of sin. [Rambam], [Ramban].",
        "keywords": ["fear", "revere", "awe", "serve", "reverence"]
    },
    {
        "number": 8,
        "title": "To serve God",
        "traditionalWording": "Serve YHWH (worship/prayer/obedience).",
        "sourceVerse": "Exodus 23:25 — \"And ye shall serve the LORD your God…\"",
        "book": "Exodus", "chapter": 23, "verse": "25",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Service includes prayer (avodah shebalev) in later rabbinic framing. [Taanit 2a], [Rambam].",
        "keywords": ["serve", "worship", "prayer", "obedience", "avodah"]
    },
    {
        "number": 9,
        "title": "To cleave to God",
        "traditionalWording": "Cling to YHWH.",
        "sourceVerse": "Deuteronomy 10:20 — \"…him shalt thou serve, and to him shalt thou cleave…\"",
        "book": "Deuteronomy", "chapter": 10, "verse": "20",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Interpreted as emulating God's ways and attaching to His Torah/servants. [Sifre Deut.], [Rambam].",
        "keywords": ["cleave", "cling", "attach", "emulate", "Torah"]
    },
    {
        "number": 10,
        "title": "To swear by His Name truthfully",
        "traditionalWording": "Swear only by YHWH, truthfully.",
        "sourceVerse": "Deuteronomy 10:20 — \"…and swear by his name.\"",
        "book": "Deuteronomy", "chapter": 10, "verse": "20",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Permits oaths in God's Name when true and necessary; false oaths condemned. [Rambam], [Sefer HaChinuch].",
        "keywords": ["swear", "oath", "truthfully", "Name", "vow"]
    },
    {
        "number": 11,
        "title": "Not to profane the Name; to sanctify it",
        "traditionalWording": "Do not profane; live to sanctify His Name.",
        "sourceVerse": "Leviticus 22:32 — \"Neither shall ye profane my holy name; but I will be hallowed among the children of Israel.\"",
        "book": "Leviticus", "chapter": 22, "verse": "32",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Kiddush Hashem vs. Chillul Hashem as ethical-religious ideals. [Rambam], [Sifra Emor].",
        "keywords": ["profane", "sanctify", "Name", "hallow", "Kiddush"]
    },
    {
        "number": 12,
        "title": "Not to test God",
        "traditionalWording": "Do not put YHWH to the test.",
        "sourceVerse": "Deuteronomy 6:16 — \"Ye shall not tempt the LORD your God, as ye tempted him in Massah.\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "16",
        "status": "direct", "category": "faith-god",
        "scholarlyNote": "Prohibits demanding signs or doubting His faithfulness. [Ramban], [Sifre Deut.].",
        "keywords": ["test", "tempt", "doubt", "faith", "signs"]
    },
    {
        "number": 13,
        "title": "To bind tefillin on the arm",
        "traditionalWording": "Bind words as a sign on your arm.",
        "sourceVerse": "Deuteronomy 6:8 — \"And thou shalt bind them for a sign upon thine hand…\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "8",
        "status": "direct", "category": "torah-study",
        "scholarlyNote": "Literal vs metaphorical interpretation debated; practice standardized rabbinically. [Rambam], [Rashi].",
        "keywords": ["tefillin", "bind", "arm", "sign", "hand"]
    },
    {
        "number": 14,
        "title": "To place tefillin on the head",
        "traditionalWording": "Bind words between your eyes.",
        "sourceVerse": "Deuteronomy 6:8 — \"…and they shall be as frontlets between thine eyes.\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "8",
        "status": "direct", "category": "torah-study",
        "scholarlyNote": "Placement, compartments, and texts regulated by tradition. [Rambam], [Sefer HaChinuch].",
        "keywords": ["tefillin", "head", "frontlets", "eyes", "phylacteries"]
    },
    {
        "number": 15,
        "title": "To affix a mezuzah",
        "traditionalWording": "Affix mezuzah to doorposts.",
        "sourceVerse": "Deuteronomy 6:9 — \"And thou shalt write them upon the posts of thy house, and on thy gates.\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "9",
        "status": "direct", "category": "torah-study",
        "scholarlyNote": "Physical act explicitly commanded; scroll text/content standardized later. [Rambam], [Rashi].",
        "keywords": ["mezuzah", "doorpost", "write", "house", "gates"]
    },
    {
        "number": 16,
        "title": "To write a Torah scroll",
        "traditionalWording": "Every man should write a Sefer Torah.",
        "sourceVerse": "Deuteronomy 31:19 — \"Now therefore write ye this song for you…\"",
        "book": "Deuteronomy", "chapter": 31, "verse": "19",
        "status": "indirect", "category": "torah-study",
        "scholarlyNote": "Verse addresses the \"Song of Moses\"; rabbinic law expands to a full Torah scroll. [Rambam], [Ramban].",
        "keywords": ["Torah", "scroll", "write", "song", "Sefer"]
    },
    {
        "number": 17,
        "title": "To study and teach Torah",
        "traditionalWording": "Teach these words diligently to your children.",
        "sourceVerse": "Deuteronomy 6:7 — \"And thou shalt teach them diligently unto thy children…\"",
        "book": "Deuteronomy", "chapter": 6, "verse": "7",
        "status": "direct", "category": "torah-study",
        "scholarlyNote": "Lifelong obligation of learning/transmission; basis of communal education. [Sifre Deut.], [Rambam].",
        "keywords": ["study", "teach", "Torah", "children", "education"]
    },
    {
        "number": 18,
        "title": "Not to add to the commandments",
        "traditionalWording": "Do not add to the Torah.",
        "sourceVerse": "Deuteronomy 4:2 — \"Ye shall not add unto the word which I command you…\"",
        "book": "Deuteronomy", "chapter": 4, "verse": "2",
        "status": "direct", "category": "torah-study",
        "scholarlyNote": "Guards integrity of Torah; debated vis-à-vis protective \"fences.\" [Rambam], [Ramban].",
        "keywords": ["add", "commandments", "Torah", "integrity", "word"]
    },
    {
        "number": 19,
        "title": "Not to subtract from the commandments",
        "traditionalWording": "Do not diminish any command.",
        "sourceVerse": "Deuteronomy 4:2 — \"…neither shall ye diminish ought from it.\"",
        "book": "Deuteronomy", "chapter": 4, "verse": "2",
        "status": "direct", "category": "torah-study",
        "scholarlyNote": "Forbids erasing or loosening Torah law. [Rambam], [Sefer HaChinuch].",
        "keywords": ["subtract", "diminish", "commandments", "Torah", "law"]
    },
    {
        "number": 20,
        "title": "To build a sanctuary for God",
        "traditionalWording": "Make a sanctuary for YHWH.",
        "sourceVerse": "Exodus 25:8 — \"And let them make me a sanctuary; that I may dwell among them.\"",
        "book": "Exodus", "chapter": 25, "verse": "8",
        "status": "direct", "category": "temple-worship",
        "scholarlyNote": "Fulfilled in Tabernacle/Temple; later hopes for restoration. [Rambam], [Ramban].",
        "keywords": ["sanctuary", "build", "Temple", "dwell", "holy"]
    }
]

async def load_user_enhanced_data():
    """Load the first 20 user-provided enhanced mitzvot as examples"""
    
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client['test_database']
    
    try:
        print("🔥 Updating first 20 mitzvot with user-provided enhanced content...")
        
        for mitzvah_data in USER_ENHANCED_MITZVOT:
            # Update the existing mitzvah with enhanced content
            filter_query = {"number": mitzvah_data["number"]}
            
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
                    "scholarlyNote": mitzvah_data["scholarlyNote"],
                    "keywords": mitzvah_data["keywords"],
                    "updatedAt": datetime.now(timezone.utc)
                }
            }
            
            result = await db.mitzvot.update_one(filter_query, update_doc)
            if result.modified_count > 0:
                print(f"✅ Updated mitzvah #{mitzvah_data['number']}: {mitzvah_data['title']}")
            else:
                print(f"⚠️ Failed to update mitzvah #{mitzvah_data['number']}")
        
        print(f"\n📖 Sample of enhanced mitzvot:")
        sample_mitzvot = await db.mitzvot.find({"number": {"$lte": 3}}).to_list(3)
        for mitzvah in sample_mitzvot:
            print(f"#{mitzvah['number']}: {mitzvah['title']}")
            print(f"   📜 Traditional: {mitzvah['traditionalWording']}")
            print(f"   📖 Source: {mitzvah['sourceVerse']}")
            print(f"   🎓 Scholarly: {mitzvah['scholarlyNote']}")
            print()
        
    except Exception as e:
        print(f"❌ Error updating mitzvot: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Loading user-provided enhanced mitzvot data...")
    asyncio.run(load_user_enhanced_data())
    print("✅ Enhanced mitzvot update complete!")