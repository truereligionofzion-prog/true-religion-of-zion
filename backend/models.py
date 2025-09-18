from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid

class Mitzvah(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: int
    title: str
    traditionalWording: str
    sourceVerse: str
    book: str
    chapter: int
    verse: str  # Can be "2" or "8-10" for ranges
    status: str  # "direct", "indirect", "rabbinic", "traditional"
    category: str  # category ID
    scholarlyNote: str
    keywords: List[str]
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MitzvahCreate(BaseModel):
    number: int
    title: str
    traditionalWording: str
    sourceVerse: str
    book: str
    chapter: int
    verse: str
    status: str
    category: str
    scholarlyNote: str
    keywords: List[str]

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str  # unique identifier like "faith-god"
    name: str
    description: Optional[str] = ""
    order: int = 0
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CategoryCreate(BaseModel):
    slug: str
    name: str
    description: Optional[str] = ""
    order: int = 0

class MitzvotResponse(BaseModel):
    mitzvot: List[Mitzvah]
    total: int
    page: int
    totalPages: int
    filters: dict

class StatsResponse(BaseModel):
    totalMitzvot: int
    directBiblical: int
    indirectBiblical: int
    rabbinic: int
    traditional: int
    categoriesCount: int
    booksCount: int