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

  // Initialize database (development/admin use)
  async initializeData() {
    return this.request('/initialize', { method: 'POST' });
  }
}

export const apiService = new ApiService();
export default apiService;