"""
Vertex AI model deployment management.

This module provides comprehensive deployment utilities for Vertex AI models,
including endpoint creation, autoscaling configuration, health checking,
and error handling with fallback strategies.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from google.cloud import aiplatform
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    UNDEPLOYING = "undeploying"
    UNDEPLOYED = "undeployed"


class DeploymentError(Exception):
    """Custom exception for deployment errors."""
    pass


class VertexDeploymentManager:
    """
    Manager for Vertex AI model deployment.
    
    Provides comprehensive deployment utilities including:
    - Model deployment to Vertex AI Endpoints
    - Autoscaling configuration
    - Health checking
    - Error handling with fallback strategies
    - Endpoint management
    """
    
    def __init__(self, project: str, location: str):
        """
        Initialize deployment manager.
        
        Args:
            project: GCP project ID
            location: GCP region
        """
        self.project = project
        self.location = location
        
        logger.info(
            f"Initialized VertexDeploymentManager: "
            f"project={project}, location={location}"
        )
    
    async def deploy_model(
        self,
        model_resource_name: str,
        endpoint_display_name: str,
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 3,
        accelerator_type: Optional[str] = None,
        accelerator_count: int = 0,
        traffic_percentage: int = 100,
        enable_access_logging: bool = True,
        enable_container_logging: bool = True,
        service_account: Optional[str] = None,
        explanation_metadata: Optional[Dict[str, Any]] = None,
        explanation_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deploy a model to a Vertex AI endpoint with comprehensive configuration.
        
        Args:
            model_resource_name: Full resource name of the model
            endpoint_display_name: Display name for the endpoint
            machine_type: Machine type for serving (e.g., 'n1-standard-2', 'n1-standard-4')
            min_replica_count: Minimum number of replicas for autoscaling
            max_replica_count: Maximum number of replicas for autoscaling
            accelerator_type: GPU type for serving (e.g., 'NVIDIA_TESLA_T4')
            accelerator_count: Number of GPUs per replica
            traffic_percentage: Percentage of traffic to route to this deployment
            enable_access_logging: Enable access logging for predictions
            enable_container_logging: Enable container logging
            service_account: Service account for the endpoint
            explanation_metadata: Metadata for model explanations
            explanation_parameters: Parameters for model explanations
            
        Returns:
            Dictionary with comprehensive endpoint information
            
        Raises:
            DeploymentError: If deployment fails
        """
        logger.info(
            f"Starting model deployment: endpoint={endpoint_display_name}, "
            f"model={model_resource_name}, machine_type={machine_type}, "
            f"replicas={min_replica_count}-{max_replica_count}"
        )
        
        try:
            # Get the model
            model = aiplatform.Model(model_resource_name)
            logger.info(f"Retrieved model: {model.display_name}")
            
            # Create or get endpoint
            endpoint = await self._create_or_get_endpoint(
                endpoint_display_name,
                enable_access_logging=enable_access_logging
            )
            logger.info(f"Using endpoint: {endpoint.resource_name}")
            
            # Configure deployment settings
            deployed_model_display_name = f"deployed_{model.display_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Deploy model to endpoint
            logger.info(f"Deploying model to endpoint (this may take several minutes)...")
            
            # Build deploy arguments (only include supported parameters)
            deploy_args = {
                "model": model,
                "deployed_model_display_name": deployed_model_display_name,
                "machine_type": machine_type,
                "min_replica_count": min_replica_count,
                "max_replica_count": max_replica_count,
                "traffic_percentage": traffic_percentage,
                "sync": True  # Wait for deployment to complete
            }
            
            # Add optional parameters only if provided
            if accelerator_type:
                deploy_args["accelerator_type"] = accelerator_type
                deploy_args["accelerator_count"] = accelerator_count
            
            if service_account:
                deploy_args["service_account"] = service_account
            
            if explanation_metadata:
                deploy_args["explanation_metadata"] = explanation_metadata
            
            if explanation_parameters:
                deploy_args["explanation_parameters"] = explanation_parameters
            
            # Note: enable_container_logging is not supported in all SDK versions
            # Logging is enabled by default in Vertex AI
            
            endpoint.deploy(**deploy_args)
            
            # Verify deployment
            await self._verify_deployment(endpoint.resource_name)
            
            # Build deployment info
            deployment_info = {
                "status": DeploymentStatus.DEPLOYED.value,
                "endpoint_id": endpoint.name.split("/")[-1],
                "endpoint_resource_name": endpoint.resource_name,
                "endpoint_url": f"https://{self.location}-aiplatform.googleapis.com/v1/{endpoint.resource_name}:predict",
                "display_name": endpoint_display_name,
                "deployed_model_display_name": deployed_model_display_name,
                "deployed_at": datetime.utcnow().isoformat(),
                "model_resource_name": model_resource_name,
                "machine_type": machine_type,
                "min_replica_count": min_replica_count,
                "max_replica_count": max_replica_count,
                "accelerator_type": accelerator_type,
                "accelerator_count": accelerator_count,
                "traffic_percentage": traffic_percentage,
                "enable_access_logging": enable_access_logging,
                "enable_container_logging": enable_container_logging
            }
            
            logger.info(
                f"Model successfully deployed to endpoint: {deployment_info['endpoint_id']}"
            )
            return deployment_info
            
        except google_exceptions.GoogleAPIError as e:
            error_msg = f"Google API error during deployment: {str(e)}"
            logger.error(error_msg)
            raise DeploymentError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during deployment: {str(e)}"
            logger.error(error_msg)
            raise DeploymentError(error_msg) from e
    
    async def _create_or_get_endpoint(
        self,
        display_name: str,
        enable_access_logging: bool = True
    ) -> aiplatform.Endpoint:
        """
        Create a new endpoint or get existing one by display name.
        
        Args:
            display_name: Display name for the endpoint
            enable_access_logging: Enable access logging
            
        Returns:
            Vertex AI Endpoint instance
        """
        try:
            # Try to find existing endpoint with the same display name
            logger.info(f"Searching for existing endpoint: {display_name}")
            endpoints = aiplatform.Endpoint.list(
                filter=f'display_name="{display_name}"',
                project=self.project,
                location=self.location
            )
            
            if endpoints:
                logger.info(f"Found existing endpoint: {display_name}")
                endpoint = endpoints[0]
                logger.info(f"Endpoint resource name: {endpoint.resource_name}")
                return endpoint
            
            # Create new endpoint
            logger.info(f"No existing endpoint found. Creating new endpoint: {display_name}")
            
            try:
                endpoint = aiplatform.Endpoint.create(
                    display_name=display_name,
                    project=self.project,
                    location=self.location,
                    sync=True  # Wait for creation to complete
                    # Note: Removed enable_request_response_logging to avoid BigQuery requirement
                    # Can be enabled later with proper BigQuery dataset configuration
                )
                logger.info(f"Successfully created endpoint: {endpoint.resource_name}")
                return endpoint
                
            except google_exceptions.Aborted as e:
                # If we get ABORTED, it might mean the endpoint is being created
                # Try to find it again
                logger.warning(f"Got ABORTED error during creation, retrying search: {e}")
                await asyncio.sleep(2)  # Wait a bit
                
                endpoints = aiplatform.Endpoint.list(
                    filter=f'display_name="{display_name}"',
                    project=self.project,
                    location=self.location
                )
                
                if endpoints:
                    logger.info(f"Found endpoint after retry: {display_name}")
                    return endpoints[0]
                else:
                    # Still not found, re-raise the original error
                    raise
            
        except google_exceptions.Aborted as e:
            error_msg = (
                f"Endpoint operation aborted: {e}\n"
                f"This usually means:\n"
                f"1. An endpoint with name '{display_name}' already exists but couldn't be found\n"
                f"2. A concurrent operation is in progress\n"
                f"3. There's a quota or resource conflict\n\n"
                f"Solutions:\n"
                f"- Run: python backend/fix_endpoint_conflict.py to list and clean up endpoints\n"
                f"- Wait a few minutes and try again\n"
                f"- Use a different endpoint name"
            )
            logger.error(error_msg)
            raise DeploymentError(error_msg) from e
        except Exception as e:
            logger.error(f"Failed to create or get endpoint: {e}")
            raise
    
    async def _verify_deployment(
        self,
        endpoint_resource_name: str,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> bool:
        """
        Verify that the deployment is healthy and ready to serve.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            max_retries: Maximum number of verification attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if deployment is healthy
            
        Raises:
            DeploymentError: If verification fails
        """
        logger.info(f"Verifying deployment health: {endpoint_resource_name}")
        
        for attempt in range(max_retries):
            try:
                endpoint = aiplatform.Endpoint(endpoint_resource_name)
                
                # Check if endpoint has deployed models
                if not endpoint.list_models():
                    raise DeploymentError("No models deployed to endpoint")
                
                # Check endpoint state
                deployed_models = endpoint.list_models()
                for deployed_model in deployed_models:
                    logger.info(
                        f"Deployed model: {deployed_model.display_name}, "
                        f"ID: {deployed_model.id}"
                    )
                
                logger.info("Deployment verification successful")
                return True
                
            except Exception as e:
                logger.warning(
                    f"Verification attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise DeploymentError(
                        f"Deployment verification failed after {max_retries} attempts"
                    ) from e
        
        return False
    
    async def check_endpoint_health(
        self,
        endpoint_resource_name: str
    ) -> Dict[str, Any]:
        """
        Check the health status of a deployed endpoint.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            
        Returns:
            Dictionary with health status information
        """
        logger.info(f"Checking endpoint health: {endpoint_resource_name}")
        
        try:
            endpoint = aiplatform.Endpoint(endpoint_resource_name)
            
            deployed_models = endpoint.list_models()
            
            health_info = {
                "endpoint_resource_name": endpoint_resource_name,
                "endpoint_display_name": endpoint.display_name,
                "is_healthy": len(deployed_models) > 0,
                "deployed_models_count": len(deployed_models),
                "deployed_models": [
                    {
                        "id": model.id,
                        "display_name": model.display_name,
                        "create_time": model.create_time.isoformat() if hasattr(model, 'create_time') else None
                    }
                    for model in deployed_models
                ],
                "checked_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Endpoint health check complete: "
                f"healthy={health_info['is_healthy']}, "
                f"models={health_info['deployed_models_count']}"
            )
            
            return health_info
            
        except google_exceptions.NotFound:
            logger.error(f"Endpoint not found: {endpoint_resource_name}")
            return {
                "endpoint_resource_name": endpoint_resource_name,
                "is_healthy": False,
                "error": "Endpoint not found",
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "endpoint_resource_name": endpoint_resource_name,
                "is_healthy": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def undeploy_model(
        self,
        endpoint_resource_name: str,
        deployed_model_id: str
    ) -> bool:
        """
        Undeploy a model from an endpoint.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            deployed_model_id: ID of the deployed model to undeploy
            
        Returns:
            True if undeployment was successful
        """
        logger.info(
            f"Undeploying model: endpoint={endpoint_resource_name}, "
            f"model_id={deployed_model_id}"
        )
        
        try:
            endpoint = aiplatform.Endpoint(endpoint_resource_name)
            endpoint.undeploy(deployed_model_id=deployed_model_id, sync=True)
            
            logger.info(f"Model undeployed successfully: {deployed_model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to undeploy model: {e}")
            raise DeploymentError(f"Undeployment failed: {str(e)}") from e
    
    async def delete_endpoint(
        self,
        endpoint_resource_name: str,
        force: bool = False
    ) -> bool:
        """
        Delete an endpoint.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            force: Force deletion even if models are deployed
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting endpoint: {endpoint_resource_name}, force={force}")
        
        try:
            endpoint = aiplatform.Endpoint(endpoint_resource_name)
            endpoint.delete(force=force, sync=True)
            
            logger.info(f"Endpoint deleted successfully: {endpoint_resource_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete endpoint: {e}")
            raise DeploymentError(f"Endpoint deletion failed: {str(e)}") from e
    
    async def predict(
        self,
        endpoint_resource_name: str,
        instances: List[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make predictions using a deployed model.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            instances: List of instances to predict
            parameters: Optional prediction parameters
            
        Returns:
            Dictionary with predictions and metadata
            
        Raises:
            DeploymentError: If prediction fails
        """
        logger.info(
            f"Making predictions: endpoint={endpoint_resource_name}, "
            f"instances={len(instances)}"
        )
        
        try:
            endpoint = aiplatform.Endpoint(endpoint_resource_name)
            
            predictions = endpoint.predict(
                instances=instances,
                parameters=parameters
            )
            
            result = {
                "predictions": predictions.predictions,
                "deployed_model_id": (
                    predictions.deployed_model_id 
                    if hasattr(predictions, 'deployed_model_id') 
                    else None
                ),
                "model_version_id": (
                    predictions.model_version_id 
                    if hasattr(predictions, 'model_version_id') 
                    else None
                ),
                "model_resource_name": (
                    predictions.model_resource_name 
                    if hasattr(predictions, 'model_resource_name') 
                    else None
                ),
                "predicted_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Predictions completed: {len(instances)} instances")
            return result
            
        except google_exceptions.GoogleAPIError as e:
            error_msg = f"Prediction API error: {str(e)}"
            logger.error(error_msg)
            raise DeploymentError(error_msg) from e
        except Exception as e:
            error_msg = f"Prediction failed: {str(e)}"
            logger.error(error_msg)
            raise DeploymentError(error_msg) from e
    
    async def update_traffic_split(
        self,
        endpoint_resource_name: str,
        traffic_split: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Update traffic split between deployed models.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            traffic_split: Dictionary mapping deployed_model_id to traffic percentage
            
        Returns:
            Updated traffic split information
        """
        logger.info(
            f"Updating traffic split: endpoint={endpoint_resource_name}, "
            f"split={traffic_split}"
        )
        
        try:
            endpoint = aiplatform.Endpoint(endpoint_resource_name)
            
            # Validate traffic split sums to 100
            total_traffic = sum(traffic_split.values())
            if total_traffic != 100:
                raise ValueError(
                    f"Traffic split must sum to 100, got {total_traffic}"
                )
            
            # Update traffic split
            endpoint.update(traffic_split=traffic_split)
            
            result = {
                "endpoint_resource_name": endpoint_resource_name,
                "traffic_split": traffic_split,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Traffic split updated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update traffic split: {e}")
            raise DeploymentError(f"Traffic split update failed: {str(e)}") from e
