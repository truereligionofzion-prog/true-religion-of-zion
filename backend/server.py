from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import math
import re

from models import (
    Mitzvah, MitzvahCreate, Category, CategoryCreate, 
    MitzvotResponse, StatsResponse
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
        
        # Load mitzvot (using sample data structure - will be expanded with full 613)
        sample_mitzvot = [
            {
                "number": 1,
                "title": "To know that God exists",
                "traditionalWording": "To believe in the existence of God.",
                "sourceVerse": "Exodus 20:2 — \"I am the LORD thy God, which have brought thee out of the land of Egypt, out of the house of bondage.\"",
                "book": "Exodus",
                "chapter": 20,
                "verse": "2",
                "status": "direct",
                "category": "faith-god",
                "scholarlyNote": "Maimonides places this as the first mitzvah. While some scholars view it as more of a declaration than a command, Dead Sea Scrolls fragments confirm its foundational role in Israelite faith.",
                "keywords": ["God", "existence", "belief", "faith", "foundation", "monotheism"]
            },
            {
                "number": 2,
                "title": "Not to entertain thoughts of other gods",
                "traditionalWording": "Do not even think there are other gods before Me.",
                "sourceVerse": "Exodus 20:3 — \"Thou shalt have no other gods before me.\"",
                "book": "Exodus",
                "chapter": 20,
                "verse": "3",
                "status": "direct",
                "category": "faith-god",
                "scholarlyNote": "This commandment is universally preserved across Bible versions, including the Septuagint. It serves as a cornerstone of monotheism.",
                "keywords": ["idolatry", "monotheism", "thoughts", "gods", "commandment"]
            },
            {
                "number": 21,
                "title": "Not to eat blood",
                "traditionalWording": "Abstain from consuming blood.",
                "sourceVerse": "Leviticus 7:26 — \"Moreover ye shall eat no manner of blood, whether it be of fowl or of beast, in any of your dwellings.\"",
                "book": "Leviticus",
                "chapter": 7,
                "verse": "26",
                "status": "direct",
                "category": "dietary-laws",
                "scholarlyNote": "Universally recognized prohibition; reinforced multiple times across Leviticus and Deuteronomy.",
                "keywords": ["blood", "dietary", "kosher", "prohibition", "consumption"]
            }
        ]
        
        # Generate sample data for remaining mitzvot (will replace with actual user data)
        all_mitzvot = []
        for i in range(1, 614):
            if i <= len(sample_mitzvot):
                mitzvah_data = sample_mitzvot[i-1]
            else:
                # Generate placeholder data structure
                categories = ["faith-god", "torah-study", "temple-worship", "dietary-laws", "festivals", "ethics-morality"]
                books = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
                statuses = ["direct", "indirect", "rabbinic", "traditional"]
                
                mitzvah_data = {
                    "number": i,
                    "title": f"Mitzvah {i} - Sample Law",
                    "traditionalWording": f"Traditional wording for mitzvah {i}.",
                    "sourceVerse": f"{books[i % len(books)]} {(i % 50) + 1}:{(i % 30) + 1} — \"Sample verse text for mitzvah {i}.\"",
                    "book": books[i % len(books)],
                    "chapter": (i % 50) + 1,
                    "verse": str((i % 30) + 1),
                    "status": statuses[i % len(statuses)],
                    "category": categories[i % len(categories)],
                    "scholarlyNote": f"Scholarly note explaining the context and significance of mitzvah {i}.",
                    "keywords": ["sample", "law", "commandment", "torah"]
                }
            
            mitzvah = Mitzvah(**mitzvah_data)
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
    status: Optional[str] = Query(None, description="Filter by status"),
    book: Optional[str] = Query(None, description="Filter by book"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get all mitzvot with optional filtering and pagination"""
    try:
        # Build query
        query = {}
        
        if category and category != "all":
            query["category"] = category
            
        if status and status != "all":
            query["status"] = status
            
        if book and book != "all":
            query["book"] = book
        
        # Text search
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"title": search_regex},
                {"traditionalWording": search_regex},
                {"sourceVerse": search_regex},
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
        
        status_types = [
            {"value": "direct", "label": "Direct in Bible", "color": "bg-green-100 text-green-800"},
            {"value": "indirect", "label": "Indirect in Bible", "color": "bg-blue-100 text-blue-800"},
            {"value": "rabbinic", "label": "Rabbinic Origin", "color": "bg-purple-100 text-purple-800"},
            {"value": "traditional", "label": "Traditional", "color": "bg-orange-100 text-orange-800"}
        ]
        
        return MitzvotResponse(
            mitzvot=mitzvot,
            total=total,
            page=page,
            totalPages=total_pages,
            filters={
                "categories": categories,
                "statusTypes": status_types,
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
        direct_biblical = await mitzvot_collection.count_documents({"status": "direct"})
        indirect_biblical = await mitzvot_collection.count_documents({"status": "indirect"})
        rabbinic = await mitzvot_collection.count_documents({"status": "rabbinic"})
        traditional = await mitzvot_collection.count_documents({"status": "traditional"})
        
        categories_count = await categories_collection.count_documents({})
        books_count = len(await mitzvot_collection.distinct("book"))
        
        return StatsResponse(
            totalMitzvot=total_mitzvot,
            directBiblical=direct_biblical,
            indirectBiblical=indirect_biblical,
            rabbinic=rabbinic,
            traditional=traditional,
            categoriesCount=categories_count,
            booksCount=books_count
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
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