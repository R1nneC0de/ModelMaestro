"""
Model deployment service with comprehensive utilities.

This module provides high-level deployment utilities that integrate
Vertex AI deployment with GCS storage for model artifacts, signed URLs,
health checking, and error handling with fallback strategies.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.services.cloud.vertex_deployment import (
    VertexDeploymentManager,
    DeploymentError,
    DeploymentStatus
)
from app.services.cloud.storage import (
    generate_signed_url,
    blob_exists,
    list_blobs
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategy enumeration."""
    ENDPOINT_ONLY = "endpoint_only"  # Deploy to Vertex AI Endpoint
    ARTIFACT_ONLY = "artifact_only"  # Provide downloadable artifact only
    BOTH = "both"  # Both endpoint and downloadable artifact


class DeploymentFallbackReason(Enum):
    """Reasons for falling back to artifact-only deployment."""
    QUOTA_EXCEEDED = "quota_exceeded"
    DEPLOYMENT_TIMEOUT = "deployment_timeout"
    ENDPOINT_ERROR = "endpoint_error"
    COST_OPTIMIZATION = "cost_optimization"
    USER_PREFERENCE = "user_preference"


class ModelDeploymentService:
    """
    High-level model deployment service.
    
    Provides comprehensive deployment utilities including:
    - Vertex AI Endpoint deployment with autoscaling
    - Model artifact preparation and signed URL generation
    - Health checking and monitoring
    - Error handling with fallback to artifact-only deployment
    - Deployment strategy selection
    """
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None
    ):
        """
        Initialize deployment service.
        
        Args:
            project: GCP project ID (defaults to settings)
            location: GCP region (defaults to settings)
        """
        self.project = project or settings.GOOGLE_CLOUD_PROJECT
        self.location = location or settings.VERTEX_AI_LOCATION
        self.vertex_deployment = VertexDeploymentManager(self.project, self.location)
        
        logger.info(
            f"Initialized ModelDeploymentService: "
            f"project={self.project}, location={self.location}"
        )
    
    async def deploy_model_with_fallback(
        self,
        model_id: str,
        model_resource_name: str,
        model_artifact_path: str,
        strategy: DeploymentStrategy = DeploymentStrategy.BOTH,
        endpoint_display_name: Optional[str] = None,
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 3,
        enable_autoscaling: bool = True,
        deployment_timeout_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Deploy model with automatic fallback to artifact-only on failure.
        
        This method attempts to deploy to Vertex AI Endpoint first, and falls
        back to providing downloadable artifacts only if deployment fails.
        
        Args:
            model_id: Unique model identifier
            model_resource_name: Vertex AI model resource name
            model_artifact_path: GCS path to model artifacts
            strategy: Deployment strategy (endpoint, artifact, or both)
            endpoint_display_name: Display name for endpoint
            machine_type: Machine type for serving
            min_replica_count: Minimum replicas for autoscaling
            max_replica_count: Maximum replicas for autoscaling
            enable_autoscaling: Enable autoscaling
            deployment_timeout_minutes: Timeout for deployment
            
        Returns:
            Dictionary with deployment information including:
            - deployment_strategy: Actual strategy used
            - endpoint_info: Endpoint information (if deployed)
            - artifact_info: Artifact download information
            - fallback_reason: Reason for fallback (if applicable)
        """
        logger.info(
            f"Deploying model with fallback: model_id={model_id}, "
            f"strategy={strategy.value}"
        )
        
        deployment_result = {
            "model_id": model_id,
            "requested_strategy": strategy.value,
            "deployment_strategy": None,
            "endpoint_info": None,
            "artifact_info": None,
            "fallback_reason": None,
            "deployed_at": datetime.utcnow().isoformat()
        }
        
        # Prepare artifact information (always available)
        artifact_info = await self.prepare_model_artifact(
            model_id=model_id,
            artifact_path=model_artifact_path
        )
        deployment_result["artifact_info"] = artifact_info
        
        # Handle artifact-only strategy
        if strategy == DeploymentStrategy.ARTIFACT_ONLY:
            deployment_result["deployment_strategy"] = DeploymentStrategy.ARTIFACT_ONLY.value
            logger.info("Artifact-only deployment completed")
            return deployment_result
        
        # Attempt endpoint deployment
        if strategy in [DeploymentStrategy.ENDPOINT_ONLY, DeploymentStrategy.BOTH]:
            try:
                endpoint_name = endpoint_display_name or f"endpoint_{model_id}"
                
                endpoint_info = await self.vertex_deployment.deploy_model(
                    model_resource_name=model_resource_name,
                    endpoint_display_name=endpoint_name,
                    machine_type=machine_type,
                    min_replica_count=min_replica_count if enable_autoscaling else 1,
                    max_replica_count=max_replica_count if enable_autoscaling else 1
                )
                
                deployment_result["endpoint_info"] = endpoint_info
                deployment_result["deployment_strategy"] = strategy.value
                
                logger.info(
                    f"Endpoint deployment successful: "
                    f"endpoint_id={endpoint_info['endpoint_id']}"
                )
                
                return deployment_result
                
            except DeploymentError as e:
                logger.warning(f"Endpoint deployment failed: {e}")
                
                # Determine fallback reason
                error_str = str(e).lower()
                if "quota" in error_str:
                    fallback_reason = DeploymentFallbackReason.QUOTA_EXCEEDED
                elif "timeout" in error_str:
                    fallback_reason = DeploymentFallbackReason.DEPLOYMENT_TIMEOUT
                else:
                    fallback_reason = DeploymentFallbackReason.ENDPOINT_ERROR
                
                deployment_result["fallback_reason"] = fallback_reason.value
                
                # Fallback to artifact-only if strategy allows
                if strategy == DeploymentStrategy.BOTH:
                    deployment_result["deployment_strategy"] = DeploymentStrategy.ARTIFACT_ONLY.value
                    logger.info(
                        f"Falling back to artifact-only deployment: "
                        f"reason={fallback_reason.value}"
                    )
                    return deployment_result
                else:
                    # ENDPOINT_ONLY strategy failed
                    raise DeploymentError(
                        f"Endpoint deployment failed and no fallback available: {e}"
                    ) from e
        
        return deployment_result
    
    async def prepare_model_artifact(
        self,
        model_id: str,
        artifact_path: str,
        expiration_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Prepare model artifact for download with signed URLs.
        
        Args:
            model_id: Unique model identifier
            artifact_path: GCS path to model artifacts
            expiration_hours: URL expiration time in hours
            
        Returns:
            Dictionary with artifact information and download URLs
        """
        logger.info(
            f"Preparing model artifact: model_id={model_id}, "
            f"path={artifact_path}"
        )
        
        try:
            # Parse GCS path
            if not artifact_path.startswith("gs://"):
                raise ValueError(f"Invalid GCS path: {artifact_path}")
            
            path_parts = artifact_path.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
            
            # List all artifact files
            artifact_blobs = await list_blobs(
                prefix=blob_prefix,
                bucket_name=bucket_name
            )
            
            if not artifact_blobs:
                logger.warning(f"No artifacts found at {artifact_path}")
                return {
                    "model_id": model_id,
                    "artifact_path": artifact_path,
                    "available": False,
                    "files": []
                }
            
            # Generate signed URLs for each artifact file
            artifact_files = []
            for blob_name in artifact_blobs:
                try:
                    signed_url = await generate_signed_url(
                        blob_name=blob_name,
                        bucket_name=bucket_name,
                        expiration_minutes=expiration_hours * 60
                    )
                    
                    artifact_files.append({
                        "filename": blob_name.split("/")[-1],
                        "blob_path": blob_name,
                        "download_url": signed_url,
                        "expires_at": (
                            datetime.utcnow() + timedelta(hours=expiration_hours)
                        ).isoformat()
                    })
                except Exception as e:
                    logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            
            artifact_info = {
                "model_id": model_id,
                "artifact_path": artifact_path,
                "available": len(artifact_files) > 0,
                "files": artifact_files,
                "file_count": len(artifact_files),
                "prepared_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Model artifact prepared: {len(artifact_files)} files available"
            )
            
            return artifact_info
            
        except Exception as e:
            logger.error(f"Failed to prepare model artifact: {e}")
            return {
                "model_id": model_id,
                "artifact_path": artifact_path,
                "available": False,
                "error": str(e),
                "files": []
            }
    
    async def check_deployment_health(
        self,
        endpoint_resource_name: Optional[str] = None,
        artifact_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check health of deployed model (endpoint and/or artifacts).
        
        Args:
            endpoint_resource_name: Vertex AI endpoint resource name
            artifact_path: GCS path to model artifacts
            
        Returns:
            Dictionary with health status information
        """
        logger.info("Checking deployment health")
        
        health_status = {
            "checked_at": datetime.utcnow().isoformat(),
            "endpoint_health": None,
            "artifact_health": None,
            "overall_healthy": False
        }
        
        # Check endpoint health
        if endpoint_resource_name:
            try:
                endpoint_health = await self.vertex_deployment.check_endpoint_health(
                    endpoint_resource_name
                )
                health_status["endpoint_health"] = endpoint_health
            except Exception as e:
                logger.error(f"Endpoint health check failed: {e}")
                health_status["endpoint_health"] = {
                    "is_healthy": False,
                    "error": str(e)
                }
        
        # Check artifact availability
        if artifact_path:
            try:
                artifact_health = await self._check_artifact_health(artifact_path)
                health_status["artifact_health"] = artifact_health
            except Exception as e:
                logger.error(f"Artifact health check failed: {e}")
                health_status["artifact_health"] = {
                    "available": False,
                    "error": str(e)
                }
        
        # Determine overall health
        endpoint_healthy = (
            health_status["endpoint_health"] 
            and health_status["endpoint_health"].get("is_healthy", False)
        )
        artifact_available = (
            health_status["artifact_health"] 
            and health_status["artifact_health"].get("available", False)
        )
        
        health_status["overall_healthy"] = endpoint_healthy or artifact_available
        
        logger.info(
            f"Health check complete: overall_healthy={health_status['overall_healthy']}"
        )
        
        return health_status
    
    async def _check_artifact_health(
        self,
        artifact_path: str
    ) -> Dict[str, Any]:
        """
        Check if model artifacts are available in GCS.
        
        Args:
            artifact_path: GCS path to model artifacts
            
        Returns:
            Dictionary with artifact availability information
        """
        try:
            # Parse GCS path
            if not artifact_path.startswith("gs://"):
                return {"available": False, "error": "Invalid GCS path"}
            
            path_parts = artifact_path.replace("gs://", "").split("/", 1)
            bucket_name = path_parts[0]
            blob_prefix = path_parts[1] if len(path_parts) > 1 else ""
            
            # Check if artifacts exist
            artifact_blobs = await list_blobs(
                prefix=blob_prefix,
                bucket_name=bucket_name
            )
            
            return {
                "available": len(artifact_blobs) > 0,
                "artifact_path": artifact_path,
                "file_count": len(artifact_blobs),
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Artifact health check failed: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    async def get_deployment_info(
        self,
        model_id: str,
        endpoint_resource_name: Optional[str] = None,
        artifact_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive deployment information for a model.
        
        Args:
            model_id: Unique model identifier
            endpoint_resource_name: Vertex AI endpoint resource name
            artifact_path: GCS path to model artifacts
            
        Returns:
            Dictionary with complete deployment information
        """
        logger.info(f"Getting deployment info for model: {model_id}")
        
        deployment_info = {
            "model_id": model_id,
            "endpoint_info": None,
            "artifact_info": None,
            "health_status": None,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        # Get endpoint information
        if endpoint_resource_name:
            try:
                endpoint_health = await self.vertex_deployment.check_endpoint_health(
                    endpoint_resource_name
                )
                deployment_info["endpoint_info"] = endpoint_health
            except Exception as e:
                logger.error(f"Failed to get endpoint info: {e}")
                deployment_info["endpoint_info"] = {"error": str(e)}
        
        # Get artifact information
        if artifact_path:
            try:
                artifact_info = await self.prepare_model_artifact(
                    model_id=model_id,
                    artifact_path=artifact_path,
                    expiration_hours=1  # Short expiration for info retrieval
                )
                deployment_info["artifact_info"] = artifact_info
            except Exception as e:
                logger.error(f"Failed to get artifact info: {e}")
                deployment_info["artifact_info"] = {"error": str(e)}
        
        # Get health status
        health_status = await self.check_deployment_health(
            endpoint_resource_name=endpoint_resource_name,
            artifact_path=artifact_path
        )
        deployment_info["health_status"] = health_status
        
        return deployment_info
