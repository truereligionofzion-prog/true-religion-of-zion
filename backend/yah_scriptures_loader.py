#!/usr/bin/env python3
"""
Yah Scriptures CSV Loader with Divine Name Standardization
Load Tanakh and Apocrypha CSVs with HWHY -> YHWH conversion
"""

import pandas as pd
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
from typing import Dict, List
import uuid
from datetime import datetime, timezone

class YahScripturesLoader:
    """Load Yah Scriptures CSV files with divine name standardization"""
    
    def __init__(self):
        # MongoDB connection
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Version identifier
        self.version = "yah_scriptures"
        
        # Divine name mapping
        self.divine_name_replacements = {
            'HWHY': 'YHWH',
            'HWYH': 'YHWH',  # Alternative ordering
            # Add more patterns as needed
        }
        
        # Statistics
        self.stats = {
            'tanakh_verses': 0,
            'apocrypha_verses': 0,
            'total_verses': 0,
            'total_books': 0,
            'divine_replacements': 0,
            'processing_time': 0
        }
    
    def standardize_divine_names(self, text: str) -> tuple[str, int]:
        """
        Standardize divine names in text
        Returns: (standardized_text, replacement_count)
        """
        if not text:
            return text, 0
            
        original_text = text
        replacement_count = 0
        
        # Apply divine name replacements
        for old_name, new_name in self.divine_name_replacements.items():
            # Case-sensitive replacement
            if old_name in text:
                text = text.replace(old_name, new_name)
                replacement_count += original_text.count(old_name)
        
        return text, replacement_count
    
    def determine_testament(self, book_name: str) -> str:
        """Determine testament based on book name"""
        
        # Old Testament books (39 books)
        old_testament_books = {
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', 
            '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
            'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
            'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah',
            'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
            'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk',
            'Zephaniah', 'Haggai', 'Zechariah', 'Malachi'
        }
        
        # Apocrypha books
        apocrypha_books = {
            'Wisdom of Solomon', 'Ecclesiasticus', 'Tobit', 'Judith',
            'Additions to Esther', '1 Maccabees', '2 Maccabees',
            'Baruch', 'Letter of Jeremiah', 'Prayer of Azariah',
            'Susanna', 'Bel and the Dragon', '1 Esdras', '2 Esdras',
            'Prayer of Manasseh'
        }
        
        if book_name in old_testament_books:
            return 'old'
        elif book_name in apocrypha_books:
            return 'apocrypha'
        else:
            return 'unknown'
    
    async def load_csv_file(self, filepath: str, file_type: str):
        """Load and process a CSV file"""
        
        print(f"\n📖 Loading {file_type.upper()}: {filepath}")
        
        # Read CSV
        df = pd.read_csv(filepath)
        print(f"   📊 Found {len(df)} verses")
        
        # Get unique books
        books = df['book'].unique()
        books = [book for book in books if book != 'book']  # Remove header duplicates
        print(f"   📚 Books: {len(books)} - {', '.join(books[:5])}{'...' if len(books) > 5 else ''}")
        
        verses_processed = 0
        divine_replacements = 0
        
        # Process each row
        for _, row in df.iterrows():
            # Skip header rows that might be mixed in
            if row['book'] == 'book':
                continue
                
            # Standardize divine names
            standardized_text, replacements = self.standardize_divine_names(row['text'])
            divine_replacements += replacements
            
            # Create verse document
            verse_doc = {
                'id': f"{row['book'].lower().replace(' ', '_')}_{row['chapter']}_{row['verse']}_{self.version}",
                'book': row['book'],
                'chapter': int(row['chapter']),
                'verse': int(row['verse']),
                'text': standardized_text,
                'version': self.version,
                'testament': self.determine_testament(row['book']),
                'has_precept': False,  # Will be updated later if needed
                'source': 'yah_scriptures_csv',
                'createdAt': datetime.now(timezone.utc)
            }
            
            # Insert or update verse
            await self.db.bible_verses.replace_one(
                {'id': verse_doc['id']},
                verse_doc,
                upsert=True
            )
            
            verses_processed += 1
            
            if verses_processed % 1000 == 0:
                print(f"   ✅ Processed {verses_processed} verses...")
        
        print(f"   🎯 Completed: {verses_processed} verses, {divine_replacements} divine name replacements")
        
        if file_type == 'tanakh':
            self.stats['tanakh_verses'] = verses_processed
        else:
            self.stats['apocrypha_verses'] = verses_processed
            
        self.stats['divine_replacements'] += divine_replacements
        self.stats['total_books'] += len(books)
        
        return verses_processed, len(books)
    
    async def create_book_records(self):
        """Create book summary records"""
        
        print("\n📚 Creating book records...")
        
        # Get all unique books from verses
        pipeline = [
            {'$match': {'version': self.version}},
            {'$group': {
                '_id': {
                    'book': '$book',
                    'testament': '$testament'
                },
                'chapter_count': {'$max': '$chapter'},
                'verse_count': {'$sum': 1}
            }}
        ]
        
        books_data = await self.db.bible_verses.aggregate(pipeline).to_list(length=None)
        
        books_processed = 0
        for book_data in books_data:
            book_doc = {
                'id': f"{book_data['_id']['book'].lower().replace(' ', '_')}_book_{self.version}",
                'name': book_data['_id']['book'],
                'testament': book_data['_id']['testament'],
                'version': self.version,
                'order': books_processed + 1,  # Simple ordering for now
                'chapter_count': book_data['chapter_count'],
                'verse_count': book_data['verse_count'],
                'source': 'yah_scriptures_csv',
                'createdAt': datetime.now(timezone.utc)
            }
            
            await self.db.bible_books.replace_one(
                {'id': book_doc['id']},
                book_doc,
                upsert=True
            )
            
            books_processed += 1
        
        print(f"   ✅ Created {books_processed} book records")
        return books_processed
    
    async def update_stats(self):
        """Update Bible statistics"""
        
        print("\n📊 Updating statistics...")
        
        # Calculate stats
        total_verses = await self.db.bible_verses.count_documents({'version': self.version})
        total_books = await self.db.bible_books.count_documents({'version': self.version})
        total_chapters = await self.db.bible_verses.distinct('chapter', {'version': self.version})
        
        old_testament_books = await self.db.bible_books.count_documents({
            'version': self.version,
            'testament': 'old'
        })
        
        apocrypha_books = await self.db.bible_books.count_documents({
            'version': self.version,
            'testament': 'apocrypha'
        })
        
        old_testament_verses = await self.db.bible_verses.count_documents({
            'version': self.version,
            'testament': 'old'
        })
        
        apocrypha_verses = await self.db.bible_verses.count_documents({
            'version': self.version,
            'testament': 'apocrypha'
        })
        
        self.stats.update({
            'total_verses': total_verses,
            'total_books': total_books,
            'total_chapters': len(total_chapters),
            'old_testament_books': old_testament_books,
            'apocrypha_books': apocrypha_books,
            'old_testament_verses': old_testament_verses,
            'apocrypha_verses': apocrypha_verses,
            'new_testament_books': 0,  # Not included yet
            'new_testament_verses': 0
        })
        
        print(f"   📊 Final Stats:")
        print(f"      📚 Books: {total_books} ({old_testament_books} OT, {apocrypha_books} Apocrypha)")
        print(f"      📖 Chapters: {len(total_chapters)}")
        print(f"      📝 Verses: {total_verses} ({old_testament_verses} OT, {apocrypha_verses} Apocrypha)")
        print(f"      ✨ Divine replacements: {self.stats['divine_replacements']}")
    
    async def run_full_import(self):
        """Run the complete import process"""
        
        start_time = datetime.now()
        print("🚀 Starting Yah Scriptures Import")
        print("=" * 50)
        
        try:
            # Load Tanakh
            await self.load_csv_file('/app/tanakh_rescan_clean.csv', 'tanakh')
            
            # Load Apocrypha  
            await self.load_csv_file('/app/apocrypha_1611_from_ranges_IMPLICIT_norm.csv', 'apocrypha')
            
            # Create book records
            await self.create_book_records()
            
            # Update statistics
            await self.update_stats()
            
            # Calculate processing time
            end_time = datetime.now()
            self.stats['processing_time'] = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 50)
            print("🎉 YAH SCRIPTURES IMPORT COMPLETE!")
            print(f"⏱️  Processing time: {self.stats['processing_time']:.1f} seconds")
            print(f"📊 Total verses: {self.stats['total_verses']:,}")
            print(f"📚 Total books: {self.stats['total_books']}")
            print(f"✨ Divine name replacements: {self.stats['divine_replacements']:,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during import: {e}")
            return False
        
        finally:
            await self.client.close()

async def main():
    loader = YahScripturesLoader()
    await loader.run_full_import()

if __name__ == "__main__":
    asyncio.run(main())