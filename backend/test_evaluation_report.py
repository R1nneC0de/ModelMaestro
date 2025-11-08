"""
Simple test for evaluation report generator.
"""

import numpy as np
from app.services.agent.evaluator import ModelEvaluator
from app.services.agent.evaluation_report import EvaluationReportGenerator
from app.services.agent.types import ProblemType
from app.services.agent.training_config import ModelConfig, TrainingOutput, SplitConfig


def test_classification_report():
    """Test classification report generation."""
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    y_true = np.random.randint(0, 2, n_samples)
    y_pred_proba = np.random.rand(n_samples, 2)
    y_pred_proba[:, 1] = np.where(y_true == 1, 
                                   np.random.uniform(0.6, 0.95, n_samples),
                                   np.random.uniform(0.05, 0.4, n_samples))
    y_pred_proba[:, 0] = 1 - y_pred_proba[:, 1]
    y_pred = (y_pred_proba[:, 1] > 0.5).astype(int)
    
    # Create config
    config = ModelConfig(
        architecture="xgboost_clf",
        vertex_ai_type="custom",
        hyperparameters={"max_depth": 6},
        acceptance_thresholds={"roc_auc": 0.70, "f1": 0.60},
        primary_metric="roc_auc"
    )
    
    training_output = TrainingOutput(
        strategy_config=config,
        training_duration_seconds=100.0,
        job_id="test_job_123"
    )
    
    # Evaluate
    evaluator = ModelEvaluator()
    result = evaluator.evaluate_model(
        training_output=training_output,
        y_true=y_true,
        y_pred=y_pred,
        y_pred_proba=y_pred_proba,
        problem_type=ProblemType.CLASSIFICATION
    )
    
    # Test plot generation
    from app.services.agent.plot_generator import ClassificationPlotGenerator
    plots = ClassificationPlotGenerator.generate_plots(y_true, y_pred, y_pred_proba)
    assert len(plots) > 0
    assert 'confusion_matrix' in plots
    print(f"✓ Generated {len(plots)} classification plots")
    
    # Test markdown report
    from app.services.agent.report_formatter import MarkdownReportFormatter
    markdown = MarkdownReportFormatter.format(
        result, training_output, ProblemType.CLASSIFICATION, plots
    )
    assert len(markdown) > 0
    assert "Model Evaluation Report" in markdown
    assert result.decision.value.upper() in markdown
    print(f"✓ Generated markdown report ({len(markdown)} chars)")
    
    # Test HTML report
    from app.services.agent.report_formatter import HTMLReportFormatter
    html = HTMLReportFormatter.format(
        result, training_output, ProblemType.CLASSIFICATION, plots
    )
    assert len(html) > 0
    assert "<!DOCTYPE html>" in html
    assert result.decision.value.upper() in html
    print(f"✓ Generated HTML report ({len(html)} chars)")
    
    # Test JSON summary
    from app.services.agent.report_formatter import JSONReportFormatter
    json_summary = JSONReportFormatter.format(result, training_output)
    assert json_summary["decision"] == result.decision.value
    assert "primary_metric" in json_summary
    assert "all_metrics" in json_summary
    print(f"✓ Generated JSON summary")


def test_regression_report():
    """Test regression report generation."""
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    y_true = np.random.randn(n_samples) * 10 + 50
    y_pred = y_true + np.random.randn(n_samples) * 3
    
    # Create config
    config = ModelConfig(
        architecture="xgboost_reg",
        vertex_ai_type="custom",
        acceptance_thresholds={"rmse": 5.0, "r2": 0.5},
        primary_metric="rmse"
    )
    
    training_output = TrainingOutput(
        strategy_config=config,
        training_duration_seconds=100.0,
        job_id="test_job_456"
    )
    
    # Evaluate
    evaluator = ModelEvaluator()
    result = evaluator.evaluate_model(
        training_output=training_output,
        y_true=y_true,
        y_pred=y_pred,
        problem_type=ProblemType.REGRESSION
    )
    
    # Test plot generation
    from app.services.agent.plot_generator import RegressionPlotGenerator
    plots = RegressionPlotGenerator.generate_plots(y_true, y_pred)
    assert len(plots) > 0
    assert 'residual_plot' in plots
    assert 'predicted_vs_actual' in plots
    print(f"✓ Generated {len(plots)} regression plots")
    
    # Test markdown report
    from app.services.agent.report_formatter import MarkdownReportFormatter
    markdown = MarkdownReportFormatter.format(
        result, training_output, ProblemType.REGRESSION, plots
    )
    assert len(markdown) > 0
    assert "RMSE" in markdown or "rmse" in markdown
    print(f"✓ Generated markdown report ({len(markdown)} chars)")


if __name__ == "__main__":
    print("Testing Evaluation Report Generator...")
    print()
    test_classification_report()
    print()
    test_regression_report()
    print()
    print("✓ All report tests passed!")
