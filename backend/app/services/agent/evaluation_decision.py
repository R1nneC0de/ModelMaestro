"""
Evaluation decision logic and reasoning generation.

Makes ACCEPT/REJECT decisions and generates human-readable explanations.
"""

from typing import Dict, List
from enum import Enum
import structlog

from .baseline_calculator import BaselineMetrics
from .training_config import ModelConfig

logger = structlog.get_logger()


class EvaluationDecision(str, Enum):
    """Evaluation decision outcomes."""
    ACCEPT = "accept"
    REJECT = "reject"


class DecisionMaker:
    """Make evaluation decisions based on checks."""
    
    @staticmethod
    def make_decision(
        threshold_checks: Dict[str, bool],
        sanity_checks: Dict[str, bool]
    ) -> EvaluationDecision:
        """
        Make ACCEPT or REJECT decision.
        
        Args:
            threshold_checks: Results of threshold checks
            sanity_checks: Results of sanity checks
            
        Returns:
            EvaluationDecision
        """
        # All threshold checks must pass
        thresholds_passed = all(threshold_checks.values())
        
        # Most sanity checks should pass (70% threshold)
        sanity_passed = (
            sum(sanity_checks.values()) >= len(sanity_checks) * 0.7
            if sanity_checks else True
        )
        
        decision = (
            EvaluationDecision.ACCEPT
            if thresholds_passed and sanity_passed
            else EvaluationDecision.REJECT
        )
        
        logger.info(
            "decision_made",
            decision=decision.value,
            thresholds_passed=thresholds_passed,
            sanity_passed=sanity_passed
        )
        
        return decision


class ReasoningGenerator:
    """Generate human-readable reasoning for evaluation decisions."""
    
    @staticmethod
    def generate_reasoning(
        decision: EvaluationDecision,
        metrics: Dict[str, float],
        baseline: Dict[str, BaselineMetrics],
        threshold_checks: Dict[str, bool],
        sanity_checks: Dict[str, bool],
        config: ModelConfig
    ) -> str:
        """Generate reasoning text."""
        lines = []
        
        # Decision summary
        if decision == EvaluationDecision.ACCEPT:
            lines.append("✓ Model ACCEPTED - Meets all acceptance criteria")
        else:
            lines.append("✗ Model REJECTED - Does not meet acceptance criteria")
        
        lines.append("")
        lines.append("Primary Metric:")
        primary_value = metrics.get(config.primary_metric, 0.0)
        primary_threshold = config.acceptance_thresholds.get(config.primary_metric, 0.0)
        lines.append(f"  {config.primary_metric}: {primary_value:.4f} (threshold: {primary_threshold:.4f})")
        
        # Threshold checks
        lines.append("")
        lines.append("Threshold Checks:")
        for metric_name, passed in threshold_checks.items():
            status = "✓" if passed else "✗"
            value = metrics.get(metric_name, 0.0)
            threshold = config.acceptance_thresholds.get(metric_name, 0.0)
            lines.append(f"  {status} {metric_name}: {value:.4f} vs {threshold:.4f}")
        
        # Baseline comparison
        lines.append("")
        lines.append("Baseline Comparison:")
        for metric_name, baseline_info in baseline.items():
            if metric_name in metrics:
                model_value = metrics[metric_name]
                baseline_value = baseline_info.baseline_value
                improvement = ReasoningGenerator._calculate_improvement(
                    metric_name, model_value, baseline_value
                )
                lines.append(
                    f"  {metric_name}: {model_value:.4f} vs baseline {baseline_value:.4f} "
                    f"({improvement:+.1f}% improvement)"
                )
        
        # Sanity checks
        if sanity_checks:
            lines.append("")
            lines.append("Sanity Checks:")
            for check_name, passed in sanity_checks.items():
                status = "✓" if passed else "✗"
                lines.append(f"  {status} {check_name}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _calculate_improvement(
        metric_name: str,
        model_value: float,
        baseline_value: float
    ) -> float:
        """Calculate improvement percentage."""
        if baseline_value == 0:
            return 0.0
        
        if metric_name in ['rmse', 'mae', 'mse']:
            # Lower is better
            return ((baseline_value - model_value) / baseline_value) * 100
        else:
            # Higher is better
            return ((model_value - baseline_value) / baseline_value) * 100


