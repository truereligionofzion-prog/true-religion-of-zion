#!/usr/bin/env python3
"""
Fix the book ordering to follow proper biblical sequence
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

class BookOrderFixer:
    """Fix book ordering in the Bible"""
    
    def __init__(self):
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
        
        # Correct biblical order
        self.book_order = {
            # OLD TESTAMENT (1-39)
            'Genesis': 1,
            'Exodus': 2,
            'Leviticus': 3,
            'Numbers': 4,
            'Deuteronomy': 5,
            'Joshua': 6,
            'Judges': 7,
            'Ruth': 8,
            '1 Samuel': 9,
            '2 Samuel': 10,
            '1 Kings': 11,
            '2 Kings': 12,
            '1 Chronicles': 13,
            '2 Chronicles': 14,
            'Ezra': 15,
            'Nehemiah': 16,
            'Esther': 17,
            'Job': 18,
            'Psalms': 19,
            'Proverbs': 20,
            'Ecclesiastes': 21,
            'Song of Songs': 22,
            'Isaiah': 23,
            'Jeremiah': 24,
            'Lamentations': 25,
            'Ezekiel': 26,
            'Daniel': 27,
            'Hosea': 28,
            'Joel': 29,
            'Amos': 30,
            'Obadiah': 31,
            'Jonah': 32,
            'Micah': 33,
            'Nahum': 34,
            'Habakkuk': 35,
            'Zephaniah': 36,
            'Haggai': 37,
            'Zechariah': 38,
            'Malachi': 39,
            
            # NEW TESTAMENT (40-66)
            'Matthew': 40,
            'Mark': 41,
            'Luke': 42,
            'John': 43,
            'Acts': 44,
            'Romans': 45,
            '1 Corinthians': 46,
            '2 Corinthians': 47,
            'Galatians': 48,
            'Ephesians': 49,
            'Philippians': 50,
            'Colossians': 51,
            '1 Thessalonians': 52,
            '2 Thessalonians': 53,
            '1 Timothy': 54,
            '2 Timothy': 55,
            'Titus': 56,
            'Philemon': 57,
            'Hebrews': 58,
            'James': 59,
            '1 Peter': 60,
            '2 Peter': 61,
            '1 John': 62,
            '2 John': 63,
            '3 John': 64,
            'Jude': 65,
            'Revelation': 66,
            
            # APOCRYPHA (67-81)
            '1 Esdras': 67,
            '2 Esdras': 68,
            'Tobit': 69,
            'Judith': 70,
            'Additions to Esther': 71,
            'Wisdom of Solomon': 72,
            'Ecclesiasticus': 73,
            'Baruch': 74,
            'Letter of Jeremiah': 75,
            'Prayer of Azariah': 76,
            'Susanna': 77,
            'Bel and the Dragon': 78,
            'Prayer of Manasseh': 79,
            '1 Maccabees': 80,
            '2 Maccabees': 81
        }
    
    async def get_current_books(self):
        """Get current books from database"""
        
        print("📚 Getting current books from database...")
        
        books = await self.db.bible_books.find({
            'version': 'yah_scriptures'
        }).sort('order', 1).to_list(length=None)
        
        print(f"   Found {len(books)} books")
        
        # Show current order
        print("   Current order:")
        for i, book in enumerate(books[:10]):  # Show first 10
            print(f"      {book['order']:2d}. {book['name']}")
        if len(books) > 10:
            print(f"      ... and {len(books) - 10} more")
        
        return books
    
    async def fix_book_order(self):
        """Fix the book ordering"""
        
        print("\n🔧 Fixing book order...")
        
        updated_count = 0
        
        try:
            for book_name, correct_order in self.book_order.items():
                # Update the book order
                result = await self.db.bible_books.update_one(
                    {
                        'version': 'yah_scriptures',
                        'name': book_name
                    },
                    {
                        '$set': {'order': correct_order}
                    }
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"   ✅ Updated {book_name} to order {correct_order}")
                elif result.matched_count > 0:
                    print(f"   ℹ️ {book_name} already has correct order {correct_order}")
                else:
                    print(f"   ❌ Book not found: {book_name}")
            
            print(f"\n📊 Updated {updated_count} book orders")
            
            return updated_count
            
        except Exception as e:
            print(f"❌ Error fixing book order: {e}")
            return 0
    
    async def verify_book_order(self):
        """Verify the corrected book order"""
        
        print("\n🔍 Verifying corrected book order...")
        
        books = await self.db.bible_books.find({
            'version': 'yah_scriptures'
        }).sort('order', 1).to_list(length=None)
        
        print(f"   📚 Books in corrected order:")
        
        # Show by testament
        old_testament = [b for b in books if 1 <= b['order'] <= 39]
        new_testament = [b for b in books if 40 <= b['order'] <= 66]
        apocrypha = [b for b in books if b['order'] >= 67]
        
        print(f"\n   📖 OLD TESTAMENT ({len(old_testament)} books):")
        for book in old_testament[:5]:  # Show first 5
            print(f"      {book['order']:2d}. {book['name']}")
        if len(old_testament) > 5:
            print(f"      ... and {len(old_testament) - 5} more")
        
        print(f"\n   📖 NEW TESTAMENT ({len(new_testament)} books):")
        for book in new_testament[:5]:  # Show first 5
            print(f"      {book['order']:2d}. {book['name']}")
        if len(new_testament) > 5:
            print(f"      ... and {len(new_testament) - 5} more")
        
        print(f"\n   📖 APOCRYPHA ({len(apocrypha)} books):")
        for book in apocrypha:
            print(f"      {book['order']:2d}. {book['name']}")
        
        return True
    
    async def run_book_order_fix(self):
        """Run the complete book order fix"""
        
        print("🚀 FIXING BIBLE BOOK ORDER")
        print("=" * 50)
        
        try:
            # Get current books
            current_books = await self.get_current_books()
            
            # Fix the order
            updated_count = await self.fix_book_order()
            
            # Verify the fix
            await self.verify_book_order()
            
            print(f"\n🎉 BOOK ORDER FIX COMPLETED:")
            print(f"   ✅ Updated {updated_count} book orders")
            print(f"   📚 Total books: {len(current_books)}")
            print(f"   📖 Books now in proper biblical sequence")
            
            return True
            
        except Exception as e:
            print(f"❌ Book order fix failed: {e}")
            return False
            
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

async def main():
    fixer = BookOrderFixer()
    success = await fixer.run_book_order_fix()
    
    if success:
        print("\n✅ Book order fix completed successfully!")
    else:
        print("\n❌ Book order fix failed")

if __name__ == "__main__":
    asyncio.run(main())