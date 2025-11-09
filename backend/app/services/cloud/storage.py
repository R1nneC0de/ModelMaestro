"""GCS storage utilities and helper functions."""

import logging
import os
from pathlib import Path
from typing import Optional, List, BinaryIO
from google.cloud import storage
from google.cloud.exceptions import NotFound, Conflict

from app.core.config import settings
from app.services.cloud.storage_manager import StorageManager
from app.schemas.project import Project
from app.schemas.dataset import Dataset
from app.schemas.model import Model
from app.schemas.audit import AuditEntry

logger = logging.getLogger(__name__)


def get_project_storage() -> StorageManager[Project]:
    """Get storage manager for projects."""
    return StorageManager(
        entity_type="projects",
        schema_class=Project
    )


def get_dataset_storage() -> StorageManager[Dataset]:
    """Get storage manager for datasets."""
    return StorageManager(
        entity_type="datasets",
        schema_class=Dataset
    )


def get_model_storage() -> StorageManager[Model]:
    """Get storage manager for models."""
    return StorageManager(
        entity_type="models",
        schema_class=Model
    )


def get_audit_storage() -> StorageManager[AuditEntry]:
    """Get storage manager for audit entries."""
    return StorageManager(
        entity_type="audit",
        schema_class=AuditEntry
    )


def get_gcs_client() -> storage.Client:
    """
    Get a configured GCS client.
    
    Returns:
        Configured Google Cloud Storage client
    """
    return storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)


