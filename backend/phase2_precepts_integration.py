#!/usr/bin/env python3
"""
Phase 2: Precepts Integration for Biblical Study Suite
Processes and integrates the comprehensive precepts list into the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from uuid import uuid4
import re
from typing import List, Dict, Any

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

class PreceptsProcessor:
    def __init__(self):
        self.precepts_data = []
        self.verses_cross_reference = {}
        
    def parse_precepts_text(self, precepts_text: str) -> List[Dict[str, Any]]:
        """Parse the provided precepts text into structured data"""
        precepts = []
        current_precept = None
        
        lines = precepts_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a new precept title
            if not line.startswith(('Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 
                                  '1Chronicles', '2Chronicles', '1Kings', '2Kings', '1Samuel', 
                                  '2Samuel', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Isaiah', 
                                  'Jeremiah', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 
                                  'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 
                                  'Haggai', 'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 
                                  'John', 'Acts', 'Romans', '1Corinthians', '2Corinthians', 
                                  'Galatians', 'Ephesians', 'Philippians', 'Colossians', 
                                  '1Thessalonians', '2Thessalonians', '1Timothy', '2Timothy', 
                                  'Titus', 'Philemon', 'Hebrews', 'James', '1Peter', '2Peter', 
                                  '1John', '2John', '3John', 'Jude', 'Revelations',
                                  # Apocryphal books
                                  'Tobit', 'Judith', 'Wisdom of Solomon', 'Ecclesiasticus', 
                                  'Baruch', '1Maccabees', '2Maccabees', '1Esdras', '2Esdras',
                                  'Prayer of Manasseh', 'Epistle of Jeremiah', 'Bel and the Dragon',
                                  'Susanna', 'Esther (Greek)', 'Songs of Solomon')):
                # This is a new precept title
                if current_precept and current_precept.get('verses'):
                    precepts.append(current_precept)
                
                current_precept = {
                    'id': str(uuid4()),
                    'title': line,
                    'verses': [],
                    'topics': self._extract_topics(line),
                    'testament': 'mixed'  # Will be determined based on verses
                }
            
            elif current_precept and self._is_bible_reference(line):
                # This is a bible verse reference
                verse_ref = line
            
            elif current_precept and not self._is_bible_reference(line) and line:
                # This is verse text, associate with the last reference
                if len(current_precept['verses']) > 0:
                    current_precept['verses'][-1]['text'] = line
                else:
                    # Sometimes verse text comes before reference, create placeholder
                    current_precept['verses'].append({
                        'reference': 'Unknown',
                        'book': 'Unknown',
                        'chapter': 0,
                        'verse': 0,
                        'text': line
                    })
            
            elif self._is_bible_reference(line):
                # This is a standalone bible reference
                parsed_ref = self._parse_bible_reference(line)
                if current_precept:
                    current_precept['verses'].append(parsed_ref)
        
        # Add the last precept
        if current_precept and current_precept.get('verses'):
            precepts.append(current_precept)
            
        return precepts
    
    def _is_bible_reference(self, line: str) -> bool:
        """Check if line is a bible verse reference"""
        # Simple pattern to match Bible references like "Genesis 1:1"
        pattern = r'^[1-3]?[A-Za-z\s()]+\s+\d+:\d+$'
        return bool(re.match(pattern, line))
    
    def _parse_bible_reference(self, reference: str) -> Dict[str, Any]:
        """Parse a bible reference into structured components"""
        # Pattern to match references like "Genesis 1:1" or "1Corinthians 15:33"
        match = re.match(r'^([1-3]?[A-Za-z\s()]+?)\s+(\d+):(\d+)$', reference)
        
        if match:
            book = match.group(1).strip()
            chapter = int(match.group(2))
            verse = int(match.group(3))
            
            return {
                'reference': reference,
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'text': ''  # Will be filled in later
            }
        else:
            return {
                'reference': reference,
                'book': 'Unknown',
                'chapter': 0,
                'verse': 0,
                'text': ''
            }
    
    def _extract_topics(self, title: str) -> List[str]:
        """Extract topic keywords from precept title"""
        # Convert title to topics/keywords
        topics = [title.lower().replace(' ', '-')]
        
        # Add some common topic mappings
        topic_mappings = {
            'god': ['deity', 'divine', 'worship'],
            'law': ['commandment', 'legal', 'judicial'],
            'marriage': ['family', 'relationship'],
            'sabbath': ['rest', 'holy-day'],
            'sacrifice': ['offering', 'ritual', 'temple'],
            'sin': ['transgression', 'iniquity'],
            'prayer': ['worship', 'communication'],
            'love': ['relationship', 'emotion'],
            'anger': ['emotion', 'conduct'],
            'fear': ['emotion', 'reverence']
        }
        
        for key, additional_topics in topic_mappings.items():
            if key in title.lower():
                topics.extend(additional_topics)
                
        return list(set(topics))
    
    def _determine_testament(self, verses: List[Dict]) -> str:
        """Determine if precept is Old Testament, New Testament, or Mixed"""
        old_testament_books = {
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1Samuel', '2Samuel', '1Kings', '2Kings',
            '1Chronicles', '2Chronicles', 'Ezra', 'Nehemiah', 'Esther',
            'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Songs of Solomon',
            'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel',
            'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah',
            'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
            # Apocryphal/Deuterocanonical books
            'Tobit', 'Judith', 'Wisdom of Solomon', 'Ecclesiasticus', 'Baruch',
            '1Maccabees', '2Maccabees', '1Esdras', '2Esdras', 'Prayer of Manasseh'
        }
        
        has_old = any(verse['book'] in old_testament_books for verse in verses)
        has_new = any(verse['book'] not in old_testament_books for verse in verses)
        
        if has_old and has_new:
            return 'mixed'
        elif has_old:
            return 'old'
        else:
            return 'new'

    async def process_raw_precepts(self, raw_precepts_text: str):
        """Process the raw precepts text and store in database"""
        print("🔄 Processing precepts from provided text...")
        
        # Parse the provided precepts text
        precepts = []
        current_title = None
        current_verses = []
        current_ref = None
        
        lines = raw_precepts_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a bible reference pattern
            if re.match(r'^[1-3]?[A-Za-z\s()]+\s+\d+:\d+$', line):
                # This is a bible reference
                current_ref = line
                
            elif current_ref and not re.match(r'^[1-3]?[A-Za-z\s()]+\s+\d+:\d+$', line):
                # This is verse text following a reference
                parsed_ref = self._parse_bible_reference(current_ref)
                parsed_ref['text'] = line
                
                if current_title:
                    current_verses.append(parsed_ref)
                
                current_ref = None
                
            elif not re.match(r'^[1-3]?[A-Za-z\s()]+\s+\d+:\d+$', line) and len(line) > 3:
                # This might be a new precept title
                # Save previous precept if exists
                if current_title and current_verses:
                    precept = {
                        'id': str(uuid4()),
                        'title': current_title,
                        'verses': current_verses,
                        'topics': self._extract_topics(current_title),
                        'testament': self._determine_testament(current_verses),
                        'verse_count': len(current_verses)
                    }
                    precepts.append(precept)
                
                # Start new precept
                current_title = line
                current_verses = []
                current_ref = None
        
        # Don't forget the last precept
        if current_title and current_verses:
            precept = {
                'id': str(uuid4()),
                'title': current_title,
                'verses': current_verses,
                'topics': self._extract_topics(current_title),
                'testament': self._determine_testament(current_verses),
                'verse_count': len(current_verses)
            }
            precepts.append(precept)
        
        print(f"✅ Parsed {len(precepts)} precepts from text")
        
        # Apply YHWH/YHUH replacements to all text
        print("🔄 Applying YHWH/YHUH divine name replacements...")
        for precept in precepts:
            for verse in precept['verses']:
                verse['text'] = self._apply_divine_name_replacements(verse['text'])
        
        # Store in database
        print("🔄 Storing precepts in database...")
        if precepts:
            await db.precepts.drop()  # Clear existing precepts
            await db.precepts.insert_many(precepts)
            print(f"✅ Successfully stored {len(precepts)} precepts in database")
        
        # Create indexes for efficient searching
        await db.precepts.create_index("title")
        await db.precepts.create_index("topics")
        await db.precepts.create_index("testament")
        await db.precepts.create_index("verses.book")
        print("✅ Created database indexes for precepts")
        
        return precepts
    
    def _apply_divine_name_replacements(self, text: str) -> str:
        """Apply YHWH/YHUH divine name replacements"""
        if not text:
            return text
            
        # Primary divine name replacements
        replacements = [
            # LORD (all caps) patterns - these represent the Tetragrammaton YHWH
            (r'\bLORD\b', 'YHWH'),
            (r'\bLord\s+God\b', 'YHWH Elohim'),
            (r'\bLord\s+thy\s+God\b', 'YHWH thy Elohim'),
            (r'\bLord\s+your\s+God\b', 'YHWH your Elohim'),
            (r'\bLord\s+our\s+God\b', 'YHWH our Elohim'),
            (r'\bthe\s+Lord\s+God\b', 'YHWH Elohim'),
            (r'\bLord\s+my\s+God\b', 'YHWH my Elohim'),
            
            # God replacements with Elohim
            (r'\bGod\b', 'Elohim'),
            (r'\bthy\s+God\b', 'thy Elohim'),
            (r'\byour\s+God\b', 'your Elohim'),
            (r'\bour\s+God\b', 'our Elohim'),
            (r'\bmy\s+God\b', 'my Elohim'),
            (r'\bthe\s+God\b', 'the Elohim'),
            
            # Specific Lord contexts (not in all caps)
            (r'\bLord\b(?!\s+(?:God|thy|your|our|my))', 'YHUH'),
        ]
        
        result = text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
        return result

async def main():
    """Main processing function"""
    processor = PreceptsProcessor()
    
    # Complete precepts text provided by user
    precepts_text = """Abomination
