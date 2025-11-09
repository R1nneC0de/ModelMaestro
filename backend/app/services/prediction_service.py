"""
Model prediction service with logging and monitoring.

This module provides high-level prediction utilities with:
- Input validation
- Prediction logging
- Usage tracking
- Error handling
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.services.cloud.vertex_deployment import VertexDeploymentManager, DeploymentError
from app.services.cloud.storage import upload_json_to_gcs
from app.core.config import settings

logger = structlog.get_logger()


class PredictionService:
    """
    High-level prediction service.
    
    Provides prediction capabilities with:
    - Input validation
    - Prediction logging for monitoring
    - Usage metrics tracking
    - Error handling and retry logic
    """
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None
    ):
        """
        Initialize prediction service.
        
        Args:
            project: GCP project ID (defaults to settings)
            location: GCP region (defaults to settings)
        """
        self.project = project or settings.GOOGLE_CLOUD_PROJECT
        self.location = location or settings.VERTEX_AI_LOCATION
        self.deployment_manager = VertexDeploymentManager(self.project, self.location)
        
        logger.info(
            "prediction_service_initialized",
            project=self.project,
            location=self.location
        )
    
    async def predict(
        self,
        model_id: str,
        endpoint_resource_name: str,
        instances: List[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]] = None,
        log_predictions: bool = True
    ) -> Dict[str, Any]:
        """
        Make predictions with input validation and logging.
        
        Args:
            model_id: Unique model identifier
            endpoint_resource_name: Vertex AI endpoint resource name
            instances: List of instances to predict
            parameters: Optional prediction parameters
            log_predictions: Whether to log predictions for monitoring
            
        Returns:
            Dictionary with predictions and metadata
        """
        logger.info(
            "prediction_request",
            model_id=model_id,
            num_instances=len(instances)
        )
        
        # Validate inputs
        if not instances:
            raise ValueError("No instances provided for prediction")
        
        if len(instances) > 1000:
            logger.warning(
                "large_prediction_request",
                num_instances=len(instances),
                recommendation="Consider using batch prediction for >1000 instances"
            )
        
        try:
            # Make prediction
            start_time = datetime.utcnow()
            
            prediction_result = await self.deployment_manager.predict(
                endpoint_resource_name=endpoint_resource_name,
                instances=instances,
                parameters=parameters
            )
            
            end_time = datetime.utcnow()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Add metadata
            result = {
                "model_id": model_id,
                "predictions": prediction_result.get("predictions", []),
                "endpoint_id": prediction_result.get("endpoint_id"),
                "deployed_model_id": prediction_result.get("deployed_model_id"),
                "metadata": {
                    "num_instances": len(instances),
                    "num_predictions": len(prediction_result.get("predictions", [])),
                    "latency_ms": latency_ms,
                    "timestamp": end_time.isoformat()
                }
            }
            
            # Log prediction for monitoring
            if log_predictions:
                await self._log_prediction(
                    model_id=model_id,
                    num_instances=len(instances),
                    latency_ms=latency_ms,
                    success=True
                )
            
            logger.info(
                "prediction_successful",
                model_id=model_id,
                num_predictions=len(result["predictions"]),
                latency_ms=latency_ms
            )
            
            return result
            
        except DeploymentError as e:
            logger.error(
                "prediction_failed",
                model_id=model_id,
                error=str(e)
            )
            
            # Log failed prediction
            if log_predictions:
                await self._log_prediction(
                    model_id=model_id,
                    num_instances=len(instances),
                    latency_ms=0,
                    success=False,
                    error=str(e)
                )
            
            raise
        except Exception as e:
            logger.error(
                "prediction_error",
                model_id=model_id,
                error=str(e)
            )
            
            # Log failed prediction
            if log_predictions:
                await self._log_prediction(
                    model_id=model_id,
                    num_instances=len(instances),
                    latency_ms=0,
                    success=False,
                    error=str(e)
                )
            
            raise
    
    async def _log_prediction(
        self,
        model_id: str,
        num_instances: int,
        latency_ms: float,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Log prediction for monitoring and usage tracking.
        
        Args:
            model_id: Model identifier
            num_instances: Number of instances predicted
            latency_ms: Prediction latency in milliseconds
            success: Whether prediction succeeded
            error: Error message if failed
        """
        try:
            log_entry = {
                "model_id": model_id,
                "timestamp": datetime.utcnow().isoformat(),
                "num_instances": num_instances,
                "latency_ms": latency_ms,
                "success": success,
                "error": error
            }
            
            # Store in GCS for monitoring
            log_path = f"prediction_logs/{model_id}/{datetime.utcnow().strftime('%Y%m%d')}/log_{datetime.utcnow().strftime('%H%M%S_%f')}.json"
            
            await upload_json_to_gcs(
                data=log_entry,
                blob_name=log_path,
                bucket_name=settings.GCS_BUCKET_NAME
            )
            
            logger.debug("prediction_logged", log_path=log_path)
            
        except Exception as e:
            # Don't fail prediction if logging fails
            logger.warning(
                "prediction_logging_failed",
                model_id=model_id,
                error=str(e)
            )
    
    async def get_usage_metrics(
        self,
        model_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get usage metrics for a model.
        
        Args:
            model_id: Model identifier
            start_date: Start date for metrics (defaults to 7 days ago)
            end_date: End date for metrics (defaults to now)
            
        Returns:
            Usage metrics including request count, latency stats, error rate
        """
        logger.info(
            "get_usage_metrics",
            model_id=model_id,
            start_date=start_date,
            end_date=end_date
        )
        
        try:
            # TODO: Implement metrics aggregation from prediction logs
            # This would:
            # 1. List prediction log files in date range
            # 2. Parse and aggregate metrics
            # 3. Calculate statistics (avg latency, error rate, etc.)
            
            return {
                "model_id": model_id,
                "metrics": {
                    "total_requests": 0,
                    "total_instances": 0,
                    "avg_latency_ms": 0.0,
                    "error_rate": 0.0,
                    "success_rate": 100.0
                },
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logger.error(
                "get_usage_metrics_failed",
                model_id=model_id,
                error=str(e)
            )
            raise
    
    def validate_instances(
        self,
        instances: List[Dict[str, Any]],
        expected_features: Optional[List[str]] = None
    ) -> bool:
        """
        Validate prediction instances.
        
        Args:
            instances: List of instances to validate
            expected_features: Optional list of expected feature names
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        if not instances:
            raise ValueError("No instances provided")
        
        if not isinstance(instances, list):
            raise ValueError("Instances must be a list")
        
        for i, instance in enumerate(instances):
            if not isinstance(instance, dict):
                raise ValueError(f"Instance {i} must be a dictionary")
            
            if expected_features:
                missing_features = set(expected_features) - set(instance.keys())
                if missing_features:
                    raise ValueError(
                        f"Instance {i} missing features: {missing_features}"
                    )
        
        return True
