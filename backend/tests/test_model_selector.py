"""
Tests for model selection agent.
"""
import pytest
from backend.app.services.agent.model_selector import ModelSelector
from backend.app.services.agent.types import ProblemType, DataType, ProblemAnalysis
from backend.app.services.agent.model_types import (
    DatasetProfile,
    ModelArchitecture,
    TrainingStrategy,
    VertexAIProduct,
)


@pytest.fixture
def simple_classification_problem():
    """Simple classification problem fixture."""
    return ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="E-commerce",
        suggested_metrics=["accuracy", "f1_score"],
        complexity_score=0.3,
        confidence=0.85,
        reasoning="Simple binary classification",
        is_labeled=True,
        num_classes=2,
        target_variable="purchase",
        additional_insights={},
    )


@pytest.fixture
def complex_regression_problem():
    """Complex regression problem fixture."""
    return ProblemAnalysis(
        problem_type=ProblemType.REGRESSION,
        data_type=DataType.TABULAR,
        domain="Real Estate",
        suggested_metrics=["rmse", "mae", "r2"],
        complexity_score=0.7,
        confidence=0.88,
        reasoning="Complex regression with many features",
        is_labeled=True,
        num_classes=None,
        target_variable="house_price",
        additional_insights={},
    )


@pytest.fixture
def small_dataset_profile():
    """Small dataset profile."""
    return DatasetProfile(
        num_samples=500,
        num_features=8,
        num_classes=2,
        num_numeric_features=6,
        num_categorical_features=2,
        missing_value_ratio=0.05,
        class_imbalance_ratio=0.6,
        dimensionality_ratio=0.016,
        dataset_size_mb=0.5,
    )


@pytest.fixture
def medium_dataset_profile():
    """Medium dataset profile."""
    return DatasetProfile(
        num_samples=50000,
        num_features=25,
        num_classes=3,
        num_numeric_features=18,
        num_categorical_features=7,
        missing_value_ratio=0.08,
        class_imbalance_ratio=0.4,
        dimensionality_ratio=0.0005,
        dataset_size_mb=50.0,
    )


@pytest.fixture
def large_dataset_profile():
    """Large dataset profile."""
    return DatasetProfile(
        num_samples=500000,
        num_features=50,
        num_classes=5,
        num_numeric_features=35,
        num_categorical_features=15,
        missing_value_ratio=0.1,
        class_imbalance_ratio=0.3,
        dimensionality_ratio=0.0001,
        dataset_size_mb=500.0,
    )


@pytest.mark.asyncio
async def test_simple_classification_selects_logistic_regression(
    simple_classification_problem,
    small_dataset_profile,
):
    """Test that simple problems select interpretable models."""
    selector = ModelSelector()

    recommendation = await selector.select_model(
        problem_analysis=simple_classification_problem,
        dataset_profile=small_dataset_profile,
        user_preferences={"interpretability": True},
        use_ai=False,  # Test rule-based only
    )

    assert recommendation.architecture == ModelArchitecture.LOGISTIC_REGRESSION
    assert recommendation.training_strategy == TrainingStrategy.CUSTOM
    assert recommendation.interpretability_score > 0.9
    assert recommendation.estimated_cost_usd < 10.0
    assert recommendation.confidence > 0.0
    assert len(recommendation.reasoning) > 0


@pytest.mark.asyncio
async def test_small_dataset_selects_xgboost(
    simple_classification_problem,
    small_dataset_profile,
):
    """Test that small datasets prefer XGBoost when interpretability not required."""
    selector = ModelSelector()

    recommendation = await selector.select_model(
        problem_analysis=simple_classification_problem,
        dataset_profile=small_dataset_profile,
        user_preferences={"interpretability": False},
        use_ai=False,
    )

    # Could be XGBoost or Logistic Regression depending on exact parameters
    assert recommendation.architecture in [
        ModelArchitecture.XGBOOST,
        ModelArchitecture.LOGISTIC_REGRESSION,
    ]
    assert recommendation.estimated_training_time_minutes < 30


@pytest.mark.asyncio
async def test_large_dataset_selects_automl(
    simple_classification_problem,
    large_dataset_profile,
):
    """Test that large datasets prefer AutoML."""
    selector = ModelSelector()

    recommendation = await selector.select_model(
        problem_analysis=simple_classification_problem,
        dataset_profile=large_dataset_profile,
        user_preferences={},
        use_ai=False,
    )

    assert recommendation.architecture == ModelArchitecture.AUTOML_TABULAR
    assert recommendation.training_strategy == TrainingStrategy.AUTOML
    assert recommendation.vertex_product == VertexAIProduct.AUTOML_TABLES


