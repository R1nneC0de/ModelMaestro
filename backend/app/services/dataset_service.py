"""Dataset service - handles dataset business logic."""

import logging
import os
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.dataset import Dataset, DataType
from app.services.cloud.storage import (
    ensure_bucket_exists,
    upload_multiple_files,
    get_dataset_storage,
    download_file_from_gcs
)
from app.services.preview_generator import (
    generate_csv_preview,
    generate_json_preview,
    generate_image_preview,
    generate_text_preview
)
from app.utils.validators import validate_multiple_files, ValidationError

logger = logging.getLogger(__name__)


class DatasetService:
    """Service for managing datasets."""
    
    @staticmethod
    async def save_uploaded_files(files: List[UploadFile], temp_dir: str) -> tuple[List[str], int]:
        """
        Save uploaded files to temporary directory.
        
        Args:
            files: List of uploaded files
            temp_dir: Temporary directory path
            
        Returns:
            Tuple of (file_paths, total_size)
            
        Raises:
            ValueError: If total size exceeds limit
        """
        temp_file_paths = []
        total_size = 0
        
        for upload_file in files:
            file_content = await upload_file.read()
            file_size = len(file_content)
            total_size += file_size
            
            # Check total size doesn't exceed limit
            if total_size > settings.max_upload_size_bytes:
                raise ValueError(
                    f"Total upload size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB"
                )
            
            # Save to temp file
            temp_file_path = os.path.join(temp_dir, upload_file.filename)
            with open(temp_file_path, 'wb') as f:
                f.write(file_content)
            
            temp_file_paths.append(temp_file_path)
            logger.info(f"Saved {upload_file.filename} ({file_size} bytes) to temp")
        
        return temp_file_paths, total_size
    
    @staticmethod
    def extract_metadata(validation_result: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """
        Extract num_samples and metadata from validation result.
        
        Args:
            validation_result: Validation result dictionary
            
        Returns:
            Tuple of (num_samples, metadata)
        """
        num_samples = 0
        metadata = {}
        
        for file_meta in validation_result["files"]:
            file_metadata = file_meta["metadata"]
            
            # Extract sample count based on file type
            if "row_count" in file_metadata:
                num_samples += file_metadata["row_count"]
            elif "num_items" in file_metadata:
                num_samples += file_metadata["num_items"]
            elif file_meta["type"] == "image":
                num_samples += 1
            
            # Store relevant metadata
            if "columns" in file_metadata:
                metadata["columns"] = file_metadata["columns"]
            if "structure" in file_metadata:
                metadata["structure"] = file_metadata["structure"]
        
        # If no samples detected, use file count
        if num_samples == 0:
            num_samples = len(validation_result["files"])
        
        return num_samples, metadata
    
    @staticmethod
    async def create_dataset(
        files: List[UploadFile],
        project_id: str,
        data_type: Optional[str] = None
    ) -> Dataset:
        """
        Create a new dataset from uploaded files.
        
        Args:
            files: List of uploaded files
            project_id: Project ID
            data_type: Optional data type override
            
        Returns:
            Created dataset
            
        Raises:
            ValueError: If validation fails or upload fails
        """
        temp_dir = None
        
        try:
            # Ensure bucket exists
            await ensure_bucket_exists()
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temp directory: {temp_dir}")
            
            # Save uploaded files
            temp_file_paths, total_size = await DatasetService.save_uploaded_files(files, temp_dir)
            
            # Validate files
            validation_result = validate_multiple_files(temp_file_paths, validate_content=True)
            
            # Determine data type
            if data_type:
                try:
                    detected_data_type = DataType(data_type.lower())
                except ValueError:
                    raise ValueError(
                        f"Invalid data type: {data_type}. Must be one of: image, text, tabular, multimodal"
                    )
            else:
                detected_data_type = validation_result["data_type"]
            
            # Generate dataset ID
            dataset_id = f"ds_{uuid4().hex[:12]}"
            
            # Upload files to GCS
            destination_prefix = f"data/{dataset_id}/raw"
            gcs_uris = await upload_multiple_files(temp_file_paths, destination_prefix)
            
            # Extract metadata
            num_samples, metadata = DatasetService.extract_metadata(validation_result)
            
            # Create dataset record
            dataset = Dataset(
                id=dataset_id,
                project_id=project_id,
                data_type=detected_data_type,
                file_paths=gcs_uris,
                size_bytes=total_size,
                num_samples=num_samples,
                is_labeled=False,
                metadata=metadata,
                created_at=datetime.utcnow()
            )
            
            # Save to storage
            storage_manager = get_dataset_storage()
            await storage_manager.create(dataset, dataset_id)
            
            logger.info(f"Created dataset {dataset_id} for project {project_id}")
            return dataset
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp directory: {e}")
    
    @staticmethod
    async def get_dataset(dataset_id: str) -> Optional[Dataset]:
        """
        Get dataset by ID.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dataset or None if not found
        """
        storage_manager = get_dataset_storage()
        return await storage_manager.get(dataset_id)
    
    @staticmethod
    async def list_datasets(project_id: str) -> List[Dataset]:
        """
        List all datasets for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of datasets
        """
        storage_manager = get_dataset_storage()
        return await storage_manager.list(filters={"project_id": project_id})
    
    @staticmethod
    async def generate_preview(dataset_id: str, max_items: int = 10) -> Dict[str, Any]:
        """
        Generate a preview of the dataset.
        
        Args:
            dataset_id: Dataset ID
            max_items: Maximum number of items to preview
            
        Returns:
            Preview data dictionary
            
        Raises:
            ValueError: If dataset not found or preview generation fails
        """
        temp_dir = None
        
        try:
            # Get dataset
            dataset = await DatasetService.get_dataset(dataset_id)
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # Generate preview based on data type
            if dataset.data_type == DataType.IMAGE:
                # For images, generate signed URLs
                preview_result = await generate_image_preview(dataset.file_paths, max_items)
                
                return {
                    "dataset_id": dataset_id,
                    "data_type": dataset.data_type,
                    "preview_type": preview_result["preview_type"],
                    "preview_data": preview_result["images"],
                    "total_samples": preview_result["total_images"],
                    "preview_count": preview_result["preview_count"]
                }
            
            else:
                # For other types, download first file and generate preview
                temp_dir = tempfile.mkdtemp()
                
                # Get first file
                first_file_gcs = dataset.file_paths[0]
                blob_name = first_file_gcs.replace(f"gs://{settings.GCS_BUCKET_NAME}/", "")
                temp_file_path = os.path.join(temp_dir, os.path.basename(blob_name))
                
                # Download file
                await download_file_from_gcs(blob_name, temp_file_path)
                
                # Generate preview based on file extension
                file_ext = os.path.splitext(temp_file_path)[1].lower()
                
                if file_ext == '.csv':
                    preview_result = await generate_csv_preview(temp_file_path, max_items)
                    preview_data = preview_result["rows"]
                    total_samples = preview_result["total_rows"]
                    preview_count = preview_result["preview_count"]
                    preview_type = preview_result["preview_type"]
                    
                elif file_ext == '.json':
                    preview_result = await generate_json_preview(temp_file_path, max_items)
                    preview_data = preview_result["data"]
                    total_samples = preview_result["total_items"]
                    preview_count = preview_result["preview_count"]
                    preview_type = preview_result["preview_type"]
                    
                elif file_ext in ['.txt', '.md', '.log']:
                    preview_result = await generate_text_preview(temp_file_path, max_items * 5)
                    preview_data = preview_result["lines"]
                    total_samples = preview_result["total_lines"]
                    preview_count = preview_result["preview_count"]
                    preview_type = preview_result["preview_type"]
                    
                else:
                    raise ValueError(f"Preview not supported for file type: {file_ext}")
                
                return {
                    "dataset_id": dataset_id,
                    "data_type": dataset.data_type,
                    "preview_type": preview_type,
                    "preview_data": preview_data,
                    "total_samples": total_samples,
                    "preview_count": preview_count
                }
            
        finally:
            # Clean up temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp directory: {e}")
