"""Project schema definitions."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    LABELING = "labeling"
    TRAINING = "training"
    EVALUATING = "evaluating"
    DEPLOYING = "deploying"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    problem_description: str = Field(..., min_length=10, max_length=5000)
    requires_approval: bool = Field(default=False)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    user_id: str = Field(..., min_length=1)


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    status: Optional[ProjectStatus] = None
    dataset_id: Optional[str] = None
    model_id: Optional[str] = None


class Project(ProjectBase):
    """Complete project schema."""
    id: str
    user_id: str
    status: ProjectStatus = ProjectStatus.ANALYZING
    created_at: datetime
    updated_at: datetime
    dataset_id: Optional[str] = None
    model_id: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "proj_abc123",
                "user_id": "user_xyz789",
                "problem_description": "Predict house prices based on features",
                "status": "training",
                "requires_approval": False,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T01:00:00Z",
                "dataset_id": "ds_def456",
                "model_id": "model_ghi789"
            }
        }
    }


class ProjectListResponse(BaseModel):
    """Response schema for paginated project list."""
    projects: list[Project]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "projects": [],
                "total": 42,
                "page": 1,
                "page_size": 10
            }
        }
    }


class ProjectProgressResponse(BaseModel):
    """Response schema for project progress."""
    project_id: str
    stage: str
    progress: float = Field(ge=0.0, le=1.0)
    logs: list[dict] = Field(default_factory=list)
    decisions: list[dict] = Field(default_factory=list)
    error: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "project_id": "proj_abc123",
                "stage": "training",
                "progress": 0.65,
                "logs": [
                    {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "message": "Starting training"}
                ],
                "decisions": [
                    {"stage": "analyzing", "decision": "tabular_classification", "confidence": 0.95}
                ],
                "error": None
            }
        }
    }


class ProjectDeleteResponse(BaseModel):
    """Response schema for project deletion."""
    message: str
    project_id: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Project deleted successfully",
                "project_id": "proj_abc123"
            }
        }
    }
