import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000, // 30 second timeout
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Enhanced response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
    // Enhanced error handling with user-friendly messages
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data as any;

      switch (status) {
        case 401:
          console.error('Unauthorized access');
          return Promise.reject(new Error('Authentication required. Please log in.'));
        case 403:
          return Promise.reject(new Error('You do not have permission to perform this action.'));
        case 404:
          return Promise.reject(new Error('The requested resource was not found.'));
        case 422:
          // Validation errors
          const message = data?.detail || data?.message || 'Validation error occurred';
          return Promise.reject(new Error(Array.isArray(message) ? message.join(', ') : message));
        case 429:
          return Promise.reject(new Error('Too many requests. Please try again later.'));
        case 500:
        case 502:
        case 503:
        case 504:
          return Promise.reject(new Error('Server error. Please try again later.'));
        default:
          const errorMessage = data?.message || data?.detail || `Request failed with status ${status}`;
          return Promise.reject(new Error(errorMessage));
      }
    } else if (error.request) {
      // Request was made but no response received
      if (error.code === 'ECONNABORTED') {
        return Promise.reject(new Error('Request timeout. Please check your connection and try again.'));
      }
      return Promise.reject(new Error('Network error. Please check your connection.'));
    } else {
      // Something else happened
      return Promise.reject(error);
    }
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
