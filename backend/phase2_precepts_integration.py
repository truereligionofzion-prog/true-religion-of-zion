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
    
    # Sample precepts text for testing (user will provide the complete text)
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
And if any man shall take away from the words of the book of this prophecy, God shall take away his part out of the book of life, and out of the holy city, and from the things which are written in this book."""
    
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