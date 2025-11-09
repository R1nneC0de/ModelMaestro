"""
Deployment health monitoring and error handling service.

This module provides comprehensive health monitoring for deployed models,
including periodic health checks, error detection, automatic recovery,
and alerting capabilities.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.services.cloud.vertex_deployment import VertexDeploymentManager
from app.services.cloud.deployment import ModelDeploymentService
from app.services.cloud.artifact_handler import ModelArtifactHandler

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeploymentHealthMonitor:
    """
    Comprehensive health monitoring service for model deployments.
    
    Provides:
    - Periodic health checks
    - Error detection and classification
    - Automatic recovery attempts
    - Health status reporting
    - Alert generation
    """
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None
    ):
        """
        Initialize health monitor.
        
        Args:
            project: GCP project ID
            location: GCP region
        """
        self.deployment_service = ModelDeploymentService(project, location)
        self.artifact_handler = ModelArtifactHandler()
        
        logger.info("Initialized DeploymentHealthMonitor")
    
    async def perform_health_check(
        self,
        model_id: str,
        endpoint_resource_name: Optional[str] = None,
        artifact_path: Optional[str] = None,
        include_predictions_test: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive health check on a deployed model.
        
        Args:
            model_id: Unique model identifier
            endpoint_resource_name: Vertex AI endpoint resource name
            artifact_path: GCS path to model artifacts
            include_predictions_test: Test predictions endpoint
            
        Returns:
            Dictionary with comprehensive health check results
        """
        logger.info(f"Performing health check for model: {model_id}")
        
        health_check = {
            "model_id": model_id,
            "overall_status": HealthStatus.UNKNOWN.value,
            "endpoint_status": None,
            "artifact_status": None,
            "prediction_test": None,
            "issues": [],
            "recommendations": [],
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Check endpoint health
        if endpoint_resource_name:
            endpoint_status = await self._check_endpoint_status(
                endpoint_resource_name
            )
            health_check["endpoint_status"] = endpoint_status
            
            # Add issues if endpoint is unhealthy
            if not endpoint_status.get("is_healthy", False):
                health_check["issues"].append({
                    "component": "endpoint",
                    "severity": ErrorSeverity.HIGH.value,
                    "message": endpoint_status.get("error", "Endpoint is unhealthy"),
                    "detected_at": datetime.utcnow().isoformat()
                })
        
        # Check artifact availability
        if artifact_path:
            artifact_status = await self._check_artifact_status(artifact_path)
            health_check["artifact_status"] = artifact_status
            
            # Add issues if artifacts are unavailable
            if not artifact_status.get("available", False):
                health_check["issues"].append({
                    "component": "artifacts",
                    "severity": ErrorSeverity.MEDIUM.value,
                    "message": "Model artifacts are not available",
                    "detected_at": datetime.utcnow().isoformat()
                })
        
        # Test predictions if requested and endpoint is available
        if include_predictions_test and endpoint_resource_name:
            if health_check["endpoint_status"] and health_check["endpoint_status"].get("is_healthy"):
                prediction_test = await self._test_predictions(
                    endpoint_resource_name
                )
                health_check["prediction_test"] = prediction_test
                
                if not prediction_test.get("success", False):
                    health_check["issues"].append({
                        "component": "predictions",
                        "severity": ErrorSeverity.CRITICAL.value,
                        "message": prediction_test.get("error", "Prediction test failed"),
                        "detected_at": datetime.utcnow().isoformat()
                    })
        
        # Determine overall status
        health_check["overall_status"] = self._determine_overall_status(
            health_check
        )
        
        # Generate recommendations
        health_check["recommendations"] = self._generate_recommendations(
            health_check
        )
        
        logger.info(
            f"Health check complete: model={model_id}, "
            f"status={health_check['overall_status']}, "
            f"issues={len(health_check['issues'])}"
        )
        
        return health_check
    
    async def _check_endpoint_status(
        self,
        endpoint_resource_name: str
    ) -> Dict[str, Any]:
        """
        Check endpoint health status.
        
        Args:
            endpoint_resource_name: Vertex AI endpoint resource name
            
        Returns:
            Dictionary with endpoint status
        """
        try:
            health_info = await self.deployment_service.vertex_deployment.check_endpoint_health(
                endpoint_resource_name
            )
            return health_info
        except Exception as e:
            logger.error(f"Endpoint status check failed: {e}")
            return {
                "is_healthy": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def _check_artifact_status(
        self,
        artifact_path: str
    ) -> Dict[str, Any]:
        """
        Check artifact availability status.
        
        Args:
            artifact_path: GCS path to model artifacts
            
        Returns:
            Dictionary with artifact status
        """
        try:
            validation = await self.artifact_handler.validate_artifacts(
                artifact_base_path=artifact_path
            )
            return {
                "available": validation.get("valid", False),
                "total_files": validation.get("total_files", 0),
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Artifact status check failed: {e}")
            return {
                "available": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def _test_predictions(
        self,
        endpoint_resource_name: str,
        test_instances: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Test prediction endpoint with sample data.
        
        Args:
            endpoint_resource_name: Vertex AI endpoint resource name
            test_instances: Test instances (uses dummy data if None)
            
        Returns:
            Dictionary with prediction test results
        """
        try:
            # Use dummy test data if none provided
            if test_instances is None:
                test_instances = [{"test": "data"}]
            
            result = await self.deployment_service.vertex_deployment.predict(
                endpoint_resource_name=endpoint_resource_name,
                instances=test_instances
            )
            
            return {
                "success": True,
                "predictions_count": len(result.get("predictions", [])),
                "tested_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tested_at": datetime.utcnow().isoformat()
            }
    
    def _determine_overall_status(
        self,
        health_check: Dict[str, Any]
    ) -> str:
        """
        Determine overall health status based on component statuses.
        
        Args:
            health_check: Health check results
            
        Returns:
            Overall health status
        """
        issues = health_check.get("issues", [])
        
        # Check for critical issues
        critical_issues = [
            issue for issue in issues 
            if issue.get("severity") == ErrorSeverity.CRITICAL.value
        ]
        if critical_issues:
            return HealthStatus.UNHEALTHY.value
        
        # Check for high severity issues
        high_issues = [
            issue for issue in issues 
            if issue.get("severity") == ErrorSeverity.HIGH.value
        ]
        if high_issues:
            return HealthStatus.DEGRADED.value
        
        # Check if at least one component is healthy
        endpoint_status = health_check.get("endpoint_status") or {}
        artifact_status = health_check.get("artifact_status") or {}
        
        endpoint_healthy = endpoint_status.get("is_healthy", False) if isinstance(endpoint_status, dict) else False
        artifact_available = artifact_status.get("available", False) if isinstance(artifact_status, dict) else False
        
        if endpoint_healthy or artifact_available:
            if issues:
                return HealthStatus.DEGRADED.value
            return HealthStatus.HEALTHY.value
        
        return HealthStatus.UNHEALTHY.value
    
    def _generate_recommendations(
        self,
        health_check: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generate recommendations based on health check results.
        
        Args:
            health_check: Health check results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Endpoint recommendations
        endpoint_status = health_check.get("endpoint_status")
        if endpoint_status and not endpoint_status.get("is_healthy", False):
            recommendations.append({
                "component": "endpoint",
                "recommendation": "Check endpoint deployment status and logs",
                "action": "Verify endpoint configuration and redeploy if necessary"
            })
        
        # Artifact recommendations
        artifact_status = health_check.get("artifact_status")
        if artifact_status and not artifact_status.get("available", False):
            recommendations.append({
                "component": "artifacts",
                "recommendation": "Verify model artifacts are uploaded to GCS",
                "action": "Re-upload model artifacts or check GCS bucket permissions"
            })
        
        # Prediction recommendations
        prediction_test = health_check.get("prediction_test")
        if prediction_test and not prediction_test.get("success", False):
            recommendations.append({
                "component": "predictions",
                "recommendation": "Prediction endpoint is not responding correctly",
                "action": "Check model compatibility and endpoint configuration"
            })
        
        # General recommendations based on overall status
        overall_status = health_check.get("overall_status")
        if overall_status == HealthStatus.UNHEALTHY.value:
            recommendations.append({
                "component": "general",
                "recommendation": "Model deployment is unhealthy",
                "action": "Consider redeploying the model or falling back to artifact-only deployment"
            })
        elif overall_status == HealthStatus.DEGRADED.value:
            recommendations.append({
                "component": "general",
                "recommendation": "Model deployment is degraded",
                "action": "Monitor closely and address issues to prevent further degradation"
            })
        
        return recommendations
    
    async def attempt_recovery(
        self,
        model_id: str,
        endpoint_resource_name: Optional[str] = None,
        model_resource_name: Optional[str] = None,
        artifact_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Attempt automatic recovery for unhealthy deployment.
        
        Args:
            model_id: Unique model identifier
            endpoint_resource_name: Vertex AI endpoint resource name
            model_resource_name: Vertex AI model resource name
            artifact_path: GCS path to model artifacts
            
        Returns:
            Dictionary with recovery attempt results
        """
        logger.info(f"Attempting recovery for model: {model_id}")
        
        recovery_result = {
            "model_id": model_id,
            "recovery_attempted": False,
            "recovery_successful": False,
            "actions_taken": [],
            "attempted_at": datetime.utcnow().isoformat()
        }
        
        # Perform health check first
        health_check = await self.perform_health_check(
            model_id=model_id,
            endpoint_resource_name=endpoint_resource_name,
            artifact_path=artifact_path
        )
        
        # Only attempt recovery if unhealthy
        if health_check["overall_status"] == HealthStatus.HEALTHY.value:
            recovery_result["message"] = "Model is healthy, no recovery needed"
            return recovery_result
        
        recovery_result["recovery_attempted"] = True
        
        # Attempt endpoint recovery if endpoint is unhealthy
        if endpoint_resource_name and not health_check.get("endpoint_status", {}).get("is_healthy"):
            try:
                # Try to verify deployment again
                await self.deployment_service.vertex_deployment._verify_deployment(
                    endpoint_resource_name,
                    max_retries=2,
                    retry_delay=10
                )
                
                recovery_result["actions_taken"].append({
                    "action": "endpoint_verification",
                    "status": "success",
                    "message": "Endpoint verification successful"
                })
                
            except Exception as e:
                logger.error(f"Endpoint recovery failed: {e}")
                recovery_result["actions_taken"].append({
                    "action": "endpoint_verification",
                    "status": "failed",
                    "error": str(e)
                })
        
        # Check if recovery was successful
        final_health_check = await self.perform_health_check(
            model_id=model_id,
            endpoint_resource_name=endpoint_resource_name,
            artifact_path=artifact_path
        )
        
        recovery_result["recovery_successful"] = (
            final_health_check["overall_status"] == HealthStatus.HEALTHY.value
        )
        recovery_result["final_status"] = final_health_check["overall_status"]
        
        logger.info(
            f"Recovery attempt complete: model={model_id}, "
            f"successful={recovery_result['recovery_successful']}"
        )
        
        return recovery_result
    
    async def generate_health_report(
        self,
        model_id: str,
        endpoint_resource_name: Optional[str] = None,
        artifact_path: Optional[str] = None,
        include_history: bool = False
    ) -> Dict[str, Any]:
        """
        Generate comprehensive health report for a model deployment.
        
        Args:
            model_id: Unique model identifier
            endpoint_resource_name: Vertex AI endpoint resource name
            artifact_path: GCS path to model artifacts
            include_history: Include historical health data
            
        Returns:
            Dictionary with comprehensive health report
        """
        logger.info(f"Generating health report for model: {model_id}")
        
        # Perform current health check
        current_health = await self.perform_health_check(
            model_id=model_id,
            endpoint_resource_name=endpoint_resource_name,
            artifact_path=artifact_path,
            include_predictions_test=True
        )
        
        report = {
            "model_id": model_id,
            "report_generated_at": datetime.utcnow().isoformat(),
            "current_health": current_health,
            "summary": {
                "overall_status": current_health["overall_status"],
                "total_issues": len(current_health["issues"]),
                "critical_issues": len([
                    i for i in current_health["issues"] 
                    if i.get("severity") == ErrorSeverity.CRITICAL.value
                ]),
                "recommendations_count": len(current_health["recommendations"])
            }
        }
        
        # Add deployment information
        if endpoint_resource_name or artifact_path:
            deployment_info = await self.deployment_service.get_deployment_info(
                model_id=model_id,
                endpoint_resource_name=endpoint_resource_name,
                artifact_path=artifact_path
            )
            report["deployment_info"] = deployment_info
        
        logger.info(f"Health report generated for model: {model_id}")
        
        return report
