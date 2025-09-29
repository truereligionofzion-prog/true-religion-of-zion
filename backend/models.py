from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid

class Mitzvah(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: int
    title: str
    sourceVerse: str  # Complete verse text with YHWH/YHUH replacements
    book: str
    chapter: int
    verse: str  # Can be "2" or "8-10" for ranges
    category: str  # category ID
    keywords: List[str]
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MitzvahCreate(BaseModel):
    number: int
    title: str
    sourceVerse: str
    book: str
    chapter: int
    verse: str
    category: str
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
    categoriesCount: int
    booksCount: int

# New Models for Progress Tracking and Flashcards

class UserProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str  # For now, we'll use a simple identifier
    mitzvahId: str
    mitzvahNumber: int
    status: str  # "learning", "reviewing", "mastered"
    correctAnswers: int = 0
    totalAttempts: int = 0
    lastStudied: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    masteredAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StudySession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    sessionType: str  # "quiz", "flashcard", "daily_review"
    category: Optional[str] = None
    questionsAnswered: int = 0
    correctAnswers: int = 0
    duration: int = 0  # in seconds
    score: float = 0.0
    completed: bool = False
    startedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completedAt: Optional[datetime] = None

class Flashcard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    mitzvahId: str
    mitzvahNumber: int
    difficulty: int = 1  # 1-5, for spaced repetition
    nextReview: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviewCount: int = 0
    correctStreak: int = 0
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lastReviewed: Optional[datetime] = None

class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    type: str  # "category_master", "streak", "quiz_champion", etc.
    title: str
    description: str
    category: Optional[str] = None
    requirement: int  # e.g., number needed for achievement
    progress: int = 0
    completed: bool = False
    unlockedAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# New Models for User Management and Authentication

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    hashedPassword: str
    isActive: bool = True
    preferences: Dict = Field(default_factory=dict)
    
    # Learning preferences
    dailyGoal: int = 5  # mitzvot per day
    preferredCategories: List[str] = Field(default_factory=list)
    difficulty: str = "medium"  # easy, medium, hard
    
    # Marketing/Analytics data
    signupSource: Optional[str] = None
    lastActiveDate: Optional[datetime] = None
    totalStudyTime: int = 0  # in minutes
    
    # Subscription/Premium features (for future)
    subscriptionType: str = "free"  # free, premium
    subscriptionExpiry: Optional[datetime] = None
    
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    preferences: Dict
    dailyGoal: int
    preferredCategories: List[str]
    difficulty: str
    totalStudyTime: int
    subscriptionType: str
    createdAt: datetime
    
class UserStats(BaseModel):
    userId: str
    totalMitzvot: int
    learning: int
    reviewing: int
    mastered: int
    overallProgress: float
    currentStreak: int
    totalStudyTime: int
    achievementsUnlocked: int
    favoriteCategory: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: UserProfile
    expiresIn: int = 86400  # 24 hours