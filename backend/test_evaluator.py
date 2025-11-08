"""
Simple test for model evaluator functionality.
"""

import numpy as np
from app.services.agent.evaluator import ModelEvaluator, EvaluationDecision
from app.services.agent.types import ProblemType
from app.services.agent.training_config import ModelConfig, TrainingOutput, SplitConfig


def test_classification_evaluation():
    """Test classification model evaluation."""
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    # Binary classification with good performance
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
        hyperparameters={"max_depth": 6, "n_estimators": 100},
        split_config=SplitConfig(),
        acceptance_thresholds={
            "roc_auc": 0.70,
            "f1": 0.60,
            "precision": 0.50,
            "recall": 0.50
        },
        primary_metric="roc_auc",
        reasoning="Test model",
        confidence=0.9
    )
    
    training_output = TrainingOutput(
        metrics={},
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
    
    # Assertions
    assert result.decision in [EvaluationDecision.ACCEPT, EvaluationDecision.REJECT]
    assert result.primary_metric_name == "roc_auc"
    assert "roc_auc" in result.all_metrics
    assert "accuracy" in result.all_metrics
    assert "f1" in result.all_metrics
    assert len(result.threshold_checks) > 0
    assert len(result.reasoning) > 0
    
    print(f"✓ Classification evaluation test passed")
    print(f"  Decision: {result.decision.value}")
    print(f"  ROC-AUC: {result.all_metrics['roc_auc']:.4f}")
    print(f"  Accuracy: {result.all_metrics['accuracy']:.4f}")
    print(f"  F1: {result.all_metrics['f1']:.4f}")


def test_regression_evaluation():
    """Test regression model evaluation."""
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    # Regression with reasonable performance
    y_true = np.random.randn(n_samples) * 10 + 50
    y_pred = y_true + np.random.randn(n_samples) * 3  # Add some noise
    
    # Create config
    config = ModelConfig(
        architecture="xgboost_reg",
        vertex_ai_type="custom",
        hyperparameters={"max_depth": 6, "n_estimators": 100},
        split_config=SplitConfig(),
        acceptance_thresholds={
            "rmse": 5.0,
            "r2": 0.5
        },
        primary_metric="rmse",
        reasoning="Test model",
        confidence=0.9
    )
    
    training_output = TrainingOutput(
        metrics={},
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
    
    # Assertions
    assert result.decision in [EvaluationDecision.ACCEPT, EvaluationDecision.REJECT]
    assert result.primary_metric_name == "rmse"
    assert "rmse" in result.all_metrics
    assert "mae" in result.all_metrics
    assert "r2" in result.all_metrics
    assert len(result.threshold_checks) > 0
    assert len(result.reasoning) > 0
    
    print(f"✓ Regression evaluation test passed")
    print(f"  Decision: {result.decision.value}")
    print(f"  RMSE: {result.all_metrics['rmse']:.4f}")
    print(f"  MAE: {result.all_metrics['mae']:.4f}")
    print(f"  R²: {result.all_metrics['r2']:.4f}")


if __name__ == "__main__":
    print("Testing Model Evaluator...")
    print()
    test_classification_evaluation()
    print()
    test_regression_evaluation()
    print()
    print("✓ All tests passed!")
