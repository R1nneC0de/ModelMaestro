# Storage Manager Setup Guide

This guide walks you through setting up and testing the GCS Storage Manager.

## Prerequisites

1. **Google Cloud Project**: `agentic-workflow-477603`
2. **Service Account Key**: Already configured in `gcp-credentials/gcp-key.json`
3. **Python Dependencies**: Install required packages

## Installation

### 1. Install Python Dependencies

```bash
cd backend
pip install google-cloud-storage google-cloud-aiplatform pydantic pydantic-settings
```

### 2. Verify Environment Configuration

The `.env` file should already be configured with:

```bash
GOOGLE_CLOUD_PROJECT=agentic-workflow-477603
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials/gcp-key.json
GCS_BUCKET_NAME=agentic-ai-data
```

### 3. Test the Storage Manager

Run the test script to verify everything works:

```bash
cd backend
python test_storage.py
```

You should see output like:

```
🔧 Testing GCS Storage Manager...

1️⃣ Checking/creating bucket...
✅ Bucket ready

2️⃣ Creating test project...
✅ Created project: test_proj_001

3️⃣ Retrieving project...
✅ Retrieved project: test_proj_001
   Status: analyzing
   Description: Test project for storage manager validation

4️⃣ Updating project...
✅ Updated project status to: training

5️⃣ Listing all projects...
✅ Found 1 project(s)
   - test_proj_001: training

6️⃣ Checking project existence...
✅ Project exists: True

✨ All tests passed! Storage manager is working correctly.
```

## GCS Bucket Structure

After running the test, your bucket will have this structure:

```
gs://agentic-ai-data/
└── projects/
    └── test_proj_001.json
```

## Usage in Your Code

### Creating a Project

```python
from backend.app.services.cloud.storage import get_project_storage
from backend.app.schemas.project import Project, ProjectStatus
from datetime import datetime

# Get storage manager
project_storage = get_project_storage()

# Create a project
project = Project(
    id="proj_abc123",
    user_id="user_xyz789",
    problem_description="Predict house prices",
    status=ProjectStatus.ANALYZING,
    requires_approval=False,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

# Save to GCS
await project_storage.create(project, project.id)
```

### Retrieving a Project

```python
# Get by ID
project = await project_storage.get("proj_abc123")
if project:
    print(f"Found project: {project.problem_description}")
```

### Updating a Project

```python
# Update fields
updated = await project_storage.update(
    "proj_abc123",
    {
        "status": ProjectStatus.TRAINING.value,
        "dataset_id": "ds_def456"
    }
)
```

### Listing Projects

```python
# List all projects
all_projects = await project_storage.list()

# List with filter
user_projects = await project_storage.list(
    filter_fn=lambda p: p.user_id == "user_xyz789"
)

# List with limit
recent_projects = await project_storage.list(limit=10)
```

### Deleting a Project

```python
# Delete by ID
deleted = await project_storage.delete("proj_abc123")
```

## Storage Managers for Other Entities

```python
from backend.app.services.cloud.storage import (
    get_project_storage,
    get_dataset_storage,
    get_model_storage,
    get_audit_storage
)

# Each entity type has its own storage manager
project_storage = get_project_storage()
dataset_storage = get_dataset_storage()
model_storage = get_model_storage()
audit_storage = get_audit_storage()
```

## Audit Logs with Subfolders

Audit logs are organized by project:

```python
from backend.app.schemas.audit import AuditEntry
from datetime import datetime

audit_entry = AuditEntry(
    id="audit_001",
    project_id="proj_abc123",
    timestamp=datetime.utcnow(),
    stage="analyzing",
    decision_type="problem_classification",
    decision="tabular_classification",
    reasoning="Based on CSV structure",
    confidence=0.95,
    metadata={}
)

# Store in audit/{project_id}/ subfolder
await audit_storage.create(
    audit_entry,
    audit_entry.id,
    subfolder="proj_abc123"
)
```

## Troubleshooting

### Authentication Error

If you see authentication errors:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="./gcp-credentials/gcp-key.json"
```

### Bucket Not Found

The script will automatically create the bucket if it doesn't exist. If creation fails, create it manually:

```bash
gsutil mb -p agentic-workflow-477603 -l us-central1 gs://agentic-ai-data
```

### Permission Denied

Ensure your service account has these roles:
- Storage Admin
- Vertex AI User

## Next Steps

Now that storage is working, you can:

1. **Task 3**: Implement data upload and storage service
2. **Task 4**: Build Problem Analyzer component (already started)
3. **Task 11**: Implement Agent Orchestrator to use storage

The storage manager is the foundation for all data persistence in the platform!
