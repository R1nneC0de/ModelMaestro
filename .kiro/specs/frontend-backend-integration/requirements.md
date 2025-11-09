# Requirements Document

## Introduction

This document defines the requirements for integrating the frontend 3D galaxy interface with the backend agentic ML training platform. The integration enables users to upload datasets, trigger ML training pipelines, monitor progress in real-time, and view training history through a seamless API connection.

## Glossary

- **Frontend**: The React-based 3D galaxy visualization interface built with Three.js and React Three Fiber
- **Backend**: The FastAPI-based agentic ML training platform with Vertex AI integration
- **API Client**: The axios-based HTTP client in the frontend for making API requests
- **WebSocket Connection**: Real-time bidirectional communication channel for streaming training progress
- **Training Pipeline**: The end-to-end ML workflow including data processing, model training, evaluation, and deployment
- **Project**: A user-initiated training session with associated dataset, configuration, and results
- **Navigation Node**: Interactive 3D objects in the galaxy representing different application sections

## Requirements

### Requirement 1: Project Management API

**User Story:** As a user, I want to create and manage ML training projects through the frontend interface, so that I can organize my training sessions.

#### Acceptance Criteria

1. WHEN the user uploads a dataset file and submits a training request, THE Backend SHALL create a new project with a unique identifier and return project metadata
2. WHEN the user requests project history, THE Backend SHALL return a list of all projects with their current status and metadata
3. WHEN the user requests details for a specific project, THE Backend SHALL return complete project information including dataset info, training status, and results
4. THE Backend SHALL validate that project IDs exist before processing requests
5. THE Backend SHALL store project metadata in Google Cloud Storage with proper organization

### Requirement 2: Training Pipeline Orchestration

**User Story:** As a user, I want to trigger ML training pipelines from the frontend, so that I can train models on my uploaded data.

#### Acceptance Criteria

1. WHEN the user submits a training request with a dataset and problem description, THE Backend SHALL initiate the agentic training pipeline
2. THE Backend SHALL validate the dataset format and size before starting training
3. WHEN the pipeline starts, THE Backend SHALL return the project ID immediately without blocking
4. THE Backend SHALL execute the training pipeline asynchronously using the orchestrator
5. IF the dataset is invalid or too large, THEN THE Backend SHALL return a validation error with specific details

### Requirement 3: Real-Time Progress Updates

**User Story:** As a user, I want to see real-time progress updates during training, so that I understand what the system is doing.

#### Acceptance Criteria

1. WHEN a training pipeline is running, THE Frontend SHALL establish a WebSocket connection to receive updates
2. THE Backend SHALL broadcast progress events including stage transitions, percentage completion, and status messages
3. THE Frontend SHALL display progress updates in the 3D interface with visual effects
4. WHEN the WebSocket connection drops, THE Frontend SHALL attempt automatic reconnection
5. THE Backend SHALL send heartbeat messages every 30 seconds to maintain connection health

### Requirement 4: API Schema Alignment

**User Story:** As a developer, I want consistent data schemas between frontend and backend, so that integration is reliable and type-safe.

#### Acceptance Criteria

1. THE Backend SHALL define Pydantic models for all API request and response schemas
2. THE Frontend SHALL define TypeScript interfaces matching the backend schemas
3. THE Backend SHALL return standardized error responses with error codes and messages
4. THE Frontend SHALL handle all documented error cases with appropriate user feedback
5. THE Backend SHALL include API documentation via OpenAPI/Swagger

### Requirement 5: CORS and Security Configuration

**User Story:** As a developer, I want proper CORS configuration, so that the frontend can communicate with the backend securely.

#### Acceptance Criteria

1. THE Backend SHALL allow cross-origin requests from the configured frontend origins
2. THE Backend SHALL include proper CORS headers in all responses
3. THE Backend SHALL support preflight OPTIONS requests for complex requests
4. WHERE authentication is required, THE Backend SHALL validate tokens on protected endpoints
5. THE Backend SHALL log all API requests for security auditing

### Requirement 6: File Upload Integration

**User Story:** As a user, I want to upload dataset files through the frontend interface, so that I can provide data for training.

#### Acceptance Criteria

1. WHEN the user selects a file in the FileUploadOverlay, THE Frontend SHALL validate file type and size before upload
2. THE Frontend SHALL send multipart/form-data requests with the file and metadata
3. THE Backend SHALL stream file uploads to Google Cloud Storage without loading entire files in memory
4. THE Backend SHALL return upload progress information during large file uploads
5. IF the upload fails, THEN THE Backend SHALL clean up any partial uploads

### Requirement 7: Training History Display

**User Story:** As a user, I want to view my training history in the galaxy interface, so that I can access previous results.

#### Acceptance Criteria

1. WHEN the user navigates to the History node, THE Frontend SHALL fetch and display all projects
2. THE Frontend SHALL show project status with visual indicators (training, completed, failed)
3. WHEN the user clicks on a project, THE Frontend SHALL display detailed results including metrics and visualizations
4. THE Backend SHALL return projects sorted by creation date (newest first)
5. THE Frontend SHALL cache project data to minimize API calls

### Requirement 8: Model Prediction Integration

**User Story:** As a user, I want to make predictions with trained models, so that I can use the models for inference.

#### Acceptance Criteria

1. WHEN a model training completes successfully, THE Backend SHALL deploy the model to a Vertex AI endpoint
2. THE Frontend SHALL display the prediction API endpoint for completed models
3. WHEN the user submits prediction instances, THE Backend SHALL return predictions from the deployed model
4. THE Backend SHALL validate prediction input format matches the model's expected schema
5. THE Backend SHALL log all predictions for monitoring and debugging

### Requirement 9: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can understand and resolve issues.

#### Acceptance Criteria

1. WHEN an API request fails, THE Frontend SHALL display user-friendly error messages
2. THE Backend SHALL return structured error responses with error codes and details
3. THE Frontend SHALL distinguish between network errors, validation errors, and server errors
4. WHEN a training pipeline fails, THE Backend SHALL provide diagnostic information about the failure
5. THE Frontend SHALL provide retry options for recoverable errors

### Requirement 10: Environment Configuration

**User Story:** As a developer, I want environment-based configuration, so that the application works in different deployment environments.

#### Acceptance Criteria

1. THE Frontend SHALL read the API base URL from environment variables
2. THE Backend SHALL read all configuration from environment variables or .env files
3. THE Frontend SHALL support different API URLs for development, staging, and production
4. THE Backend SHALL validate required environment variables on startup
5. WHERE environment variables are missing, THEN THE Backend SHALL fail fast with clear error messages
