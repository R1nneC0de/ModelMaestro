"""
Agent services module for autonomous ML pipeline orchestration.

This module provides intelligent components for analyzing problems,
processing data, selecting models, and managing training workflows.
"""

from app.services.agent.analyzer import ProblemAnalyzer
from app.services.agent.confidence_scorer import ConfidenceScorer
from app.services.agent.data_processor import DataProcessor
from app.services.agent.data_quality import (
    DataQualityIssue,
    DataQualityReport,
    DataQualityValidator,
    MissingValueStrategy,
    ProcessingStrategy,
)
from app.services.agent.data_splitter import DataSplit, DataSplitter
from app.services.agent.data_type_detector import DataTypeDetector
from app.services.agent.evaluator import (
    ModelEvaluator,
    EvaluationResult,
)
from app.services.agent.evaluation_decision import EvaluationDecision
from app.services.agent.baseline_calculator import BaselineMetrics
from app.services.agent.evaluation_report import EvaluationReportGenerator
from app.services.agent.metrics_calculator import (
    ClassificationMetricsCalculator,
    RegressionMetricsCalculator,
)
from app.services.agent.threshold_checker import ThresholdChecker, SanityChecker
from app.services.agent.plot_generator import (
    ClassificationPlotGenerator,
    RegressionPlotGenerator,
)
from app.services.agent.report_formatter import (
    MarkdownReportFormatter,
    HTMLReportFormatter,
    JSONReportFormatter,
)
from app.services.agent.exceptions import (
    GeminiAPIError,
    GeminiClientError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiValidationError,
)
from app.services.agent.feature_engineer import FeatureEngineer, ProcessedData
from app.services.agent.gemini_client import GeminiClient
from app.services.agent.reasoning_generator import ReasoningGenerator
from app.services.agent.types import DataType, ProblemAnalysis, ProblemType

__all__ = [
    "ProblemAnalyzer",
    "GeminiClient",
    "ConfidenceScorer",
    "DataTypeDetector",
    "ReasoningGenerator",
    "DataProcessor",
    "DataQualityValidator",
    "DataQualityReport",
    "DataQualityIssue",
    "ProcessingStrategy",
    "MissingValueStrategy",
    "DataSplitter",
    "DataSplit",
    "FeatureEngineer",
    "ProcessedData",
    "ModelEvaluator",
    "EvaluationResult",
    "EvaluationDecision",
    "BaselineMetrics",
    "EvaluationReportGenerator",
    "ClassificationMetricsCalculator",
    "RegressionMetricsCalculator",
    "ThresholdChecker",
    "SanityChecker",
    "ClassificationPlotGenerator",
    "RegressionPlotGenerator",
    "MarkdownReportFormatter",
    "HTMLReportFormatter",
    "JSONReportFormatter",
    "GeminiClientError",
    "GeminiAPIError",
    "GeminiRateLimitError",
    "GeminiTimeoutError",
    "GeminiValidationError",
    "ProblemAnalysis",
    "ProblemType",
    "DataType",
]
