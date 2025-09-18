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