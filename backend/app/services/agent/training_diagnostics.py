"""
Training diagnostics and failure analysis.

Provides utilities for diagnosing training failures and exceptions.
"""

import logging
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class TrainingDiagnostics:
    """Utilities for diagnosing training failures."""
    
    @staticmethod
    def diagnose_failure(job_status: Dict[str, Any], config: Any) -> str:
        """
        Diagnose training failure and provide actionable cause.
        
        Args:
            job_status: Job status information
            config: Model configuration
            
        Returns:
            Diagnostic message with probable cause
        """
        error_msg = job_status.get("error", {}).get("message", "").lower()
        
        # Schema/Read Errors
        if any(keyword in error_msg for keyword in ["schema", "delimiter", "header", "parse"]):
            return "SCHEMA_ERROR: Data format issue. Check CSV delimiter, headers, or column types."
        
        # OOM Errors
        if any(keyword in error_msg for keyword in ["memory", "oom", "resource"]):
            return f"OUT_OF_MEMORY: Insufficient memory for {config.architecture}. Consider using AutoML or reducing data size."
        
        # Training Errors
        if any(keyword in error_msg for keyword in ["convergence", "nan", "inf", "diverge"]):
            return "TRAINING_ERROR: Model failed to converge. Try different hyperparameters or algorithm."
        
        # Timeout
        if job_status.get("timeout"):
            return f"TIMEOUT: Training exceeded {settings.MAX_TRAINING_HOURS} hours. Consider reducing data size or budget."
        
        # Generic failure
        return f"TRAINING_FAILED: {error_msg}"
    
    @staticmethod
    def diagnose_exception(exception: Exception, config: Any) -> str:
        """
        Diagnose exception and provide actionable cause.
        
        Args:
            exception: Exception that occurred
            config: Model configuration
            
        Returns:
            Diagnostic message
        """
        error_msg = str(exception).lower()
        
        if "permission" in error_msg or "forbidden" in error_msg:
            return "PERMISSION_ERROR: Insufficient permissions for Vertex AI. Check service account roles."
        
        if "quota" in error_msg:
            return "QUOTA_EXCEEDED: Vertex AI quota exceeded. Request quota increase or try later."
        
        if "not found" in error_msg:
            return "RESOURCE_NOT_FOUND: Required resource not found. Check dataset URIs and bucket access."
        
        return f"EXCEPTION: {str(exception)}"
    
    @staticmethod
    def get_training_container(architecture: str) -> str:
        """
        Get Docker container URI for training.
        
        Args:
            architecture: Model architecture
            
        Returns:
            Container URI
        """
        container_map = {
            "xgboost": "gcr.io/cloud-aiplatform/training/xgboost-cpu.1-6:latest",
            "xgboost_clf": "gcr.io/cloud-aiplatform/training/xgboost-cpu.1-6:latest",
            "xgboost_reg": "gcr.io/cloud-aiplatform/training/xgboost-cpu.1-6:latest",
            "linear_regression": "gcr.io/cloud-aiplatform/training/sklearn-cpu.1-0:latest",
            "logistic_regression": "gcr.io/cloud-aiplatform/training/sklearn-cpu.1-0:latest",
            "text_dnn": "gcr.io/cloud-aiplatform/training/tf-cpu.2-11:latest"
        }
        
        return container_map.get(
            architecture,
            "gcr.io/cloud-aiplatform/training/sklearn-cpu.1-0:latest"
        )
    
    @staticmethod
    def get_training_script(architecture: str) -> str:
        """
        Get training script path for architecture.
        
        Args:
            architecture: Model architecture
            
        Returns:
            Script path
        """
        script_map = {
            "xgboost": "/app/train_xgboost.py",
            "xgboost_clf": "/app/train_xgboost.py",
            "xgboost_reg": "/app/train_xgboost.py",
            "linear_regression": "/app/train_linear.py",
            "logistic_regression": "/app/train_logistic.py",
            "text_dnn": "/app/train_text_dnn.py"
        }
        
        return script_map.get(architecture, "/app/train.py")
    
    @staticmethod
    def get_default_objective(problem_analysis: Any) -> str:
        """
        Get default optimization objective based on problem type.
        
        Args:
            problem_analysis: Problem analysis
            
        Returns:
            Optimization objective string
        """
        from app.services.agent.types import ProblemType
        
        if problem_analysis.problem_type == ProblemType.REGRESSION:
            return "minimize-rmse"
        elif problem_analysis.problem_type == ProblemType.CLASSIFICATION:
            if problem_analysis.num_classes and problem_analysis.num_classes == 2:
                return "maximize-au-roc"
            else:
                return "maximize-au-prc"
        else:
            return "maximize-au-roc"
