# Frontend-Backend Integration Design

## Overview

This design document outlines the architecture for integrating the React-based 3D galaxy frontend with the FastAPI backend ML training platform. The integration provides a seamless user experience for uploading datasets, triggering training pipelines, monitoring progress in real-time via WebSocket, and viewing results.

The design focuses on:
- RESTful API endpoints for project management
- WebSocket connections for real-time progress streaming
- Type-safe schema alignment between frontend and backend
- Robust error handling and retry logic
- Efficient data flow and state management

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ 3D Galaxy UI │  │ API Client   │  │ WebSocket    │      │
│  │ (Three.js)   │  │ (Axios)      │  │ Manager      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          │         HTTP/REST│         WebSocket│
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────┐
│         │                  │                  │              │
│  ┌──────▼───────┐  ┌───────▼──────┐  ┌───────▼──────┐      │
│  │ CORS         │  │ API Router   │  │ WebSocket    │      │
│  │ Middleware   │  │ (FastAPI)    │  │ Manager      │      │
│  └──────────────┘  └───────┬──────┘  └───────┬──────┘      │
│                            │                  │              │
│                    ┌───────▼──────────────────▼──────┐      │
│                    │   Event Broadcaster            │      │
│                    └───────┬────────────────────────┘      │
│                            │                                │
│                    ┌───────▼──────────┐                     │
│                    │  Orchestrator    │                     │
│                    │  (ML Pipeline)   │                     │
│                    └───────┬──────────┘                     │
│                            │                                │
│                    ┌───────▼──────────┐                     │
│                    │  GCS Storage     │                     │
│                    │  Vertex AI       │                     │
│                    └──────────────────┘                     │
│                     Backend (FastAPI)                        │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow

1. **Project Creation Flow**:
   - User uploads file in FileUploadOverlay
   - Frontend validates file and creates FormData
   - POST request to `/api/v1/projects` with multipart data
   - Backend creates project, uploads to GCS, returns project ID
   - Frontend establishes WebSocket connection for updates
   - Backend starts orchestrator pipeline asynchronously

2. **Real-Time Updates Flow**:
   - Frontend connects to `/api/v1/ws/projects/{project_id}/stream`
   - Orchestrator emits events during pipeline execution
   - EventBroadcaster pushes events to WebSocket connections
   - Frontend receives events and updates UI with visual effects
   - Connection maintained with heartbeat/ping-pong

3. **History Retrieval Flow**:
   - User navigates to History node in galaxy
   - Frontend fetches GET `/api/v1/projects`
   - Backend queries GCS for project metadata
   - Frontend displays projects in HistoryBrowserOverlay
   - User clicks project to view details

## Components and Interfaces

### Backend API Endpoints

#### Projects Router (`/api/v1/projects`)

```python
# New router to add to backend/app/api/v1/endpoints/projects.py

@router.post("/", response_model=ProjectResponse)
async def create_project(
    file: UploadFile,
    problem_description: str = Form(...),
    project_name: Optional[str] = Form(None)
) -> ProjectResponse:
    """Create new ML training project"""
    
@router.get("/", response_model=List[ProjectSummary])
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
) -> List[ProjectSummary]:
    """List all projects with pagination"""
    
@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str) -> ProjectDetail:
    """Get detailed project information"""
    
@router.get("/{project_id}/progress", response_model=ProjectProgress)
async def get_project_progress(project_id: str) -> ProjectProgress:
    """Get current training progress"""
    
@router.delete("/{project_id}")
async def delete_project(project_id: str) -> Dict[str, str]:
    """Delete a project and its artifacts"""
```

#### WebSocket Endpoint

```python
# Already exists in backend/app/api/v1/endpoints/websocket.py

@router.websocket("/projects/{project_id}/stream")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """Stream real-time pipeline updates"""
```

### Frontend API Client

#### Enhanced API Service (`frontend/src/services/api.ts`)

