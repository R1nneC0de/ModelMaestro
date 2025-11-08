"""API response models."""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel

from app.schemas.dataset import DataType


class DataUploadResponse(BaseModel):
    """Response model for data upload."""
    dataset_id: str
    project_id: str
    data_type: DataType
    num_files: int
    total_size: int
    num_samples: int
    message: str


class DataUploadError(BaseModel):
    """Error response for data upload."""
    error: str
    details: Optional[str] = None


class DataPreview(BaseModel):
    """Response model for data preview."""
    dataset_id: str
    data_type: DataType
    preview_type: str
    preview_data: Union[List[Dict[str, Any]], List[str], Dict[str, Any]]
    total_samples: int
    preview_count: int
