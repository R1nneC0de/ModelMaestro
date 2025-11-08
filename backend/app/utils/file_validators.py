"""Core file validation utilities."""

import logging
from pathlib import Path
from typing import Optional
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class FileType(str, Enum):
    """Supported file types."""
    CSV = "csv"
    JSON = "json"
    IMAGE = "image"
    TEXT = "text"
    UNKNOWN = "unknown"


# Image file extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

# Text file extensions
TEXT_EXTENSIONS = {".txt", ".md", ".log"}


def get_file_extension(filename: str) -> str:
    """
    Get the file extension in lowercase.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension including the dot (e.g., '.csv')
    """
    return Path(filename).suffix.lower()


def get_file_type(filename: str) -> FileType:
    """
    Determine the file type based on extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        FileType enum value
    """
    ext = get_file_extension(filename)
    
    if ext == ".csv":
        return FileType.CSV
    elif ext == ".json":
        return FileType.JSON
    elif ext in IMAGE_EXTENSIONS:
        return FileType.IMAGE
    elif ext in TEXT_EXTENSIONS:
        return FileType.TEXT
    else:
        return FileType.UNKNOWN


def validate_file_extension(filename: str) -> bool:
    """
    Validate that the file extension is allowed.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if extension is allowed
        
    Raises:
        ValidationError: If extension is not allowed
    """
    ext = get_file_extension(filename)
    allowed = settings.allowed_extensions_list
    
    if ext not in allowed:
        raise ValidationError(
            f"File extension '{ext}' not allowed. "
            f"Allowed extensions: {', '.join(allowed)}"
        )
    
    return True


def validate_file_size(file_size: int, max_size: Optional[int] = None) -> bool:
    """
    Validate that the file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
        max_size: Maximum allowed size in bytes (defaults to settings.max_upload_size_bytes)
        
    Returns:
        True if size is valid
        
    Raises:
        ValidationError: If file is too large
    """
    max_size = max_size or settings.max_upload_size_bytes
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise ValidationError(
            f"File size ({actual_mb:.2f} MB) exceeds maximum allowed size ({max_mb:.2f} MB)"
        )
    
    if file_size == 0:
        raise ValidationError("File is empty (0 bytes)")
    
    return True