```typescript
// Project management
export const projectApi = {
  create: async (file: File, problemDescription: string, projectName?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('problem_description', problemDescription);
    if (projectName) formData.append('project_name', projectName);
    
    const response = await apiClient.post('/projects', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  
  list: async (params?: { limit?: number; offset?: number; status?: string }) => {
    const response = await apiClient.get('/projects', { params });
    return response.data;
  },
  
  getById: async (projectId: string) => {
    const response = await apiClient.get(`/projects/${projectId}`);
    return response.data;
  },
  
  getProgress: async (projectId: string) => {
    const response = await apiClient.get(`/projects/${projectId}/progress`);
    return response.data;
  },
  
  delete: async (projectId: string) => {
    const response = await apiClient.delete(`/projects/${projectId}`);
    return response.data;
  }
};

// WebSocket connection
export class TrainingWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  
  connect(projectId: string, callbacks: WebSocketCallbacks): void {
    const wsUrl = `${getWebSocketUrl()}/projects/${projectId}/stream`;
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      callbacks.onOpen?.();
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callbacks.onMessage(data);
    };
    
    this.ws.onerror = (error) => {
      callbacks.onError?.(error);
    };
    
    this.ws.onclose = () => {
      callbacks.onClose?.();
      this.attemptReconnect(projectId, callbacks);
    };
  }
  
  private attemptReconnect(projectId: string, callbacks: WebSocketCallbacks): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        this.connect(projectId, callbacks);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }
  
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
  
  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
```

## Data Models

### Backend Schemas

```python
# backend/app/schemas/project.py

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ProjectStatus(str, Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    TRAINING = "training"
    EVALUATING = "evaluating"
    DEPLOYING = "deploying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PipelineStage(str, Enum):
    DATA_UPLOAD = "data_upload"
    DATA_ANALYSIS = "data_analysis"
    DATA_PROCESSING = "data_processing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_SELECTION = "model_selection"
    MODEL_TRAINING = "model_training"
    MODEL_EVALUATION = "model_evaluation"
    MODEL_DEPLOYMENT = "model_deployment"

class ProjectResponse(BaseModel):
    project_id: str
    project_name: str
    status: ProjectStatus
    created_at: datetime
    dataset_info: Dict[str, Any]
    message: str = "Project created successfully"

class ProjectSummary(BaseModel):
    project_id: str
    project_name: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    dataset_name: str
    problem_description: str
    progress_percentage: int = 0

class ProjectDetail(BaseModel):
    project_id: str
    project_name: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    # Dataset information
    dataset_id: str
    dataset_name: str
    dataset_type: str
    num_samples: int
    num_features: Optional[int] = None
    
    # Training configuration
    problem_description: str
    problem_type: Optional[str] = None
    selected_models: Optional[List[str]] = None
    
    # Results
    best_model_id: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    evaluation_report: Optional[Dict[str, Any]] = None
    
    # Deployment
    endpoint_id: Optional[str] = None
    prediction_endpoint: Optional[str] = None
    
    # Artifacts
    artifact_paths: Dict[str, str] = {}
    
class ProjectProgress(BaseModel):
    project_id: str
    status: ProjectStatus
    current_stage: PipelineStage
    progress_percentage: int
    message: str
    stage_details: Optional[Dict[str, Any]] = None
    estimated_time_remaining: Optional[int] = None  # seconds

class WebSocketEvent(BaseModel):
    event_type: str  # stage_change, progress_update, log, error, completed
    project_id: str
    timestamp: datetime
    data: Dict[str, Any]
```

### Frontend Types

