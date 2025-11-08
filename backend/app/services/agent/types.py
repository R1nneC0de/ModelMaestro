"""
Type definitions and enums for the agent services.

This module defines common types, enums, and data classes used across
the agent components for type safety and consistency.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProblemType(str, Enum):
    """Types of ML problems the platform can handle."""

    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    OBJECT_DETECTION = "object_detection"
    IMAGE_SEGMENTATION = "image_segmentation"
    TEXT_CLASSIFICATION = "text_classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    TIME_SERIES_FORECASTING = "time_series_forecasting"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"
    UNKNOWN = "unknown"


class DataType(str, Enum):
    """Types of data the platform can process."""

    IMAGE = "image"
    TEXT = "text"
    TABULAR = "tabular"
    TIME_SERIES = "time_series"
    MULTIMODAL = "multimodal"
    UNKNOWN = "unknown"


@dataclass
class ProblemAnalysis:
    """
    Result of problem analysis containing all insights about the ML problem.

    Attributes:
        problem_type: The identified type of ML problem
        data_type: The type of data being processed
        domain: The domain/industry of the problem
        suggested_metrics: List of recommended evaluation metrics
        complexity_score: Problem complexity from 0.0 (simple) to 1.0 (complex)
        reasoning: Human-readable explanation of the analysis
        confidence: Confidence score from 0.0 to 1.0
        is_labeled: Whether the data has labels
        num_classes: Number of classes for classification problems
        target_variable: Target variable name for regression/forecasting
        additional_insights: Additional problem-specific insights
    """

    problem_type: ProblemType
    data_type: DataType
    domain: str
    suggested_metrics: List[str]
    complexity_score: float
    reasoning: str
    confidence: float
    is_labeled: bool
    num_classes: Optional[int] = None
    target_variable: Optional[str] = None
    additional_insights: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate fields after initialization."""
        if not 0.0 <= self.complexity_score <= 1.0:
            raise ValueError("complexity_score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
