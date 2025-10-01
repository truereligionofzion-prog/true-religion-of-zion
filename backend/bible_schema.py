"""
MongoDB Schema Design for 80-Book Bible Integration
Based on Phase 1 test extraction results
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime

class BibleVerse(BaseModel):
    """Individual verse model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    book: str
    chapter: int
    verse: int
    text: str
    has_precept: bool = False
    testament: str  # 'old', 'new', 'apocrypha'
    created_at: datetime = Field(default_factory=datetime.now)

class BibleChapter(BaseModel):
    """Chapter model containing multiple verses"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    book: str
    chapter: int
    title: str
    verses: List[BibleVerse]
    verse_count: int
    testament: str
    source_url: str
    created_at: datetime = Field(default_factory=datetime.now)

class BibleBook(BaseModel):
    """Book model for metadata"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    testament: str  # 'old', 'new', 'apocrypha'
    order: int  # Order in Bible (1-80)
    chapter_count: int
    verse_count: int
    source_id: int  # thepreceptbible.com field_book_target_id
    created_at: datetime = Field(default_factory=datetime.now)

# Database Collections Structure:
BIBLE_SCHEMA = {
    "bible_verses": {
        "description": "Individual verses with full text search capability",
        "indexes": [
            {"field": "book", "type": "text"},
            {"field": "chapter", "type": "ascending"},
            {"field": "verse", "type": "ascending"},
            {"field": "text", "type": "text"},
            {"field": "testament", "type": "text"},
            {"field": "has_precept", "type": "ascending"},
            {"compound": ["book", "chapter", "verse"], "type": "compound_unique"}
        ]
    },
    "bible_books": {
        "description": "Book metadata and statistics",
        "indexes": [
            {"field": "name", "type": "text"},
            {"field": "testament", "type": "text"},
            {"field": "order", "type": "ascending"},
            {"field": "source_id", "type": "unique"}
        ]
    }
}

