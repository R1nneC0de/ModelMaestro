"""
Model artifact handling utilities.

This module provides utilities for preparing, packaging, and managing
model artifacts for download, including batch signed URL generation,
artifact validation, and metadata extraction.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from app.services.cloud.storage import (
    generate_signed_url,
    list_blobs,
    blob_exists,
    download_file_from_gcs
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class ArtifactType:
    """Model artifact type constants."""
    MODEL_FILE = "model_file"
    PREPROCESSING = "preprocessing"
    METADATA = "metadata"
    REPORT = "report"
    TRAINING_LOGS = "training_logs"
    EVALUATION_RESULTS = "evaluation_results"


class ModelArtifactHandler:
    """
    Handler for model artifact preparation and management.
    
    Provides utilities for:
    - Batch signed URL generation
    - Artifact validation and verification
    - Metadata extraction
    - Artifact packaging information
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize artifact handler.
        
        Args:
            bucket_name: GCS bucket name (defaults to settings)
        """
        self.bucket_name = bucket_name or settings.GCS_BUCKET_NAME
        logger.info(f"Initialized ModelArtifactHandler: bucket={self.bucket_name}")
    
    async def prepare_model_download(
        self,
        model_id: str,
        artifact_base_path: str,
        expiration_hours: int = 24,
        include_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive model download package with signed URLs.
        
        Args:
            model_id: Unique model identifier
            artifact_base_path: Base GCS path for model artifacts
            expiration_hours: URL expiration time in hours
            include_types: List of artifact types to include (None = all)
            
        Returns:
            Dictionary with organized artifact download information
        """
        logger.info(
            f"Preparing model download: model_id={model_id}, "
            f"path={artifact_base_path}"
        )
        
        try:
            # Parse GCS path
            if not artifact_base_path.startswith("gs://"):
                artifact_base_path = f"gs://{self.bucket_name}/{artifact_base_path}"
            
            path_parts = artifact_base_path.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
            
            # List all artifacts
            all_blobs = await list_blobs(
                prefix=blob_prefix,
                bucket_name=bucket_name
            )
            
            if not all_blobs:
                logger.warning(f"No artifacts found at {artifact_base_path}")
                return {
                    "model_id": model_id,
                    "available": False,
                    "artifacts": {},
                    "total_files": 0
                }
            
            # Categorize artifacts by type
            categorized_artifacts = await self._categorize_artifacts(
                all_blobs,
                include_types=include_types
            )
            
            # Generate signed URLs for each artifact
            artifacts_with_urls = {}
            total_files = 0
            
            for artifact_type, blob_list in categorized_artifacts.items():
                artifacts_with_urls[artifact_type] = []
                
                for blob_name in blob_list:
                    try:
                        signed_url = await generate_signed_url(
                            blob_name=blob_name,
                            bucket_name=bucket_name,
                            expiration_minutes=expiration_hours * 60
                        )
                        
                        artifacts_with_urls[artifact_type].append({
                            "filename": blob_name.split("/")[-1],
                            "blob_path": blob_name,
                            "gcs_uri": f"gs://{bucket_name}/{blob_name}",
                            "download_url": signed_url,
                            "artifact_type": artifact_type,
                            "expires_at": (
                                datetime.utcnow() + timedelta(hours=expiration_hours)
                            ).isoformat()
                        })
                        
                        total_files += 1
                        
                    except Exception as e:
                        logger.error(
                            f"Failed to generate signed URL for {blob_name}: {e}"
                        )
            
            download_package = {
                "model_id": model_id,
                "available": total_files > 0,
                "artifact_base_path": artifact_base_path,
                "artifacts": artifacts_with_urls,
                "total_files": total_files,
                "expiration_hours": expiration_hours,
                "prepared_at": datetime.utcnow().isoformat(),
                "expires_at": (
                    datetime.utcnow() + timedelta(hours=expiration_hours)
                ).isoformat()
            }
            
            logger.info(
                f"Model download package prepared: {total_files} files across "
                f"{len(artifacts_with_urls)} categories"
            )
            
            return download_package
            
        except Exception as e:
            logger.error(f"Failed to prepare model download: {e}")
            return {
                "model_id": model_id,
                "available": False,
                "error": str(e),
                "artifacts": {},
                "total_files": 0
            }
    
    async def _categorize_artifacts(
        self,
        blob_names: List[str],
        include_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Categorize artifact blobs by type.
        
        Args:
            blob_names: List of blob names
            include_types: List of types to include (None = all)
            
        Returns:
            Dictionary mapping artifact type to list of blob names
        """
        categorized = {
            ArtifactType.MODEL_FILE: [],
            ArtifactType.PREPROCESSING: [],
            ArtifactType.METADATA: [],
            ArtifactType.REPORT: [],
            ArtifactType.TRAINING_LOGS: [],
            ArtifactType.EVALUATION_RESULTS: []
        }
        
        for blob_name in blob_names:
            filename = blob_name.split("/")[-1].lower()
            
            # Categorize based on filename patterns
            if any(ext in filename for ext in ['.pkl', '.h5', '.pb', '.onnx', '.pt', '.pth', '.joblib']):
                artifact_type = ArtifactType.MODEL_FILE
            elif any(keyword in filename for keyword in ['preprocess', 'scaler', 'encoder', 'imputer']):
                artifact_type = ArtifactType.PREPROCESSING
            elif any(keyword in filename for keyword in ['metadata', 'config', 'schema']):
                artifact_type = ArtifactType.METADATA
            elif any(keyword in filename for keyword in ['report', 'summary']):
                artifact_type = ArtifactType.REPORT
            elif any(keyword in filename for keyword in ['log', 'training']):
                artifact_type = ArtifactType.TRAINING_LOGS
            elif any(keyword in filename for keyword in ['evaluation', 'metrics', 'results']):
                artifact_type = ArtifactType.EVALUATION_RESULTS
            else:
                # Default to model file
                artifact_type = ArtifactType.MODEL_FILE
            
            # Add to category if included
            if include_types is None or artifact_type in include_types:
                categorized[artifact_type].append(blob_name)
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        return categorized
    
    async def validate_artifacts(
        self,
        artifact_base_path: str,
        required_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate that required model artifacts exist.
        
        Args:
            artifact_base_path: Base GCS path for model artifacts
            required_files: List of required filenames (None = check any exist)
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating artifacts at {artifact_base_path}")
        
        try:
            # Parse GCS path
            if not artifact_base_path.startswith("gs://"):
                artifact_base_path = f"gs://{self.bucket_name}/{artifact_base_path}"
            
            path_parts = artifact_base_path.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
            
            # List all artifacts
            all_blobs = await list_blobs(
                prefix=blob_prefix,
                bucket_name=bucket_name
            )
            
            validation_result = {
                "valid": False,
                "artifact_base_path": artifact_base_path,
                "total_files": len(all_blobs),
                "required_files": required_files or [],
                "missing_files": [],
                "found_files": [blob.split("/")[-1] for blob in all_blobs],
                "validated_at": datetime.utcnow().isoformat()
            }
            
            # Check if any artifacts exist
            if not all_blobs:
                validation_result["error"] = "No artifacts found"
                logger.warning(f"No artifacts found at {artifact_base_path}")
                return validation_result
            
            # If no required files specified, just check that some exist
            if not required_files:
                validation_result["valid"] = True
                logger.info(f"Artifacts validated: {len(all_blobs)} files found")
                return validation_result
            
            # Check for required files
            found_filenames = {blob.split("/")[-1] for blob in all_blobs}
            missing_files = [
                req_file for req_file in required_files 
                if req_file not in found_filenames
            ]
            
            validation_result["missing_files"] = missing_files
            validation_result["valid"] = len(missing_files) == 0
            
            if validation_result["valid"]:
                logger.info("All required artifacts found")
            else:
                logger.warning(f"Missing required artifacts: {missing_files}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Artifact validation failed: {e}")
            return {
                "valid": False,
                "error": str(e),
                "artifact_base_path": artifact_base_path
            }
    
    async def get_artifact_metadata(
        self,
        artifact_base_path: str
    ) -> Dict[str, Any]:
        """
        Extract metadata from model artifacts.
        
        Args:
            artifact_base_path: Base GCS path for model artifacts
            
        Returns:
            Dictionary with artifact metadata
        """
        logger.info(f"Extracting artifact metadata from {artifact_base_path}")
        
        try:
            # Parse GCS path
            if not artifact_base_path.startswith("gs://"):
                artifact_base_path = f"gs://{self.bucket_name}/{artifact_base_path}"
            
            path_parts = artifact_base_path.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
            
            # Look for metadata files
            metadata_blobs = []
            all_blobs = await list_blobs(
                prefix=blob_prefix,
                bucket_name=bucket_name
            )
            
            for blob_name in all_blobs:
                filename = blob_name.split("/")[-1].lower()
                if any(keyword in filename for keyword in ['metadata', 'config', 'info']):
                    if filename.endswith('.json'):
                        metadata_blobs.append(blob_name)
            
            metadata = {
                "artifact_base_path": artifact_base_path,
                "has_metadata": len(metadata_blobs) > 0,
                "metadata_files": metadata_blobs,
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            # Try to read first metadata file if exists
            if metadata_blobs:
                try:
                    # For now, just return the list of metadata files
                    # In production, you might want to download and parse them
                    metadata["metadata_available"] = True
                except Exception as e:
                    logger.warning(f"Could not read metadata file: {e}")
                    metadata["metadata_available"] = False
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract artifact metadata: {e}")
            return {
                "artifact_base_path": artifact_base_path,
                "has_metadata": False,
                "error": str(e)
            }
    
    async def generate_download_instructions(
        self,
        model_id: str,
        download_package: Dict[str, Any],
        include_code_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Generate download instructions and code examples.
        
        Args:
            model_id: Unique model identifier
            download_package: Download package from prepare_model_download
            include_code_examples: Include code examples for downloading
            
        Returns:
            Dictionary with download instructions
        """
        logger.info(f"Generating download instructions for model: {model_id}")
        
        instructions = {
            "model_id": model_id,
            "summary": f"Model artifacts ready for download ({download_package.get('total_files', 0)} files)",
            "expiration": download_package.get("expires_at"),
            "artifact_categories": list(download_package.get("artifacts", {}).keys()),
            "instructions": []
        }
        
        # Add basic instructions
        instructions["instructions"].append({
            "step": 1,
            "description": "Download artifacts using the provided signed URLs",
            "note": "URLs expire after the specified time period"
        })
        
        instructions["instructions"].append({
            "step": 2,
            "description": "Organize downloaded files in a local directory",
            "note": "Maintain the artifact type structure for easier management"
        })
        
        # Add code examples if requested
        if include_code_examples:
            instructions["code_examples"] = {
                "python": self._generate_python_download_example(download_package),
                "curl": self._generate_curl_download_example(download_package),
                "javascript": self._generate_javascript_download_example(download_package)
            }
        
        return instructions
    
    def _generate_python_download_example(
        self,
        download_package: Dict[str, Any]
    ) -> str:
        """Generate Python code example for downloading artifacts."""
        return """
import requests
import os
from pathlib import Path

# Create download directory
download_dir = Path("model_artifacts")
download_dir.mkdir(exist_ok=True)

# Download all artifacts
artifacts = {artifacts_json}

for artifact_type, files in artifacts.items():
    type_dir = download_dir / artifact_type
    type_dir.mkdir(exist_ok=True)
    
    for file_info in files:
        filename = file_info['filename']
        url = file_info['download_url']
        
        print(f"Downloading {{filename}}...")
        response = requests.get(url)
        response.raise_for_status()
        
        filepath = type_dir / filename
        filepath.write_bytes(response.content)
        print(f"Saved to {{filepath}}")

print("All artifacts downloaded successfully!")
""".replace("{artifacts_json}", json.dumps(download_package.get("artifacts", {}), indent=2))
    
    def _generate_curl_download_example(
        self,
        download_package: Dict[str, Any]
    ) -> str:
        """Generate curl command example for downloading artifacts."""
        artifacts = download_package.get("artifacts", {})
        
        if not artifacts:
            return "# No artifacts available"
        
        # Get first artifact as example
        first_type = list(artifacts.keys())[0]
        first_file = artifacts[first_type][0] if artifacts[first_type] else None
        
        if not first_file:
            return "# No artifacts available"
        
        return f"""
# Download single artifact
curl -o "{first_file['filename']}" "{first_file['download_url']}"

# Download all artifacts (create script)
# Save URLs to a file and use wget or curl in a loop
"""
    
    def _generate_javascript_download_example(
        self,
        download_package: Dict[str, Any]
    ) -> str:
        """Generate JavaScript code example for downloading artifacts."""
        return """
// Download artifacts using fetch API
const artifacts = {artifacts_json};

async function downloadArtifacts() {
  for (const [artifactType, files] of Object.entries(artifacts)) {
    for (const fileInfo of files) {
      console.log(`Downloading ${fileInfo.filename}...`);
      
      const response = await fetch(fileInfo.download_url);
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileInfo.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      console.log(`Downloaded ${fileInfo.filename}`);
    }
  }
  
  console.log('All artifacts downloaded!');
}

downloadArtifacts();
""".replace("{artifacts_json}", json.dumps(download_package.get("artifacts", {}), indent=2))
