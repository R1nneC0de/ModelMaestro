"""Data preview generation service."""

import logging
import os
import csv
import json
from typing import Dict, Any, List

from app.core.config import settings
from app.services.cloud.storage import generate_signed_url

logger = logging.getLogger(__name__)


async def generate_csv_preview(file_path: str, max_rows: int = 10) -> Dict[str, Any]:
    """
    Generate preview for CSV file.
    
    Args:
        file_path: Path to the CSV file
        max_rows: Maximum number of rows to preview
        
    Returns:
        Dictionary with preview data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = []
            total_rows = 0
            
            for i, row in enumerate(reader):
                total_rows += 1
                if i < max_rows:
                    rows.append(row)
            
            return {
                "preview_type": "table",
                "columns": list(reader.fieldnames) if reader.fieldnames else [],
                "rows": rows,
                "total_rows": total_rows,
                "preview_count": len(rows)
            }
    except Exception as e:
        logger.error(f"Failed to generate CSV preview: {e}")
        raise


async def generate_json_preview(file_path: str, max_items: int = 10) -> Dict[str, Any]:
    """
    Generate preview for JSON file.
    
    Args:
        file_path: Path to the JSON file
        max_items: Maximum number of items to preview
        
    Returns:
        Dictionary with preview data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            total_items = len(data)
            preview_data = data[:max_items]
            preview_type = "array"
        elif isinstance(data, dict):
            total_items = len(data)
            preview_data = dict(list(data.items())[:max_items])
            preview_type = "object"
        else:
            total_items = 1
            preview_data = data
            preview_type = "value"
        
        return {
            "preview_type": preview_type,
            "data": preview_data,
            "total_items": total_items,
            "preview_count": len(preview_data) if isinstance(preview_data, (list, dict)) else 1
        }
    except Exception as e:
        logger.error(f"Failed to generate JSON preview: {e}")
        raise


async def generate_image_preview(file_paths: List[str], max_images: int = 10) -> Dict[str, Any]:
    """
    Generate preview for image files.
    
    Args:
        file_paths: List of GCS paths to image files
        max_images: Maximum number of images to preview
        
    Returns:
        Dictionary with preview data (signed URLs)
    """
    try:
        preview_urls = []
        
        for i, gcs_path in enumerate(file_paths[:max_images]):
            # Extract blob name from gs://bucket/path
            blob_name = gcs_path.replace(f"gs://{settings.GCS_BUCKET_NAME}/", "")
            
            # Generate signed URL for temporary access
            signed_url = await generate_signed_url(blob_name, expiration_minutes=60)
            
            preview_urls.append({
                "index": i,
                "url": signed_url,
                "path": gcs_path
            })
        
        return {
            "preview_type": "images",
            "images": preview_urls,
            "total_images": len(file_paths),
            "preview_count": len(preview_urls)
        }
    except Exception as e:
        logger.error(f"Failed to generate image preview: {e}")
        raise


async def generate_text_preview(file_path: str, max_lines: int = 50) -> Dict[str, Any]:
    """
    Generate preview for text file.
    
    Args:
        file_path: Path to the text file
        max_lines: Maximum number of lines to preview
        
    Returns:
        Dictionary with preview data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            total_lines = 0
            
            for i, line in enumerate(f):
                total_lines += 1
                if i < max_lines:
                    lines.append(line.rstrip('\n'))
        
        return {
            "preview_type": "text",
            "lines": lines,
            "total_lines": total_lines,
            "preview_count": len(lines)
        }
    except Exception as e:
        logger.error(f"Failed to generate text preview: {e}")
        raise