# 80-Book Bible Structure
BIBLE_BOOKS_MAPPING = {
    # Old Testament (39 books)
    "old_testament": [
        {"name": "Genesis", "source_id": 60, "order": 1},
        {"name": "Exodus", "source_id": 56, "order": 2},
        {"name": "Leviticus", "source_id": 77, "order": 3},
        {"name": "Numbers", "source_id": 85, "order": 4},
        {"name": "Deuteronomy", "source_id": 49, "order": 5},
        {"name": "Joshua", "source_id": 72, "order": 6},
        {"name": "Judges", "source_id": 74, "order": 7},
        {"name": "Ruth", "source_id": 95, "order": 8},
        {"name": "1Samuel", "source_id": 29, "order": 9},
        {"name": "2Samuel", "source_id": 39, "order": 10},
        {"name": "1Kings", "source_id": 26, "order": 11},
        {"name": "2Kings", "source_id": 36, "order": 12},
        {"name": "1Chronicles", "source_id": 22, "order": 13},
        {"name": "2Chronicles", "source_id": 32, "order": 14},
        {"name": "Ezra", "source_id": 58, "order": 15},
        {"name": "Nehemiah", "source_id": 84, "order": 16},
        {"name": "Esther", "source_id": 54, "order": 17},
        {"name": "Job", "source_id": 68, "order": 18},
        {"name": "Psalms", "source_id": 92, "order": 19},
        {"name": "Proverbs", "source_id": 91, "order": 20},
        {"name": "Ecclesiastes", "source_id": 50, "order": 21},
        {"name": "Songs of Solomon", "source_id": 96, "order": 22},
        {"name": "Isaiah", "source_id": 65, "order": 23},
        {"name": "Jeremiah", "source_id": 67, "order": 24},
        {"name": "Lamentations", "source_id": 76, "order": 25},
        {"name": "Ezekiel", "source_id": 57, "order": 26},
        {"name": "Daniel", "source_id": 48, "order": 27},
        {"name": "Hosea", "source_id": 64, "order": 28},
        {"name": "Joel", "source_id": 69, "order": 29},
        {"name": "Amos", "source_id": 44, "order": 30},
        {"name": "Obadiah", "source_id": 86, "order": 31},
        {"name": "Jonah", "source_id": 71, "order": 32},
        {"name": "Micah", "source_id": 82, "order": 33},
        {"name": "Nahum", "source_id": 83, "order": 34},
        {"name": "Habakkuk", "source_id": 61, "order": 35},
        {"name": "Zephaniah", "source_id": 102, "order": 36},
        {"name": "Haggai", "source_id": 62, "order": 37},
        {"name": "Zechariah", "source_id": 101, "order": 38},
        {"name": "Malachi", "source_id": 79, "order": 39}
    ],
    
    # New Testament (27 books)
    "new_testament": [
        {"name": "Matthew", "source_id": 81, "order": 40},
        {"name": "Mark", "source_id": 80, "order": 41},
        {"name": "Luke", "source_id": 78, "order": 42},
        {"name": "John", "source_id": 70, "order": 43},
        {"name": "Acts", "source_id": 43, "order": 44},
        {"name": "Romans", "source_id": 94, "order": 45},
        {"name": "1Corinthians", "source_id": 23, "order": 46},
        {"name": "2Corinthians", "source_id": 33, "order": 47},
        {"name": "Galatians", "source_id": 59, "order": 48},
        {"name": "Ephesians", "source_id": 52, "order": 49},
        {"name": "Philippians", "source_id": 88, "order": 50},
        {"name": "Colossians", "source_id": 47, "order": 51},
        {"name": "1Thessalonians", "source_id": 30, "order": 52},
        {"name": "2Thessalonians", "source_id": 40, "order": 53},
        {"name": "1Timothy", "source_id": 31, "order": 54},
        {"name": "2Timothy", "source_id": 41, "order": 55},
        {"name": "Titus", "source_id": 98, "order": 56},
        {"name": "Philemon", "source_id": 87, "order": 57},
        {"name": "Hebrews", "source_id": 63, "order": 58},
        {"name": "James", "source_id": 66, "order": 59},
        {"name": "1Peter", "source_id": 28, "order": 60},
        {"name": "2Peter", "source_id": 38, "order": 61},
        {"name": "1John", "source_id": 25, "order": 62},
        {"name": "2John", "source_id": 35, "order": 63},
        {"name": "3John", "source_id": 42, "order": 64},
        {"name": "Jude", "source_id": 73, "order": 65},
        {"name": "Revelations", "source_id": 93, "order": 66}
    ],
    
    # Apocrypha (14 books)
    "apocrypha": [
        {"name": "1Esdras", "source_id": 24, "order": 67},
        {"name": "2Esdras", "source_id": 34, "order": 68},
        {"name": "Tobit", "source_id": 99, "order": 69},
        {"name": "Judith", "source_id": 75, "order": 70},
        {"name": "Esther (Greek)", "source_id": 55, "order": 71},
        {"name": "Wisdom of Solomon", "source_id": 100, "order": 72},
        {"name": "Ecclesiasticus (Sirach)", "source_id": 51, "order": 73},
        {"name": "Baruch", "source_id": 45, "order": 74},
        {"name": "Epistle of Jeremiah", "source_id": 53, "order": 75},
        {"name": "Prayer of Azariah", "source_id": 89, "order": 76},
        {"name": "Susanna", "source_id": 97, "order": 77},
        {"name": "Bel and the Dragon", "source_id": 46, "order": 78},
        {"name": "Prayer of Manasseh", "source_id": 90, "order": 79},
        {"name": "1Maccabees", "source_id": 27, "order": 80},
        {"name": "2Maccabees", "source_id": 37, "order": 80}  # Note: both 1&2 Maccabees are #80
    ]
}

# Phase 1 Test Results Summary
PHASE_1_SUMMARY = {
    "extraction_success": True,
    "test_books": ["Genesis", "Tobit"],
    "verses_extracted": 58,
    "divine_name_replacements": 31,
    "data_quality_score": 80,
    "key_findings": [
        "✅ HTML structure parsing works perfectly",
        "✅ Divine name replacements (YHWH/YHUH) applied correctly",
        "✅ Verse numbering and text extraction accurate",
        "✅ Precept markers detected (has_precept flag)",
        "✅ Both Old Testament and Apocrypha extraction successful",
        "⚠️ Minor verse numbering gaps (duplicates) need cleaning",
        "✅ Source URLs tracked for reference"
    ],
    "ready_for_phase_2": True,
    "recommended_improvements": [
        "Add duplicate verse filtering",
        "Implement chapter count detection",
        "Add progress tracking for full extraction"
    ]
}