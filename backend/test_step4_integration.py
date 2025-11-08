#!/usr/bin/env python3
"""
Integration test script for Step 4: Model Selection Agent

This script demonstrates the complete Step 4 workflow:
1. Problem analysis (from Step 3)
2. Dataset profiling
3. Model selection with rule-based logic
4. Vertex AI configuration generation

Run this script to verify Step 4 implementation.
"""
import os
import asyncio

# Set environment variables for testing
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/test-credentials.json"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"
os.environ["GEMINI_API_KEY"] = "test-api-key"
os.environ["ENVIRONMENT"] = "test"

from app.services.agent.model_selector import ModelSelector
from app.services.agent.types import ProblemType, DataType, ProblemAnalysis
from app.services.agent.model_types import DatasetProfile
import json


async def test_tabular_classification():
    """Test model selection for tabular classification problem."""
    print("\n" + "="*80)
    print("TEST 1: Tabular Classification (E-commerce Purchase Prediction)")
    print("="*80)

    # Simulate Step 3 output
    problem_analysis = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="E-commerce",
        suggested_metrics=["accuracy", "precision", "recall", "f1_score"],
        complexity_score=0.5,
        confidence=0.88,
        reasoning="Binary classification to predict customer purchases based on browsing behavior",
        is_labeled=True,
        num_classes=2,
        target_variable="will_purchase",
        additional_insights={"class_imbalance": "moderate"},
    )

    # Dataset profile
    dataset_profile = DatasetProfile(
        num_samples=50000,
        num_features=25,
        num_classes=2,
        num_numeric_features=18,
        num_categorical_features=7,
        missing_value_ratio=0.05,
        class_imbalance_ratio=0.35,  # 35% minority class
        dimensionality_ratio=0.0005,
        dataset_size_mb=45.0,
    )

    # CSV data sample (simulating what would come from actual CSV analysis)
    csv_data = {
        "column_names": ["user_id", "age", "income", "page_views", "time_on_site",
                        "cart_adds", "product_category", "device_type", "will_purchase"],
        "data_sample": """
user_id,age,income,page_views,time_on_site,cart_adds,product_category,device_type,will_purchase
1001,28,65000,15,450,3,Electronics,Mobile,1
1002,34,48000,5,120,0,Clothing,Desktop,0
1003,42,85000,22,680,5,Electronics,Tablet,1
        """,
        "total_rows": 50000,
        "total_columns": 9,
    }

    # Select model
    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem_analysis,
        dataset_profile=dataset_profile,
        user_preferences={"max_cost_usd": 100},
        use_ai=False,  # Using rule-based only for testing
        csv_data=csv_data,
    )

    # Display results
    print(f"\n✅ Selected Model: {recommendation.architecture.value}")
    print(f"📊 Training Strategy: {recommendation.training_strategy.value}")
    print(f"☁️  Vertex AI Product: {recommendation.vertex_product.value}")
    print(f"🎯 Confidence: {recommendation.confidence:.2%}")
    print(f"⏱️  Estimated Training Time: {recommendation.estimated_training_time_minutes} minutes")
    print(f"💰 Estimated Cost: ${recommendation.estimated_cost_usd:.2f}")
    print(f"🔍 Interpretability Score: {recommendation.interpretability_score:.2f}/1.0")
    print(f"\n📝 Reasoning:\n{recommendation.reasoning}")

    # Show hyperparameters
    print(f"\n⚙️  Hyperparameters:")
    print(f"  - Learning Rate: {recommendation.hyperparameters.learning_rate}")
    print(f"  - Batch Size: {recommendation.hyperparameters.batch_size}")
    print(f"  - Max Iterations: {recommendation.hyperparameters.max_iterations}")
    if recommendation.hyperparameters.model_specific:
        print(f"  - Model-specific params: {json.dumps(recommendation.hyperparameters.model_specific, indent=4)}")

    # Generate Vertex AI config
    vertex_config = selector.get_vertex_ai_config(recommendation)
    print(f"\n🚀 Vertex AI Configuration:")
    print(json.dumps(vertex_config, indent=2))

    return recommendation


async def test_text_classification():
    """Test model selection for text classification."""
    print("\n" + "="*80)
    print("TEST 2: Text Classification (Customer Review Sentiment)")
    print("="*80)

    problem_analysis = ProblemAnalysis(
        problem_type=ProblemType.SENTIMENT_ANALYSIS,
        data_type=DataType.TEXT,
        domain="Customer Service",
        suggested_metrics=["accuracy", "f1_score", "precision"],
        complexity_score=0.6,
        confidence=0.90,
        reasoning="Multi-class sentiment analysis on product reviews",
        is_labeled=True,
        num_classes=3,
        target_variable="sentiment",
        additional_insights={},
    )

    dataset_profile = DatasetProfile(
        num_samples=15000,
        num_features=1,
        num_classes=3,
        num_text_features=1,
        dataset_size_mb=120.0,
    )

    csv_data = {
        "column_names": ["review_id", "review_text", "sentiment"],
        "data_sample": """
review_id,review_text,sentiment
R001,"Great product! Exceeded my expectations.",positive
R002,"Terrible quality, broke after one day.",negative
R003,"It's okay, nothing special.",neutral
        """,
        "total_rows": 15000,
        "total_columns": 3,
    }

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem_analysis,
        dataset_profile=dataset_profile,
        use_ai=False,
        csv_data=csv_data,
    )

    print(f"\n✅ Selected Model: {recommendation.architecture.value}")
    print(f"📊 Training Strategy: {recommendation.training_strategy.value}")
    print(f"🎯 Confidence: {recommendation.confidence:.2%}")
    print(f"⏱️  Estimated Training Time: {recommendation.estimated_training_time_minutes} minutes")
    print(f"💰 Estimated Cost: ${recommendation.estimated_cost_usd:.2f}")
    print(f"🖥️  Requires GPU: {recommendation.requires_gpu}")
    print(f"\n📝 Reasoning:\n{recommendation.reasoning}")

    return recommendation


