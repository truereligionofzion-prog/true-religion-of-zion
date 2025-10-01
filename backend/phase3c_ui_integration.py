#!/usr/bin/env python3
"""
Phase 3C: UI Integration & Enhancement
Prepare the frontend for complete Bible integration with advanced features
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json

class UIIntegrationEnhancer:
    """Enhance UI integration for complete Bible"""
    
    def __init__(self):
        # MongoDB connection
        self.MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.MONGO_URL)
        self.db = self.client[os.environ.get('DB_NAME', 'test_database')]
    
    async def analyze_bible_content(self):
        """Analyze current Bible content for UI enhancements"""
        print("📊 Phase 3C: Analyzing Bible Content for UI Integration")
        print("=" * 60)
        
        # Get current database statistics
        total_verses = await self.db.bible_verses.count_documents({})
        books = await self.db.bible_verses.distinct('book')
        
        print(f"📚 Current Bible Database:")
        print(f"   📖 Books: {len(books)}")
        print(f"   📝 Total verses: {total_verses:,}")
        
        # Analyze book structure
        book_stats = {}
        for book in sorted(books):
            verse_count = await self.db.bible_verses.count_documents({'book': book})
            chapters = await self.db.bible_verses.distinct('chapter', {'book': book})
            
            book_stats[book] = {
                'verses': verse_count,
                'chapters': len(chapters),
                'max_chapter': max(chapters) if chapters else 0
            }
            
            print(f"   📖 {book}: {verse_count} verses, {len(chapters)} chapters")
        
        # Analyze divine names usage
        yhwh_verses = await self.db.bible_verses.count_documents({'text': {'$regex': 'YHWH', '$options': 'i'}})
        elohim_verses = await self.db.bible_verses.count_documents({'text': {'$regex': 'Elohim', '$options': 'i'}})
        yhuh_verses = await self.db.bible_verses.count_documents({'text': {'$regex': 'YHUH', '$options': 'i'}})
        
        print(f"\\n✨ Divine Names Analysis:")
        print(f"   🔥 YHWH: {yhwh_verses:,} verses")
        print(f"   ⭐ Elohim: {elohim_verses:,} verses") 
        print(f"   💫 YHUH: {yhuh_verses:,} verses")
        
        # Check for precepts integration
        precept_verses = await self.db.bible_verses.count_documents({'has_precept': True})
        print(f"   📜 Verses with precepts: {precept_verses:,}")
        
        return {
            'total_verses': total_verses,
            'total_books': len(books),
            'book_stats': book_stats,
            'divine_names': {
                'yhwh': yhwh_verses,
                'elohim': elohim_verses,
                'yhuh': yhuh_verses
            },
            'precept_verses': precept_verses
        }
    
    async def generate_ui_enhancements(self, bible_stats):
        """Generate UI enhancement recommendations"""
        print("\\n🎨 UI Enhancement Recommendations:")
        print("=" * 50)
        
        enhancements = []
        
        # Book navigation enhancement
        if bible_stats['total_books'] > 50:
            enhancements.append({
                'type': 'navigation',
                'priority': 'high',
                'description': 'Enhanced book navigation with Old Testament/New Testament/Apocrypha sections',
                'reason': f"With {bible_stats['total_books']} books, organized navigation is essential"
            })
        
        # Search enhancement
        if bible_stats['total_verses'] > 10000:
            enhancements.append({
                'type': 'search',
                'priority': 'high', 
                'description': 'Advanced search with book, chapter, verse filters',
                'reason': f"With {bible_stats['total_verses']:,} verses, powerful search is needed"
            })
        
        # Divine names highlighting
        if bible_stats['divine_names']['yhwh'] > 0 or bible_stats['divine_names']['elohim'] > 0:
            enhancements.append({
                'type': 'highlighting',
                'priority': 'medium',
                'description': 'Divine name highlighting (YHWH, Elohim, YHUH)',
                'reason': f"Ancient Hebrew divine names appear in {bible_stats['divine_names']['yhwh'] + bible_stats['divine_names']['elohim']:,} verses"
            })
        
        # Chapter navigation
        max_chapters = max([book['max_chapter'] for book in bible_stats['book_stats'].values()])
        if max_chapters > 10:
            enhancements.append({
                'type': 'chapter_nav',
                'priority': 'medium',
                'description': 'Chapter-by-chapter navigation within books',
                'reason': f"Books have up to {max_chapters} chapters, need easy navigation"
            })
        
        # Cross-reference system
        if bible_stats['precept_verses'] > 0:
            enhancements.append({
                'type': 'cross_reference',
                'priority': 'high',
                'description': 'Cross-reference between Bible verses and precepts',
                'reason': f"{bible_stats['precept_verses']:,} verses have precept connections"
            })
        
        for enhancement in enhancements:
            priority_icon = "🔥" if enhancement['priority'] == 'high' else "⭐" if enhancement['priority'] == 'medium' else "💡"
            print(f"   {priority_icon} {enhancement['type'].upper()}: {enhancement['description']}")
            print(f"      Reason: {enhancement['reason']}")
            print()
        
        return enhancements
    
    async def prepare_api_enhancements(self):
        """Prepare API endpoint enhancements for complete Bible"""
        print("🔧 API Enhancement Preparation:")
        print("=" * 40)
        
        # Test current API endpoints
        current_books = await self.db.bible_verses.distinct('book')
        
        api_enhancements = {
            'new_endpoints': [
                '/api/bible/books/categories',  # OT/NT/Apocrypha categorization
                '/api/bible/search/advanced',   # Advanced search with filters
                '/api/bible/chapters/{book}',   # Chapter listing for book
                '/api/bible/verse/{book}/{chapter}/{verse}',  # Single verse lookup
                '/api/bible/cross-references',  # Cross-reference system
                '/api/bible/divine-names/search'  # Divine name specific search
            ],
            'enhanced_endpoints': [
                '/api/bible/books',  # Enhanced with categorization
                '/api/bible/verses', # Enhanced with pagination and filtering
                '/api/bible-stats'   # Enhanced with divine name statistics
            ],
            'current_books': current_books
        }
        
        print(f"📊 Current API Status:")
        print(f"   📚 Books available: {len(current_books)}")
        print(f"   🔧 New endpoints needed: {len(api_enhancements['new_endpoints'])}")
        print(f"   ⚡ Enhancements needed: {len(api_enhancements['enhanced_endpoints'])}")
        
        return api_enhancements
    
    async def generate_integration_plan(self):
        """Generate comprehensive integration plan"""
        print("\\n📋 Phase 3C Integration Plan:")
        print("=" * 45)
        
        bible_stats = await self.analyze_bible_content()
        ui_enhancements = await self.generate_ui_enhancements(bible_stats)
        api_enhancements = await self.prepare_api_enhancements()
        
        integration_plan = {
            'phase': '3C',
            'status': 'ready',
            'bible_stats': bible_stats,
            'ui_enhancements': ui_enhancements,
            'api_enhancements': api_enhancements,
            'implementation_priority': [
                '1. Enhanced book navigation',
                '2. Advanced search functionality', 
                '3. Divine name highlighting',
                '4. Cross-reference system',
                '5. Chapter navigation',
                '6. Performance optimization'
            ]
        }
        
        # Save integration plan
        with open('/app/backend/phase3c_integration_plan.json', 'w') as f:
            json.dump(integration_plan, f, indent=2)
        
        print(f"✅ Integration plan created and saved")
        print(f"🎯 Ready to implement UI enhancements for complete Bible")
        
        return integration_plan

if __name__ == "__main__":
    async def main():
        enhancer = UIIntegrationEnhancer()
        await enhancer.generate_integration_plan()
        
        print(f"\\n🚀 Phase 3C Complete!")
        print(f"📊 Analysis done, enhancements identified, plan created")
        print(f"🔄 While Phase 3B continues extraction, UI is ready for enhancement")
    
    asyncio.run(main())