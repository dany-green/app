import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API_URL = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    if (error.response?.status === 401 && window.location.pathname !== '/login') {
      // Token expired or invalid - only redirect if not on login page
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// ============== AUTH API ==============

export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  initDatabase: async () => {
    const response = await api.post('/init');
    return response.data;
  },

  loadTestData: async () => {
    const response = await api.post('/load-test-data');
    return response.data;
  },
};

// ============== USERS API ==============

export const usersAPI = {
  getAll: async () => {
    const response = await api.get('/users');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },
};

// ============== PROJECTS API ==============

export const projectsAPI = {
  getAll: async () => {
    const response = await api.get('/projects');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  create: async (projectData) => {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  update: async (id, projectData) => {
    const response = await api.patch(`/projects/${id}`, projectData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  },
};

// ============== INVENTORY API ==============

export const inventoryAPI = {
  getAll: async () => {
    const response = await api.get('/inventory');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/inventory/${id}`);
    return response.data;
  },

  create: async (itemData) => {
    const response = await api.post('/inventory', itemData);
    return response.data;
  },

  update: async (id, itemData) => {
    const response = await api.patch(`/inventory/${id}`, itemData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/inventory/${id}`);
    return response.data;
  },

  // Image management
  uploadImage: async (itemId, formData) => {
    const response = await axios.post(
      `${API_URL}/inventory/${itemId}/images`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  },

  deleteImage: async (itemId, imageUrl) => {
    const response = await api.delete(`/inventory/${itemId}/images`, {
      params: { image_url: imageUrl },
    });
    return response.data;
  },
};

// ============== EQUIPMENT API ==============

export const equipmentAPI = {
  getAll: async () => {
    const response = await api.get('/equipment');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/equipment/${id}`);
    return response.data;
  },

  create: async (itemData) => {
    const response = await api.post('/equipment', itemData);
    return response.data;
  },

  update: async (id, itemData) => {
    const response = await api.patch(`/equipment/${id}`, itemData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/equipment/${id}`);
    return response.data;
  },

  // Image management
  uploadImage: async (itemId, formData) => {
    const response = await axios.post(
      `${API_URL}/equipment/${itemId}/images`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  },

  deleteImage: async (itemId, imageUrl) => {
    const response = await api.delete(`/equipment/${itemId}/images`, {
      params: { image_url: imageUrl },
    });
    return response.data;
  },
};

// ============== LOGS API ==============

export const logsAPI = {
  getAll: async (limit = 100) => {
    const response = await api.get(`/logs?limit=${limit}`);
    return response.data;
  },
  
  cleanup: async () => {
    const response = await api.delete('/logs/cleanup');
    return response.data;
  },
};
