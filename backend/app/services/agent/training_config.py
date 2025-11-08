"""
Training configuration data structures.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from enum import Enum


class TrainingState(str, Enum):
    """Training job states."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class SplitConfig:
    """Data split configuration."""
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    random_seed: int = 42
    stratify: bool = True
    split_type: str = "random"
    no_shuffle: bool = False


@dataclass
class ModelConfig:
    """
    Complete model configuration for training.
    
    This represents the single-model strategy determined by the Model Selector.
    """
    architecture: str
    vertex_ai_type: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    split_config: SplitConfig = field(default_factory=SplitConfig)
    acceptance_thresholds: Dict[str, float] = field(default_factory=dict)
    primary_metric: str = "roc_auc"
    reasoning: str = ""
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "architecture": self.architecture,
            "vertex_ai_type": self.vertex_ai_type,
            "hyperparameters": self.hyperparameters,
            "split_config": asdict(self.split_config),
            "acceptance_thresholds": self.acceptance_thresholds,
            "primary_metric": self.primary_metric,
            "reasoning": self.reasoning,
            "confidence": self.confidence
        }


@dataclass
class TrainingOutput:
    """Standard output format for all training jobs."""
    metrics: Dict[str, float] = field(default_factory=dict)
    primary_metric_value: float = 0.0
    model_uri: str = ""
    prep_uri: str = ""
    report_uri: str = ""
    step3_summary_hash: str = ""
    strategy_config: Optional[ModelConfig] = None
    package_versions: Dict[str, str] = field(default_factory=dict)
    random_seed: int = 42
    training_duration_seconds: float = 0.0
    job_id: str = ""
    job_resource_name: str = ""
    state: str = TrainingState.QUEUED.value
    error_message: Optional[str] = None
    error_cause: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "metrics": self.metrics,
            "primary_metric_value": self.primary_metric_value,
            "model_uri": self.model_uri,
            "prep_uri": self.prep_uri,
            "report_uri": self.report_uri,
            "step3_summary_hash": self.step3_summary_hash,
            "strategy_config": self.strategy_config.to_dict() if self.strategy_config else None,
            "package_versions": self.package_versions,
            "random_seed": self.random_seed,
            "training_duration_seconds": self.training_duration_seconds,
            "job_id": self.job_id,
            "job_resource_name": self.job_resource_name,
            "state": self.state
        }
        
        if self.error_message:
            result["error_message"] = self.error_message
            result["error_cause"] = self.error_cause
        
        return result
