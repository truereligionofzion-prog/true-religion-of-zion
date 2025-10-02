const API_BASE = process.env.REACT_APP_BACKEND_URL + '/api';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Get all mitzvot with filtering and pagination
  async getMitzvot(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/mitzvot${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Get specific mitzvah by ID
  async getMitzvah(id) {
    return this.request(`/mitzvot/${id}`);
  }

  // Get all categories
  async getCategories() {
    return this.request('/categories');
  }

  // Get statistics
  async getStats() {
    return this.request('/stats');
  }

  // Get mitzvah of the day
  async getMitzvahOfTheDay() {
    return this.request('/mitzvah-of-the-day');
  }

  // Get quiz questions
  async getQuizQuestions(category = 'all', limit = 5) {
    return this.request(`/quiz/${category}?limit=${limit}`);
  }

  // Progress Tracking
  async getUserProgress(userId = 'user_001') {
    return this.request(`/progress?user_id=${userId}`);
  }

  async updateMitzvahProgress(mitzvahId, correct, userId = 'user_001') {
    return this.request(`/progress/${mitzvahId}?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correct })
    });
  }

  // Flashcards
  async getFlashcards(userId = 'user_001', limit = 10) {
    return this.request(`/flashcards?user_id=${userId}&limit=${limit}`);
  }

  async reviewFlashcard(flashcardId, difficulty, correct) {
    return this.request(`/flashcards/${flashcardId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ difficulty, correct })
    });
  }

  // Authentication
  async register(email, name, password) {
    return this.request('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name, password })
    });
  }

  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
  }

  async getCurrentUser(token) {
    return this.request('/auth/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }

  async updateProfile(profileData, token) {
    return this.request('/auth/profile', {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(profileData)
    });
  }

  // ===== PRECEPTS API METHODS =====
  
  // Get all precepts with filtering and pagination
  async getPrecepts(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/precepts${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Get specific precept by ID
  async getPrecept(id) {
    return this.request(`/precepts/${id}`);
  }

  // Get precepts statistics
  async getPreceptsStats() {
    return this.request('/precepts-stats');
  }

  // ===== BIBLE API METHODS =====
  
  // Get all Bible books
  async getBibleBooks(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/bible/books${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Get Bible verses with filtering and pagination
  async getBibleVerses(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/bible/verses${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Get specific Bible chapter
  async getBibleChapter(book, chapter) {
    return this.request(`/bible/verses/${encodeURIComponent(book)}/${chapter}`);
  }

  // Get specific Bible verse
  async getBibleVerse(book, chapter, verse) {
    return this.request(`/bible/verse/${encodeURIComponent(book)}/${chapter}/${verse}`);
  }

  // Get Bible statistics
  async getBibleStats(version = 'kjv1611_divine') {
    return this.request(`/bible/stats?version=${encodeURIComponent(version)}`);
  }

  // Get available Bible versions
  async getBibleVersions() {
    return this.request('/bible/versions');
  }

  // ===== PHASE 3C: ADVANCED BIBLE SEARCH METHODS =====
  
  // Advanced Bible search with multiple filters
  async getAdvancedBibleSearch(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/bible/search/advanced${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Get cross-references between Bible verses and precepts
  async getCrossReferences(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/bible/cross-references${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Search for specific divine names (YHWH, Elohim, YHUH)
  async searchDivineNames(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '' && value !== 'all') {
        queryParams.append(key, value);
      }
    });

    const endpoint = `/bible/divine-names/search${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  // Initialize database (development/admin use)
  async initializeData() {
    return this.request('/initialize', { method: 'POST' });
  }
}

export const apiService = new ApiService();
export default apiService;