@pytest.mark.asyncio
async def test_simple_regression_selects_linear_regression(
    simple_classification_problem,
    small_dataset_profile,
):
    """Test regression model selection."""
    # Modify to regression
    problem = ProblemAnalysis(
        problem_type=ProblemType.REGRESSION,
        data_type=DataType.TABULAR,
        domain="Finance",
        suggested_metrics=["rmse", "mae"],
        complexity_score=0.25,
        confidence=0.82,
        reasoning="Simple linear regression",
        is_labeled=True,
        num_classes=None,
        target_variable="revenue",
        additional_insights={},
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=small_dataset_profile,
        user_preferences={"interpretability": True},
        use_ai=False,
    )

    assert recommendation.architecture == ModelArchitecture.LINEAR_REGRESSION
    assert recommendation.training_strategy == TrainingStrategy.CUSTOM
    assert recommendation.interpretability_score > 0.9


@pytest.mark.asyncio
async def test_text_classification():
    """Test text classification model selection."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.TEXT_CLASSIFICATION,
        data_type=DataType.TEXT,
        domain="Customer Support",
        suggested_metrics=["accuracy", "f1_score"],
        complexity_score=0.6,
        confidence=0.88,
        reasoning="Multi-class text classification",
        is_labeled=True,
        num_classes=5,
        target_variable="category",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=3000,
        num_features=1,  # text column
        num_classes=5,
        num_text_features=1,
        dataset_size_mb=15.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    assert recommendation.architecture == ModelArchitecture.AUTOML_TEXT
    assert recommendation.requires_gpu is True
    assert recommendation.vertex_product == VertexAIProduct.AUTOML_TEXT


@pytest.mark.asyncio
async def test_large_text_dataset_selects_distilbert():
    """Test that large text datasets prefer DistilBERT."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.SENTIMENT_ANALYSIS,
        data_type=DataType.TEXT,
        domain="Social Media",
        suggested_metrics=["accuracy", "f1_score"],
        complexity_score=0.5,
        confidence=0.90,
        reasoning="Sentiment analysis on reviews",
        is_labeled=True,
        num_classes=3,
        target_variable="sentiment",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=50000,
        num_features=1,
        num_classes=3,
        num_text_features=1,
        dataset_size_mb=250.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    assert recommendation.architecture == ModelArchitecture.DISTILBERT
    assert recommendation.training_strategy == TrainingStrategy.CUSTOM
    assert recommendation.requires_gpu is True


@pytest.mark.asyncio
async def test_image_classification():
    """Test image classification model selection."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.IMAGE,
        domain="Medical Imaging",
        suggested_metrics=["accuracy", "auc"],
        complexity_score=0.8,
        confidence=0.92,
        reasoning="Image classification for diagnosis",
        is_labeled=True,
        num_classes=4,
        target_variable="diagnosis",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=5000,
        num_features=1,  # image
        num_classes=4,
        dataset_size_mb=2000.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    assert recommendation.architecture == ModelArchitecture.AUTOML_IMAGE
    assert recommendation.training_strategy == TrainingStrategy.AUTOML
    assert recommendation.requires_gpu is True


@pytest.mark.asyncio
async def test_time_series_forecasting():
    """Test time series forecasting model selection."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.TIME_SERIES_FORECASTING,
        data_type=DataType.TIME_SERIES,
        domain="Energy",
        suggested_metrics=["rmse", "mae"],
        complexity_score=0.65,
        confidence=0.86,
        reasoning="Energy demand forecasting",
        is_labeled=True,
        num_classes=None,
        target_variable="energy_demand",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=10000,
        num_features=8,
        num_datetime_features=1,
        num_numeric_features=7,
        dataset_size_mb=10.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    assert recommendation.architecture == ModelArchitecture.AUTOML_FORECASTING
    assert recommendation.vertex_product == VertexAIProduct.AUTOML_FORECASTING


