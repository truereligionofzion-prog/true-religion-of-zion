from fastapi import FastAPI, APIRouter, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import math
import re
import uuid
from datetime import datetime, timezone, timedelta

from models import (
    Mitzvah, MitzvahCreate, Category, CategoryCreate, 
    MitzvotResponse, StatsResponse, UserCreate, UserLogin, 
    UserProfile, AuthResponse
)
from data_loader import load_mitzvot_data, get_categories

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Collections
mitzvot_collection = db.mitzvot
categories_collection = db.categories
precepts_collection = db.precepts
bible_verses_collection = db.bible_verses
bible_books_collection = db.bible_books

# Create the main app
app = FastAPI(title="613 Biblical Laws API")

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_router.get("/")
async def root():
    return {"message": "613 Biblical Laws API", "version": "1.0"}

@api_router.post("/initialize")
async def initialize_data():
    """Initialize database with 613 mitzvot and categories"""
    try:
        # Clear existing data
        await mitzvot_collection.delete_many({})
        await categories_collection.delete_many({})
        
        # Load categories
        categories_data = get_categories()
        for cat_data in categories_data:
            category = Category(**cat_data.dict())
            await categories_collection.insert_one(category.dict())
        
        # Load mitzvot from data_loader
        from data_loader import load_mitzvot_data
        mitzvot_data = load_mitzvot_data()
        
        # Convert to Mitzvah objects and insert
        all_mitzvot = []
        for mitzvah_create in mitzvot_data:
            mitzvah = Mitzvah(**mitzvah_create.dict())
            all_mitzvot.append(mitzvah.dict())
        
        # Insert all mitzvot
        await mitzvot_collection.insert_many(all_mitzvot)
        
        return {
            "message": "Database initialized successfully",
            "mitzvot_count": len(all_mitzvot),
            "categories_count": len(categories_data)
        }
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mitzvot", response_model=MitzvotResponse)
async def get_mitzvot(
    search: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    book: Optional[str] = Query(None, description="Filter by book"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get all mitzvot with optional filtering and pagination - status parameter removed in new structure"""
    try:
        # Build query
        query = {}
        
        if category and category != "all":
            query["category"] = category
            
        if book and book != "all":
            query["book"] = book
        
        # Enhanced text search across all fields
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"title": search_regex},
                {"sourceVerse": search_regex},
                {"book": search_regex},
                {"keywords": {"$in": [re.compile(search, re.IGNORECASE)]}}
            ]
        
        # Get total count
        total = await mitzvot_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        total_pages = math.ceil(total / limit)
        
        # Get mitzvot
        cursor = mitzvot_collection.find(query).sort("number", 1).skip(skip).limit(limit)
        mitzvot_data = await cursor.to_list(length=limit)
        
        # Convert MongoDB documents to Pydantic models
        mitzvot = []
        for m in mitzvot_data:
            # Remove MongoDB _id field
            if '_id' in m:
                del m['_id']
            mitzvot.append(Mitzvah(**m))
        
        # Get filter options
        categories_data = await categories_collection.find().sort("order", 1).to_list(length=None)
        categories = []
        for cat in categories_data:
            if '_id' in cat:
                del cat['_id']
            categories.append(cat)
        books = await mitzvot_collection.distinct("book")
        books.sort()
        
        return MitzvotResponse(
            mitzvot=mitzvot,
            total=total,
            page=page,
            totalPages=total_pages,
            filters={
                "categories": categories,
                "books": books
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting mitzvot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mitzvot/{mitzvah_id}")
async def get_mitzvah(mitzvah_id: str):
    """Get specific mitzvah by ID"""
    try:
        mitzvah_data = await mitzvot_collection.find_one({"id": mitzvah_id})
        if not mitzvah_data:
            raise HTTPException(status_code=404, detail="Mitzvah not found")
        
        # Remove MongoDB _id field
        if '_id' in mitzvah_data:
            del mitzvah_data['_id']
        
        return Mitzvah(**mitzvah_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mitzvah: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/categories")
async def get_categories_endpoint():
    """Get all categories"""
    try:
        categories_data = await categories_collection.find().sort("order", 1).to_list(length=None)
        
        # Add counts and clean MongoDB fields
        categories = []
        for category in categories_data:
            if '_id' in category:
                del category['_id']
            count = await mitzvot_collection.count_documents({"category": category["slug"]})
            category["count"] = count
            categories.append(category)
        
        return categories
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get summary statistics"""
    try:
        total_mitzvot = await mitzvot_collection.count_documents({})
        categories_count = await categories_collection.count_documents({})
        books_count = len(await mitzvot_collection.distinct("book"))
        
        return StatsResponse(
            totalMitzvot=total_mitzvot,
            categoriesCount=categories_count,
            booksCount=books_count
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PRECEPTS API ENDPOINTS =====

@api_router.get("/precepts")
async def get_precepts(
    testament: Optional[str] = Query(None, description="Filter by testament: old, new, mixed"),
    search: Optional[str] = Query(None, description="Search in title, topics, and verse text"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get all precepts with optional filtering and pagination"""
    try:
        # Build query
        query = {}
        
        if testament and testament != "all":
            query["testament"] = testament
        
        # Enhanced text search across all fields
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"title": search_regex},
                {"topics": {"$in": [re.compile(search, re.IGNORECASE)]}},
                {"verses.text": search_regex},
                {"verses.book": search_regex}
            ]
        
        # Get total count
        total = await precepts_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        total_pages = math.ceil(total / limit)
        
        # Get precepts
        cursor = precepts_collection.find(query).sort("title", 1).skip(skip).limit(limit)
        precepts_data = await cursor.to_list(length=limit)
        
        # Clean MongoDB documents
        precepts = []
        for p in precepts_data:
            if '_id' in p:
                del p['_id']
            precepts.append(p)
        
        # Get filter options
        testaments = await precepts_collection.distinct("testament")
        testaments.sort()
        
        return {
            "precepts": precepts,
            "total": total,
            "page": page,
            "totalPages": total_pages,
            "filters": {
                "testaments": testaments
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting precepts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/precepts/{precept_id}")
async def get_precept(precept_id: str):
    """Get a specific precept by ID"""
    try:
        precept = await precepts_collection.find_one({"id": precept_id})
        
        if not precept:
            raise HTTPException(status_code=404, detail="Precept not found")
        
        # Remove MongoDB _id field
        if '_id' in precept:
            del precept['_id']
        
        return precept
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting precept {precept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/precepts-stats")
async def get_precepts_stats():
    """Get precepts summary statistics"""
    try:
        total_precepts = await precepts_collection.count_documents({})
        
        # Count by testament
        old_testament = await precepts_collection.count_documents({"testament": "old"})
        new_testament = await precepts_collection.count_documents({"testament": "new"})
        mixed_testament = await precepts_collection.count_documents({"testament": "mixed"})
        
        # Count unique topics
        all_topics = []
        async for precept in precepts_collection.find({}, {"topics": 1}):
            if precept.get("topics"):
                all_topics.extend(precept["topics"])
        unique_topics = len(set(all_topics))
        
        # Count total verses
        total_verses = 0
        async for precept in precepts_collection.find({}, {"verse_count": 1}):
            total_verses += precept.get("verse_count", 0)
        
        return {
            "totalPrecepts": total_precepts,
            "oldTestament": old_testament,
            "newTestament": new_testament,
            "mixedTestament": mixed_testament,
            "uniqueTopics": unique_topics,
            "totalVerses": total_verses
        }
        
    except Exception as e:
        logger.error(f"Error getting precepts stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== BIBLE API ENDPOINTS =====

@api_router.get("/bible/books")
async def get_bible_books(
    testament: Optional[str] = Query(None, description="Filter by testament: old, new, apocrypha")
):
    """Get all Bible books with metadata"""
    try:
        # Build query
        query = {}
        if testament and testament != "all":
            query["testament"] = testament
        
        # Get books
        cursor = bible_books_collection.find(query).sort("order", 1)
        books_data = await cursor.to_list(length=None)
        
        # Clean MongoDB documents
        books = []
        for book in books_data:
            if '_id' in book:
                del book['_id']
            books.append(book)
        
        # Get available testaments
        testaments = await bible_books_collection.distinct("testament")
        testaments.sort()
        
        return {
            "books": books,
            "total": len(books),
            "filters": {
                "testaments": testaments
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting bible books: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bible/verses")
async def get_bible_verses(
    book: Optional[str] = Query(None, description="Filter by book name"),
    chapter: Optional[int] = Query(None, description="Filter by chapter number"),
    testament: Optional[str] = Query(None, description="Filter by testament: old, new, apocrypha"),
    search: Optional[str] = Query(None, description="Search in verse text"),
    has_precept: Optional[bool] = Query(None, description="Filter verses with precept connections"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get Bible verses with filtering and pagination"""
    try:
        # Build query
        query = {}
        
        if book:
            query["book"] = book
        
        if chapter is not None:
            query["chapter"] = chapter
        
        if testament and testament != "all":
            query["testament"] = testament
            
        if has_precept is not None:
            query["has_precept"] = has_precept
        
        # Text search
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["text"] = search_regex
        
        # Get total count
        total = await bible_verses_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        total_pages = math.ceil(total / limit)
        
        # Get verses without sorting first (to avoid comparison errors)
        cursor = bible_verses_collection.find(query).skip(skip).limit(limit)
        verses_data = await cursor.to_list(length=limit)
        
        # Sort manually after ensuring proper data types
        def safe_sort_key(verse):
            book = verse.get('book') or ''
            chapter = verse.get('chapter')
            verse_num = verse.get('verse')
            
            # Ensure chapter and verse are integers
            try:
                chapter = int(chapter) if chapter is not None else 0
            except (ValueError, TypeError):
                chapter = 0
                
            try:
                verse_num = int(verse_num) if verse_num is not None else 0
            except (ValueError, TypeError):
                verse_num = 0
                
            return (book, chapter, verse_num)
        
        verses_data.sort(key=safe_sort_key)
        
        # Remove any duplicate verses (same book, chapter, verse)
        seen_verses = set()
        unique_verses = []
        for verse in verses_data:
            # Handle None values to prevent comparison errors
            book = verse.get('book') or ''
            chapter = verse.get('chapter') or 0
            verse_num = verse.get('verse') or 0
            verse_key = (book, chapter, verse_num)
            if verse_key not in seen_verses:
                seen_verses.add(verse_key)
                unique_verses.append(verse)
        
        verses_data = unique_verses
        
        # Clean MongoDB documents
        verses = []
        for verse in verses_data:
            if '_id' in verse:
                del verse['_id']
            verses.append(verse)
        
        # Get filter options
        books = await bible_verses_collection.distinct("book")
        testaments = await bible_verses_collection.distinct("testament")
        books.sort()
        testaments.sort()
        
        return {
            "verses": verses,
            "total": total,
            "page": page,
            "totalPages": total_pages,
            "filters": {
                "books": books,
                "testaments": testaments
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting bible verses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bible/verses/{book}/{chapter}")
async def get_bible_chapter(book: str, chapter: int):
    """Get all verses for a specific chapter"""
    try:
        # Get verses for the chapter
        query = {"book": book, "chapter": chapter}
        cursor = bible_verses_collection.find(query).sort("verse", 1)
        verses_data = await cursor.to_list(length=None)
        
        if not verses_data:
            raise HTTPException(status_code=404, detail=f"{book} {chapter} not found")
        
        # Clean MongoDB documents
        verses = []
        for verse in verses_data:
            if '_id' in verse:
                del verse['_id']
            verses.append(verse)
        
        # Get chapter metadata
        book_data = await bible_books_collection.find_one({"name": book})
        testament = book_data.get("testament", "unknown") if book_data else "unknown"
        
        return {
            "book": book,
            "chapter": chapter,
            "testament": testament,
            "verses": verses,
            "verse_count": len(verses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chapter {book} {chapter}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bible/verse/{book}/{chapter}/{verse}")
async def get_bible_verse(book: str, chapter: int, verse: int):
    """Get a specific verse"""
    try:
        query = {"book": book, "chapter": chapter, "verse": verse}
        verse_data = await bible_verses_collection.find_one(query)
        
        if not verse_data:
            raise HTTPException(status_code=404, detail=f"{book} {chapter}:{verse} not found")
        
        # Remove MongoDB _id field
        if '_id' in verse_data:
            del verse_data['_id']
        
        return verse_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting verse {book} {chapter}:{verse}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bible/stats")
async def get_bible_stats():
    """Get Bible summary statistics"""
    try:
        total_books = await bible_books_collection.count_documents({})
        total_verses = await bible_verses_collection.count_documents({})
        
        # Count by testament
        old_testament_books = await bible_books_collection.count_documents({"testament": "old"})
        new_testament_books = await bible_books_collection.count_documents({"testament": "new"})
        apocrypha_books = await bible_books_collection.count_documents({"testament": "apocrypha"})
        
        old_testament_verses = await bible_verses_collection.count_documents({"testament": "old"})
        new_testament_verses = await bible_verses_collection.count_documents({"testament": "new"})
        apocrypha_verses = await bible_verses_collection.count_documents({"testament": "apocrypha"})
        
        # Count verses with precepts
        verses_with_precepts = await bible_verses_collection.count_documents({"has_precept": True})
        
        # Get unique chapters count
        pipeline = [
            {"$group": {"_id": {"book": "$book", "chapter": "$chapter"}}},
            {"$count": "total_chapters"}
        ]
        result = await bible_verses_collection.aggregate(pipeline).to_list(1)
        total_chapters = result[0]["total_chapters"] if result else 0
        
        return {
            "totalBooks": total_books,
            "totalChapters": total_chapters,
            "totalVerses": total_verses,
            "oldTestamentBooks": old_testament_books,
            "newTestamentBooks": new_testament_books,
            "apocryphaBooks": apocrypha_books,
            "oldTestamentVerses": old_testament_verses,
            "newTestamentVerses": new_testament_verses,
            "apocryphaVerses": apocrypha_verses,
            "versesWithPrecepts": verses_with_precepts
        }
        
    except Exception as e:
        logger.error(f"Error getting bible stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== PHASE 3C: ADVANCED BIBLE ENHANCEMENTS =====

@api_router.get("/bible/search/advanced")
async def advanced_bible_search(
    search_text: Optional[str] = Query(None, description="Text to search for"),
    books: Optional[str] = Query(None, description="Comma-separated list of books"),
    testament: Optional[str] = Query(None, description="Filter by testament: old, new, apocrypha"),
    chapters: Optional[str] = Query(None, description="Chapter range (e.g., '1-5' or '1,3,5')"),
    has_precept: Optional[bool] = Query(None, description="Filter verses with precept connections"),
    divine_names: Optional[bool] = Query(None, description="Filter verses with divine names (YHWH, Elohim, YHUH)"),
    exact_match: Optional[bool] = Query(False, description="Use exact phrase matching"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Advanced search with multiple filters and divine name highlighting"""
    try:
        # Build advanced query
        query = {}
        
        # Text search with exact/fuzzy matching
        if search_text:
            if exact_match:
                query["text"] = {"$regex": f"\\b{re.escape(search_text)}\\b", "$options": "i"}
            else:
                # Split search terms and search for any
                terms = search_text.split()
                term_queries = [{"text": {"$regex": term, "$options": "i"}} for term in terms]
                query["$or"] = term_queries
        
        # Books filter
        if books:
            book_list = [book.strip() for book in books.split(",")]
            query["book"] = {"$in": book_list}
        
        # Testament filter
        if testament and testament != "all":
            query["testament"] = testament
        
        # Precept filter
        if has_precept is not None:
            query["has_precept"] = has_precept
        
        # Divine names filter
        if divine_names:
            divine_name_query = {
                "$or": [
                    {"text": {"$regex": "YHWH", "$options": "i"}},
                    {"text": {"$regex": "Elohim", "$options": "i"}}, 
                    {"text": {"$regex": "YHUH", "$options": "i"}}
                ]
            }
            if "$or" in query:
                query = {"$and": [query, divine_name_query]}
            else:
                query.update(divine_name_query)
        
        # Get total count
        total = await bible_verses_collection.count_documents(query)
        
        # Pagination
        skip = (page - 1) * limit
        total_pages = math.ceil(total / limit)
        
        # Get results with sorting
        cursor = bible_verses_collection.find(query).sort([("book", 1), ("chapter", 1), ("verse", 1)]).skip(skip).limit(limit)
        verses_data = await cursor.to_list(length=limit)
        
        # Clean and enhance results
        enhanced_verses = []
        for verse in verses_data:
            if '_id' in verse:
                del verse['_id']
            
            # Add divine name highlighting info
            verse_text = verse.get('text', '')
            verse['divine_names'] = {
                'has_yhwh': 'YHWH' in verse_text,
                'has_elohim': 'Elohim' in verse_text,
                'has_yhuh': 'YHUH' in verse_text
            }
            
            enhanced_verses.append(verse)
        
        # Get search statistics
        search_stats = {
            'total_matches': total,
            'books_matched': len(await bible_verses_collection.distinct("book", query)),
            'testaments_matched': len(await bible_verses_collection.distinct("testament", query))
        }
        
        return {
            "verses": enhanced_verses,
            "total": total,
            "page": page,
            "totalPages": total_pages,
            "searchStats": search_stats,
            "query_info": {
                "search_text": search_text,
                "exact_match": exact_match,
                "books_filter": books,
                "testament_filter": testament,
                "divine_names_filter": divine_names
            }
        }
        
    except Exception as e:
        logger.error(f"Error in advanced bible search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bible/cross-references")
async def get_cross_references(
    book: Optional[str] = Query(None, description="Book name"),
    chapter: Optional[int] = Query(None, description="Chapter number"),
    verse: Optional[int] = Query(None, description="Verse number")
):
    """Get cross-references between Bible verses and precepts"""
    try:
        # Build query for Bible verse
        bible_query = {}
        if book:
            bible_query["book"] = book
        if chapter:
            bible_query["chapter"] = chapter
        if verse:
            bible_query["verse"] = verse
        
        # Add precept filter
        bible_query["has_precept"] = True
        
        # Get Bible verses with precept connections
        bible_verses = await bible_verses_collection.find(bible_query).sort([("book", 1), ("chapter", 1), ("verse", 1)]).to_list(length=100)
        
        cross_references = []
        for bible_verse in bible_verses:
            # Find related precepts by searching for this verse reference
            verse_ref = f"{bible_verse['book']} {bible_verse['chapter']}:{bible_verse['verse']}"
            
            # Search precepts that reference this verse
            precept_query = {
                "verses.book": bible_verse['book'],
                "verses.chapter": bible_verse['chapter'], 
                "verses.verse": bible_verse['verse']
            }
            
            related_precepts = await precepts_collection.find(precept_query).to_list(length=10)
            
            if related_precepts:
                # Clean precepts data
                clean_precepts = []
                for precept in related_precepts:
                    if '_id' in precept:
                        del precept['_id']
                    clean_precepts.append({
                        'title': precept.get('title'),
                        'topic': precept.get('topic'), 
                        'verse_count': len(precept.get('verses', []))
                    })
                
                # Clean Bible verse data
                if '_id' in bible_verse:
                    del bible_verse['_id']
                
                cross_references.append({
                    'bible_verse': bible_verse,
                    'related_precepts': clean_precepts,
                    'connection_count': len(clean_precepts)
                })
        
        return {
            "cross_references": cross_references,
            "total_connections": len(cross_references),
            "search_criteria": {
                "book": book,
                "chapter": chapter,
                "verse": verse
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting cross references: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bible/divine-names/search")
async def search_divine_names(
    divine_name: Optional[str] = Query(None, description="Specific divine name: YHWH, Elohim, YHUH"),
    book: Optional[str] = Query(None, description="Filter by book"),
    testament: Optional[str] = Query(None, description="Filter by testament"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page")
):
    """Search specifically for divine names with statistics"""
    try:
        # Build divine name query
        query = {}
        
        if divine_name:
            query["text"] = {"$regex": divine_name, "$options": "i"}
        else:
            # Search for any divine name
            query["$or"] = [
                {"text": {"$regex": "YHWH", "$options": "i"}},
                {"text": {"$regex": "Elohim", "$options": "i"}},
                {"text": {"$regex": "YHUH", "$options": "i"}}
            ]
        
        # Additional filters
        if book:
            query["book"] = book
        if testament and testament != "all":
            query["testament"] = testament
        
        # Get results with pagination
        total = await bible_verses_collection.count_documents(query)
        skip = (page - 1) * limit
        total_pages = math.ceil(total / limit)
        
        cursor = bible_verses_collection.find(query).sort([("book", 1), ("chapter", 1), ("verse", 1)]).skip(skip).limit(limit)
        verses_data = await cursor.to_list(length=limit)
        
        # Analyze divine name occurrences
        divine_name_stats = {
            'yhwh_count': 0,
            'elohim_count': 0,
            'yhuh_count': 0,
            'total_verses': len(verses_data)
        }
        
        enhanced_verses = []
        for verse in verses_data:
            if '_id' in verse:
                del verse['_id']
            
            # Count divine names in this verse
            verse_text = verse.get('text', '')
            yhwh_in_verse = verse_text.count('YHWH')
            elohim_in_verse = verse_text.count('Elohim') 
            yhuh_in_verse = verse_text.count('YHUH')
            
            divine_name_stats['yhwh_count'] += yhwh_in_verse
            divine_name_stats['elohim_count'] += elohim_in_verse
            divine_name_stats['yhuh_count'] += yhuh_in_verse
            
            # Add divine name info to verse
            verse['divine_name_analysis'] = {
                'yhwh_count': yhwh_in_verse,
                'elohim_count': elohim_in_verse,
                'yhuh_count': yhuh_in_verse,
                'total_divine_names': yhwh_in_verse + elohim_in_verse + yhuh_in_verse
            }
            
            enhanced_verses.append(verse)
        
        return {
            "verses": enhanced_verses,
            "total": total,
            "page": page,
            "totalPages": total_pages,
            "divine_name_statistics": divine_name_stats,
            "search_info": {
                "divine_name_filter": divine_name,
                "book_filter": book,
                "testament_filter": testament
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching divine names: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mitzvah-of-the-day", response_model=Mitzvah)
async def get_mitzvah_of_the_day():
    """Get the daily featured mitzvah"""
    import datetime
    try:
        # Use date-based algorithm to ensure same mitzvah per day for all users
        today = datetime.date.today()
        
        # Create a deterministic seed based on the date
        day_of_year = today.timetuple().tm_yday
        year = today.year
        
        # Calculate mitzvah number (1-613) based on date
        # This ensures the same mitzvah for everyone on the same day
        # and cycles through all mitzvot over ~1.7 years
        mitzvah_number = ((day_of_year + (year * 365)) % 613) + 1
        
        # Get the specific mitzvah by number
        mitzvah = await mitzvot_collection.find_one({"number": mitzvah_number})
        
        if not mitzvah:
            # Fallback to first mitzvah if something goes wrong
            mitzvah = await mitzvot_collection.find_one({"number": 1})
        
        if not mitzvah:
            raise HTTPException(status_code=404, detail="No mitzvot found")
        
        # Convert MongoDB document to Mitzvah model
        mitzvah_obj = Mitzvah(**mitzvah)
        return mitzvah_obj
        
    except Exception as e:
        logger.error(f"Error getting mitzvah of the day: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/quiz/{category}")
async def get_quiz_questions(category: str = "all", limit: int = 5):
    """Generate quiz questions for a specific category"""
    import random
    try:
        # Validate category exists (unless "all")
        if category != "all":
            valid_categories = [cat["slug"] for cat in await categories_collection.find({}).to_list(length=None)]
            if category not in valid_categories:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}. Valid categories: {valid_categories}")
        
        # Build query based on category
        query = {}
        if category != "all":
            query["category"] = category
        
        # Get ALL mitzvot for diverse wrong answers (not just from selected category)
        all_mitzvot_for_questions = await mitzvot_collection.find({}).to_list(length=None)
        
        if len(all_mitzvot_for_questions) < 4:  # Need at least 4 for multiple choice
            raise HTTPException(status_code=400, detail="Not enough mitzvot in database for quiz")
        
        # Randomly select mitzvot for questions from the specified category
        if category != "all":
            category_mitzvot = [m for m in all_mitzvot_for_questions if m["category"] == category]
            if len(category_mitzvot) < 1:
                raise HTTPException(status_code=400, detail="No mitzvot found in specified category")
            selected_mitzvot = random.sample(category_mitzvot, min(limit, len(category_mitzvot)))
        else:
            selected_mitzvot = random.sample(all_mitzvot_for_questions, min(limit, len(all_mitzvot_for_questions)))
        
        quiz_questions = []
        
        for mitzvah in selected_mitzvot:
            # Get diverse wrong answers from ALL mitzvot, ensuring variety
            other_mitzvot = [m for m in all_mitzvot_for_questions if m["number"] != mitzvah["number"]]
            
            # Create diverse wrong answers by mixing different categories, books, etc.
            diverse_wrong_answers = []
            
            # Try to get wrong answers from different categories
            different_categories = [m for m in other_mitzvot if m["category"] != mitzvah["category"]]
            if len(different_categories) >= 2:
                diverse_wrong_answers.extend(random.sample(different_categories, 2))
            
            # Add one from same category if available (for reasonable difficulty)
            same_category = [m for m in other_mitzvot if m["category"] == mitzvah["category"]]
            if len(same_category) >= 1 and len(diverse_wrong_answers) < 3:
                diverse_wrong_answers.extend(random.sample(same_category, min(1, 3 - len(diverse_wrong_answers))))
            
            # Fill remaining slots with any other mitzvot if needed
            while len(diverse_wrong_answers) < 3 and len(other_mitzvot) >= 3:
                remaining = [m for m in other_mitzvot if m not in diverse_wrong_answers]
                if remaining:
                    diverse_wrong_answers.append(random.choice(remaining))
                else:
                    break
            
            # Fallback to simple random selection if diversity approach fails
            if len(diverse_wrong_answers) < 3:
                diverse_wrong_answers = random.sample(other_mitzvot, 3)
            
            wrong_answers = diverse_wrong_answers[:3]  # Ensure exactly 3 wrong answers
            
            # Create meaningful question types for the new structure
            question_types = [
                "verse_from_title",
                "book_from_title", 
                "category_from_title",
                "title_from_verse"
            ]
            
            question_type = random.choice(question_types)
            
            if question_type == "verse_from_title":
                # Show title, ask for verse
                wrong_verses = []
                for wrong_answer in wrong_answers:
                    if wrong_answer["sourceVerse"] != mitzvah["sourceVerse"] and wrong_answer["sourceVerse"] not in wrong_verses:
                        # Show first 60 chars of verse for readability
                        verse_preview = wrong_answer["sourceVerse"][:60] + "..." if len(wrong_answer["sourceVerse"]) > 60 else wrong_answer["sourceVerse"]
                        wrong_verses.append(verse_preview)
                
                # Fill with more options if needed
                while len(wrong_verses) < 3:
                    additional_wrong = random.choice([m for m in other_mitzvot if m["sourceVerse"] != mitzvah["sourceVerse"]])
                    verse_preview = additional_wrong["sourceVerse"][:60] + "..." if len(additional_wrong["sourceVerse"]) > 60 else additional_wrong["sourceVerse"]
                    if verse_preview not in wrong_verses:
                        wrong_verses.append(verse_preview)
                
                correct_verse = mitzvah["sourceVerse"][:60] + "..." if len(mitzvah["sourceVerse"]) > 60 else mitzvah["sourceVerse"]
                
                question = {
                    "id": len(quiz_questions) + 1,
                    "type": "multiple_choice",
                    "question": f"Which biblical verse corresponds to: \"{mitzvah['title']}\"?",
                    "correct_answer": correct_verse,
                    "options": [correct_verse] + wrong_verses[:3],
                    "explanation": f"This is from {mitzvah['book']} {mitzvah['chapter']}:{mitzvah['verse']}. Full verse: {mitzvah['sourceVerse'][:150]}..."
                }
            
            elif question_type == "title_from_verse":
                # Show verse, ask for title
                wrong_titles = []
                for wrong_answer in wrong_answers:
                    if wrong_answer["title"] != mitzvah["title"] and wrong_answer["title"] not in wrong_titles:
                        wrong_titles.append(wrong_answer["title"])
                
                # Fill with more options if needed
                while len(wrong_titles) < 3:
                    additional_wrong = random.choice([m for m in other_mitzvot if m["title"] != mitzvah["title"] and m["title"] not in wrong_titles])
                    wrong_titles.append(additional_wrong["title"])
                
                verse_preview = mitzvah["sourceVerse"][:100] + "..." if len(mitzvah["sourceVerse"]) > 100 else mitzvah["sourceVerse"]
                
                question = {
                    "id": len(quiz_questions) + 1,
                    "type": "multiple_choice",
                    "question": f"Which mitzvah is derived from this verse: \"{verse_preview}\"?",
                    "correct_answer": mitzvah["title"],
                    "options": [mitzvah["title"]] + wrong_titles[:3],
                    "explanation": f"This verse from {mitzvah['book']} {mitzvah['chapter']}:{mitzvah['verse']} establishes the commandment: {mitzvah['title']}"
                }
            
            elif question_type == "book_from_title":
                # Show title, ask for book
                wrong_books = []
                for wrong_answer in wrong_answers:
                    if wrong_answer["book"] != mitzvah["book"] and wrong_answer["book"] not in wrong_books:
                        wrong_books.append(wrong_answer["book"])
                
                # Fill with more books if needed
                all_books = await mitzvot_collection.distinct("book")
                while len(wrong_books) < 3:
                    random_book = random.choice(all_books)
                    if random_book != mitzvah["book"] and random_book not in wrong_books:
                        wrong_books.append(random_book)
                
                question = {
                    "id": len(quiz_questions) + 1,
                    "type": "multiple_choice", 
                    "question": f"In which book of the Bible is this commandment found: \"{mitzvah['title']}\"?",
                    "correct_answer": mitzvah["book"],
                    "options": [mitzvah["book"]] + wrong_books[:3],
                    "explanation": f"This commandment is found in {mitzvah['book']} {mitzvah['chapter']}:{mitzvah['verse']}"
                }
            
            else:  # category_from_title
                # Get category name
                category_doc = await categories_collection.find_one({"slug": mitzvah["category"]})
                correct_category = category_doc["name"] if category_doc else mitzvah["category"]
                
                # Get unique wrong categories
                wrong_categories = []
                for wrong_mitzvah in wrong_answers:
                    wrong_cat_doc = await categories_collection.find_one({"slug": wrong_mitzvah["category"]})
                    wrong_cat_name = wrong_cat_doc["name"] if wrong_cat_doc else wrong_mitzvah["category"]
                    if wrong_cat_name != correct_category and wrong_cat_name not in wrong_categories:
                        wrong_categories.append(wrong_cat_name)
                
                # Fill with more categories if needed
                all_categories = await categories_collection.find({}).to_list(length=None)
                while len(wrong_categories) < 3:
                    random_cat = random.choice(all_categories)
                    cat_name = random_cat["name"]
                    if cat_name != correct_category and cat_name not in wrong_categories:
                        wrong_categories.append(cat_name)
                
                question = {
                    "id": len(quiz_questions) + 1,
                    "type": "multiple_choice", 
                    "question": f"Which category does this commandment belong to: \"{mitzvah['title']}\"?",
                    "correct_answer": correct_category,
                    "options": [correct_category] + wrong_categories[:3],
                    "explanation": f"This commandment belongs to {correct_category}. Found in {mitzvah['book']} {mitzvah['chapter']}:{mitzvah['verse']}"
                }
            
            # Shuffle options
            random.shuffle(question["options"])
            quiz_questions.append(question)
        
        return {
            "category": category,
            "questions": quiz_questions,
            "total_questions": len(quiz_questions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New collections for progress tracking
progress_collection = db["user_progress"]
sessions_collection = db["study_sessions"] 
flashcards_collection = db["flashcards"]
achievements_collection = db["achievements"]

# Simple user ID for now (in production, would use authentication)
DEFAULT_USER_ID = "user_001"

@api_router.get("/progress")
async def get_user_progress(user_id: str = DEFAULT_USER_ID):
    """Get user's learning progress"""
    try:
        # Get overall progress stats
        total_mitzvot = await mitzvot_collection.count_documents({})
        
        progress_records = await progress_collection.find({"userId": user_id}).to_list(length=None)
        
        learning_count = len([p for p in progress_records if p["status"] == "learning"])
        reviewing_count = len([p for p in progress_records if p["status"] == "reviewing"])  
        mastered_count = len([p for p in progress_records if p["status"] == "mastered"])
        
        # Calculate category progress
        category_progress = {}
        categories = await categories_collection.find({}).to_list(length=None)
        
        for category in categories:
            category_mitzvot = await mitzvot_collection.count_documents({"category": category["slug"]})
            # Use the 'id' field instead of MongoDB '_id' field to avoid ObjectId serialization issues
            category_mitzvot_ids = [str(m["id"]) for m in await mitzvot_collection.find({"category": category["slug"]}).to_list(length=None)]
            category_mastered = await progress_collection.count_documents({
                "userId": user_id,
                "status": "mastered",
                "mitzvahId": {"$in": category_mitzvot_ids}
            })
            
            category_progress[category["name"]] = {
                "total": category_mitzvot,
                "mastered": category_mastered,
                "percentage": round((category_mastered / category_mitzvot) * 100, 1) if category_mitzvot > 0 else 0
            }
        
        return {
            "userId": user_id,
            "totalMitzvot": total_mitzvot,
            "learning": learning_count,
            "reviewing": reviewing_count,
            "mastered": mastered_count,
            "overallProgress": round((mastered_count / total_mitzvot) * 100, 1) if total_mitzvot > 0 else 0,
            "categoryProgress": category_progress,
            "currentStreak": 0,  # TODO: Calculate streak
            "totalStudyTime": 0  # TODO: Calculate from sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/progress/{mitzvah_id}")
async def update_mitzvah_progress(mitzvah_id: str, correct: bool, user_id: str = DEFAULT_USER_ID):
    """Update progress for a specific mitzvah"""
    try:
        # Get the mitzvah
        mitzvah = await mitzvot_collection.find_one({"id": mitzvah_id})
        if not mitzvah:
            raise HTTPException(status_code=404, detail="Mitzvah not found")
        
        # Find or create progress record
        progress = await progress_collection.find_one({"userId": user_id, "mitzvahId": mitzvah_id})
        
        if not progress:
            progress = {
                "id": str(uuid.uuid4()),
                "userId": user_id,
                "mitzvahId": mitzvah_id,
                "mitzvahNumber": mitzvah["number"],
                "status": "learning",
                "correctAnswers": 0,
                "totalAttempts": 0,
                "lastStudied": datetime.now(timezone.utc),
                "masteredAt": None,
                "createdAt": datetime.now(timezone.utc)
            }
            
        # Update progress
        progress["totalAttempts"] += 1
        if correct:
            progress["correctAnswers"] += 1
            
        progress["lastStudied"] = datetime.now(timezone.utc)
        
        # Update status based on performance
        accuracy = progress["correctAnswers"] / progress["totalAttempts"]
        if progress["totalAttempts"] >= 3:
            if accuracy >= 0.8 and progress["correctAnswers"] >= 3:
                progress["status"] = "mastered"
                if not progress.get("masteredAt"):
                    progress["masteredAt"] = datetime.now(timezone.utc)
            elif accuracy >= 0.6:
                progress["status"] = "reviewing"
            else:
                progress["status"] = "learning"
        
        # Upsert progress record
        await progress_collection.replace_one(
            {"userId": user_id, "mitzvahId": mitzvah_id},
            progress,
            upsert=True
        )
        
        # Remove ObjectId fields for JSON serialization
        progress_response = dict(progress)
        if "_id" in progress_response:
            del progress_response["_id"]
        
        return {"status": "success", "progress": progress_response}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/flashcards")
async def get_flashcards_for_review(user_id: str = DEFAULT_USER_ID, limit: int = 10):
    """Get flashcards due for review"""
    try:
        # Get flashcards due for review
        now = datetime.now(timezone.utc)
        due_flashcards = await flashcards_collection.find({
            "userId": user_id,
            "nextReview": {"$lte": now}
        }).limit(limit).to_list(length=None)
        
        # If not enough due cards, add new ones
        if len(due_flashcards) < limit:
            # Get mitzvot that don't have flashcards yet
            existing_mitzvah_ids = [f["mitzvahId"] for f in await flashcards_collection.find({"userId": user_id}).to_list(length=None)]
            
            query = {}
            if existing_mitzvah_ids:
                query["id"] = {"$nin": existing_mitzvah_ids}
                
            new_mitzvot = await mitzvot_collection.find(query).limit(limit - len(due_flashcards)).to_list(length=None)
            
            # Create new flashcards
            for mitzvah in new_mitzvot:
                flashcard = {
                    "id": str(uuid.uuid4()),
                    "userId": user_id,
                    "mitzvahId": mitzvah["id"],
                    "mitzvahNumber": mitzvah["number"],
                    "difficulty": 1,
                    "nextReview": now,
                    "reviewCount": 0,
                    "correctStreak": 0,
                    "createdAt": now,
                    "lastReviewed": None
                }
                await flashcards_collection.insert_one(flashcard)
                due_flashcards.append(flashcard)
        
        # Get full mitzvah details for each flashcard
        flashcard_data = []
        for flashcard in due_flashcards:
            mitzvah = await mitzvot_collection.find_one({"id": flashcard["mitzvahId"]})
            if mitzvah:
                # Convert mitzvah to proper format, removing MongoDB ObjectId
                mitzvah_dict = dict(mitzvah)
                if "_id" in mitzvah_dict:
                    del mitzvah_dict["_id"]
                
                # Convert flashcard to proper format
                flashcard_dict = dict(flashcard) 
                if "_id" in flashcard_dict:
                    del flashcard_dict["_id"]
                
                flashcard_data.append({
                    "flashcard": flashcard_dict,
                    "mitzvah": mitzvah_dict
                })
        
        return {
            "flashcards": flashcard_data,
            "total": len(flashcard_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting flashcards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/flashcards/{flashcard_id}/review")
async def review_flashcard(flashcard_id: str, difficulty: int, correct: bool):
    """Update flashcard after review using spaced repetition"""
    try:
        flashcard = await flashcards_collection.find_one({"id": flashcard_id})
        if not flashcard:
            raise HTTPException(status_code=404, detail="Flashcard not found")
        
        now = datetime.now(timezone.utc)
        flashcard["lastReviewed"] = now
        flashcard["reviewCount"] += 1
        
        if correct:
            flashcard["correctStreak"] += 1
            # Increase interval based on difficulty and streak
            intervals = {
                1: timedelta(days=1),
                2: timedelta(days=3),
                3: timedelta(days=7),
                4: timedelta(days=14),
                5: timedelta(days=30)
            }
            
            # Increase difficulty if doing well
            if flashcard["correctStreak"] >= 2:
                flashcard["difficulty"] = min(5, flashcard["difficulty"] + 1)
                
            interval = intervals.get(flashcard["difficulty"], timedelta(days=1))
            flashcard["nextReview"] = now + interval
        else:
            flashcard["correctStreak"] = 0
            # Reset to easier difficulty
            flashcard["difficulty"] = max(1, flashcard["difficulty"] - 1)
            # Review again soon
            flashcard["nextReview"] = now + timedelta(hours=1)
        
        await flashcards_collection.replace_one({"id": flashcard_id}, flashcard)
        
        return {"status": "success", "nextReview": flashcard["nextReview"]}
        
    except Exception as e:
        logger.error(f"Error reviewing flashcard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New collections for user management
users_collection = db["users"]

# Simple JWT token handling (in production, use proper JWT library)
import secrets
import hashlib
from datetime import timedelta

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt in production)"""
    return hashlib.sha256((password + "salt_key_2024").encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def create_access_token(user_id: str) -> str:
    """Create simple access token (use proper JWT in production)"""
    return hashlib.sha256((user_id + secrets.token_hex(16)).encode()).hexdigest()

@api_router.post("/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        user_id = str(uuid.uuid4())
        
        user = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "hashedPassword": hashed_password,
            "isActive": True,
            "preferences": {},
            "dailyGoal": 5,
            "preferredCategories": [],
            "difficulty": "medium",
            "signupSource": "web",
            "lastActiveDate": datetime.now(timezone.utc),
            "totalStudyTime": 0,
            "subscriptionType": "free",
            "subscriptionExpiry": None,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc)
        }
        
        await users_collection.insert_one(user)
        
        # Create access token
        token = create_access_token(user_id)
        
        # Remove sensitive data for response
        user_profile = UserProfile(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            preferences=user["preferences"],
            dailyGoal=user["dailyGoal"],
            preferredCategories=user["preferredCategories"],
            difficulty=user["difficulty"],
            totalStudyTime=user["totalStudyTime"],
            subscriptionType=user["subscriptionType"],
            createdAt=user["createdAt"]
        )
        
        return AuthResponse(
            token=token,
            user=user_profile,
            expiresIn=86400
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin):
    """Login user and return auth token"""
    try:
        # Find user by email
        user = await users_collection.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(login_data.password, user["hashedPassword"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user.get("isActive", True):
            raise HTTPException(status_code=401, detail="Account is disabled")
        
        # Update last active date
        await users_collection.update_one(
            {"id": user["id"]},
            {"$set": {"lastActiveDate": datetime.now(timezone.utc)}}
        )
        
        # Create access token
        token = create_access_token(user["id"])
        
        # Create user profile response
        user_profile = UserProfile(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            preferences=user.get("preferences", {}),
            dailyGoal=user.get("dailyGoal", 5),
            preferredCategories=user.get("preferredCategories", []),
            difficulty=user.get("difficulty", "medium"),
            totalStudyTime=user.get("totalStudyTime", 0),
            subscriptionType=user.get("subscriptionType", "free"),
            createdAt=user["createdAt"]
        )
        
        return AuthResponse(
            token=token,
            user=user_profile,
            expiresIn=86400
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/auth/me", response_model=UserProfile)
async def get_current_user(authorization: str = Header(None)):
    """Get current user profile (requires auth token)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization token required")
        
        # In production, properly decode and validate JWT token
        # For now, we'll use a simple token lookup (not secure for production)
        token = authorization.replace("Bearer ", "")
        
        # Find user by checking recent activity (simplified auth)
        # In production, decode JWT and get user_id from token
        users = await users_collection.find({
            "lastActiveDate": {"$gte": datetime.now(timezone.utc) - timedelta(days=1)}
        }).to_list(length=10)
        
        if not users:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # For demo, return the most recently active user
        user = max(users, key=lambda u: u["lastActiveDate"])
        
        user_profile = UserProfile(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            preferences=user.get("preferences", {}),
            dailyGoal=user.get("dailyGoal", 5),
            preferredCategories=user.get("preferredCategories", []),
            difficulty=user.get("difficulty", "medium"),
            totalStudyTime=user.get("totalStudyTime", 0),
            subscriptionType=user.get("subscriptionType", "free"),
            createdAt=user["createdAt"]
        )
        
        return user_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/auth/profile")
async def update_user_profile(profile_data: dict, authorization: str = Header(None)):
    """Update user profile and preferences"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization token required")
        
        # Get current user (simplified - in production, decode JWT properly)
        token = authorization.replace("Bearer ", "")
        users = await users_collection.find({
            "lastActiveDate": {"$gte": datetime.now(timezone.utc) - timedelta(days=1)}
        }).to_list(length=10)
        
        if not users:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user = max(users, key=lambda u: u["lastActiveDate"])
        
        # Update allowed fields
        update_data = {}
        if "name" in profile_data:
            update_data["name"] = profile_data["name"]
        if "dailyGoal" in profile_data:
            update_data["dailyGoal"] = profile_data["dailyGoal"]
        if "preferredCategories" in profile_data:
            update_data["preferredCategories"] = profile_data["preferredCategories"]
        if "difficulty" in profile_data:
            update_data["difficulty"] = profile_data["difficulty"]
        if "preferences" in profile_data:
            update_data["preferences"] = profile_data["preferences"]
        
        update_data["updatedAt"] = datetime.now(timezone.utc)
        
        await users_collection.update_one(
            {"id": user["id"]},
            {"$set": update_data}
        )
        
        return {"status": "success", "message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()