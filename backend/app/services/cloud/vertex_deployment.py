"""
Vertex AI model deployment management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from google.cloud import aiplatform

logger = logging.getLogger(__name__)


class VertexDeploymentManager:
    """Manager for Vertex AI model deployment."""
    
    def __init__(self, project: str, location: str):
        """
        Initialize deployment manager.
        
        Args:
            project: GCP project ID
            location: GCP region
        """
        self.project = project
        self.location = location
    
    async def deploy_model(
        self,
        model_resource_name: str,
        endpoint_display_name: str,
        machine_type: str = "n1-standard-2",
        min_replica_count: int = 1,
        max_replica_count: int = 3,
        accelerator_type: Optional[str] = None,
        accelerator_count: int = 0
    ) -> Dict[str, Any]:
        """
        Deploy a model to a Vertex AI endpoint.
        
        Args:
            model_resource_name: Full resource name of the model
            endpoint_display_name: Display name for the endpoint
            machine_type: Machine type for serving
            min_replica_count: Minimum number of replicas
            max_replica_count: Maximum number of replicas
            accelerator_type: GPU type for serving
            accelerator_count: Number of GPUs
            
        Returns:
            Dictionary with endpoint information
        """
        logger.info(
            f"Deploying model to endpoint: {endpoint_display_name}, "
            f"machine_type={machine_type}"
        )
        
        try:
            model = aiplatform.Model(model_resource_name)
            
            # Create or get endpoint
            endpoint = aiplatform.Endpoint.create(
                display_name=endpoint_display_name,
                project=self.project,
                location=self.location
            )
            
            # Deploy model to endpoint
            endpoint.deploy(
                model=model,
                deployed_model_display_name=f"deployed_{model.display_name}",
                machine_type=machine_type,
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
                accelerator_type=accelerator_type,
                accelerator_count=accelerator_count,
                sync=True
            )
            
            deployment_info = {
                "endpoint_id": endpoint.name.split("/")[-1],
                "endpoint_resource_name": endpoint.resource_name,
                "endpoint_url": f"https://{self.location}-aiplatform.googleapis.com/v1/{endpoint.resource_name}:predict",
                "display_name": endpoint_display_name,
                "deployed_at": datetime.utcnow().isoformat(),
                "machine_type": machine_type,
                "min_replica_count": min_replica_count,
                "max_replica_count": max_replica_count
            }
            
            logger.info(f"Model deployed to endpoint: {deployment_info['endpoint_id']}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Failed to deploy model: {e}")
            raise
    
    async def predict(
        self,
        endpoint_resource_name: str,
        instances: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Make predictions using a deployed model.
        
        Args:
            endpoint_resource_name: Full resource name of the endpoint
            instances: List of instances to predict
            
        Returns:
            Dictionary with predictions
        """
        try:
            endpoint = aiplatform.Endpoint(endpoint_resource_name)
            
            predictions = endpoint.predict(instances=instances)
            
            result = {
                "predictions": predictions.predictions,
                "deployed_model_id": predictions.deployed_model_id if hasattr(predictions, 'deployed_model_id') else None,
                "model_version_id": predictions.model_version_id if hasattr(predictions, 'model_version_id') else None
            }
            
            logger.info(f"Made {len(instances)} predictions")
            return result
            
        except Exception as e:
            logger.error(f"Failed to make predictions: {e}")
            raise
