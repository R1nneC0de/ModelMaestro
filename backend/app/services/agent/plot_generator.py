"""
Plot generation for evaluation reports.

Generates visualization plots for classification and regression models.
"""

import io
from typing import Dict, Optional
import numpy as np
import structlog

logger = structlog.get_logger()


class ClassificationPlotGenerator:
    """Generate plots for classification models."""
    
    @staticmethod
    def generate_plots(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None
    ) -> Dict[str, bytes]:
        """Generate all classification plots."""
        plots = {}
        
        plots.update(ClassificationPlotGenerator._generate_confusion_matrix(y_true, y_pred))
        
        if y_pred_proba is not None:
            plots.update(ClassificationPlotGenerator._generate_roc_curve(y_true, y_pred_proba))
            plots.update(ClassificationPlotGenerator._generate_pr_curve(y_true, y_pred_proba))
        
        return plots
    
    @staticmethod
    def _generate_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, bytes]:
        """Generate confusion matrix plot."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
            
            cm = confusion_matrix(y_true, y_pred)
            fig, ax = plt.subplots(figsize=(8, 6))
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp.plot(ax=ax, cmap='Blues')
            ax.set_title('Confusion Matrix')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            result = {'confusion_matrix': buf.getvalue()}
            plt.close(fig)
            return result
        except Exception as e:
            logger.warning("failed_to_generate_confusion_matrix", error=str(e))
            return {}
    
    @staticmethod
    def _generate_roc_curve(y_true: np.ndarray, y_pred_proba: np.ndarray) -> Dict[str, bytes]:
        """Generate ROC curve plot."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from sklearn.metrics import roc_curve, auc
            
            num_classes = len(np.unique(y_true))
            if num_classes != 2:
                return {}
            
            # Binary classification
            if y_pred_proba.ndim == 2:
                y_pred_proba_binary = y_pred_proba[:, 1]
            else:
                y_pred_proba_binary = y_pred_proba
            
            fpr, tpr, _ = roc_curve(y_true, y_pred_proba_binary)
            roc_auc = auc(fpr, tpr)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(fpr, tpr, color='darkorange', lw=2,
                   label=f'ROC curve (AUC = {roc_auc:.3f})')
            ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                   label='Random classifier')
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
            ax.set_title('ROC Curve')
            ax.legend(loc="lower right")
            ax.grid(alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            result = {'roc_curve': buf.getvalue()}
            plt.close(fig)
            return result
        except Exception as e:
            logger.warning("failed_to_generate_roc_curve", error=str(e))
            return {}
    
    @staticmethod
    def _generate_pr_curve(y_true: np.ndarray, y_pred_proba: np.ndarray) -> Dict[str, bytes]:
        """Generate precision-recall curve plot."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from sklearn.metrics import precision_recall_curve
            
            num_classes = len(np.unique(y_true))
            if num_classes != 2:
                return {}
            
            if y_pred_proba.ndim == 2:
                y_pred_proba_binary = y_pred_proba[:, 1]
            else:
                y_pred_proba_binary = y_pred_proba
            
            precision, recall, _ = precision_recall_curve(y_true, y_pred_proba_binary)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(recall, precision, color='darkorange', lw=2)
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('Recall')
            ax.set_ylabel('Precision')
            ax.set_title('Precision-Recall Curve')
            ax.grid(alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            result = {'precision_recall_curve': buf.getvalue()}
            plt.close(fig)
            return result
        except Exception as e:
            logger.warning("failed_to_generate_pr_curve", error=str(e))
            return {}


class RegressionPlotGenerator:
    """Generate plots for regression models."""
    
    @staticmethod
    def generate_plots(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, bytes]:
        """Generate all regression plots."""
        plots = {}
        
        plots.update(RegressionPlotGenerator._generate_residual_plot(y_true, y_pred))
        plots.update(RegressionPlotGenerator._generate_pred_vs_actual(y_true, y_pred))
        plots.update(RegressionPlotGenerator._generate_residual_distribution(y_true, y_pred))
        
        return plots
    
    @staticmethod
    def _generate_residual_plot(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, bytes]:
        """Generate residual plot."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            residuals = y_true - y_pred
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(y_pred, residuals, alpha=0.5, s=20)
            ax.axhline(y=0, color='r', linestyle='--', linewidth=2)
            ax.set_xlabel('Predicted Values')
            ax.set_ylabel('Residuals')
            ax.set_title('Residual Plot')
            ax.grid(alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            result = {'residual_plot': buf.getvalue()}
            plt.close(fig)
            return result
        except Exception as e:
            logger.warning("failed_to_generate_residual_plot", error=str(e))
            return {}
    
    @staticmethod
    def _generate_pred_vs_actual(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, bytes]:
        """Generate predicted vs actual plot."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.scatter(y_true, y_pred, alpha=0.5, s=20)
            
            # Perfect prediction line
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            ax.plot([min_val, max_val], [min_val, max_val],
                   'r--', linewidth=2, label='Perfect prediction')
            
            ax.set_xlabel('Actual Values')
            ax.set_ylabel('Predicted Values')
            ax.set_title('Predicted vs Actual')
            ax.legend()
            ax.grid(alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            result = {'predicted_vs_actual': buf.getvalue()}
            plt.close(fig)
            return result
        except Exception as e:
            logger.warning("failed_to_generate_pred_vs_actual", error=str(e))
            return {}
    
    @staticmethod
    def _generate_residual_distribution(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, bytes]:
        """Generate residual distribution plot."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            residuals = y_true - y_pred
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(residuals, bins=50, edgecolor='black', alpha=0.7)
            ax.axvline(x=0, color='r', linestyle='--', linewidth=2)
            ax.set_xlabel('Residuals')
            ax.set_ylabel('Frequency')
            ax.set_title('Residual Distribution')
            ax.grid(alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            result = {'residual_distribution': buf.getvalue()}
            plt.close(fig)
            return result
        except Exception as e:
            logger.warning("failed_to_generate_residual_dist", error=str(e))
            return {}