Deuteronomy 14:3
Thou shalt not eat any abominable thing.
Deuteronomy 22:5
The woman shall not wear that which pertaineth unto a man, neither shall a man put on a woman's garment: for all that do so are abomination unto the Lord thy God.
Ecclesiasticus (Sirach) 15:13
The Lord hateth all abomination; and they that fear God love it not.
Ezekiel 14:6
Therefore say unto the house of Israel, Thus saith the Lord God; Repent, and turn yourselves from your idols; and turn away your faces from all your abominations.
Leviticus 18:29
For whosoever shall commit any of these abominations, even the souls that commit them shall be cut off from among their people.
Leviticus 20:13
If a man also lie with mankind, as he lieth with a woman, both of them have committed an abomination: they shall surely be put to death; their blood shall be upon them.
Luke 16:15
And he said unto them, Ye are they which justify yourselves before men; but God knoweth your hearts: for that which is highly esteemed among men is abomination in the sight of God.
Proverbs 15:26
The thoughts of the wicked are an abomination to the Lord: but the words of the pure are pleasant words.
Proverbs 28:9
He that turneth away his ear from hearing the law, even his prayer shall be abomination.
Revelations 21:27
And there shall in no wise enter into it any thing that defileth, neither whatsoever worketh abomination, or maketh a lie: but they which are written in the Lamb's book of life.
Titus 1:16
They profess that they know God; but in works they deny him, being abominable, and disobedient, and unto every good work reprobate.
Abortion
Deuteronomy 5:17
Thou shalt not kill.
Exodus 20:13
Thou shalt not kill.
Wisdom of Solomon 12:6
With their priests out of the midst of their idolatrous crew, and the parents, that killed with their own hands souls destitute of help:
Wisdom of Solomon 14:23
For whilst they slew their children in sacrifices, or used secret ceremonies, or made revellings of strange rites;
Acceptable
Ecclesiasticus (Sirach) 2:5
For gold is tried in the fire, and acceptable men in the furnace of adversity.
Ecclesiasticus (Sirach) 15:15
If thou wilt, to keep the commandments, and to perform acceptable faithfulness.
Ecclesiasticus (Sirach) 19:18
The fear of the Lord is the first step to be accepted [of him,] and wisdom obtaineth his love.
Psalms 19:14
Let the words of my mouth, and the meditation of my heart, be acceptable in thy sight, O Lord, my strength, and my redeemer.
Romans 12:2
And be not conformed to this world: but be ye transformed by the renewing of your mind, that ye may prove what is that good, and acceptable, and perfect, will of God.
Add nor Remove
Deuteronomy 4:2
Ye shall not add unto the word which I command you, neither shall ye diminish ought from it, that ye may keep the commandments of the Lord your God which I command you.
Deuteronomy 12:32
What thing soever I command you, observe to do it: thou shalt not add thereto, nor diminish from it.
Proverbs 30:6
Add thou not unto his words, lest he reprove thee, and thou be found a liar.
Revelations 22:18
For I testify unto every man that heareth the words of the prophecy of this book, If any man shall add unto these things, God shall add unto him the plagues that are written in this book:
Revelations 22:19
And if any man shall take away from the words of the book of this prophecy, God shall take away his part out of the book of life, and out of the holy city, and from the things which are written in this book.
Adultery
1Corinthians 6:9
Know ye not that the unrighteous shall not inherit the kingdom of God? Be not deceived: neither fornicators, nor idolaters, nor adulterers, nor effeminate, nor abusers of themselves with mankind,
Deuteronomy 5:18
Neither shalt thou commit adultery.
Deuteronomy 22:22
If a man be found lying with a woman married to an husband, then they shall both of them die, both the man that lay with the woman, and the woman: so shalt thou put away evil from Israel.
Ecclesiasticus (Sirach) 23:18
A man that breaketh wedlock, saying thus in his heart, Who seeth me? I am compassed about with darkness, the walls cover me, and no body seeth me; what need I to fear? the most High will not remember my sins:
Exodus 20:14
Thou shalt not commit adultery.
Hebrews 13:4
Marriage is honourable in all, and the bed undefiled: but whoremongers and adulterers God will judge.
Leviticus 20:10
And the man that committeth adultery with another man's wife, even he that committeth adultery with his neighbour's wife, the adulterer and the adulteress shall surely be put to death.
Matthew 5:28
But I say unto you, That whosoever looketh on a woman to lust after her hath committed adultery with her already in his heart.
Proverbs 6:32
But whoso committeth adultery with a woman lacketh understanding: he that doeth it destroyeth his own soul.
Affections
Colossians 3:2
Set your affection on things above, not on things on the earth.
Galatians 5:24
And they that are Christ's have crucified the flesh with the affections and lusts.
Wisdom of Solomon 6:11
Wherefore set your affection upon my words; desire them, and ye shall be instructed.
Afflict your soul
Isaiah 58:3
Wherefore have we fasted, say they, and thou seest not? wherefore have we afflicted our soul, and thou takest no knowledge? Behold, in the day of your fast ye find pleasure, and exact all your labours.
Leviticus 23:27
Also on the tenth day of this seventh month there shall be a day of atonement: it shall be an holy convocation unto you; and ye shall afflict your souls, and offer an offering made by fire unto the Lord.
Agreement
2Corinthians 6:16
And what agreement hath the temple of God with idols? for ye are the temple of the living God; as God hath said, I will dwell in them, and walk in them; and I will be their God, and they shall be my people.
Amos 3:3
Can two walk together, except they be agreed?
Ecclesiasticus (Sirach) 13:17
What fellowship hath the wolf with the lamb? so the sinner with the godly.
Ecclesiasticus (Sirach) 25:1
In three things I was beautified, and stood up beautiful both before God and men: the unity of brethren, the love of neighbours, a man and a wife that agree together.
Alms deliver
Acts 9:36
Now there was at Joppa a certain disciple named Tabitha, which by interpretation is called Dorcas: this woman was full of good works and almsdeeds which she did.
Acts 10:2
A devout man, and one that feared God with all his house, which gave much alms to the people, and prayed to God alway.
Acts 10:4
And when he looked on him, he was afraid, and said, What is it, Lord? And he said unto him, Thy prayers and thine alms are come up for a memorial before God.
Ecclesiasticus (Sirach) 3:30
Water will quench a flaming fire; and alms maketh an atonement for sins.
Ecclesiasticus (Sirach) 12:3
There can no good come to him that is always occupied in evil, nor to him that giveth no alms.
Ecclesiasticus (Sirach) 17:22
The alms of a man is as a signet with him, and he will keep the good deeds of man as the apple of the eye, and give repentance to his sons and daughters.
Ecclesiasticus (Sirach) 29:12
Shut up alms in thy storehouses: and it shall deliver thee from all affliction.
Ecclesiasticus (Sirach) 40:24
Brethren and help are against time of trouble: but alms shall deliver more than them both.
Matthew 6:4
That thine alms may be in secret: and thy Father which seeth in secret himself shall reward thee openly.
Tobit 4:10
Because that alms do deliver from death, and suffereth not to come into darkness.
Tobit 12:9
For alms doth deliver from death, and shall purge away all sin. Those that exercise alms and righteousness shall be filled with life:
Tobit 14:11
Wherefore now, my son, consider what alms doeth, and how righteousness doth deliver. When he had said these things, he gave up the ghost in the bed, being an hundred and eight and fifty years old; and he buried him honourably.
Angel of Prayer
Acts 10:4
And when he looked on him, he was afraid, and said, What is it, Lord? And he said unto him, Thy prayers and thine alms are come up for a memorial before God.
Tobit 12:15
I am Raphael, one of the seven holy angels, which present the prayers of the saints, and which go in and out before the glory of the Holy One.
Anger
Ecclesiastes 7:9
Be not hasty in thy spirit to be angry: for anger resteth in the bosom of fools.
Ecclesiasticus (Sirach) 1:22
A furious man cannot be justified; for the sway of his fury shall be his destruction.
Ephesians 4:26
Be ye angry, and sin not: let not the sun go down upon your wrath:
James 1:19
Wherefore, my beloved brethren, let every man be swift to hear, slow to speak, slow to wrath:
Matthew 5:22
But I say unto you, That whosoever is angry with his brother without a cause shall be in danger of the judgment: and whosoever shall say to his brother, Raca, shall be in danger of the council: but whosoever shall say, Thou fool, shall be in danger of hell fire.
Proverbs 14:17
He that is soon angry dealeth foolishly: and a man of wicked devices is hated.
Proverbs 14:29
He that is slow to wrath is of great understanding: but he that is hasty of spirit exalteth folly.
Proverbs 15:1
A soft answer turneth away wrath: but grievous words stir up anger.
Proverbs 16:32
He that is slow to anger is better than the mighty; and he that ruleth his spirit than he that taketh a city.
Psalms 37:8
Cease from anger, and forsake wrath: fret not thyself in any wise to do evil.
Apparel
Ecclesiasticus (Sirach) 19:30
A man's attire, and excessive laughter, and gait, shew what he is.
Joshua 7:21
When I saw among the spoils a goodly Babylonish garment, and two hundred shekels of silver, and a wedge of gold of fifty shekels weight, then I coveted them, and took them; and, behold, they are hid in the earth in the midst of my tent, and the silver under it.
Matthew 23:26
Thou blind Pharisee, cleanse first that which is within the cup and platter, that the outside of them may be clean also.
Numbers 15:38
Speak unto the children of Israel, and bid them that they make them fringes in the borders of their garments throughout their generations, and that they put upon the fringe of the borders a ribband of blue:
Proverbs 7:10
And, behold, there met him a woman with the attire of an harlot, and subtil of heart.
Zephaniah 1:8
And it shall come to pass in the day of the Lord's sacrifice, that I will punish the princes, and the king's children, and all such as are clothed with strange apparel.
Appear 3 Times
2Chronicles 8:13
Even after a certain rate every day, offering according to the commandment of Moses, on the sabbaths, and on the new moons, and on the solemn feasts, three times in the year, even in the feast of unleavened bread, and in the feast of weeks, and in the feast of tabernacles.
Deuteronomy 16:16
Three times in a year shall all thy males appear before the Lord thy God in the place which he shall choose; in the feast of unleavened bread, and in the feast of weeks, and in the feast of tabernacles: and they shall not appear before the Lord empty:
Exodus 23:17
Three times in the year all thy males shall appear before the Lord God.
Exodus 34:23
Thrice in the year shall all your menchildren appear before the Lord God, the God of Israel.
Appearance
Ecclesiasticus (Sirach) 19:29
A man may be known by his look, and one that hath understanding by his countenance, when thou meetest him.
Matthew 23:26
Thou blind Pharisee, cleanse first that which is within the cup and platter, that the outside of them may be clean also.
Proverbs 7:10
And, behold, there met him a woman with the attire of an harlot, and subtil of heart.
Ark of Covenant
2Maccabees 2:4
It was also contained in the same writing, that the prophet, being warned of God, commanded the tabernacle and the ark to go with him, as he went forth into the mountain, where Moses climbed up, and saw the heritage of God.
Jeremiah 3:16
And it shall come to pass, when ye be multiplied and increased in the land, in those days, saith the Lord, they shall say no more, The ark of the covenant of the Lord: neither shall it come to mind: neither shall they remember it; neither shall they visit it; neither shall that be done any more.
Army
2Samuel 22:35
He teacheth my hands to war; so that a bow of steel is broken by mine arms.
2Timothy 2:3
Thou therefore endure hardness, as a good soldier of Jesus Christ.
Ephesians 6:11
Put on the whole armour of God, that ye may be able to stand against the wiles of the devil.
Exodus 6:26
These are that Aaron and Moses, to whom the Lord said, Bring out the children of Israel from the land of Egypt according to their armies.
Exodus 15:3
The Lord is a man of war: the Lord is his name.
Ezekiel 37:10
So I prophesied as he commanded me, and the breath came into them, and they lived, and stood up upon their feet, an exceeding great army.
Isaiah 59:17
For he put on righteousness as a breastplate, and an helmet of salvation upon his head; and he put on the garments of vengeance for clothing, and was clad with zeal as a cloak.
Philemon 1:2
And to our beloved Apphia, and Archippus our fellowsoldier, and to the church in thy house:
Psalms 18:34
He teacheth my hands to war, so that a bow of steel is broken by mine arms.
Psalms 144:1
Blessed be the Lord my strength which teacheth my hands to war, and my fingers to fight:
Assimilation
1Maccabees 1:43
Yea, many also of the Israelites consented to his religion, and sacrificed unto idols, and profaned the sabbath.
2Maccabees 4:16
By reason whereof sore calamity came upon them: for they had them to be their enemies and avengers, whose custom they followed so earnestly, and unto whom they desired to be like in all things.
Isaiah 28:15
Because ye have said, We have made a covenant with death, and with hell are we at agreement; when the overflowing scourge shall pass through, it shall not come unto us: for we have made lies our refuge, and under falsehood have we hid ourselves:
Jeremiah 10:2
Thus saith the Lord, Learn not the way of the heathen, and be not dismayed at the signs of heaven; for the heathen are dismayed at them.
Leviticus 13:30
Then the priest shall see the plague: and, behold, if it be in sight deeper than the skin; and there be in it a yellow thin hair; then the priest shall pronounce him unclean: it is a dry scall, even a leprosy upon the head or beard.
Leviticus 18:3
After the doings of the land of Egypt, wherein ye dwelt, shall ye not do: and after the doings of the land of Canaan, whither I bring you, shall ye not do: neither shall ye walk in their ordinances.
Proverbs 3:31
Envy thou not the oppressor, and choose none of his ways.
Psalms 106:35
But were mingled among the heathen, and learned their works."""
    
    # Process the precepts text 
    await processor.process_raw_precepts(precepts_text)
    
    print("\n" + "="*60)
    print("✅ Phase 2: Precepts Integration Complete")
    print("="*60)
    print("✅ Precepts processed and stored in database")
    print("✅ YHWH/YHUH divine name replacements applied")
    print("✅ Database indexes created for efficient searching")
    print("✅ Ready for API integration")

if __name__ == "__main__":
    asyncio.run(main())