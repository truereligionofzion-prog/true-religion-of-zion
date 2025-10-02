#!/usr/bin/env python3
"""
Create missing book records for KJV 1611 extraction data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class BookRecordCreator:
    """Create book records from existing verse data"""
    
    def __init__(self):
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
    async def analyze_verses(self):
        """Analyze verses to see what books exist"""
        
        print("🔍 Analyzing verses to find books...")
        
        pipeline = [
            {'$match': {'version': 'kjv1611_divine'}},
            {'$group': {
                '_id': '$book',
                'chapter_count': {'$max': '$chapter'},
                'verse_count': {'$sum': 1},
                'min_chapter': {'$min': '$chapter'},
                'max_chapter': {'$max': '$chapter'}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        books_data = await self.db.bible_verses.aggregate(pipeline).to_list(length=None)
        
        print(f"📚 Found {len(books_data)} unique books in verses:")
        for book in books_data[:10]:  # Show first 10
            print(f"   📖 {book['_id']}: {book['verse_count']} verses, {book['chapter_count']} chapters")
        
        if len(books_data) > 10:
            print(f"   ... and {len(books_data) - 10} more books")
        
        return books_data
    
    async def determine_testament(self, book_name):
        """Determine testament for a book"""
        
        old_testament = [
            'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
            'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', 
            '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
            'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs',
            'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah',
            'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel',
            'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk',
            'Zephaniah', 'Haggai', 'Zechariah', 'Malachi'
        ]
        
        new_testament = [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
            '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
            'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
            '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews',
            'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
            'Jude', 'Revelation'
        ]
        
        if book_name in old_testament:
            return 'old'
        elif book_name in new_testament:
            return 'new'
        else:
            return 'apocrypha'  # Everything else is apocrypha
    
    async def create_book_records(self, books_data):
        """Create book records for all found books"""
        
        print(f"\n📚 Creating book records for {len(books_data)} books...")
        
        created_count = 0
        
        for i, book_data in enumerate(books_data):
            book_name = book_data['_id']
            testament = await self.determine_testament(book_name)
            
            book_record = {
                'id': f"{book_name.lower().replace(' ', '_')}_book_kjv1611_divine",
                'name': book_name,
                'testament': testament,
                'version': 'kjv1611_divine',
                'order': i + 1,  # Simple ordering
                'chapter_count': book_data['chapter_count'],
                'verse_count': book_data['verse_count'],
                'source': 'thepreceptbible.com',
                'createdAt': datetime.now(timezone.utc)
            }
            
            # Insert or update
            result = await self.db.bible_books.replace_one(
                {'id': book_record['id']},
                book_record,
                upsert=True
            )
            
            if result.upserted_id or result.modified_count:
                created_count += 1
                
            if (i + 1) % 10 == 0:
                print(f"   ✅ Processed {i + 1}/{len(books_data)} books...")
        
        print(f"   🎯 Created/updated {created_count} book records")
        return created_count
    
    async def verify_books(self):
        """Verify book creation worked"""
        
        print("\n🔍 Verifying book records...")
        
        kjv_books = await self.db.bible_books.count_documents({'version': 'kjv1611_divine'})
        yah_books = await self.db.bible_books.count_documents({'version': 'yah_scriptures'})
        
        print(f"📊 KJV 1611 books: {kjv_books}")
        print(f"📊 Yah Scriptures books: {yah_books}")
        print(f"📊 Total books: {kjv_books + yah_books}")
        
        # Show some examples
        sample_books = await self.db.bible_books.find(
            {'version': 'kjv1611_divine'}, 
            {'name': 1, 'testament': 1, 'verse_count': 1}
        ).limit(5).to_list(length=5)
        
        print("📖 Sample KJV books:")
        for book in sample_books:
            print(f"   - {book['name']} ({book['testament']}): {book['verse_count']} verses")
        
        return kjv_books > 0
    
    async def run_creation(self):
        """Run the book creation process"""
        
        start_time = datetime.now()
        print("📚 Starting Book Record Creation")
        print("=" * 50)
        
        try:
            # Analyze existing verses
            books_data = await self.analyze_verses()
            
            if not books_data:
                print("❌ No verse data found for kjv1611_divine version")
                return False
            
            # Create book records
            created_count = await self.create_book_records(books_data)
            
            # Verify creation
            success = await self.verify_books()
            
            # Summary
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 50)
            if success:
                print("🎉 BOOK CREATION COMPLETE!")
            else:
                print("❌ BOOK CREATION FAILED!")
                
            print(f"⏱️  Processing time: {processing_time:.1f} seconds")
            print(f"📚 Books processed: {len(books_data)}")
            print(f"📝 Records created/updated: {created_count}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during book creation: {e}")
            return False
        
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    creator = BookRecordCreator()
    await creator.run_creation()

if __name__ == "__main__":
    asyncio.run(main())