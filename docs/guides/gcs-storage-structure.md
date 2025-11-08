# GCS Storage Structure

This document describes how the platform uses Google Cloud Storage for all data and metadata storage.

## Overview

Instead of using a traditional database, all metadata is stored as JSON files in Google Cloud Storage. This simplifies the architecture and reduces infrastructure dependencies.

## Bucket Structure

```
gs://{GCS_BUCKET_NAME}/
├── projects/
│   └── {project_id}.json          # Project metadata
├── datasets/
│   └── {dataset_id}.json          # Dataset metadata
├── models/
│   └── {model_id}.json            # Model metadata
├── audit/
│   └── {project_id}/
│       └── {timestamp}_{stage}.json  # Audit logs
├── data/
│   └── {dataset_id}/
│       ├── raw/                   # Original uploaded files
│       └── processed/             # Processed data for training
└── artifacts/
    └── {model_id}/                # Model artifacts and exports
```

## Data Models

### Project
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "problem_description": "string",
  "status": "analyzing|processing|training|complete|failed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "dataset_id": "uuid",
  "model_id": "uuid|null"
}
```

### Dataset
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "data_type": "image|text|tabular|multimodal",
  "file_paths": ["gs://bucket/path/to/file"],
  "size_bytes": 1024000,
  "num_samples": 1000,
  "is_labeled": true,
  "metadata": {
    "columns": ["col1", "col2"],
    "image_dimensions": [224, 224]
  }
}
```

### Model
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "architecture": "automl_image_classification",
  "vertex_job_id": "vertex-ai-job-id",
  "endpoint_url": "https://endpoint-url",
  "artifact_path": "gs://bucket/artifacts/model-id",
  "metrics": {
    "accuracy": 0.95,
    "precision": 0.93,
    "recall": 0.94
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

### AuditEntry
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "timestamp": "2024-01-01T00:00:00Z",
  "stage": "analyzing",
  "decision_type": "problem_classification",
  "decision": "image_classification",
  "reasoning": "Based on the uploaded images...",
  "confidence": 0.95
}
```

## Storage Manager

The `StorageManager` class in `backend/app/services/cloud/storage_manager.py` provides methods for:

- **Create**: Save new entities as JSON files
- **Read**: Load entities by ID
- **Update**: Update existing JSON files
- **Delete**: Remove JSON files
- **List**: Query and filter entities (loads all matching files)

## Querying

Since we're using JSON files instead of a database:

- **Simple queries**: Load individual files by ID (fast)
- **List operations**: Load all files in a folder and filter in memory (slower for large datasets)
- **Pagination**: Implement in-memory pagination after loading files
- **Indexing**: Use file naming conventions for basic indexing (e.g., `{timestamp}_{id}.json`)

## Trade-offs

**Pros:**
- Simpler architecture (no database to manage)
- Lower infrastructure costs
- Easy backups (just copy the bucket)
- Works well for prototypes and MVPs

**Cons:**
- Slower queries for large datasets
- No ACID transactions
- No complex joins or relationships
- Concurrency requires careful handling

## Migration Path

If you need to scale beyond GCS storage:
1. Keep the Pydantic schemas
2. Add SQLAlchemy models with the same structure
3. Implement a repository pattern that can use either GCS or database
4. Migrate data from JSON files to database tables
