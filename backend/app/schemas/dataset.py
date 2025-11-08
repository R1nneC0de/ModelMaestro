"""Dataset schema definitions."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DataType(str, Enum):
    """Data type enumeration."""
    IMAGE = "image"
    TEXT = "text"
    TABULAR = "tabular"
    MULTIMODAL = "multimodal"


class DatasetBase(BaseModel):
    """Base dataset schema with common fields."""
    data_type: DataType
    is_labeled: bool = Field(default=False)


class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset."""
    project_id: str = Field(..., min_length=1)
    file_paths: List[str] = Field(..., min_items=1)
    size_bytes: int = Field(..., gt=0)
    num_samples: int = Field(..., gt=0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DatasetUpdate(BaseModel):
    """Schema for updating a dataset."""
    is_labeled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class Dataset(DatasetBase):
    """Complete dataset schema."""
    id: str
    project_id: str
    file_paths: List[str]
    size_bytes: int
    num_samples: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "ds_abc123",
                "project_id": "proj_xyz789",
                "data_type": "tabular",
                "file_paths": ["gs://bucket/data/ds_abc123/raw/data.csv"],
                "size_bytes": 1024000,
                "num_samples": 1000,
                "is_labeled": True,
                "metadata": {
                    "columns": ["feature1", "feature2", "target"],
                    "target_column": "target"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }
