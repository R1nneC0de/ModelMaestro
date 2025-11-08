"""Model schema definitions."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ModelBase(BaseModel):
    """Base model schema with common fields."""
    architecture: str = Field(..., min_length=1)


class ModelCreate(ModelBase):
    """Schema for creating a new model."""
    project_id: str = Field(..., min_length=1)
    vertex_job_id: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ModelUpdate(BaseModel):
    """Schema for updating a model."""
    vertex_job_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    artifact_path: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    hyperparameters: Optional[Dict[str, Any]] = None


class Model(ModelBase):
    """Complete model schema."""
    id: str
    project_id: str
    vertex_job_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    artifact_path: Optional[str] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "model_abc123",
                "project_id": "proj_xyz789",
                "architecture": "automl_tabular_classification",
                "vertex_job_id": "vertex-job-12345",
                "endpoint_url": "https://us-central1-aiplatform.googleapis.com/v1/projects/123/locations/us-central1/endpoints/456",
                "artifact_path": "gs://bucket/artifacts/model_abc123",
                "metrics": {
                    "accuracy": 0.95,
                    "precision": 0.93,
                    "recall": 0.94,
                    "f1_score": 0.935
                },
                "hyperparameters": {
                    "learning_rate": 0.001,
                    "batch_size": 32
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }
