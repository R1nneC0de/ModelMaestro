"""
Metrics calculation utilities.

Provides focused metric calculation for different problem types.
"""

import numpy as np
from typing import Dict
import structlog

logger = structlog.get_logger()


class ClassificationMetricsCalculator:
    """Calculate classification metrics."""
    
    @staticmethod
    def calculate(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None
    ) -> Dict[str, float]:
        """
        Calculate classification metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            roc_auc_score, confusion_matrix
        )
        
        metrics = {}
        
        # Basic metrics
        metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
        
        # Handle binary vs multiclass
        num_classes = len(np.unique(y_true))
        average = 'binary' if num_classes == 2 else 'weighted'
        
        metrics['precision'] = float(precision_score(
            y_true, y_pred, average=average, zero_division=0
        ))
        metrics['recall'] = float(recall_score(
            y_true, y_pred, average=average, zero_division=0
        ))
        metrics['f1'] = float(f1_score(
            y_true, y_pred, average=average, zero_division=0
        ))
        
        # ROC-AUC (if probabilities provided)
        if y_pred_proba is not None:
            metrics['roc_auc'] = ClassificationMetricsCalculator._calculate_roc_auc(
                y_true, y_pred_proba, num_classes
            )
        
        # Confusion matrix stats
        ClassificationMetricsCalculator._add_confusion_matrix_stats(
            metrics, y_true, y_pred, num_classes
        )
        
        logger.debug("classification_metrics_calculated", metrics=metrics)
        return metrics
    
    @staticmethod
    def _calculate_roc_auc(
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        num_classes: int
    ) -> float:
        """Calculate ROC-AUC score."""
        from sklearn.metrics import roc_auc_score
        
        try:
            if num_classes == 2:
                # Binary classification
                if y_pred_proba.ndim == 2:
                    y_pred_proba = y_pred_proba[:, 1]
                return float(roc_auc_score(y_true, y_pred_proba))
            else:
                # Multiclass
                return float(roc_auc_score(
                    y_true, y_pred_proba, multi_class='ovr', average='weighted'
                ))
        except Exception as e:
            logger.warning("failed_to_calculate_roc_auc", error=str(e))
            return 0.0
    
    @staticmethod
    def _add_confusion_matrix_stats(
        metrics: Dict[str, float],
        y_true: np.ndarray,
        y_pred: np.ndarray,
        num_classes: int
    ):
        """Add confusion matrix statistics to metrics."""
        from sklearn.metrics import confusion_matrix
        
        cm = confusion_matrix(y_true, y_pred)
        if num_classes == 2:
            tn, fp, fn, tp = cm.ravel()
            metrics['true_positives'] = float(tp)
            metrics['true_negatives'] = float(tn)
            metrics['false_positives'] = float(fp)
            metrics['false_negatives'] = float(fn)
            
            # Specificity
            if (tn + fp) > 0:
                metrics['specificity'] = float(tn / (tn + fp))


class RegressionMetricsCalculator:
    """Calculate regression metrics."""
    
    @staticmethod
    def calculate(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate regression metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import (
            mean_squared_error, mean_absolute_error, r2_score,
            mean_absolute_percentage_error
        )
        
        metrics = {}
        
        # Core metrics
        metrics['rmse'] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        metrics['mae'] = float(mean_absolute_error(y_true, y_pred))
        metrics['r2'] = float(r2_score(y_true, y_pred))
        metrics['mse'] = float(mean_squared_error(y_true, y_pred))
        
        # MAPE (if no zeros in y_true)
        if not np.any(y_true == 0):
            try:
                metrics['mape'] = float(mean_absolute_percentage_error(y_true, y_pred))
            except Exception as e:
                logger.warning("failed_to_calculate_mape", error=str(e))
        
        # Residual statistics
        residuals = y_true - y_pred
        metrics['mean_residual'] = float(np.mean(residuals))
        metrics['std_residual'] = float(np.std(residuals))
        metrics['max_residual'] = float(np.max(np.abs(residuals)))
        
        logger.debug("regression_metrics_calculated", metrics=metrics)
        return metrics
