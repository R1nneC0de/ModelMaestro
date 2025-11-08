"""
Vertex AI client for model training and deployment.

This module provides a unified interface for interacting with Google Cloud
Vertex AI services, including AutoML and Custom Training jobs.
"""

import logging
from typing import Dict, Any, Optional, List

from google.cloud import aiplatform

from app.core.config import settings
from app.services.cloud.vertex_automl import VertexAutoMLManager
from app.services.cloud.vertex_custom import VertexCustomTrainingManager
from app.services.cloud.vertex_jobs import VertexJobManager, JobState
from app.services.cloud.vertex_deployment import VertexDeploymentManager

logger = logging.getLogger(__name__)


class VertexAIClient:
    """
    Unified client for interacting with Google Cloud Vertex AI.
    
    Delegates to specialized managers for different operations.
    """
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        staging_bucket: Optional[str] = None
    ):
        """
        Initialize Vertex AI client.
        
        Args:
            project: GCP project ID (defaults to settings)
            location: GCP region (defaults to settings)
            staging_bucket: GCS bucket for staging (defaults to settings)
        """
        self.project = project or settings.GOOGLE_CLOUD_PROJECT
        self.location = location or settings.VERTEX_AI_LOCATION
        self.staging_bucket = staging_bucket or f"gs://{settings.GCS_BUCKET_NAME}"
        
        # Initialize Vertex AI SDK
        aiplatform.init(
            project=self.project,
            location=self.location,
            staging_bucket=self.staging_bucket
        )
        
        # Initialize specialized managers
        self.automl = VertexAutoMLManager(self.project, self.location)
        self.custom = VertexCustomTrainingManager(self.project, self.location)
        self.jobs = VertexJobManager()
        self.deployment = VertexDeploymentManager(self.project, self.location)
        
        logger.info(
            f"Initialized Vertex AI client: "
            f"project={self.project}, location={self.location}"
        )
    
    async def create_automl_tabular_training_job(
        self,
        dataset_id: str,
        target_column: str,
        training_data_uri: str,
        validation_data_uri: str,
        test_data_uri: str,
        display_name: str,
        optimization_objective: str = "minimize-rmse",
        budget_milli_node_hours: int = 1000,
        model_display_name: Optional[str] = None,
        disable_early_stopping: bool = False,
        column_specs: Optional[Dict[str, str]] = None,
        predefined_split_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delegate to AutoML manager."""
        return await self.automl.create_tabular_training_job(
            dataset_id=dataset_id,
            target_column=target_column,
            training_data_uri=training_data_uri,
            validation_data_uri=validation_data_uri,
            test_data_uri=test_data_uri,
            display_name=display_name,
            optimization_objective=optimization_objective,
            budget_milli_node_hours=budget_milli_node_hours,
            model_display_name=model_display_name,
            disable_early_stopping=disable_early_stopping,
            column_specs=column_specs,
            predefined_split_column=predefined_split_column
        )
    
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
        """Delegate to custom training manager."""
        return await self.custom.create_custom_training_job(
            dataset_id=dataset_id,
            display_name=display_name,
            script_path=script_path,
            container_uri=container_uri,
            training_data_uri=training_data_uri,
            validation_data_uri=validation_data_uri,
            test_data_uri=test_data_uri,
            model_output_uri=model_output_uri,
            hyperparameters=hyperparameters,
            machine_type=machine_type,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            replica_count=replica_count,
            args=args,
            environment_variables=environment_variables
        )
    
    async def get_job_status(self, job_resource_name: str) -> Dict[str, Any]:
        """Delegate to job manager."""
        return await self.jobs.get_job_status(job_resource_name)
    
    async def cancel_job(self, job_resource_name: str) -> bool:
        """Delegate to job manager."""
        return await self.jobs.cancel_job(job_resource_name)
    
    async def get_model_evaluation(self, model_resource_name: str) -> Dict[str, Any]:
        """Delegate to job manager."""
        return await self.jobs.get_model_evaluation(model_resource_name)
    
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
        """Delegate to deployment manager."""
        return await self.deployment.deploy_model(
            model_resource_name=model_resource_name,
            endpoint_display_name=endpoint_display_name,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count
        )
    
    async def predict(
        self,
        endpoint_resource_name: str,
        instances: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Delegate to deployment manager."""
        return await self.deployment.predict(
            endpoint_resource_name=endpoint_resource_name,
            instances=instances
        )