async def ensure_bucket_exists(bucket_name: Optional[str] = None) -> bool:
    """
    Ensure the GCS bucket exists, create if it doesn't.
    
    Args:
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        True if bucket exists or was created successfully
        
    Raises:
        Exception: If bucket creation fails
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = get_gcs_client()
    
    try:
        bucket = client.get_bucket(bucket_name)
        logger.info(f"Bucket {bucket_name} already exists")
        return True
    except NotFound:
        logger.info(f"Bucket {bucket_name} not found, creating...")
    except Exception as e:
        logger.error(f"Error checking bucket {bucket_name}: {e}")
        raise
        
    try:
        bucket = client.create_bucket(
            bucket_name,
            location=settings.VERTEX_AI_LOCATION
        )
        logger.info(f"Created bucket {bucket_name} in {settings.VERTEX_AI_LOCATION}")
        return True
    except Conflict:
        logger.warning(f"Bucket {bucket_name} already exists (race condition)")
        return True
    except Exception as e:
        logger.error(f"Failed to create bucket {bucket_name}: {e}")
        raise


async def upload_file_to_gcs(
    local_path: str,
    destination_blob_name: str,
    bucket_name: Optional[str] = None,
    content_type: Optional[str] = None
) -> str:
    """
    Upload a file to GCS from a local path.
    
    Args:
        local_path: Path to the local file
        destination_blob_name: Destination path in GCS (e.g., 'data/dataset_id/file.csv')
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        content_type: MIME type of the file (auto-detected if not provided)
        
    Returns:
        GCS URI of the uploaded file (gs://bucket/path)
        
    Raises:
        FileNotFoundError: If local file doesn't exist
        Exception: If upload fails
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    if content_type:
        blob.content_type = content_type
    
    try:
        blob.upload_from_filename(local_path)
        gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
        file_size = os.path.getsize(local_path)
        logger.info(f"Uploaded {local_path} ({file_size} bytes) to {gcs_uri}")
        return gcs_uri
    except Exception as e:
        logger.error(f"Failed to upload {local_path} to {destination_blob_name}: {e}")
        raise


async def upload_file_from_bytes(
    file_data: bytes,
    destination_blob_name: str,
    bucket_name: Optional[str] = None,
    content_type: Optional[str] = None
) -> str:
    """
    Upload a file to GCS from bytes.
    
    Args:
        file_data: File content as bytes
        destination_blob_name: Destination path in GCS (e.g., 'data/dataset_id/file.csv')
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        content_type: MIME type of the file
        
    Returns:
        GCS URI of the uploaded file (gs://bucket/path)
        
    Raises:
        Exception: If upload fails
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    if content_type:
        blob.content_type = content_type
    
    try:
        blob.upload_from_string(file_data)
        gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
        logger.info(f"Uploaded {len(file_data)} bytes to {gcs_uri}")
        return gcs_uri
    except Exception as e:
        logger.error(f"Failed to upload bytes to {destination_blob_name}: {e}")
        raise


async def upload_multiple_files(
    file_paths: List[str],
    destination_prefix: str,
    bucket_name: Optional[str] = None
) -> List[str]:
    """
    Upload multiple files to GCS.
    
    Args:
        file_paths: List of local file paths
        destination_prefix: Prefix for destination paths (e.g., 'data/dataset_id/raw/')
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        List of GCS URIs for uploaded files
        
    Raises:
        Exception: If any upload fails
    """
    gcs_uris = []
    
    for local_path in file_paths:
        filename = os.path.basename(local_path)
        destination_blob_name = f"{destination_prefix.rstrip('/')}/{filename}"
        gcs_uri = await upload_file_to_gcs(local_path, destination_blob_name, bucket_name)
        gcs_uris.append(gcs_uri)
    
    logger.info(f"Uploaded {len(gcs_uris)} files to {destination_prefix}")
    return gcs_uris


async def list_blobs(
    prefix: str,
    bucket_name: Optional[str] = None
) -> List[str]:
    """
    List all blobs with a given prefix.
    
    Args:
        prefix: Prefix to filter blobs (e.g., 'data/dataset_id/')
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        List of blob names
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    
    blobs = bucket.list_blobs(prefix=prefix)
    blob_names = [blob.name for blob in blobs]
    
    logger.info(f"Found {len(blob_names)} blobs with prefix {prefix}")
    return blob_names


async def delete_blob(
    blob_name: str,
    bucket_name: Optional[str] = None
) -> bool:
    """
    Delete a blob from GCS.
    
    Args:
        blob_name: Name of the blob to delete
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        True if deleted successfully
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    try:
        blob.delete()
        logger.info(f"Deleted blob {blob_name}")
        return True
    except NotFound:
        logger.warning(f"Blob {blob_name} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to delete blob {blob_name}: {e}")
        raise


async def blob_exists(
    blob_name: str,
    bucket_name: Optional[str] = None
) -> bool:
    """
    Check if a blob exists in GCS.
    
    Args:
        blob_name: Name of the blob
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        True if blob exists
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    return blob.exists()


async def download_file_from_gcs(
    source_blob_name: str,
    destination_path: str,
    bucket_name: Optional[str] = None
) -> str:
    """
    Download a file from GCS.
    
    Args:
        source_blob_name: Source path in GCS
        destination_path: Local destination path
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        Local path to the downloaded file
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    blob.download_to_filename(destination_path)
    
    logger.info(f"Downloaded gs://{bucket_name}/{source_blob_name} to {destination_path}")
    return destination_path


async def generate_signed_url(
    blob_name: str,
    bucket_name: Optional[str] = None,
    expiration_minutes: int = 60
) -> str:
    """
    Generate a signed URL for temporary access to a GCS object.
    
    Args:
        blob_name: Path to the blob in GCS
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        expiration_minutes: URL expiration time in minutes
        
    Returns:
        Signed URL for accessing the object
    """
    from datetime import timedelta
    
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )
    
    logger.info(f"Generated signed URL for {blob_name}")
    return url


async def upload_json_to_gcs(
    data: dict,
    blob_name: str,
    bucket_name: Optional[str] = None
) -> str:
    """
    Upload JSON data to GCS.
    
    Args:
        data: Dictionary to upload as JSON
        blob_name: Name/path of the blob in GCS
        bucket_name: Bucket name (defaults to settings)
        
    Returns:
        GCS URI of uploaded file
    """
    import json
    
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Upload JSON data
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        
        uri = f"gs://{bucket_name}/{blob_name}"
        logger.debug(f"Uploaded JSON to {uri}")
        return uri
        
    except Exception as e:
        logger.error(f"Failed to upload JSON to GCS: {e}")
        raise
