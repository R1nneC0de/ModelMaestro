"""
Vertex AI AutoML training job management.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from google.cloud import aiplatform

from app.core.config import settings

logger = logging.getLogger(__name__)


class VertexAutoMLManager:
    """Manager for Vertex AI AutoML training jobs."""
    
    def __init__(self, project: str, location: str):
        """
        Initialize AutoML manager.
        
        Args:
            project: GCP project ID
            location: GCP region
        """
        self.project = project
        self.location = location
    
    async def create_tabular_training_job(
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
        """
        Create an AutoML Tabular training job.
        
        Args:
            dataset_id: Unique identifier for the dataset
            target_column: Name of the target column
            training_data_uri: GCS URI to training data
            validation_data_uri: GCS URI to validation data
            test_data_uri: GCS URI to test data
            display_name: Display name for the training job
            optimization_objective: Objective to optimize
            budget_milli_node_hours: Training budget in milli node hours
            model_display_name: Display name for the trained model
            disable_early_stopping: Whether to disable early stopping
            column_specs: Optional column specifications
            predefined_split_column: Column name for predefined data splits
            
        Returns:
            Dictionary with job information
        """
        logger.info(
            f"Creating AutoML Tabular job: {display_name}, "
            f"target={target_column}, budget={budget_milli_node_hours}"
        )
        
        try:
            # Create TabularDataset from CSV
            dataset = aiplatform.TabularDataset.create(
                display_name=f"dataset_{dataset_id}",
                gcs_source=training_data_uri,  # Should be CSV file
                bq_source=None
            )
            
            logger.info(f"Created TabularDataset: {dataset.resource_name}")
            
            # Create AutoML training job
            job = aiplatform.AutoMLTabularTrainingJob(
                display_name=display_name,
                optimization_prediction_type=self._get_prediction_type(optimization_objective),
                optimization_objective=optimization_objective,
                column_specs=column_specs,
                column_transformations=None
            )
            
            # Start training with predefined split column
            model = job.run(
                dataset=dataset,
                target_column=target_column,
                training_fraction_split=None,
                validation_fraction_split=None,
                test_fraction_split=None,
                predefined_split_column_name=predefined_split_column or "ml_use",  # Use ml_use column for splits
                budget_milli_node_hours=budget_milli_node_hours,
                model_display_name=model_display_name or f"model_{dataset_id}",
                disable_early_stopping=disable_early_stopping,
                sync=True
            )
            
            job_info = {
                "job_id": job.name.split("/")[-1],
                "resource_name": job.resource_name,
                "display_name": display_name,
                "state": job.state.name if hasattr(job.state, 'name') else str(job.state),
                "created_at": datetime.utcnow().isoformat(),
                "dataset_id": dataset_id,
                "target_column": target_column,
                "optimization_objective": optimization_objective,
                "budget_milli_node_hours": budget_milli_node_hours,
                "training_type": "automl_tabular"
            }
            
            logger.info(f"AutoML Tabular job created: {job_info['job_id']}")
            return job_info
            
        except Exception as e:
            logger.error(f"Failed to create AutoML Tabular job: {e}")
            raise
    
    def _get_prediction_type(self, optimization_objective: str) -> str:
        """Determine prediction type from optimization objective."""
        regression_objectives = [
            "minimize-rmse",
            "minimize-mae",
            "minimize-rmsle"
        ]
        
        if any(obj in optimization_objective.lower() for obj in regression_objectives):
            return "regression"
        else:
            return "classification"
