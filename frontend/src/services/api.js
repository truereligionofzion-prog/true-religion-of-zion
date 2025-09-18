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

  // Initialize database (development/admin use)
  async initializeData() {
    return this.request('/initialize', { method: 'POST' });
  }
}

export const apiService = new ApiService();
export default apiService;