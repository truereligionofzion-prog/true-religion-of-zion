# 613 Biblical Laws App - API Contracts & Integration Protocol

## Overview
This document defines the API contracts, data structure, and integration protocol for replacing mock data with actual backend implementation for the 613 mitzvot application.

## Current Mock Data Structure

### Mitzvah Object Schema
```json
{
  "id": 1,
  "number": 1,
  "title": "To know that God exists",
  "traditionalWording": "To believe in the existence of God.",
  "sourceVerse": "Exodus 20:2 — \"I am the LORD thy God...\"",
  "book": "Exodus",
  "chapter": 20,
  "verse": "2",
  "status": "direct",
  "category": "faith-god", 
  "scholarlyNote": "Maimonides places this as the first mitzvah...",
  "keywords": ["God", "existence", "belief", "faith", "foundation", "monotheism"]
}
```

### Categories Schema
```json
{
  "id": "faith-god",
  "name": "Faith & Relationship with God", 
  "count": 8
}
```

### Status Types Schema
```json
{
  "value": "direct",
  "label": "Direct in Bible",
  "color": "bg-green-100 text-green-800"
}
```

## API Endpoints to Implement

### 1. GET /api/mitzvot
**Purpose**: Retrieve all 613 mitzvot with optional filtering
**Query Parameters**: 
- `search` (string): Search term for title, traditional wording, source verse, keywords
- `category` (string): Filter by category ID
- `status` (string): Filter by status (direct, indirect, rabbinic, traditional)
- `book` (string): Filter by biblical book
- `page` (number): Pagination
- `limit` (number): Items per page

**Response**:
```json
{
  "mitzvot": [/* array of mitzvah objects */],
  "total": 613,
  "page": 1,
  "totalPages": 21,
  "filters": {
    "categories": [/* category objects */],
    "statusTypes": [/* status type objects */],
    "books": ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy"]
  }
}
```

### 2. GET /api/mitzvot/:id
**Purpose**: Get specific mitzvah by ID
**Response**: Single mitzvah object

### 3. GET /api/categories
**Purpose**: Get all categories with counts
**Response**: Array of category objects

### 4. GET /api/stats
**Purpose**: Get summary statistics
**Response**:
```json
{
  "totalMitzvot": 613,
  "directBiblical": 430,
  "indirectBiblical": 120,
  "rabbinic": 40,
  "traditional": 23,
  "categoriesCount": 14,
  "booksCount": 5
}
```

## Database Schema

### Collections/Tables Needed

#### 1. mitzvot
```javascript
{
  _id: ObjectId,
  number: Number (1-613, unique),
  title: String,
  traditionalWording: String,
  sourceVerse: String,
  book: String,
  chapter: Number,
  verse: String, // Can be "2" or "8-10" for ranges
  status: String, // "direct", "indirect", "rabbinic", "traditional"
  category: String, // category ID
  scholarlyNote: String,
  keywords: [String],
  createdAt: Date,
  updatedAt: Date
}
```

#### 2. categories
```javascript
{
  _id: ObjectId,
  id: String (unique slug),
  name: String,
  description: String,
  order: Number,
  createdAt: Date
}
```

## Data Population Strategy

### Source Data to Process
User provided mitzvot 1-49 in detailed format, plus continuation 50-613. Need to:

1. **Parse and structure** the provided text data into database documents
2. **Categorize** each mitzvah based on content analysis
3. **Extract keywords** from title, traditional wording, and scholarly notes
4. **Standardize** biblical references (book/chapter/verse)
5. **Validate** status assignments (direct vs indirect vs rabbinic)

### Categories to Implement
```javascript
const categories = [
  { id: 'faith-god', name: 'Faith & Relationship with God' },
  { id: 'torah-study', name: 'Torah Study & Teaching' },
  { id: 'temple-worship', name: 'Temple & Worship' },
  { id: 'dietary-laws', name: 'Dietary Laws' },
  { id: 'tithes-offerings', name: 'Tithes & Offerings' },
  { id: 'festivals', name: 'Festivals & Holy Days' },
  { id: 'ethics-morality', name: 'Ethics & Morality' },
  { id: 'family-marriage', name: 'Family & Marriage' },
  { id: 'civil-criminal', name: 'Civil & Criminal Law' },
  { id: 'purity-laws', name: 'Purity Laws' },
  { id: 'business-society', name: 'Business & Society' },
  { id: 'leadership', name: 'Leadership & Government' },
  { id: 'land-agriculture', name: 'Land & Agriculture' },
  { id: 'other', name: 'Other Laws' }
];
```

## Frontend Integration Changes

### Files to Update
1. **Remove mock data**: Delete `/app/frontend/src/data/mockMitzvot.js`
2. **Update MitzvotApp.jsx**: Replace mock imports with API calls
3. **Add API service**: Create `/app/frontend/src/services/api.js`

### API Service Implementation
```javascript
// /app/frontend/src/services/api.js
const API_BASE = process.env.REACT_APP_BACKEND_URL + '/api';

export const mitzvotApi = {
  getAllMitzvot: (params) => fetch(`${API_BASE}/mitzvot?${new URLSearchParams(params)}`),
  getMitzvah: (id) => fetch(`${API_BASE}/mitzvot/${id}`),
  getCategories: () => fetch(`${API_BASE}/categories`),
  getStats: () => fetch(`${API_BASE}/stats`)
};
```

### State Management Updates
Replace useState with useEffect for data fetching:
```javascript
const [mitzvot, setMitzvot] = useState([]);
const [categories, setCategories] = useState([]);
const [loading, setLoading] = useState(true);
const [stats, setStats] = useState({});

useEffect(() => {
  // Fetch data from API instead of using mock
}, [searchTerm, selectedCategory, selectedStatus, selectedBook]);
```

## Backend Implementation Priority

### Phase 1: Core API
1. Set up MongoDB models (mitzvot, categories)
2. Implement basic CRUD endpoints
3. Add search and filtering logic
4. Parse and import the 613 mitzvot data

### Phase 2: Advanced Features  
1. Full-text search optimization
2. Advanced filtering combinations
3. Pagination and performance optimization
4. Data validation and error handling

### Phase 3: Enhancement
1. Analytics and usage tracking
2. Export functionality
3. Advanced categorization
4. Search highlighting

## Data Quality Assurance

### Validation Requirements
- All 613 mitzvot properly numbered (1-613)
- Biblical references validated (book/chapter/verse exists)
- Categories assigned consistently
- Keywords extracted and standardized
- Status properly classified
- No duplicate numbers or missing entries

### Testing Strategy
- Unit tests for API endpoints
- Integration tests for search/filter combinations
- Data integrity tests for all 613 entries
- Performance tests for large dataset queries

## Success Metrics
- ✅ All 613 mitzvot properly imported and accessible
- ✅ Search returns relevant results in <500ms
- ✅ Filters work in all combinations
- ✅ Data matches original source accuracy
- ✅ Frontend seamlessly integrated with backend
- ✅ No mock data remaining in production