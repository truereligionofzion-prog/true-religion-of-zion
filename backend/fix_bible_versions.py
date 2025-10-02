#!/usr/bin/env python3
"""
Fix Bible versions: Delete broken KJV extraction, rename Yah Scriptures to KJV 1611
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class BibleVersionFixer:
    """Fix Bible version names and remove broken data"""
    
    def __init__(self):
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
    async def analyze_current_state(self):
        """Check current Bible data"""
        
        print("🔍 Analyzing current Bible data...")
        
        # Check verses by version
        kjv_verses = await self.db.bible_verses.count_documents({'version': 'kjv1611_divine'})
        yah_verses = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
        
        # Check books by version
        kjv_books = await self.db.bible_books.count_documents({'version': 'kjv1611_divine'})
        yah_books = await self.db.bible_books.count_documents({'version': 'yah_scriptures'})
        
        print(f"📊 CURRENT STATE:")
        print(f"   KJV 1611 (broken): {kjv_books} books, {kjv_verses} verses")
        print(f"   Yah Scriptures (working): {yah_books} books, {yah_verses} verses")
        
        # Sample KJV verse to confirm it's broken
        kjv_sample = await self.db.bible_verses.find_one({'version': 'kjv1611_divine'})
        if kjv_sample:
            print(f"   KJV Sample text: '{kjv_sample.get('text', 'NO TEXT')[:50]}...'")
        
        # Sample Yah verse to confirm it's working
        yah_sample = await self.db.bible_verses.find_one({'version': 'yah_scriptures'})
        if yah_sample:
            print(f"   Yah Sample text: '{yah_sample.get('text', 'NO TEXT')[:50]}...'")
        
        return kjv_verses, yah_verses, kjv_books, yah_books
    
    async def delete_broken_kjv_data(self):
        """Delete the broken KJV 1611 extraction data"""
        
        print("\n🗑️  Deleting broken KJV 1611 extraction data...")
        
        # Delete verses
        verse_result = await self.db.bible_verses.delete_many({'version': 'kjv1611_divine'})
        print(f"   🗑️  Deleted {verse_result.deleted_count} broken verses")
        
        # Delete books
        book_result = await self.db.bible_books.delete_many({'version': 'kjv1611_divine'})
        print(f"   🗑️  Deleted {book_result.deleted_count} broken book records")
        
        return verse_result.deleted_count, book_result.deleted_count
    
    async def rename_yah_to_kjv(self):
        """Rename Yah Scriptures to KJV 1611"""
        
        print("\n🔄 Renaming Yah Scriptures to KJV 1611...")
        
        # Update verses
        verse_result = await self.db.bible_verses.update_many(
            {'version': 'yah_scriptures'},
            {
                '$set': {
                    'version': 'kjv1611',
                    'source': 'yah_scriptures_csv',
                    'updatedAt': datetime.now(timezone.utc)
                }
            }
        )
        print(f"   ✅ Updated {verse_result.modified_count} verses")
        
        # Update books
        book_result = await self.db.bible_books.update_many(
            {'version': 'yah_scriptures'},
            {
                '$set': {
                    'version': 'kjv1611',
                    'source': 'yah_scriptures_csv',
                    'updatedAt': datetime.now(timezone.utc)
                }
            }
        )
        print(f"   ✅ Updated {book_result.modified_count} books")
        
        # Update book IDs to reflect new version
        async for book in self.db.bible_books.find({'version': 'kjv1611'}):
            old_id = book['id']
            new_id = old_id.replace('yah_scriptures', 'kjv1611')
            
            await self.db.bible_books.update_one(
                {'_id': book['_id']},
                {'$set': {'id': new_id}}
            )
        
        return verse_result.modified_count, book_result.modified_count
    
    async def verify_final_state(self):
        """Verify the fix worked"""
        
        print("\n🔍 Verifying final state...")
        
        # Check final counts
        kjv_verses = await self.db.bible_verses.count_documents({'version': 'kjv1611'})
        kjv_books = await self.db.bible_books.count_documents({'version': 'kjv1611'})
        
        # Check that old versions are gone
        old_kjv = await self.db.bible_verses.count_documents({'version': 'kjv1611_divine'})
        old_yah = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'})
        
        print(f"📊 FINAL STATE:")
        print(f"   KJV 1611: {kjv_books} books, {kjv_verses} verses")
        print(f"   Old versions remaining: kjv1611_divine={old_kjv}, yah_scriptures={old_yah}")
        
        # Sample verse to confirm text is real
        sample = await self.db.bible_verses.find_one({'version': 'kjv1611'})
        if sample:
            print(f"   Sample text: '{sample.get('text', 'NO TEXT')[:100]}...'")
        
        # Get book breakdown by testament
        pipeline = [
            {'$match': {'version': 'kjv1611'}},
            {'$group': {
                '_id': '$testament',
                'count': {'$sum': 1}
            }}
        ]
        
        testament_counts = await self.db.bible_books.aggregate(pipeline).to_list(length=None)
        print("   Testament breakdown:")
        for item in testament_counts:
            print(f"     {item['_id']}: {item['count']} books")
        
        return kjv_verses > 0 and kjv_books > 0 and old_kjv == 0 and old_yah == 0
    
    async def run_fix(self):
        """Run the complete fix process"""
        
        start_time = datetime.now()
        print("🔧 Starting Bible Version Fix")
        print("=" * 50)
        
        try:
            # Analyze current state
            await self.analyze_current_state()
            
            # Delete broken KJV data
            deleted_verses, deleted_books = await self.delete_broken_kjv_data()
            
            # Rename Yah Scriptures to KJV 1611
            updated_verses, updated_books = await self.rename_yah_to_kjv()
            
            # Verify final state
            success = await self.verify_final_state()
            
            # Summary
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 50)
            if success:
                print("🎉 BIBLE VERSION FIX COMPLETE!")
            else:
                print("❌ BIBLE VERSION FIX FAILED!")
                
            print(f"⏱️  Processing time: {processing_time:.1f} seconds")
            print(f"🗑️  Deleted: {deleted_verses} verses, {deleted_books} books")
            print(f"🔄 Updated: {updated_verses} verses, {updated_books} books")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during version fix: {e}")
            return False
        
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    fixer = BibleVersionFixer()
    await fixer.run_fix()

if __name__ == "__main__":
    asyncio.run(main())