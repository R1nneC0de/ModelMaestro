"""
Model selection type definitions and enums.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class ModelArchitecture(str, Enum):
    """Supported model architectures."""
    # Tabular Models
    AUTOML_TABULAR = "automl_tabular"
    XGBOOST = "xgboost"
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"

    # Deep Learning Models
    FEEDFORWARD_NN = "feedforward_nn"
    WIDE_AND_DEEP = "wide_and_deep"
    TABNET = "tabnet"

    # Text Models
    AUTOML_TEXT = "automl_text"
    BERT = "bert"
    DISTILBERT = "distilbert"

    # Image Models
    AUTOML_IMAGE = "automl_image"
    RESNET = "resnet"
    EFFICIENTNET = "efficientnet"

    # Time Series Models
    AUTOML_FORECASTING = "automl_forecasting"
    ARIMA = "arima"
    LSTM = "lstm"

    # Other
    CUSTOM = "custom"


class TrainingStrategy(str, Enum):
    """Training strategy to use."""
    AUTOML = "automl"  # Fully automated with Vertex AI AutoML
    CUSTOM = "custom"  # Custom training job with specified parameters
    HYBRID = "hybrid"  # AutoML with custom preprocessing


class VertexAIProduct(str, Enum):
    """Vertex AI product to use for training."""
    AUTOML_TABLES = "automl_tables"
    AUTOML_TEXT = "automl_text"
    AUTOML_IMAGE = "automl_image"
    AUTOML_VIDEO = "automl_video"
    AUTOML_FORECASTING = "automl_forecasting"
    CUSTOM_TRAINING = "custom_training"
    MATCHING_ENGINE = "matching_engine"


@dataclass
class HyperparameterConfig:
    """Hyperparameter configuration for a model."""

    # Common parameters
    learning_rate: float = 0.01
    batch_size: int = 32
    max_iterations: int = 1000
    early_stopping_patience: int = 10

    # Model-specific parameters
    model_specific: Dict[str, Any] = field(default_factory=dict)

    # Search space for AutoML
    search_space: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ModelRecommendation:
    """
    Complete model recommendation with architecture, hyperparameters,
    and training strategy.
    """
    # Primary recommendation
    architecture: ModelArchitecture
    training_strategy: TrainingStrategy
    vertex_product: VertexAIProduct

    # Configuration
    hyperparameters: HyperparameterConfig

    # Alternative options
    alternatives: List['ModelRecommendation'] = field(default_factory=list)

    # Decision metadata
    confidence: float = 0.0  # 0.0 to 1.0
    reasoning: str = ""
    estimated_training_time_minutes: Optional[int] = None
    estimated_cost_usd: Optional[float] = None

    # Additional context
    requires_gpu: bool = False
    supports_incremental_training: bool = False
    interpretability_score: float = 0.5  # 0.0 (black box) to 1.0 (interpretable)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API."""
        return {
            "architecture": self.architecture.value,
            "training_strategy": self.training_strategy.value,
            "vertex_product": self.vertex_product.value,
            "hyperparameters": {
                "learning_rate": self.hyperparameters.learning_rate,
                "batch_size": self.hyperparameters.batch_size,
                "max_iterations": self.hyperparameters.max_iterations,
                "early_stopping_patience": self.hyperparameters.early_stopping_patience,
                "model_specific": self.hyperparameters.model_specific,
                "search_space": self.hyperparameters.search_space,
            },
            "alternatives": [alt.to_dict() for alt in self.alternatives] if self.alternatives else [],
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "estimated_training_time_minutes": self.estimated_training_time_minutes,
            "estimated_cost_usd": self.estimated_cost_usd,
            "requires_gpu": self.requires_gpu,
            "supports_incremental_training": self.supports_incremental_training,
            "interpretability_score": self.interpretability_score,
        }


@dataclass
class DatasetProfile:
    """
    Dataset profile for model selection decisions.
    """
    num_samples: int
    num_features: int
    num_classes: Optional[int] = None

    # Feature analysis
    num_numeric_features: int = 0
    num_categorical_features: int = 0
    num_text_features: int = 0
    num_datetime_features: int = 0

    # Data quality
    missing_value_ratio: float = 0.0
    class_imbalance_ratio: Optional[float] = None  # ratio of smallest to largest class

    # Complexity indicators
    has_high_cardinality_categoricals: bool = False
    has_sparse_features: bool = False
    dimensionality_ratio: float = 0.0  # num_features / num_samples

    # Resource constraints
    dataset_size_mb: float = 0.0
    estimated_memory_gb: float = 0.0