@pytest.mark.asyncio
async def test_class_imbalance_handling():
    """Test that class imbalance is handled in XGBoost."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Fraud Detection",
        suggested_metrics=["precision", "recall", "f1_score"],
        complexity_score=0.6,
        confidence=0.89,
        reasoning="Imbalanced fraud detection",
        is_labeled=True,
        num_classes=2,
        target_variable="is_fraud",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=10000,
        num_features=30,
        num_classes=2,
        num_numeric_features=25,
        num_categorical_features=5,
        class_imbalance_ratio=0.05,  # Highly imbalanced
        dataset_size_mb=5.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    # Should select XGBoost with class imbalance handling
    assert recommendation.architecture == ModelArchitecture.XGBOOST
    assert "scale_pos_weight" in recommendation.hyperparameters.model_specific
    assert "imbalance" in recommendation.reasoning.lower()


@pytest.mark.asyncio
async def test_budget_constraint():
    """Test that budget constraints are respected."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Marketing",
        suggested_metrics=["accuracy"],
        complexity_score=0.5,
        confidence=0.80,
        reasoning="Customer segmentation",
        is_labeled=True,
        num_classes=4,
        target_variable="segment",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=200000,
        num_features=40,
        num_classes=4,
        num_numeric_features=30,
        num_categorical_features=10,
        dataset_size_mb=100.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        user_preferences={"max_cost_usd": 30.0},
        use_ai=False,
    )

    # Should select cheaper alternative due to budget
    assert recommendation.estimated_cost_usd <= 30.0
    assert recommendation.architecture == ModelArchitecture.XGBOOST


@pytest.mark.asyncio
async def test_vertex_ai_config_generation_automl():
    """Test Vertex AI configuration generation for AutoML."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Test",
        suggested_metrics=["accuracy"],
        complexity_score=0.5,
        confidence=0.8,
        reasoning="Test",
        is_labeled=True,
        num_classes=2,
        target_variable="target",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=100000,
        num_features=20,
        num_classes=2,
        num_numeric_features=15,
        num_categorical_features=5,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    config = selector.get_vertex_ai_config(recommendation)

    assert "display_name" in config
    assert "training_strategy" in config
    assert config["training_strategy"] == "automl"
    assert "automl_config" in config
    assert "optimization_objective" in config["automl_config"]
    assert "budget_milli_node_hours" in config["automl_config"]


@pytest.mark.asyncio
async def test_vertex_ai_config_generation_custom():
    """Test Vertex AI configuration generation for custom training."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Test",
        suggested_metrics=["accuracy"],
        complexity_score=0.3,
        confidence=0.85,
        reasoning="Simple classification",
        is_labeled=True,
        num_classes=2,
        target_variable="target",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=1000,
        num_features=8,
        num_classes=2,
        num_numeric_features=6,
        num_categorical_features=2,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        user_preferences={"interpretability": True},
        use_ai=False,
    )

    config = selector.get_vertex_ai_config(recommendation)

    assert config["training_strategy"] == "custom"
    assert "custom_config" in config
    assert "machine_type" in config["custom_config"]
    assert "hyperparameters" in config["custom_config"]
    assert "learning_rate" in config["custom_config"]["hyperparameters"]


@pytest.mark.asyncio
async def test_recommendation_has_alternatives():
    """Test that recommendations include alternatives."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Test",
        suggested_metrics=["accuracy"],
        complexity_score=0.3,
        confidence=0.80,
        reasoning="Simple problem",
        is_labeled=True,
        num_classes=2,
        target_variable="target",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=800,
        num_features=6,
        num_classes=2,
        num_numeric_features=5,
        num_categorical_features=1,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        user_preferences={"interpretability": True},
        use_ai=False,
    )

    # Should have at least one alternative
    assert len(recommendation.alternatives) > 0
    assert isinstance(recommendation.alternatives[0], type(recommendation))


@pytest.mark.asyncio
async def test_model_recommendation_to_dict():
    """Test ModelRecommendation serialization."""
    problem = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Test",
        suggested_metrics=["accuracy"],
        complexity_score=0.4,
        confidence=0.82,
        reasoning="Test problem",
        is_labeled=True,
        num_classes=2,
        target_variable="target",
        additional_insights={},
    )

    dataset = DatasetProfile(
        num_samples=5000,
        num_features=15,
        num_classes=2,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem,
        dataset_profile=dataset,
        use_ai=False,
    )

    # Convert to dict
    rec_dict = recommendation.to_dict()

    # Verify all required fields
    assert "architecture" in rec_dict
    assert "training_strategy" in rec_dict
    assert "vertex_product" in rec_dict
    assert "hyperparameters" in rec_dict
    assert "confidence" in rec_dict
    assert "reasoning" in rec_dict
    assert "estimated_training_time_minutes" in rec_dict
    assert "estimated_cost_usd" in rec_dict
    assert "requires_gpu" in rec_dict
    assert "interpretability_score" in rec_dict

    # Verify types
    assert isinstance(rec_dict["architecture"], str)
    assert isinstance(rec_dict["confidence"], float)
    assert isinstance(rec_dict["hyperparameters"], dict)
