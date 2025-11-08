"""
Model evaluation utilities with acceptance gates.

This module provides comprehensive evaluation capabilities for trained models,
including metric calculation, baseline comparison, and acceptance threshold logic.
"""

import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass, field
import structlog

from .types import ProblemType
from .training_config import ModelConfig, TrainingOutput
from .metrics_calculator import ClassificationMetricsCalculator, RegressionMetricsCalculator
from .baseline_calculator import BaselineCalculator, BaselineMetrics
from .threshold_checker import ThresholdChecker, SanityChecker
from .evaluation_decision import (
    EvaluationDecision,
    DecisionMaker,
    ReasoningGenerator as DecisionReasoningGenerator,
    RecommendationGenerator
)

logger = structlog.get_logger()


@dataclass
class EvaluationResult:
    """
    Complete evaluation result with decision and diagnostics.
    
    Attributes:
        decision: ACCEPT or REJECT
        primary_metric_value: Value of the primary metric
        primary_metric_name: Name of the primary metric
        all_metrics: All computed metrics
        baseline_metrics: Baseline comparison metrics
        threshold_checks: Results of threshold checks
        sanity_checks: Results of sanity checks
        reasoning: Human-readable explanation
        recommendations: List of recommendations for improvement
        confidence: Confidence in the evaluation (0.0 to 1.0)
    """
    decision: EvaluationDecision
    primary_metric_value: float
    primary_metric_name: str
    all_metrics: Dict[str, float]
    baseline_metrics: Dict[str, BaselineMetrics]
    threshold_checks: Dict[str, bool]
    sanity_checks: Dict[str, bool]
    reasoning: str
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 1.0


class ModelEvaluator:
    """
    Model evaluation with acceptance gates.
    
    Evaluates trained models against acceptance thresholds without iteration.
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        logger.info("model_evaluator_initialized")
    
    def evaluate_model(
        self,
        training_output: TrainingOutput,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None,
        problem_type: Optional[ProblemType] = None
    ) -> EvaluationResult:
        """
        Evaluate a trained model against acceptance thresholds.
        
        Args:
            training_output: Training output with metrics and config
            y_true: True labels/values
            y_pred: Predicted labels/values
            y_pred_proba: Predicted probabilities (for classification)
            problem_type: Type of problem (inferred from config if not provided)
            
        Returns:
            EvaluationResult with decision and diagnostics
        """
        config = training_output.strategy_config
        if not config:
            raise ValueError("Training output must contain strategy_config")
        
        # Infer problem type if not provided
        if problem_type is None:
            problem_type = self._infer_problem_type(config)
        
        logger.info(
            "evaluating_model",
            problem_type=problem_type.value,
            primary_metric=config.primary_metric,
            architecture=config.architecture
        )
        
        # Calculate metrics based on problem type
        if problem_type in [ProblemType.CLASSIFICATION, ProblemType.TEXT_CLASSIFICATION, 
                           ProblemType.SENTIMENT_ANALYSIS]:
            metrics = ClassificationMetricsCalculator.calculate(
                y_true, y_pred, y_pred_proba
            )
            baseline = BaselineCalculator.calculate_classification_baseline(y_true)
        elif problem_type in [ProblemType.REGRESSION, ProblemType.TIME_SERIES_FORECASTING]:
            metrics = RegressionMetricsCalculator.calculate(y_true, y_pred)
            baseline = BaselineCalculator.calculate_regression_baseline(y_true, y_pred)
        else:
            raise ValueError(f"Unsupported problem type for evaluation: {problem_type}")
        
        # Check thresholds
        threshold_checks = ThresholdChecker.check_thresholds(
            metrics, config.acceptance_thresholds, baseline
        )
        
        # Perform sanity checks
        sanity_checks = SanityChecker.perform_sanity_checks(
            metrics, problem_type, y_true
        )
        
        # Make decision
        decision = DecisionMaker.make_decision(threshold_checks, sanity_checks)
        
        # Generate reasoning and recommendations
        reasoning = DecisionReasoningGenerator.generate_reasoning(
            decision, metrics, baseline, threshold_checks, sanity_checks, config
        )
        recommendations = RecommendationGenerator.generate_recommendations(
            decision, metrics, baseline, threshold_checks, config
        )
        
        primary_value = metrics.get(config.primary_metric, 0.0)
        
        logger.info(
            "evaluation_complete",
            decision=decision.value,
            primary_metric=config.primary_metric,
            primary_value=primary_value
        )
        
        return EvaluationResult(
            decision=decision,
            primary_metric_value=primary_value,
            primary_metric_name=config.primary_metric,
            all_metrics=metrics,
            baseline_metrics=baseline,
            threshold_checks=threshold_checks,
            sanity_checks=sanity_checks,
            reasoning=reasoning,
            recommendations=recommendations,
            confidence=0.95
        )

    
    def _infer_problem_type(self, config: ModelConfig) -> ProblemType:
        """Infer problem type from config."""
        architecture = config.architecture.lower()
        
        if 'clf' in architecture or 'classification' in architecture:
            return ProblemType.CLASSIFICATION
        elif 'reg' in architecture or 'regression' in architecture:
            return ProblemType.REGRESSION
        elif 'text' in architecture:
            return ProblemType.TEXT_CLASSIFICATION
        else:
            # Default based on primary metric
            if config.primary_metric in ['roc_auc', 'accuracy', 'f1', 'precision', 'recall']:
                return ProblemType.CLASSIFICATION
            else:
                return ProblemType.REGRESSION
