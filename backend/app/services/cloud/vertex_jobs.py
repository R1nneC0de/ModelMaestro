"""
Vertex AI job monitoring and management.
"""

import logging
from typing import Dict, Any
from enum import Enum

from google.cloud import aiplatform
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)


class JobState(str, Enum):
    """Vertex AI job states."""
    QUEUED = "JOB_STATE_QUEUED"
    PENDING = "JOB_STATE_PENDING"
    RUNNING = "JOB_STATE_RUNNING"
    SUCCEEDED = "JOB_STATE_SUCCEEDED"
    FAILED = "JOB_STATE_FAILED"
    CANCELLING = "JOB_STATE_CANCELLING"
    CANCELLED = "JOB_STATE_CANCELLED"
    PAUSED = "JOB_STATE_PAUSED"
    EXPIRED = "JOB_STATE_EXPIRED"


class VertexJobManager:
    """Manager for Vertex AI job monitoring and control."""
    
    async def get_job_status(self, job_resource_name: str) -> Dict[str, Any]:
        """
        Get the status of a training job.
        
        Args:
            job_resource_name: Full resource name of the job
            
        Returns:
            Dictionary with job status information
        """
        try:
            # Determine job type from resource name
            if "autoMlTabularTrainingJobs" in job_resource_name:
                job = aiplatform.AutoMLTabularTrainingJob(job_resource_name)
            elif "customJobs" in job_resource_name:
                job = aiplatform.CustomTrainingJob(job_resource_name)
            else:
                raise ValueError(f"Unknown job type: {job_resource_name}")
            
            # Get job state
            state = job.state.name if hasattr(job.state, 'name') else str(job.state)
            
            status = {
                "job_id": job.name.split("/")[-1],
                "resource_name": job_resource_name,
                "state": state,
                "display_name": job.display_name,
                "create_time": job.create_time.isoformat() if job.create_time else None,
                "start_time": job.start_time.isoformat() if job.start_time else None,
                "end_time": job.end_time.isoformat() if job.end_time else None,
                "update_time": job.update_time.isoformat() if job.update_time else None
            }
            
            # Add error information if failed
            if state == JobState.FAILED.value:
                status["error"] = {
                    "message": str(job.error) if hasattr(job, 'error') and job.error else "Unknown error"
                }
            
            return status
            
        except google_exceptions.NotFound:
            logger.error(f"Job not found: {job_resource_name}")
            raise
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            raise
    
    async def cancel_job(self, job_resource_name: str) -> bool:
        """
        Cancel a running training job.
        
        Args:
            job_resource_name: Full resource name of the job
            
        Returns:
            True if cancellation was successful
        """
        try:
            # Determine job type from resource name
            if "autoMlTabularTrainingJobs" in job_resource_name:
                job = aiplatform.AutoMLTabularTrainingJob(job_resource_name)
            elif "customJobs" in job_resource_name:
                job = aiplatform.CustomTrainingJob(job_resource_name)
            else:
                raise ValueError(f"Unknown job type: {job_resource_name}")
            
            job.cancel()
            logger.info(f"Cancelled job: {job_resource_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job: {e}")
            raise
    
    async def get_model_evaluation(self, model_resource_name: str) -> Dict[str, Any]:
        """
        Get evaluation metrics for a trained model.
        
        Args:
            model_resource_name: Full resource name of the model
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            model = aiplatform.Model(model_resource_name)
            
            # Get model evaluations
            evaluations = model.list_model_evaluations()
            
            if not evaluations:
                logger.warning(f"No evaluations found for model: {model_resource_name}")
                return {}
            
            # Get the first (usually only) evaluation
            evaluation = evaluations[0]
            
            metrics = {
                "evaluation_id": evaluation.name.split("/")[-1],
                "metrics": evaluation.metrics if hasattr(evaluation, 'metrics') else {},
                "create_time": evaluation.create_time.isoformat() if evaluation.create_time else None
            }
            
            logger.info(f"Retrieved evaluation for model: {model_resource_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get model evaluation: {e}")
            raise
