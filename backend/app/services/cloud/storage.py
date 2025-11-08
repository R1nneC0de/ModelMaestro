"""GCS storage utilities and helper functions."""

import logging
from typing import Optional
from google.cloud import storage

from backend.app.core.config import settings
from backend.app.services.cloud.storage_manager import StorageManager
from backend.app.schemas.project import Project
from backend.app.schemas.dataset import Dataset
from backend.app.schemas.model import Model
from backend.app.schemas.audit import AuditEntry

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


async def ensure_bucket_exists(bucket_name: Optional[str] = None) -> bool:
    """
    Ensure the GCS bucket exists, create if it doesn't.
    
    Args:
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        True if bucket exists or was created successfully
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
    
    try:
        bucket = client.get_bucket(bucket_name)
        logger.info(f"Bucket {bucket_name} already exists")
        return True
    except Exception:
        logger.info(f"Bucket {bucket_name} not found, creating...")
        
    try:
        bucket = client.create_bucket(
            bucket_name,
            location=settings.VERTEX_AI_LOCATION
        )
        logger.info(f"Created bucket {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create bucket {bucket_name}: {e}")
        return False


async def upload_file_to_gcs(
    local_path: str,
    destination_blob_name: str,
    bucket_name: Optional[str] = None
) -> str:
    """
    Upload a file to GCS.
    
    Args:
        local_path: Path to the local file
        destination_blob_name: Destination path in GCS (e.g., 'data/dataset_id/file.csv')
        bucket_name: Name of the bucket (defaults to settings.GCS_BUCKET_NAME)
        
    Returns:
        GCS URI of the uploaded file (gs://bucket/path)
    """
    bucket_name = bucket_name or settings.GCS_BUCKET_NAME
    client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(local_path)
    gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
    
    logger.info(f"Uploaded {local_path} to {gcs_uri}")
    return gcs_uri


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
