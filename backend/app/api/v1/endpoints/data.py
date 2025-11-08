"""Data upload and management endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.schemas.dataset import Dataset
from app.schemas.api_responses import (
    DataUploadResponse,
    DataUploadError,
    DataPreview
)
from app.services.dataset_service import DatasetService
from app.utils.validators import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DataUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": DataUploadError, "description": "Validation error"},
        413: {"model": DataUploadError, "description": "File too large"},
        500: {"model": DataUploadError, "description": "Server error"}
    }
)
async def upload_data(
    files: List[UploadFile] = File(..., description="Data files to upload"),
    project_id: str = Form(..., description="Project ID this dataset belongs to"),
    data_type: Optional[str] = Form(None, description="Optional data type override (image, text, tabular, multimodal)")
) -> DataUploadResponse:
    """
    Upload dataset files for a project.
    
    This endpoint accepts multiple files and:
    1. Validates file formats and sizes
    2. Uploads files to Google Cloud Storage
    3. Creates dataset metadata
    4. Returns dataset information
    
    Supported formats:
    - CSV files for tabular data
    - JSON files for structured data
    - Image files (jpg, png, etc.) for image data
    - Text files for text data
    
    Maximum total upload size: 10GB (configurable)
    """
    try:
        # Validate inputs
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        if not project_id or not project_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID is required"
            )
        
        # Create dataset
        dataset = await DatasetService.create_dataset(files, project_id, data_type)
        
        return DataUploadResponse(
            dataset_id=dataset.id,
            project_id=dataset.project_id,
            data_type=dataset.data_type,
            num_files=len(dataset.file_paths),
            total_size=dataset.size_bytes,
            num_samples=dataset.num_samples,
            message=f"Successfully uploaded {len(dataset.file_paths)} file(s)"
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        error_msg = str(e)
        if "exceeds maximum" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/{dataset_id}",
    response_model=Dataset,
    responses={
        404: {"model": DataUploadError, "description": "Dataset not found"}
    }
)
async def get_dataset(dataset_id: str) -> Dataset:
    """
    Get dataset metadata by ID.
    
    Args:
        dataset_id: The dataset ID
        
    Returns:
        Dataset metadata
    """
    try:
        dataset = await DatasetService.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found"
            )
        
        return dataset
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dataset: {str(e)}"
        )


@router.get(
    "/project/{project_id}",
    response_model=List[Dataset],
)
async def list_project_datasets(project_id: str) -> List[Dataset]:
    """
    List all datasets for a project.
    
    Args:
        project_id: The project ID
        
    Returns:
        List of datasets
    """
    try:
        datasets = await DatasetService.list_datasets(project_id)
        return datasets
        
    except Exception as e:
        logger.error(f"Error listing datasets for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets: {str(e)}"
        )


@router.get(
    "/{dataset_id}/preview",
    response_model=DataPreview,
    responses={
        404: {"model": DataUploadError, "description": "Dataset not found"},
        500: {"model": DataUploadError, "description": "Preview generation failed"}
    }
)
async def get_data_preview(
    dataset_id: str,
    max_items: int = 10
) -> DataPreview:
    """
    Generate a preview of the dataset.
    
    This endpoint generates previews based on data type:
    - CSV: First N rows with column headers
    - JSON: First N items or key-value pairs
    - Images: Signed URLs for first N images
    - Text: First N lines
    
    Args:
        dataset_id: The dataset ID
        max_items: Maximum number of items to include in preview (default: 10)
        
    Returns:
        Preview data appropriate for the data type
    """
    try:
        preview_data = await DatasetService.generate_preview(dataset_id, max_items)
        return DataPreview(**preview_data)
        
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        logger.error(f"Error generating preview for dataset {dataset_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate preview: {str(e)}"
        )
