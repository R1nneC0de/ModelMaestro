import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access');
    } else if (error.response?.status >= 500) {
      // Show server error message
      console.error('Server error:', error);
    }
    return Promise.reject(error);
  }
);

// Training endpoints
export const trainingApi = {
  submit: async (data: FormData) => {
    const response = await apiClient.post('/projects', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  getProgress: async (projectId: string) => {
    const response = await apiClient.get(`/projects/${projectId}/progress`);
    return response.data;
  }
};

// History endpoints
export const historyApi = {
  getAll: async () => {
    const response = await apiClient.get('/projects');
    return response.data;
  },
  
  getById: async (id: string) => {
    const response = await apiClient.get(`/projects/${id}`);
    return response.data;
  }
};
