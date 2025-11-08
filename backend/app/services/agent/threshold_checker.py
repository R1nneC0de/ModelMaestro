"""
Threshold checking and sanity checks.

Validates model metrics against acceptance thresholds and performs sanity checks.
"""

import numpy as np
from typing import Dict
from collections import Counter
import structlog

from .types import ProblemType
from .baseline_calculator import BaselineMetrics

logger = structlog.get_logger()


class ThresholdChecker:
    """Check if metrics meet acceptance thresholds."""
    
    @staticmethod
    def check_thresholds(
        metrics: Dict[str, float],
        thresholds: Dict[str, float],
        baseline: Dict[str, BaselineMetrics]
    ) -> Dict[str, bool]:
        """
        Check if metrics meet acceptance thresholds.
        
        Args:
            metrics: Calculated metrics
            thresholds: Acceptance thresholds
            baseline: Baseline metrics for comparison
            
        Returns:
            Dictionary of threshold check results
        """
        checks = {}
        
        for metric_name, threshold_value in thresholds.items():
            metric_value = metrics.get(metric_name, 0.0)
            
            # Handle baseline-relative thresholds
            if isinstance(threshold_value, str) and 'baseline' in threshold_value:
                threshold_value = ThresholdChecker._resolve_baseline_threshold(
                    threshold_value, metric_name, baseline
                )
            
            # Check threshold based on metric type
            checks[metric_name] = ThresholdChecker._compare_metric(
                metric_name, metric_value, threshold_value
            )
            
            logger.debug(
                "threshold_check",
                metric=metric_name,
                value=metric_value,
                threshold=threshold_value,
                passed=checks[metric_name]
            )
        
        return checks
    
    @staticmethod
    def _resolve_baseline_threshold(
        threshold_expr: str,
        metric_name: str,
        baseline: Dict[str, BaselineMetrics]
    ) -> float:
        """Resolve baseline-relative threshold expression."""
        if metric_name in baseline:
            baseline_value = baseline[metric_name].baseline_value
            return eval(threshold_expr.replace('baseline', str(baseline_value)))
        return 0.0
    
    @staticmethod
    def _compare_metric(metric_name: str, value: float, threshold: float) -> bool:
        """Compare metric value against threshold."""
        # For error metrics (lower is better)
        if metric_name in ['rmse', 'mae', 'mse', 'mape']:
            return value <= threshold
        # For performance metrics (higher is better)
        return value >= threshold


class SanityChecker:
    """Perform sanity checks on model metrics."""
    
    @staticmethod
    def perform_sanity_checks(
        metrics: Dict[str, float],
        problem_type: ProblemType,
        y_true: np.ndarray
    ) -> Dict[str, bool]:
        """
        Perform sanity checks on metrics.
        
        Args:
            metrics: Calculated metrics
            problem_type: Type of problem
            y_true: True labels/values
            
        Returns:
            Dictionary of sanity check results
        """
        if problem_type in [ProblemType.CLASSIFICATION, ProblemType.TEXT_CLASSIFICATION]:
            return SanityChecker._classification_sanity_checks(metrics, y_true)
        elif problem_type in [ProblemType.REGRESSION, ProblemType.TIME_SERIES_FORECASTING]:
            return SanityChecker._regression_sanity_checks(metrics)
        return {}
    
    @staticmethod
    def _classification_sanity_checks(
        metrics: Dict[str, float],
        y_true: np.ndarray
    ) -> Dict[str, bool]:
        """Sanity checks for classification."""
        checks = {}
        
        # Check for class imbalance
        class_counts = Counter(y_true)
        imbalance_ratio = max(class_counts.values()) / min(class_counts.values())
        
        if imbalance_ratio > 4:
            # For imbalanced data, check F1, precision, recall
            checks['f1_reasonable'] = metrics.get('f1', 0.0) >= 0.3
            checks['precision_reasonable'] = metrics.get('precision', 0.0) >= 0.3
            checks['recall_reasonable'] = metrics.get('recall', 0.0) >= 0.3
        else:
            # For balanced data, less strict
            checks['f1_reasonable'] = metrics.get('f1', 0.0) >= 0.2
        
        # Check accuracy is above random
        num_classes = len(class_counts)
        random_accuracy = 1.0 / num_classes
        checks['better_than_random'] = metrics.get('accuracy', 0.0) > random_accuracy * 1.1
        
        logger.debug("classification_sanity_checks", checks=checks)
        return checks
    
    @staticmethod
    def _regression_sanity_checks(metrics: Dict[str, float]) -> Dict[str, bool]:
        """Sanity checks for regression."""
        checks = {}
        
        # Check R² is positive
        checks['r2_positive'] = metrics.get('r2', -1.0) >= 0.0
        
        # Check residuals are centered
        mean_residual = metrics.get('mean_residual', 0.0)
        std_residual = metrics.get('std_residual', 1.0)
        checks['residuals_centered'] = abs(mean_residual) < 0.1 * std_residual
        
        # Check MAE/RMSE ratio is reasonable
        mae = metrics.get('mae', 0.0)
        rmse = metrics.get('rmse', 0.0)
        if rmse > 0:
            checks['mae_rmse_ratio_reasonable'] = (mae / rmse) >= 0.5
        
        logger.debug("regression_sanity_checks", checks=checks)
        return checks
