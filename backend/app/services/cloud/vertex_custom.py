"""
Vertex AI Custom training job management.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from google.cloud import aiplatform

logger = logging.getLogger(__name__)


class VertexCustomTrainingManager:
    """Manager for Vertex AI Custom training jobs."""
    
    def __init__(self, project: str, location: str):
        """
        Initialize custom training manager.
        
        Args:
            project: GCP project ID
            location: GCP region
        """
        self.project = project
        self.location = location
    
    async def create_custom_training_job(
        self,
        dataset_id: str,
        display_name: str,
        script_path: str,
        container_uri: str,
        training_data_uri: str,
        validation_data_uri: str,
        test_data_uri: str,
        model_output_uri: str,
        hyperparameters: Dict[str, Any],
        machine_type: str = "n1-standard-4",
        accelerator_type: Optional[str] = None,
        accelerator_count: int = 0,
        replica_count: int = 1,
        args: Optional[List[str]] = None,
        environment_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a custom training job.
        
        Args:
            dataset_id: Unique identifier for the dataset
            display_name: Display name for the training job
            script_path: Path to training script in container
            container_uri: Docker container URI for training
            training_data_uri: GCS URI to training data
            validation_data_uri: GCS URI to validation data
            test_data_uri: GCS URI to test data
            model_output_uri: GCS URI for model output
            hyperparameters: Dictionary of hyperparameters
            machine_type: Machine type for training
            accelerator_type: GPU type
            accelerator_count: Number of GPUs
            replica_count: Number of replicas
            args: Additional command-line arguments
            environment_variables: Environment variables for the job
            
        Returns:
            Dictionary with job information
        """
        logger.info(
            f"Creating custom training job: {display_name}, "
            f"machine_type={machine_type}, accelerator={accelerator_type}"
        )
        
        try:
            # Prepare environment variables
            env_vars = environment_variables or {}
            env_vars.update({
                "TRAINING_DATA_URI": training_data_uri,
                "VALIDATION_DATA_URI": validation_data_uri,
                "TEST_DATA_URI": test_data_uri,
                "MODEL_OUTPUT_URI": model_output_uri,
                "HYPERPARAMETERS": str(hyperparameters)
            })
            
            # Create custom training job
            job = aiplatform.CustomTrainingJob(
                display_name=display_name,
                script_path=script_path,
                container_uri=container_uri,
                requirements=None,
                model_serving_container_image_uri=None
            )
            
            # Prepare run parameters
            run_params = {
                "dataset": None,
                "replica_count": replica_count,
                "machine_type": machine_type,
                "args": args,
                "environment_variables": env_vars,
                "sync": False
            }
            
            # Only add accelerator params if accelerator_type is specified
            if accelerator_type:
                run_params["accelerator_type"] = accelerator_type
                run_params["accelerator_count"] = accelerator_count
            
            # Start training
            model = job.run(**run_params)
            
            job_info = {
                "job_id": job.name.split("/")[-1],
                "resource_name": job.resource_name,
                "display_name": display_name,
                "state": job.state.name if hasattr(job.state, 'name') else str(job.state),
                "created_at": datetime.utcnow().isoformat(),
                "dataset_id": dataset_id,
                "machine_type": machine_type,
                "accelerator_type": accelerator_type,
                "accelerator_count": accelerator_count,
                "hyperparameters": hyperparameters,
                "training_type": "custom"
            }
            
            logger.info(f"Custom training job created: {job_info['job_id']}")
            return job_info
            
        except Exception as e:
            logger.error(f"Failed to create custom training job: {e}")
            raise
