#!/usr/bin/env python3
"""
Fix thepreceptbible.com extracted verses by adding proper version identifiers
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

class VersionFixer:
    """Add version identifiers to extracted Bible data"""
    
    def __init__(self):
        # MongoDB connection
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        self.stats = {
            'verses_updated': 0,
            'books_updated': 0,
            'total_verses': 0,
            'total_books': 0
        }
    
    async def analyze_database(self):
        """Analyze what's currently in the database"""
        
        print("🔍 Analyzing database content...")
        
        # Check verses
        total_verses = await self.db.bible_verses.count_documents({})
        verses_with_version = await self.db.bible_verses.count_documents({'version': {'$exists': True}})
        verses_without_version = await self.db.bible_verses.count_documents({'version': {'$exists': False}})
        
        # Check books  
        total_books = await self.db.bible_books.count_documents({})
        books_with_version = await self.db.bible_books.count_documents({'version': {'$exists': True}})
        books_without_version = await self.db.bible_books.count_documents({'version': {'$exists': False}})
        
        print(f"📊 VERSES:")
        print(f"   Total verses: {total_verses}")
        print(f"   With version: {verses_with_version}")
        print(f"   Without version: {verses_without_version}")
        
        print(f"📚 BOOKS:")
        print(f"   Total books: {total_books}")
        print(f"   With version: {books_with_version}")
        print(f"   Without version: {books_without_version}")
        
        # Check which versions exist
        existing_versions = await self.db.bible_verses.distinct('version')
        print(f"🏷️  Existing versions: {existing_versions}")
        
        self.stats.update({
            'total_verses': total_verses,
            'total_books': total_books,
            'verses_without_version': verses_without_version,
            'books_without_version': books_without_version
        })
        
        return verses_without_version > 0 or books_without_version > 0
    
    async def fix_verses(self):
        """Add kjv1611_divine version to verses without version"""
        
        print("\n📝 Updating verses without version identifier...")
        
        result = await self.db.bible_verses.update_many(
            {'version': {'$exists': False}},
            {
                '$set': {
                    'version': 'kjv1611_divine',
                    'source': 'thepreceptbible.com',
                    'updatedAt': datetime.now(timezone.utc)
                }
            }
        )
        
        self.stats['verses_updated'] = result.modified_count
        print(f"   ✅ Updated {result.modified_count} verses")
        
        return result.modified_count > 0
    
    async def fix_books(self):
        """Add kjv1611_divine version to books without version"""
        
        print("\n📚 Updating books without version identifier...")
        
        result = await self.db.bible_books.update_many(
            {'version': {'$exists': False}},
            {
                '$set': {
                    'version': 'kjv1611_divine',
                    'source': 'thepreceptbible.com',
                    'updatedAt': datetime.now(timezone.utc)
                }
            }
        )
        
        self.stats['books_updated'] = result.modified_count  
        print(f"   ✅ Updated {result.modified_count} books")
        
        return result.modified_count > 0
    
    async def verify_fix(self):
        """Verify the fix worked"""
        
        print("\n🔍 Verifying fix...")
        
        # Check kjv1611_divine version
        kjv_verses = await self.db.bible_verses.count_documents({'version': 'kjv1611_divine'})
        kjv_books = await self.db.bible_books.count_documents({'version': 'kjv1611_divine'})
        
        # Check yah_scriptures version
        yah_verses = await self.db.bible_verses.count_documents({'version': 'yah_scriptures'}) 
        yah_books = await self.db.bible_books.count_documents({'version': 'yah_scriptures'})
        
        print(f"📊 KJV 1611 (Divine Names): {kjv_books} books, {kjv_verses} verses")
        print(f"📊 Yah Scriptures: {yah_books} books, {yah_verses} verses") 
        print(f"📊 Total: {kjv_books + yah_books} books, {kjv_verses + yah_verses} verses")
        
        return kjv_verses > 0 and kjv_books > 0
    
    async def run_fix(self):
        """Run the complete version fix process"""
        
        start_time = datetime.now()
        print("🔧 Starting Version Fix Process")
        print("=" * 50)
        
        try:
            # Analyze current state
            needs_fix = await self.analyze_database()
            
            if not needs_fix:
                print("✅ No fixes needed - all data already has version identifiers!")
                return True
            
            # Apply fixes
            verses_updated = await self.fix_verses()
            books_updated = await self.fix_books()
            
            if not verses_updated and not books_updated:
                print("⚠️  No updates were made")
                return False
            
            # Verify fix
            success = await self.verify_fix()
            
            # Summary
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 50)
            if success:
                print("🎉 VERSION FIX COMPLETE!")
            else:
                print("❌ VERSION FIX FAILED!")
                
            print(f"⏱️  Processing time: {processing_time:.1f} seconds")
            print(f"📝 Verses updated: {self.stats['verses_updated']}")
            print(f"📚 Books updated: {self.stats['books_updated']}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during version fix: {e}")
            return False
        
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    fixer = VersionFixer()
    await fixer.run_fix()

if __name__ == "__main__":
    asyncio.run(main())