# Frontend-Backend Integration - Remaining Tasks

## Status: 85% Complete ✅

Most of the integration is already built! Only 3 critical tasks remain to connect everything.

---

# What's Already Done ✅

- ✅ Backend project schemas and models
- ✅ Projects API router with all CRUD endpoints
- ✅ Project service layer
- ✅ WebSocket infrastructure with real-time updates
- ✅ Event broadcaster
- ✅ Frontend API client
- ✅ WebSocket hook with reconnection logic
- ✅ Progress dashboard UI
- ✅ Pipeline stages visualization
- ✅ Log stream component
- ✅ Model results page
- ✅ CORS configuration

---

# Critical Tasks Remaining (2 hours total)

## 1. Wire Orchestrator to Project Service (45 min)

**File**: `backend/app/services/project_service.py`

**Current State**: `_start_pipeline` method is a placeholder

**What to do**:
- [ ] 1.1 Implement dataset loading from GCS
  - Load dataset using dataset_id from DatasetService
  - Parse CSV/JSON into pandas DataFrame
  - Validate data format
  - _Requirements: 2.3, 2.4_

- [ ] 1.2 Call orchestrator.run_pipeline
  - Pass project_id, dataset, and problem_description
  - Execute in background asyncio task
  - Handle orchestrator exceptions
  - _Requirements: 2.3, 2.4_

- [ ] 1.3 Update project status during execution
  - Update status in GCS as pipeline progresses
  - Store model_id when training completes
  - Set status to FAILED on errors
  - _Requirements: 2.4, 8.1_

## 2. Connect FileUploadOverlay to Backend (30 min)

**File**: `frontend/src/3d/components/ui/FileUploadOverlay.tsx`

**Current State**: Uses placeholder API calls

**What to do**:
- [ ] 2.1 Implement two-step upload process
  - First: Upload file to `/data/upload` endpoint
  - Get dataset_id from response
  - Second: Create project with `/projects?dataset_id={id}`
  - _Requirements: 6.1, 6.2_

- [ ] 2.2 Show ProgressDashboardOverlay after creation
  - Store project_id from response
  - Set showProgressDashboard state to true
  - Pass project_id to ProgressDashboardOverlay
  - _Requirements: 3.1, 3.2_

- [ ] 2.3 Handle errors gracefully
  - Show user-friendly error messages
  - Allow retry on failure
  - Validate file before upload
  - _Requirements: 9.1, 9.5_

## 3. Connect HistoryBrowserOverlay to Backend (20 min)

**File**: `frontend/src/3d/components/ui/HistoryBrowserOverlay.tsx`

**Current State**: Uses placeholder history API

**What to do**:
- [ ] 3.1 Fetch projects from backend
  - Call `/projects` endpoint with useQuery
  - Handle pagination
  - Map ProjectListResponse to display format
  - _Requirements: 1.2, 7.1_

- [ ] 3.2 Display project status with colors
  - Map ProjectStatus to visual indicators
  - Show training=yellow, completed=green, failed=red
  - Display progress percentage
  - _Requirements: 7.2, 7.3_

- [ ] 3.3 Implement project detail view
  - Click handler to view full project details
  - Show metrics and evaluation report
  - Display prediction endpoint if available
  - _Requirements: 7.3, 8.2_

---

# Optional Tasks (Can be done later)

- [ ]* 4. Add comprehensive error handling tests
  - Test API error scenarios (400, 404, 500)
  - Test WebSocket reconnection logic
  - Test file upload validation
  - _Requirements: 9.1, 9.2, 9.3_

- [ ]* 5. Add integration tests
  - Test project creation end-to-end
  - Test WebSocket event delivery
  - Test project list retrieval
  - _Requirements: 1.1, 1.2, 3.1_

- [ ]* 6. Add API documentation
  - Generate OpenAPI/Swagger docs
  - Add request/response examples
  - Document WebSocket events
  - _Requirements: 4.5_

- [ ]* 7. Performance optimization
  - Add request caching
  - Implement connection pooling
  - Monitor WebSocket health
  - _Requirements: 3.5, 5.4_

---

# Quick Start Guide

## To Complete Integration:

1. **Start with Task 1** - Wire the orchestrator (most important)
2. **Then Task 2** - Connect file upload
3. **Finally Task 3** - Connect history display
4. **Test** - Upload a file and watch it train!

## Testing:

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Browser: http://localhost:3000
# Upload a CSV file and watch the magic happen!
```

---

# Summary

**Total remaining work**: ~2 hours
**Critical tasks**: 3
**Optional tasks**: 4

You're 85% done! Just need to connect the dots between your existing frontend and backend code.
