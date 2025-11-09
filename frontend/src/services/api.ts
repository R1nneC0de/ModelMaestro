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

// Data upload endpoints
export const dataApi = {
  upload: async (file: File, projectId: string) => {
    const formData = new FormData();
    formData.append('files', file);
    formData.append('project_id', projectId);
    
    const response = await apiClient.post('/data/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }
};

// Training endpoints
export const trainingApi = {
  submit: async (data: FormData) => {
    const response = await apiClient.post('/projects', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  // Two-step process: upload dataset first, then create project
  submitTwoStep: async (file: File, problemDescription: string, userId: string = 'default-user') => {
    // Step 1: Upload dataset
    const tempProjectId = `temp_${Date.now()}`;
    const uploadResponse = await dataApi.upload(file, tempProjectId);
    
    // Step 2: Create project with dataset_id
    const projectData = {
      user_id: userId,
      problem_description: problemDescription,
      requires_approval: false
    };
    
    const response = await apiClient.post(
      `/projects?dataset_id=${uploadResponse.dataset_id}`,
      projectData
    );
    
    return response.data;
  },
  
  getProgress: async (projectId: string) => {
    const response = await apiClient.get(`/projects/${projectId}/progress`);
    return response.data;
  }
};

// History endpoints
export const historyApi = {
  // Task 3.1: Fetch projects from backend with pagination
  getAll: async (page: number = 1, pageSize: number = 50) => {
    const response = await apiClient.get('/projects', {
      params: { page, page_size: pageSize }
    });
    
    // Task 3.1: Map ProjectListResponse to display format
    const { projects, total } = response.data;
    
    // Map backend Project schema to frontend TrainingSession format
    const sessions = projects.map((project: any) => ({
      id: project.id,
      datasetName: project.dataset_id || 'Unknown Dataset',
      prompt: project.problem_description,
      status: mapProjectStatus(project.status),
      timestamp: project.created_at,
      metrics: project.metrics || undefined,
      modelId: project.model_id || undefined,
      progress: calculateProgress(project.status)
    }));
    
    return { sessions, total, page: response.data.page, pageSize: response.data.page_size };
  },
  
  getById: async (id: string) => {
    const response = await apiClient.get(`/projects/${id}`);
    
    // Map backend Project to frontend TrainingSession format
    const project = response.data;
    return {
      id: project.id,
      datasetName: project.dataset_id || 'Unknown Dataset',
      prompt: project.problem_description,
      status: mapProjectStatus(project.status),
      timestamp: project.created_at,
      metrics: project.metrics || undefined,
      modelId: project.model_id || undefined,
      progress: calculateProgress(project.status)
    };
  }
};

// Task 3.2: Map ProjectStatus to visual indicators
function mapProjectStatus(backendStatus: string): 'training' | 'completed' | 'failed' {
  const statusMap: Record<string, 'training' | 'completed' | 'failed'> = {
    'analyzing': 'training',
    'processing': 'training',
    'labeling': 'training',
    'training': 'training',
    'evaluating': 'training',
    'deploying': 'training',
    'complete': 'completed',
    'failed': 'failed',
    'cancelled': 'failed'
  };
  
  return statusMap[backendStatus.toLowerCase()] || 'training';
}

// Task 3.2: Calculate progress percentage based on status
function calculateProgress(status: string): number {
  const progressMap: Record<string, number> = {
    'analyzing': 10,
    'processing': 30,
    'labeling': 40,
    'training': 60,
    'evaluating': 80,
    'deploying': 90,
    'complete': 100,
    'failed': 0,
    'cancelled': 0
  };
  
  return progressMap[status.toLowerCase()] || 0;
}

// Model endpoints
export const modelApi = {
  getModel: async (modelId: string) => {
    const response = await apiClient.get(`/models/${modelId}`);
    return response.data;
  },
  
  downloadModel: async (modelId: string) => {
    const response = await apiClient.get(`/models/${modelId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },
  
  predict: async (modelId: string, data: any) => {
    const response = await apiClient.post(`/models/${modelId}/predict`, data);
    return response.data;
  },
  
  getStatus: async (modelId: string) => {
    const response = await apiClient.get(`/models/${modelId}/status`);
    return response.data;
  }
};
