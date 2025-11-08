"""GCS Storage Manager for metadata and data persistence."""

import json
import logging
from datetime import datetime
from typing import List, Optional, Type, TypeVar, Generic, Dict, Any, Callable
from google.cloud import storage
from google.cloud.exceptions import NotFound
from pydantic import BaseModel

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class StorageManager(Generic[T]):
    """
    Generic storage manager for persisting Pydantic models as JSON in GCS.
    
    Provides CRUD operations for entities stored in Google Cloud Storage.
    Each entity type has its own folder structure in the bucket.
    """
    
    def __init__(
        self,
        entity_type: str,
        schema_class: Type[T],
        bucket_name: Optional[str] = None
    ):
        """
        Initialize the storage manager.
        
        Args:
            entity_type: Type of entity (e.g., 'projects', 'datasets', 'models', 'audit')
            schema_class: Pydantic model class for validation
            bucket_name: GCS bucket name (defaults to settings.GCS_BUCKET_NAME)
        """
        self.entity_type = entity_type
        self.schema_class = schema_class
        self.bucket_name = bucket_name or settings.GCS_BUCKET_NAME
        
        # Initialize GCS client
        self.client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        self.bucket = self.client.bucket(self.bucket_name)
        
        logger.info(
            f"Initialized StorageManager for {entity_type} in bucket {self.bucket_name}"
        )
    
    def _get_blob_path(self, entity_id: str, subfolder: Optional[str] = None) -> str:
        """
        Get the GCS blob path for an entity.
        
        Args:
            entity_id: Unique identifier for the entity
            subfolder: Optional subfolder (e.g., for audit logs by project)
            
        Returns:
            Full blob path in GCS
        """
        if subfolder:
            return f"{self.entity_type}/{subfolder}/{entity_id}.json"
        return f"{self.entity_type}/{entity_id}.json"
    
    async def create(self, entity: T, entity_id: str, subfolder: Optional[str] = None) -> T:
        """
        Create a new entity in GCS.
        
        Args:
            entity: Pydantic model instance to store
            entity_id: Unique identifier for the entity
            subfolder: Optional subfolder for organization
            
        Returns:
            The created entity
            
        Raises:
            ValueError: If entity already exists
        """
        blob_path = self._get_blob_path(entity_id, subfolder)
        blob = self.bucket.blob(blob_path)
        
        # Check if already exists
        if blob.exists():
            raise ValueError(f"{self.entity_type} with id {entity_id} already exists")
        
        # Serialize and upload
        entity_dict = entity.model_dump(mode='json')
        blob.upload_from_string(
            json.dumps(entity_dict, indent=2),
            content_type='application/json'
        )
        
        logger.info(f"Created {self.entity_type} {entity_id} at {blob_path}")
        return entity
    
    async def get(self, entity_id: str, subfolder: Optional[str] = None) -> Optional[T]:
        """
        Retrieve an entity from GCS.
        
        Args:
            entity_id: Unique identifier for the entity
            subfolder: Optional subfolder where entity is stored
            
        Returns:
            The entity if found, None otherwise
        """
        blob_path = self._get_blob_path(entity_id, subfolder)
        blob = self.bucket.blob(blob_path)
        
        try:
            content = blob.download_as_text()
            entity_dict = json.loads(content)
            return self.schema_class(**entity_dict)
        except NotFound:
            logger.warning(f"{self.entity_type} {entity_id} not found at {blob_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading {self.entity_type} {entity_id}: {e}")
            raise
    
    async def update(
        self,
        entity_id: str,
        updates: Dict[str, Any],
        subfolder: Optional[str] = None
    ) -> Optional[T]:
        """
        Update an existing entity in GCS.
        
        Args:
            entity_id: Unique identifier for the entity
            updates: Dictionary of fields to update
            subfolder: Optional subfolder where entity is stored
            
        Returns:
            The updated entity if found, None otherwise
        """
        # Get existing entity
        entity = await self.get(entity_id, subfolder)
        if not entity:
            return None
        
        # Update fields
        entity_dict = entity.model_dump()
        entity_dict.update(updates)
        entity_dict['updated_at'] = datetime.utcnow().isoformat()
        
        # Validate and save
        updated_entity = self.schema_class(**entity_dict)
        blob_path = self._get_blob_path(entity_id, subfolder)
        blob = self.bucket.blob(blob_path)
        
        blob.upload_from_string(
            json.dumps(updated_entity.model_dump(mode='json'), indent=2),
            content_type='application/json'
        )
        
        logger.info(f"Updated {self.entity_type} {entity_id}")
        return updated_entity
    
    async def delete(self, entity_id: str, subfolder: Optional[str] = None) -> bool:
        """
        Delete an entity from GCS.
        
        Args:
            entity_id: Unique identifier for the entity
            subfolder: Optional subfolder where entity is stored
            
        Returns:
            True if deleted, False if not found
        """
        blob_path = self._get_blob_path(entity_id, subfolder)
        blob = self.bucket.blob(blob_path)
        
        try:
            blob.delete()
            logger.info(f"Deleted {self.entity_type} {entity_id}")
            return True
        except NotFound:
            logger.warning(f"{self.entity_type} {entity_id} not found for deletion")
            return False
    
    async def list(
        self,
        prefix: Optional[str] = None,
        filter_fn: Optional[Callable[[T], bool]] = None,
        limit: Optional[int] = None
    ) -> List[T]:
        """
        List entities from GCS with optional filtering.
        
        Args:
            prefix: Optional prefix to filter blobs (e.g., subfolder)
            filter_fn: Optional function to filter entities after loading
            limit: Maximum number of entities to return
            
        Returns:
            List of entities matching the criteria
        """
        folder_prefix = f"{self.entity_type}/"
        if prefix:
            folder_prefix = f"{self.entity_type}/{prefix}/"
        
        blobs = self.bucket.list_blobs(prefix=folder_prefix)
        entities = []
        
        for blob in blobs:
            # Skip non-JSON files
            if not blob.name.endswith('.json'):
                continue
            
            try:
                content = blob.download_as_text()
                entity_dict = json.loads(content)
                entity = self.schema_class(**entity_dict)
                
                # Apply filter if provided
                if filter_fn is None or filter_fn(entity):
                    entities.append(entity)
                    
                    # Check limit
                    if limit and len(entities) >= limit:
                        break
                        
            except Exception as e:
                logger.error(f"Error loading entity from {blob.name}: {e}")
                continue
        
        logger.info(f"Listed {len(entities)} {self.entity_type}")
        return entities
    
    async def exists(self, entity_id: str, subfolder: Optional[str] = None) -> bool:
        """
        Check if an entity exists in GCS.
        
        Args:
            entity_id: Unique identifier for the entity
            subfolder: Optional subfolder where entity might be stored
            
        Returns:
            True if entity exists, False otherwise
        """
        blob_path = self._get_blob_path(entity_id, subfolder)
        blob = self.bucket.blob(blob_path)
        return blob.exists()