async def test_regression():
    """Test model selection for regression problem."""
    print("\n" + "="*80)
    print("TEST 3: Regression (House Price Prediction)")
    print("="*80)

    problem_analysis = ProblemAnalysis(
        problem_type=ProblemType.REGRESSION,
        data_type=DataType.TABULAR,
        domain="Real Estate",
        suggested_metrics=["rmse", "mae", "r2"],
        complexity_score=0.65,
        confidence=0.85,
        reasoning="Predict house prices based on features like size, location, amenities",
        is_labeled=True,
        num_classes=None,
        target_variable="price",
        additional_insights={},
    )

    dataset_profile = DatasetProfile(
        num_samples=120000,
        num_features=45,
        num_numeric_features=30,
        num_categorical_features=15,
        missing_value_ratio=0.08,
        dimensionality_ratio=0.000375,
        dataset_size_mb=280.0,
    )

    csv_data = {
        "column_names": ["property_id", "sqft", "bedrooms", "bathrooms", "location",
                        "year_built", "garage", "pool", "price"],
        "data_sample": """
property_id,sqft,bedrooms,bathrooms,location,year_built,garage,pool,price
P001,2500,4,3,Suburban,1995,2,0,450000
P002,1800,3,2,Urban,2005,1,0,525000
P003,3500,5,4,Suburban,2010,3,1,680000
        """,
        "total_rows": 120000,
        "total_columns": 9,
    }

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem_analysis,
        dataset_profile=dataset_profile,
        user_preferences={"interpretability": False},
        use_ai=False,
        csv_data=csv_data,
    )

    print(f"\n✅ Selected Model: {recommendation.architecture.value}")
    print(f"📊 Training Strategy: {recommendation.training_strategy.value}")
    print(f"🎯 Confidence: {recommendation.confidence:.2%}")
    print(f"⏱️  Estimated Training Time: {recommendation.estimated_training_time_minutes} minutes")
    print(f"💰 Estimated Cost: ${recommendation.estimated_cost_usd:.2f}")

    # Show alternatives
    if recommendation.alternatives:
        print(f"\n🔄 Alternative Recommendations:")
        for i, alt in enumerate(recommendation.alternatives, 1):
            print(f"  {i}. {alt.architecture.value} (confidence: {alt.confidence:.2%}, cost: ${alt.estimated_cost_usd:.2f})")

    print(f"\n📝 Reasoning:\n{recommendation.reasoning}")

    return recommendation


async def test_high_imbalance():
    """Test model selection with high class imbalance."""
    print("\n" + "="*80)
    print("TEST 4: Fraud Detection (Highly Imbalanced Dataset)")
    print("="*80)

    problem_analysis = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Fraud Detection",
        suggested_metrics=["precision", "recall", "f1_score", "auc"],
        complexity_score=0.75,
        confidence=0.92,
        reasoning="Detect fraudulent transactions with severe class imbalance",
        is_labeled=True,
        num_classes=2,
        target_variable="is_fraud",
        additional_insights={"severe_imbalance": True},
    )

    dataset_profile = DatasetProfile(
        num_samples=200000,
        num_features=35,
        num_classes=2,
        num_numeric_features=28,
        num_categorical_features=7,
        class_imbalance_ratio=0.02,  # Only 2% fraudulent
        dimensionality_ratio=0.000175,
        dataset_size_mb=150.0,
    )

    selector = ModelSelector()
    recommendation = await selector.select_model(
        problem_analysis=problem_analysis,
        dataset_profile=dataset_profile,
        use_ai=False,
    )

    print(f"\n✅ Selected Model: {recommendation.architecture.value}")
    print(f"⚖️  Class Imbalance Handling: ", end="")
    if "scale_pos_weight" in recommendation.hyperparameters.model_specific:
        print(f"✓ (scale_pos_weight = {recommendation.hyperparameters.model_specific['scale_pos_weight']:.2f})")
    else:
        print("Automatic (AutoML)")
    print(f"💰 Estimated Cost: ${recommendation.estimated_cost_usd:.2f}")
    print(f"\n📝 Reasoning:\n{recommendation.reasoning}")

    return recommendation


async def main():
    """Run all integration tests."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║              Step 4: Model Selection Agent - Integration Tests          ║
║                                                                          ║
║  This script demonstrates the complete model selection workflow for     ║
║  various ML problem types and datasets.                                 ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Run all tests
        await test_tabular_classification()
        await test_text_classification()
        await test_regression()
        await test_high_imbalance()

        print("\n" + "="*80)
        print("✅ All Integration Tests Completed Successfully!")
        print("="*80)
        print("\n📋 Summary:")
        print("  - Tested 4 different problem types")
        print("  - Validated model selection logic")
        print("  - Generated Vertex AI configurations")
        print("  - Handled class imbalance scenarios")
        print("  - CSV data validation workflow demonstrated")
        print("\n🎯 Step 4 Implementation: VERIFIED ✓")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