class RecommendationGenerator:
    """Generate recommendations for model improvement."""
    
    @staticmethod
    def generate_recommendations(
        decision: EvaluationDecision,
        metrics: Dict[str, float],
        baseline: Dict[str, BaselineMetrics],
        threshold_checks: Dict[str, bool],
        config: ModelConfig
    ) -> List[str]:
        """Generate improvement recommendations."""
        if decision == EvaluationDecision.ACCEPT:
            return ["Model meets acceptance criteria and is ready for deployment"]
        
        recommendations = []
        failed_checks = [k for k, v in threshold_checks.items() if not v]
        
        if not failed_checks:
            recommendations.append(
                "Model failed sanity checks - review data quality and preprocessing"
            )
            return recommendations
        
        # Generate specific recommendations
        for metric_name in failed_checks:
            rec = RecommendationGenerator._get_metric_recommendation(
                metric_name, metrics, baseline, config
            )
            if rec:
                recommendations.append(rec)
        
        # General recommendation for multiple failures
        if len(failed_checks) > 2:
            recommendations.append(
                "Multiple metrics failed. Consider switching to AutoML for automated optimization"
            )
        
        return recommendations
    
    @staticmethod
    def _get_metric_recommendation(
        metric_name: str,
        metrics: Dict[str, float],
        baseline: Dict[str, BaselineMetrics],
        config: ModelConfig
    ) -> str:
        """Get recommendation for specific metric failure."""
        value = metrics.get(metric_name, 0.0)
        threshold = config.acceptance_thresholds.get(metric_name, 0.0)
        
        if metric_name == 'roc_auc':
            gap = threshold - value
            if gap > 0.15:
                return (
                    f"ROC-AUC is significantly below threshold ({value:.3f} vs {threshold:.3f}). "
                    "Consider: (1) Switch to AutoML, (2) Increase max_depth for XGBoost, "
                    "(3) Check data quality"
                )
            return (
                f"ROC-AUC is slightly below threshold ({value:.3f} vs {threshold:.3f}). "
                "Consider: (1) Increase n_estimators, (2) Tune learning rate"
            )
        
        elif metric_name == 'rmse':
            baseline_rmse = baseline.get('rmse')
            if baseline_rmse and value > baseline_rmse.baseline_value:
                return (
                    f"RMSE is worse than baseline ({value:.3f} vs {baseline_rmse.baseline_value:.3f}). "
                    "Model is not learning. Check: (1) Feature engineering, "
                    "(2) Data preprocessing, (3) Target distribution"
                )
            return (
                f"RMSE needs improvement ({value:.3f} vs threshold {threshold:.3f}). "
                "Consider: (1) Increase model complexity, (2) Add features, (3) Try AutoML"
            )
        
        elif metric_name in ['f1', 'precision', 'recall']:
            return (
                f"{metric_name.upper()} is below threshold ({value:.3f} vs {threshold:.3f}). "
                "For imbalanced data: (1) Adjust class weights, (2) Use resampling, "
                "(3) Tune decision threshold"
            )
        
        elif metric_name == 'r2':
            if value < 0:
                return (
                    f"R² is negative ({value:.3f}), worse than mean baseline. "
                    "Critical: (1) Check preprocessing, (2) Verify target, (3) Review features"
                )
            return (
                f"R² is low ({value:.3f} vs threshold {threshold:.3f}). "
                "Consider: (1) Add features, (2) Increase complexity, "
                "(3) Check for non-linear relationships"
            )
        
        return ""
