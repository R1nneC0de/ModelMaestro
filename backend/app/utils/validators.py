"""Main validation module - aggregates all validators."""

import logging
import os
from typing import Dict, Any, List, Tuple

from app.utils.file_validators import (
    ValidationError,
    FileType,
    get_file_type,
    get_file_extension,
    validate_file_extension,
    validate_file_size
)
from app.utils.content_validators import (
    validate_csv_file,
    validate_json_file,
    validate_image_file,
    validate_image_folder
)
from app.schemas.dataset import DataType

logger = logging.getLogger(__name__)


def detect_data_type(file_paths: List[str]) -> DataType:
    """
    Detect the data type based on file extensions.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        DataType enum value
    """
    file_types = set()
    
    for file_path in file_paths:
        file_type = get_file_type(file_path)
        file_types.add(file_type)
    
    # Determine data type
    if FileType.IMAGE in file_types:
        if len(file_types) > 1:
            return DataType.MULTIMODAL
        return DataType.IMAGE
    elif FileType.CSV in file_types:
        return DataType.TABULAR
    elif FileType.TEXT in file_types or FileType.JSON in file_types:
        return DataType.TEXT
    else:
        # Default to tabular for unknown types
        return DataType.TABULAR


def validate_upload(
    file_path: str,
    validate_content: bool = True
) -> Tuple[FileType, Dict[str, Any]]:
    """
    Validate an uploaded file.
    
    Args:
        file_path: Path to the file
        validate_content: Whether to validate file content (default: True)
        
    Returns:
        Tuple of (FileType, metadata dictionary)
        
    Raises:
        ValidationError: If validation fails
    """
    # Check file exists
    if not os.path.exists(file_path):
        raise ValidationError(f"File not found: {file_path}")
    
    # Get filename
    filename = os.path.basename(file_path)
    
    # Validate extension
    validate_file_extension(filename)
    
    # Validate size
    file_size = os.path.getsize(file_path)
    validate_file_size(file_size)
    
    # Determine file type
    file_type = get_file_type(filename)
    
    # Validate content if requested
    metadata = {"file_size": file_size, "filename": filename}
    
    if validate_content:
        if file_type == FileType.CSV:
            content_metadata = validate_csv_file(file_path)
            metadata.update(content_metadata)
        elif file_type == FileType.JSON:
            content_metadata = validate_json_file(file_path)
            metadata.update(content_metadata)
        elif file_type == FileType.IMAGE:
            content_metadata = validate_image_file(file_path)
            metadata.update(content_metadata)
    
    return file_type, metadata


def validate_multiple_files(
    file_paths: List[str],
    validate_content: bool = True
) -> Dict[str, Any]:
    """
    Validate multiple uploaded files.
    
    Args:
        file_paths: List of file paths
        validate_content: Whether to validate file content (default: True)
        
    Returns:
        Dictionary with validation results and metadata
        
    Raises:
        ValidationError: If validation fails
    """
    if not file_paths:
        raise ValidationError("No files provided")
    
    total_size = 0
    file_metadata = []
    
    for file_path in file_paths:
        file_type, metadata = validate_upload(file_path, validate_content)
        file_metadata.append({
            "path": file_path,
            "type": file_type,
            "metadata": metadata
        })
        total_size += metadata.get("file_size", 0)
    
    # Validate total size
    validate_file_size(total_size)
    
    # Detect overall data type
    data_type = detect_data_type(file_paths)
    
    result = {
        "num_files": len(file_paths),
        "total_size": total_size,
        "data_type": data_type,
        "files": file_metadata
    }
    
    logger.info(f"Validated {len(file_paths)} files, total size: {total_size} bytes")
    return result