```typescript
// frontend/src/types/project.ts

export enum ProjectStatus {
  CREATED = 'created',
  UPLOADING = 'uploading',
  ANALYZING = 'analyzing',
  PROCESSING = 'processing',
  TRAINING = 'training',
  EVALUATING = 'evaluating',
  DEPLOYING = 'deploying',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum PipelineStage {
  DATA_UPLOAD = 'data_upload',
  DATA_ANALYSIS = 'data_analysis',
  DATA_PROCESSING = 'data_processing',
  FEATURE_ENGINEERING = 'feature_engineering',
  MODEL_SELECTION = 'model_selection',
  MODEL_TRAINING = 'model_training',
  MODEL_EVALUATION = 'model_evaluation',
  MODEL_DEPLOYMENT = 'model_deployment'
}

export interface ProjectResponse {
  project_id: string;
  project_name: string;
  status: ProjectStatus;
  created_at: string;
  dataset_info: Record<string, any>;
  message: string;
}

export interface ProjectSummary {
  project_id: string;
  project_name: string;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
  dataset_name: string;
  problem_description: string;
  progress_percentage: number;
}

export interface ProjectDetail {
  project_id: string;
  project_name: string;
  status: ProjectStatus;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  
  dataset_id: string;
  dataset_name: string;
  dataset_type: string;
  num_samples: number;
  num_features?: number;
  
  problem_description: string;
  problem_type?: string;
  selected_models?: string[];
  
  best_model_id?: string;
  metrics?: Record<string, number>;
  evaluation_report?: Record<string, any>;
  
  endpoint_id?: string;
  prediction_endpoint?: string;
  
  artifact_paths: Record<string, string>;
}

export interface ProjectProgress {
  project_id: string;
  status: ProjectStatus;
  current_stage: PipelineStage;
  progress_percentage: number;
  message: string;
  stage_details?: Record<string, any>;
  estimated_time_remaining?: number;
}

export interface WebSocketEvent {
  event_type: 'stage_change' | 'progress_update' | 'log' | 'error' | 'completed';
  project_id: string;
  timestamp: string;
  data: Record<string, any>;
}
```

## Error Handling

### Backend Error Responses

```python
# Standardized error response model
class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

# Error codes
class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PIPELINE_FAILED = "PIPELINE_FAILED"
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

### Frontend Error Handling

```typescript
// Enhanced error handling in API client
apiClient.interceptors.response.use(
  response => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response) {
      const { error: message, error_code, details } = error.response.data;
      
      // Map error codes to user-friendly messages
      const userMessage = getUserFriendlyMessage(error_code, details);
      
      // Log for debugging
      console.error('API Error:', {
        code: error_code,
        message,
        details,
        status: error.response.status
      });
      
      return Promise.reject(new ApiError(userMessage, error_code, details));
    }
    
    // Network error
    return Promise.reject(new Error('Network error. Please check your connection.'));
  }
);
```

## Testing Strategy

### Backend Testing

1. **Unit Tests**:
   - Test project creation with valid/invalid data
   - Test WebSocket connection management
   - Test event broadcasting logic
   - Test error handling and validation

2. **Integration Tests**:
   - Test complete project creation flow with GCS upload
   - Test WebSocket message delivery
   - Test orchestrator integration
   - Test CORS configuration

3. **E2E Tests**:
   - Test full training pipeline from upload to completion
   - Test WebSocket reconnection scenarios
   - Test concurrent project handling

### Frontend Testing

1. **Unit Tests**:
   - Test API client methods
   - Test WebSocket connection logic
   - Test error handling and retry logic
   - Test type conversions

2. **Integration Tests**:
   - Test file upload with mock backend
   - Test WebSocket event handling
   - Test progress visualization updates
   - Test history display

3. **E2E Tests**:
   - Test complete user flow from upload to results
   - Test real-time progress updates
   - Test error scenarios and recovery

## Deployment Considerations

### Environment Configuration

**Backend (.env)**:
```bash
# API Configuration
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://app.example.com"]

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project
GCS_BUCKET_NAME=ml-platform-data
VERTEX_AI_LOCATION=us-central1

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS_PER_PROJECT=10
```

**Frontend (.env)**:
```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/ws

# Feature Flags
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_AUTO_RECONNECT=true
```

### CORS Configuration

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=3600
)
```

### Performance Optimization

1. **Connection Pooling**: Reuse HTTP connections with keep-alive
2. **Request Batching**: Batch multiple API calls where possible
3. **Caching**: Cache project list and details with appropriate TTL
4. **Compression**: Enable gzip compression for API responses
5. **WebSocket Throttling**: Limit event frequency to prevent UI overload

## Security Considerations

1. **Input Validation**: Validate all user inputs on both frontend and backend
2. **File Upload Security**: Scan uploaded files, limit file types and sizes
3. **Rate Limiting**: Implement rate limiting on API endpoints
4. **Authentication**: Add JWT-based authentication for production
5. **HTTPS**: Use HTTPS in production for all API and WebSocket connections
6. **CORS**: Restrict CORS origins to known frontend domains
7. **Error Messages**: Don't expose sensitive information in error messages
