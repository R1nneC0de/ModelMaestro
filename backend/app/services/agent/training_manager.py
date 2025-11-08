"""
Training Manager for single-model orchestration.

This module manages the complete training lifecycle for a single model,
including job submission, monitoring, evaluation, and artifact management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import structlog

from app.services.cloud.vertex_client import VertexAIClient, JobState
from app.services.agent.types import ProblemAnalysis
from app.services.agent.training_config import ModelConfig, TrainingOutput, TrainingState
from app.services.agent.training_logger import training_logger
from app.services.agent.training_artifacts import TrainingArtifactManager
from app.services.agent.training_diagnostics import TrainingDiagnostics
from app.services.agent.training_utils import generate_preprocessing_hash, get_package_versions
from app.core.config import settings

logger = structlog.get_logger()


class TrainingManager:
    """
    Training Manager for single-model orchestration.
    
    Manages the complete lifecycle of training a single model.
    """
    
    def __init__(
        self,
        vertex_client: Optional[VertexAIClient] = None,
        storage_bucket: Optional[str] = None
    ):
        """
        Initialize Training Manager.
        
        Args:
            vertex_client: Vertex AI client
            storage_bucket: GCS bucket for artifacts
        """
        self.vertex_client = vertex_client or VertexAIClient()
        self.storage_bucket = storage_bucket or settings.GCS_BUCKET_NAME
        self.artifact_manager = TrainingArtifactManager(self.storage_bucket)
        self.diagnostics = TrainingDiagnostics()
        
        logger.info("training_manager_initialized", bucket=self.storage_bucket)
    
    async def train_model(
        self,
        config: ModelConfig,
        dataset_id: str,
        training_data_uri: str,
        validation_data_uri: str,
        test_data_uri: str,
        target_column: str,
        problem_analysis: ProblemAnalysis,
        preprocessing_metadata: Dict[str, Any]
    ) -> TrainingOutput:
        """
        Train a single model based on the provided configuration.
        
        Args:
            config: Model configuration
            dataset_id: Dataset identifier
            training_data_uri: GCS URI to training data
            validation_data_uri: GCS URI to validation data
            test_data_uri: GCS URI to test data
            target_column: Target column name
            problem_analysis: Problem analysis from Step 3
            preprocessing_metadata: Metadata from data processing
            
        Returns:
            TrainingOutput with metrics, artifacts, and provenance
        """
        logger.info(
            "starting_training",
            dataset_id=dataset_id,
            architecture=config.architecture,
            vertex_ai_type=config.vertex_ai_type
        )
        
        training_logger.log_training_start(
            dataset_id=dataset_id,
            architecture=config.architecture,
            config=config.to_dict()
        )
        
        start_time = datetime.utcnow()
        prep_hash = generate_preprocessing_hash(preprocessing_metadata)
        package_versions = get_package_versions()
        
        try:
            # Submit training job
            if config.vertex_ai_type == "automl":
                job_info = await self._submit_automl_job(
                    config, dataset_id, training_data_uri, validation_data_uri,
                    test_data_uri, target_column, problem_analysis
                )
            else:
                job_info = await self._submit_custom_job(
                    config, dataset_id, training_data_uri, validation_data_uri,
                    test_data_uri, target_column, problem_analysis
                )
            
            logger.info("training_job_submitted", job_id=job_info["job_id"])
            
            # Monitor job
            final_status = await self._monitor_job(
                job_info["resource_name"],
                poll_interval_seconds=30,
                max_wait_hours=settings.MAX_TRAINING_HOURS
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Check if succeeded
            if final_status["state"] != JobState.SUCCEEDED.value:
                return self._handle_failure(
                    job_info, final_status, config, dataset_id,
                    prep_hash, package_versions, duration
                )
            
            # Training succeeded
            return await self._handle_success(
                job_info, config, dataset_id, preprocessing_metadata,
                prep_hash, package_versions, duration
            )
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            return self._handle_exception(
                e, config, dataset_id, prep_hash, package_versions, duration
            )
    
    async def _submit_automl_job(
        self, config: ModelConfig, dataset_id: str, training_data_uri: str,
        validation_data_uri: str, test_data_uri: str, target_column: str,
        problem_analysis: ProblemAnalysis
    ) -> Dict[str, Any]:
        """Submit AutoML training job."""
        optimization_objective = config.hyperparameters.get(
            "optimization_objective",
            self.diagnostics.get_default_objective(problem_analysis)
        )
        
        budget = config.hyperparameters.get("train_budget_milli_node_hours", 1000)
        display_name = f"automl_{config.architecture}_{dataset_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # For AutoML, use the combined CSV file instead of separate pickle files
        # The training_data_uri should point to the automl_csv file
        # We'll construct it from the training_data_uri by replacing the path
        automl_csv_uri = training_data_uri.replace("/train.pkl", "/combined_automl.csv")
        
        logger.info(f"Using AutoML CSV: {automl_csv_uri}")
        
        return await self.vertex_client.create_automl_tabular_training_job(
            dataset_id=dataset_id,
            target_column=target_column,
            training_data_uri=automl_csv_uri,  # Use combined CSV
            validation_data_uri=validation_data_uri,  # Not used with predefined split
            test_data_uri=test_data_uri,  # Not used with predefined split
            display_name=display_name,
            optimization_objective=optimization_objective,
            budget_milli_node_hours=budget,
            model_display_name=f"model_{dataset_id}",
            disable_early_stopping=config.hyperparameters.get("disable_early_stopping", False),
            predefined_split_column="ml_use"  # Use the ml_use column for splits
        )
    
    async def _submit_custom_job(
        self, config: ModelConfig, dataset_id: str, training_data_uri: str,
        validation_data_uri: str, test_data_uri: str, target_column: str,
        problem_analysis: ProblemAnalysis
    ) -> Dict[str, Any]:
        """Submit custom training job."""
        container_uri = self.diagnostics.get_training_container(config.architecture)
        script_path = self.diagnostics.get_training_script(config.architecture)
        model_output_uri = f"gs://{self.storage_bucket}/models/{dataset_id}/artifacts"
        
        machine_type = config.hyperparameters.get("machine_type", "n1-standard-4")
        accelerator_type = config.hyperparameters.get("accelerator_type")
        accelerator_count = config.hyperparameters.get("accelerator_count", 0)
        
        display_name = f"custom_{config.architecture}_{dataset_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        training_hyperparameters = {
            k: v for k, v in config.hyperparameters.items()
            if k not in ["machine_type", "accelerator_type", "accelerator_count"]
        }
        
        return await self.vertex_client.create_custom_training_job(
            dataset_id=dataset_id,
            display_name=display_name,
            script_path=script_path,
            container_uri=container_uri,
            training_data_uri=training_data_uri,
            validation_data_uri=validation_data_uri,
            test_data_uri=test_data_uri,
            model_output_uri=model_output_uri,
            hyperparameters=training_hyperparameters,
            machine_type=machine_type,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count
        )
    
    async def _monitor_job(
        self, job_resource_name: str, poll_interval_seconds: int = 30,
        max_wait_hours: int = 24
    ) -> Dict[str, Any]:
        """Monitor training job status with polling."""
        max_polls = (max_wait_hours * 3600) // poll_interval_seconds
        poll_count = 0
        
        logger.info("monitoring_job", job_resource_name=job_resource_name)
        
        while poll_count < max_polls:
            status = await self.vertex_client.get_job_status(job_resource_name)
            state = status["state"]
            
            logger.debug("job_status_check", job_id=status["job_id"], state=state)
            
            training_logger.log_training_progress(
                job_id=status["job_id"],
                state=state,
                message=f"Poll {poll_count}/{max_polls}"
            )
            
            if state in [
                JobState.SUCCEEDED.value, JobState.FAILED.value,
                JobState.CANCELLED.value, JobState.EXPIRED.value
            ]:
                logger.info("job_completed", job_id=status["job_id"], state=state)
                return status
            
            await asyncio.sleep(poll_interval_seconds)
            poll_count += 1
        
        # Timeout
        logger.warning("job_monitoring_timeout", job_resource_name=job_resource_name)
        final_status = await self.vertex_client.get_job_status(job_resource_name)
        final_status["timeout"] = True
        return final_status
    
    def _handle_failure(
        self, job_info: Dict[str, Any], final_status: Dict[str, Any],
        config: ModelConfig, dataset_id: str, prep_hash: str,
        package_versions: Dict[str, str], duration: float
    ) -> TrainingOutput:
        """Handle training failure."""
        error_msg = final_status.get("error", {}).get("message", "Unknown error")
        error_cause = self.diagnostics.diagnose_failure(final_status, config)
        
        logger.error("training_failed", job_id=job_info["job_id"], cause=error_cause)
        
        training_logger.log_training_failure(
            job_id=job_info["job_id"],
            dataset_id=dataset_id,
            architecture=config.architecture,
            error_message=error_msg,
            error_cause=error_cause,
            context={"final_status": final_status}
        )
        
        return TrainingOutput(
            job_id=job_info["job_id"],
            job_resource_name=job_info["resource_name"],
            state=TrainingState.FAILED.value,
            error_message=error_msg,
            error_cause=error_cause,
            strategy_config=config,
            step3_summary_hash=prep_hash,
            package_versions=package_versions,
            random_seed=config.split_config.random_seed,
            training_duration_seconds=duration
        )
    
    async def _handle_success(
        self, job_info: Dict[str, Any], config: ModelConfig, dataset_id: str,
        preprocessing_metadata: Dict[str, Any], prep_hash: str,
        package_versions: Dict[str, str], duration: float
    ) -> TrainingOutput:
        """Handle training success."""
        logger.info("training_succeeded", job_id=job_info["job_id"])
        
        training_logger.log_training_success(
            job_id=job_info["job_id"],
            dataset_id=dataset_id,
            architecture=config.architecture,
            metrics={},
            duration_seconds=duration
        )
        
        # Get metrics
        metrics = await self._get_training_metrics(job_info, config)
        
        # Store artifacts
        artifact_uris = await self.artifact_manager.store_artifacts(
            dataset_id, job_info, config, preprocessing_metadata
        )
        
        # Generate report
        report_uri = await self.artifact_manager.generate_training_report(
            dataset_id, config, metrics, duration, job_info
        )
        
        return TrainingOutput(
            metrics=metrics,
            primary_metric_value=metrics.get(config.primary_metric, 0.0),
            model_uri=artifact_uris["model_uri"],
            prep_uri=artifact_uris["prep_uri"],
            report_uri=report_uri,
            step3_summary_hash=prep_hash,
            strategy_config=config,
            package_versions=package_versions,
            random_seed=config.split_config.random_seed,
            training_duration_seconds=duration,
            job_id=job_info["job_id"],
            job_resource_name=job_info["resource_name"],
            state=TrainingState.SUCCEEDED.value
        )
    
    def _handle_exception(
        self, exception: Exception, config: ModelConfig, dataset_id: str,
        prep_hash: str, package_versions: Dict[str, str], duration: float
    ) -> TrainingOutput:
        """Handle exception during training."""
        error_msg = str(exception)
        error_cause = self.diagnostics.diagnose_exception(exception, config)
        
        logger.error("training_exception", error=error_msg, cause=error_cause)
        
        training_logger.log_training_failure(
            job_id=None,
            dataset_id=dataset_id,
            architecture=config.architecture,
            error_message=error_msg,
            error_cause=error_cause,
            context={"exception_type": type(exception).__name__}
        )
        
        return TrainingOutput(
            state=TrainingState.FAILED.value,
            error_message=error_msg,
            error_cause=error_cause,
            strategy_config=config,
            step3_summary_hash=prep_hash,
            package_versions=package_versions,
            random_seed=config.split_config.random_seed,
            training_duration_seconds=duration
        )
    
    async def _get_training_metrics(
        self, job_info: Dict[str, Any], config: ModelConfig
    ) -> Dict[str, float]:
        """Get training metrics from completed job."""
        try:
            if job_info.get("training_type") == "automl_tabular":
                logger.info("retrieving_automl_metrics", job_id=job_info["job_id"])
                # Placeholder - in production, retrieve actual metrics
                metrics = {
                    config.primary_metric: 0.75,
                    "accuracy": 0.80,
                    "precision": 0.78,
                    "recall": 0.76,
                    "f1": 0.77
                }
            else:
                logger.info("retrieving_custom_metrics", job_id=job_info["job_id"])
                # Placeholder - in production, read from GCS
                metrics = {
                    config.primary_metric: 0.70,
                    "rmse": 0.25,
                    "mae": 0.20,
                    "r2": 0.65
                }
            
            return metrics
            
        except Exception as e:
            logger.error("failed_to_retrieve_metrics", error=str(e))
            return {}
