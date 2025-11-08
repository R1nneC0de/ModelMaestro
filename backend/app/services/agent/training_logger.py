"""
Training observability and logging utilities.

Provides structured logging with Cloud Logging integration and
error tracking for training operations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field
import structlog

from app.core.config import settings


@dataclass
class TrainingError:
    """Structured training error information."""
    timestamp: str
    error_type: str
    error_message: str
    error_cause: str
    job_id: Optional[str] = None
    dataset_id: Optional[str] = None
    architecture: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_cause": self.error_cause,
            "job_id": self.job_id,
            "dataset_id": self.dataset_id,
            "architecture": self.architecture,
            "context": self.context
        }


class TrainingLogger:
    """
    Training logger with structured logging and error tracking.
    
    Provides:
    - Structured logging with Cloud Logging integration
    - Error history tracking (last N errors)
    - Explicit error cause surfacing
    - No automatic retry logic
    """
    
    def __init__(self, max_errors: int = 100):
        """
        Initialize training logger.
        
        Args:
            max_errors: Maximum number of errors to keep in history
        """
        self.logger = structlog.get_logger(__name__)
        self.max_errors = max_errors
        self.error_history: deque = deque(maxlen=max_errors)
        
        # Configure Cloud Logging if in production
        if settings.is_production:
            self._setup_cloud_logging()
    
    def _setup_cloud_logging(self):
        """Set up Google Cloud Logging integration."""
        try:
            from google.cloud import logging as cloud_logging
            
            client = cloud_logging.Client(project=settings.GOOGLE_CLOUD_PROJECT)
            client.setup_logging()
            
            self.logger.info("cloud_logging_configured")
        except Exception as e:
            self.logger.warning(
                "cloud_logging_setup_failed",
                error=str(e)
            )
    
    def log_training_start(
        self,
        dataset_id: str,
        architecture: str,
        config: Dict[str, Any]
    ):
        """
        Log training start event.
        
        Args:
            dataset_id: Dataset identifier
            architecture: Model architecture
            config: Training configuration
        """
        self.logger.info(
            "training_started",
            dataset_id=dataset_id,
            architecture=architecture,
            config=config,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_training_progress(
        self,
        job_id: str,
        state: str,
        progress_percent: Optional[float] = None,
        message: Optional[str] = None
    ):
        """
        Log training progress update.
        
        Args:
            job_id: Job identifier
            state: Current job state
            progress_percent: Progress percentage (0-100)
            message: Optional progress message
        """
        self.logger.info(
            "training_progress",
            job_id=job_id,
            state=state,
            progress_percent=progress_percent,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_training_success(
        self,
        job_id: str,
        dataset_id: str,
        architecture: str,
        metrics: Dict[str, float],
        duration_seconds: float
    ):
        """
        Log training success event.
        
        Args:
            job_id: Job identifier
            dataset_id: Dataset identifier
            architecture: Model architecture
            metrics: Training metrics
            duration_seconds: Training duration
        """
        self.logger.info(
            "training_succeeded",
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            metrics=metrics,
            duration_seconds=duration_seconds,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_training_failure(
        self,
        job_id: Optional[str],
        dataset_id: str,
        architecture: str,
        error_message: str,
        error_cause: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TrainingError:
        """
        Log training failure with explicit cause.
        
        NO automatic retry logic - just log and surface the error.
        
        Args:
            job_id: Job identifier (if available)
            dataset_id: Dataset identifier
            architecture: Model architecture
            error_message: Error message
            error_cause: Explicit error cause (e.g., SCHEMA_ERROR, OOM)
            context: Additional context
            
        Returns:
            TrainingError object
        """
        error = TrainingError(
            timestamp=datetime.utcnow().isoformat(),
            error_type="TRAINING_FAILURE",
            error_message=error_message,
            error_cause=error_cause,
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            context=context or {}
        )
        
        # Add to error history
        self.error_history.append(error)
        
        # Log error
        self.logger.error(
            "training_failed",
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            error_message=error_message,
            error_cause=error_cause,
            context=context,
            timestamp=error.timestamp
        )
        
        return error
    
    def log_schema_error(
        self,
        dataset_id: str,
        error_details: str,
        sample_data: Optional[str] = None
    ) -> TrainingError:
        """
        Log schema/data format error.
        
        Args:
            dataset_id: Dataset identifier
            error_details: Detailed error information
            sample_data: Sample of problematic data
            
        Returns:
            TrainingError object
        """
        context = {"error_details": error_details}
        if sample_data:
            context["sample_data"] = sample_data
        
        error = TrainingError(
            timestamp=datetime.utcnow().isoformat(),
            error_type="SCHEMA_ERROR",
            error_message="Data format or schema error",
            error_cause="SCHEMA_ERROR: Check CSV delimiter, headers, or column types",
            dataset_id=dataset_id,
            context=context
        )
        
        self.error_history.append(error)
        
        self.logger.error(
            "schema_error",
            dataset_id=dataset_id,
            error_details=error_details,
            sample_data=sample_data,
            timestamp=error.timestamp
        )
        
        return error
    
    def log_oom_error(
        self,
        job_id: str,
        dataset_id: str,
        architecture: str,
        memory_requested: Optional[str] = None,
        data_size_mb: Optional[float] = None
    ) -> TrainingError:
        """
        Log out-of-memory error.
        
        Args:
            job_id: Job identifier
            dataset_id: Dataset identifier
            architecture: Model architecture
            memory_requested: Memory that was requested
            data_size_mb: Size of dataset in MB
            
        Returns:
            TrainingError object
        """
        context = {}
        if memory_requested:
            context["memory_requested"] = memory_requested
        if data_size_mb:
            context["data_size_mb"] = data_size_mb
        
        error = TrainingError(
            timestamp=datetime.utcnow().isoformat(),
            error_type="OUT_OF_MEMORY",
            error_message="Insufficient memory for training",
            error_cause=f"OUT_OF_MEMORY: Insufficient memory for {architecture}. Consider using AutoML or reducing data size.",
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            context=context
        )
        
        self.error_history.append(error)
        
        self.logger.error(
            "out_of_memory",
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            memory_requested=memory_requested,
            data_size_mb=data_size_mb,
            timestamp=error.timestamp
        )
        
        return error
    
    def log_convergence_error(
        self,
        job_id: str,
        dataset_id: str,
        architecture: str,
        hyperparameters: Dict[str, Any]
    ) -> TrainingError:
        """
        Log model convergence error.
        
        Args:
            job_id: Job identifier
            dataset_id: Dataset identifier
            architecture: Model architecture
            hyperparameters: Hyperparameters used
            
        Returns:
            TrainingError object
        """
        error = TrainingError(
            timestamp=datetime.utcnow().isoformat(),
            error_type="CONVERGENCE_ERROR",
            error_message="Model failed to converge",
            error_cause="TRAINING_ERROR: Model failed to converge. Try different hyperparameters or algorithm.",
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            context={"hyperparameters": hyperparameters}
        )
        
        self.error_history.append(error)
        
        self.logger.error(
            "convergence_error",
            job_id=job_id,
            dataset_id=dataset_id,
            architecture=architecture,
            hyperparameters=hyperparameters,
            timestamp=error.timestamp
        )
        
        return error
    
    def get_recent_errors(self, n: int = 10) -> List[TrainingError]:
        """
        Get the N most recent errors.
        
        Args:
            n: Number of errors to retrieve
            
        Returns:
            List of recent TrainingError objects
        """
        return list(self.error_history)[-n:]
    
    def get_errors_for_dataset(self, dataset_id: str) -> List[TrainingError]:
        """
        Get all errors for a specific dataset.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            List of TrainingError objects for the dataset
        """
        return [
            error for error in self.error_history
            if error.dataset_id == dataset_id
        ]
    
    def get_errors_by_type(self, error_type: str) -> List[TrainingError]:
        """
        Get all errors of a specific type.
        
        Args:
            error_type: Error type to filter by
            
        Returns:
            List of TrainingError objects of the specified type
        """
        return [
            error for error in self.error_history
            if error.error_type == error_type
        ]
    
    def clear_error_history(self):
        """Clear the error history."""
        self.error_history.clear()
        self.logger.info("error_history_cleared")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of error history.
        
        Returns:
            Dictionary with error statistics
        """
        if not self.error_history:
            return {
                "total_errors": 0,
                "error_types": {},
                "recent_errors": []
            }
        
        # Count errors by type
        error_types = {}
        for error in self.error_history:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "recent_errors": [e.to_dict() for e in self.get_recent_errors(5)]
        }


# Global logger instance
training_logger = TrainingLogger()
