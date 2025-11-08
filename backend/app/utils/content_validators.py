"""Content validation for different file types."""

import logging
import json
import csv
import os
from typing import Dict, Any

from app.utils.file_validators import ValidationError, IMAGE_EXTENSIONS

logger = logging.getLogger(__name__)


def validate_csv_file(file_path: str, sample_size: int = 5) -> Dict[str, Any]:
    """
    Validate a CSV file and extract metadata.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with metadata (columns, row_count, sample_data)
        
    Raises:
        ValidationError: If CSV is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to detect dialect
            sample = f.read(8192)
            f.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            
            reader = csv.DictReader(f, dialect=dialect)
            
            # Get column names
            columns = reader.fieldnames
            if not columns:
                raise ValidationError("CSV file has no columns")
            
            # Count rows and get sample
            rows = []
            row_count = 0
            for i, row in enumerate(reader):
                row_count += 1
                if i < sample_size:  # Get sample rows
                    rows.append(row)
            
            if row_count == 0:
                raise ValidationError("CSV file has no data rows")
            
            metadata = {
                "columns": list(columns),
                "row_count": row_count,
                "sample_data": rows,
                "file_type": "csv"
            }
            
            logger.info(f"Validated CSV: {row_count} rows, {len(columns)} columns")
            return metadata
            
    except UnicodeDecodeError:
        raise ValidationError("CSV file encoding is not UTF-8")
    except csv.Error as e:
        raise ValidationError(f"Invalid CSV format: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Failed to validate CSV file: {str(e)}")


def validate_json_file(file_path: str, sample_size: int = 5) -> Dict[str, Any]:
    """
    Validate a JSON file and extract metadata.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary with metadata (structure, sample_data)
        
    Raises:
        ValidationError: If JSON is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determine structure
        if isinstance(data, list):
            num_items = len(data)
            sample = data[:sample_size] if num_items > sample_size else data
            structure = "array"
        elif isinstance(data, dict):
            num_items = len(data)
            sample = dict(list(data.items())[:sample_size])
            structure = "object"
        else:
            raise ValidationError("JSON must be an array or object")
        
        metadata = {
            "structure": structure,
            "num_items": num_items,
            "sample_data": sample,
            "file_type": "json"
        }
        
        logger.info(f"Validated JSON: {structure} with {num_items} items")
        return metadata
        
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}")
    except UnicodeDecodeError:
        raise ValidationError("JSON file encoding is not UTF-8")
    except Exception as e:
        raise ValidationError(f"Failed to validate JSON file: {str(e)}")


def validate_image_file(file_path: str) -> Dict[str, Any]:
    """
    Validate an image file and extract metadata.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Dictionary with metadata (width, height, format)
        
    Raises:
        ValidationError: If image is invalid
    """
    try:
        from PIL import Image
        
        with Image.open(file_path) as img:
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "file_type": "image"
            }
            
            logger.info(f"Validated image: {img.width}x{img.height}, {img.format}")
            return metadata
            
    except ImportError:
        # Pillow not installed, do basic validation
        logger.warning("Pillow not installed, skipping detailed image validation")
        return {
            "file_type": "image",
            "validated": False
        }
    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")


def validate_image_folder(folder_path: str) -> Dict[str, Any]:
    """
    Validate a folder containing images.
    
    Args:
        folder_path: Path to the folder
        
    Returns:
        Dictionary with metadata (num_images, image_files)
        
    Raises:
        ValidationError: If folder is invalid or contains no images
    """
    from app.utils.file_validators import validate_file_size, get_file_extension
    
    if not os.path.isdir(folder_path):
        raise ValidationError(f"Path is not a directory: {folder_path}")
    
    image_files = []
    total_size = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            ext = get_file_extension(file)
            if ext in IMAGE_EXTENSIONS:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                total_size += file_size
                image_files.append({
                    "path": file_path,
                    "name": file,
                    "size": file_size
                })
    
    if not image_files:
        raise ValidationError("Folder contains no image files")
    
    # Validate total size
    validate_file_size(total_size)
    
    metadata = {
        "num_images": len(image_files),
        "image_files": image_files,
        "total_size": total_size,
        "file_type": "image_folder"
    }
    
    logger.info(f"Validated image folder: {len(image_files)} images, {total_size} bytes")
    return metadata
