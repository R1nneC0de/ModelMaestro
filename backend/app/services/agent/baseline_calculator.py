"""
Baseline metrics calculation.

Calculates baseline metrics for comparison with trained models.
"""

import numpy as np
from typing import Dict
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


@dataclass
class BaselineMetrics:
    """Baseline metrics for comparison."""
    metric_name: str
    baseline_value: float
    description: str


class BaselineCalculator:
    """Calculate baseline metrics for different problem types."""
    
    @staticmethod
    def calculate_classification_baseline(y_true: np.ndarray) -> Dict[str, BaselineMetrics]:
        """
        Calculate baseline metrics for classification.
        
        Uses majority class prediction as baseline.
        
        Args:
            y_true: True labels
            
        Returns:
            Dictionary of baseline metrics
        """
        from collections import Counter
        
        # Majority class baseline
        class_counts = Counter(y_true)
        majority_class = max(class_counts, key=class_counts.get)
        majority_count = class_counts[majority_class]
        total_count = len(y_true)
        
        baseline_accuracy = majority_count / total_count
        
        baseline = {
            'accuracy': BaselineMetrics(
                metric_name='accuracy',
                baseline_value=float(baseline_accuracy),
                description=f"Majority class baseline (always predict class {majority_class})"
            )
        }
        
        # For binary classification, add random baseline
        if len(class_counts) == 2:
            baseline['random'] = BaselineMetrics(
                metric_name='random',
                baseline_value=0.5,
                description="Random guessing baseline"
            )
        
        logger.debug("classification_baseline_calculated", baseline_accuracy=baseline_accuracy)
        return baseline
    
    @staticmethod
    def calculate_regression_baseline(
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, BaselineMetrics]:
        """
        Calculate baseline metrics for regression.
        
        Uses mean prediction as baseline.
        
        Args:
            y_true: True values
            y_pred: Predicted values (for comparison)
            
        Returns:
            Dictionary of baseline metrics
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        
        # Mean baseline
        y_mean = np.mean(y_true)
        y_baseline_pred = np.full_like(y_true, y_mean)
        
        baseline_rmse = float(np.sqrt(mean_squared_error(y_true, y_baseline_pred)))
        baseline_mae = float(mean_absolute_error(y_true, y_baseline_pred))
        
        baseline = {
            'rmse': BaselineMetrics(
                metric_name='rmse',
                baseline_value=baseline_rmse,
                description=f"Mean prediction baseline (always predict {y_mean:.4f})"
            ),
            'mae': BaselineMetrics(
                metric_name='mae',
                baseline_value=baseline_mae,
                description=f"Mean prediction baseline (always predict {y_mean:.4f})"
            )
        }
        
        logger.debug(
            "regression_baseline_calculated",
            baseline_rmse=baseline_rmse,
            baseline_mae=baseline_mae
        )
        return baseline
