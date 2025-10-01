#!/usr/bin/env python3
"""
Bible Data Loader - Load Phase 1 test data into MongoDB
"""

import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class BibleDataLoader:
    def __init__(self):
        # MongoDB connection
        mongo_url = os.environ['MONGO_URL']
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[os.environ['DB_NAME']]
        
        # Collections
        self.bible_verses_collection = self.db.bible_verses
        self.bible_books_collection = self.db.bible_books

    async def load_sample_data(self):
        """Load Genesis 1 and Tobit 1 from Phase 1 test results"""
        
        # Load Phase 1 test results
        results_file = "/app/backend/bible_test_results.json"
        
        if not os.path.exists(results_file):
            print("❌ Phase 1 test results not found. Please run bible_test_extraction.py first.")
            return False

        with open(results_file, 'r') as f:
            results = json.load(f)

        print("🔄 Loading sample Bible data into MongoDB...")
        
        # Clear existing Bible data
        await self.bible_verses_collection.delete_many({})
        await self.bible_books_collection.delete_many({})
        
        total_verses_loaded = 0
        books_loaded = 0

        # Process each chapter from Phase 1 results
        for chapter_key, chapter_data in results['chapters'].items():
            book_name = chapter_data['book']
            chapter_num = chapter_data['chapter']
            
            print(f"📖 Loading {book_name} {chapter_num}...")
            
            # Determine testament
            testament = 'apocrypha' if book_name == 'Tobit' else 'old'
            
            # Load verses
            verses_to_insert = []
            for verse_data in chapter_data['verses']:
                verse_doc = {
                    'id': f"{book_name.lower()}_{chapter_num}_{verse_data['verse']}",
                    'book': book_name,
                    'chapter': chapter_num,
                    'verse': verse_data['verse'],
                    'text': verse_data['text'],
                    'has_precept': verse_data.get('has_precept', False),
                    'testament': testament,
                    'createdAt': datetime.now(timezone.utc)
                }
                verses_to_insert.append(verse_doc)
            
            # Insert verses
            if verses_to_insert:
                await self.bible_verses_collection.insert_many(verses_to_insert)
                total_verses_loaded += len(verses_to_insert)
                
            # Load book metadata
            book_doc = {
                'id': f"{book_name.lower()}_book",
                'name': book_name,
                'testament': testament,
                'order': 1 if book_name == 'Genesis' else 69,  # Genesis=1, Tobit=69
                'chapter_count': 1,  # For now, we only have chapter 1
                'verse_count': len(verses_to_insert),
                'source_id': 60 if book_name == 'Genesis' else 99,  # From Phase 1 mapping
                'createdAt': datetime.now(timezone.utc)
            }
            
            await self.bible_books_collection.insert_one(book_doc)
            books_loaded += 1
            
            print(f"  ✅ Loaded {len(verses_to_insert)} verses")

        # Create indexes for performance
        await self.create_indexes()
        
        print(f"\n📊 SAMPLE DATA LOADING COMPLETE")
        print(f"Books loaded: {books_loaded}")
        print(f"Verses loaded: {total_verses_loaded}")
        
        return True

    async def create_indexes(self):
        """Create database indexes for Bible collections"""
        print("🔧 Creating database indexes...")
        
        # Bible verses indexes
        await self.bible_verses_collection.create_index("book")
        await self.bible_verses_collection.create_index("testament")
        await self.bible_verses_collection.create_index("has_precept")
        await self.bible_verses_collection.create_index([("book", 1), ("chapter", 1), ("verse", 1)])
        await self.bible_verses_collection.create_index([("text", "text")])  # Text search
        
        # Bible books indexes
        await self.bible_books_collection.create_index("name")
        await self.bible_books_collection.create_index("testament")
        await self.bible_books_collection.create_index("order")
        
        print("✅ Database indexes created")

    async def get_sample_stats(self):
        """Get stats about loaded sample data"""
        
        # Count verses by testament
        old_testament = await self.bible_verses_collection.count_documents({"testament": "old"})
        apocrypha = await self.bible_verses_collection.count_documents({"testament": "apocrypha"})
        total_verses = await self.bible_verses_collection.count_documents({})
        
        # Count books
        total_books = await self.bible_books_collection.count_documents({})
        
        # Count verses with precepts
        verses_with_precepts = await self.bible_verses_collection.count_documents({"has_precept": True})
        
        stats = {
            "total_books": total_books,
            "total_verses": total_verses,
            "old_testament_verses": old_testament,
            "apocrypha_verses": apocrypha,
            "verses_with_precepts": verses_with_precepts
        }
        
        return stats

async def main():
    """Run the Bible data loader"""
    print("🔄 Starting Bible Sample Data Loader")
    print("=" * 50)
    
    loader = BibleDataLoader()
    
    try:
        # Load sample data
        success = await loader.load_sample_data()
        
        if success:
            # Show stats
            stats = await loader.get_sample_stats()
            
            print(f"\n📈 FINAL STATISTICS")
            print("=" * 30)
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            
            print(f"\n🎉 Bible sample data loaded successfully!")
            print(f"Ready for Phase 2 API and UI integration.")
        
    except Exception as e:
        print(f"❌ Error during data loading: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        loader.client.close()

if __name__ == "__main__":
    asyncio.run(main())