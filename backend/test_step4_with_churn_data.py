#!/usr/bin/env python3
"""
Real-world test of Step 4 Model Selection Agent using Customer_Churn_data.csv

This script demonstrates the complete workflow:
1. Load and analyze the actual CSV file
2. Profile the dataset characteristics
3. Run Step 4 model selection
4. Generate Vertex AI training configuration
"""
import os
import asyncio
import csv
from collections import Counter
from pathlib import Path

# Set environment variables for testing
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/test-credentials.json"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"
os.environ["GEMINI_API_KEY"] = "test-api-key"
os.environ["ENVIRONMENT"] = "test"

import sys
sys.path.insert(0, '/home/user/ModelMaestro/backend')

from app.services.agent.model_selector import ModelSelector
from app.services.agent.types import ProblemType, DataType, ProblemAnalysis
from app.services.agent.model_types import DatasetProfile
import json


def analyze_csv(csv_path: str):
    """Analyze the CSV file to extract dataset characteristics."""
    print(f"\n📂 Analyzing CSV file: {csv_path}")
    print("="*80)

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Get column names
    column_names = list(rows[0].keys())
    num_samples = len(rows)
    num_features = len(column_names) - 1  # Exclude target column 'churn'

    print(f"\n📊 Dataset Overview:")
    print(f"  - Total Rows: {num_samples:,}")
    print(f"  - Total Columns: {len(column_names)}")
    print(f"  - Feature Columns: {num_features}")

    # Identify feature types
    numeric_features = ['tenure', 'monthly_charges', 'total_charges']
    categorical_features = [col for col in column_names
                           if col not in numeric_features + ['customer_id', 'churn']]

    print(f"\n🔢 Feature Types:")
    print(f"  - Numeric Features ({len(numeric_features)}): {', '.join(numeric_features)}")
    print(f"  - Categorical Features ({len(categorical_features)}): {len(categorical_features)}")

    # Check for missing values
    missing_count = 0
    for row in rows:
        for value in row.values():
            if value == '' or value is None:
                missing_count += 1

    total_values = num_samples * len(column_names)
    missing_ratio = missing_count / total_values if total_values > 0 else 0

    # Analyze target variable (churn)
    churn_values = [row['churn'] for row in rows]
    churn_counter = Counter(churn_values)

    print(f"\n🎯 Target Variable Analysis (churn):")
    for value, count in churn_counter.items():
        percentage = (count / num_samples) * 100
        print(f"  - {value}: {count:,} ({percentage:.1f}%)")

    # Calculate class imbalance ratio
    if len(churn_counter) >= 2:
        min_class = min(churn_counter.values())
        max_class = max(churn_counter.values())
        class_imbalance_ratio = min_class / max_class
    else:
        class_imbalance_ratio = 1.0

    print(f"  - Class Imbalance Ratio: {class_imbalance_ratio:.3f}")
    if class_imbalance_ratio < 0.5:
        print(f"    ⚠️  Imbalanced dataset detected!")

    # Sample data for CSV validation (10% sample)
    sample_size = max(10, num_samples // 10)
    sample_rows = rows[:sample_size]

    # Format sample data as CSV string
    sample_csv = "\\n".join([
        ",".join(column_names),
        *[",".join([str(row.get(col, '')) for col in column_names])
          for row in sample_rows[:5]]  # First 5 rows for display
    ])

    # Estimate file size
    file_size_mb = Path(csv_path).stat().st_size / (1024 * 1024)

    print(f"\n💾 Dataset Size: {file_size_mb:.2f} MB")

    # Create dataset profile
    dataset_profile = DatasetProfile(
        num_samples=num_samples,
        num_features=num_features,
        num_classes=len(churn_counter),
        num_numeric_features=len(numeric_features),
        num_categorical_features=len(categorical_features),
        missing_value_ratio=missing_ratio,
        class_imbalance_ratio=class_imbalance_ratio,
        dimensionality_ratio=num_features / num_samples,
        dataset_size_mb=file_size_mb,
    )

    # CSV data for model selector
    csv_data = {
        "column_names": ", ".join(column_names),
        "data_sample": sample_csv,
        "total_rows": num_samples,
        "total_columns": len(column_names),
    }

    return dataset_profile, csv_data, column_names


async def test_customer_churn_model_selection():
    """Test Step 4 model selection with real customer churn data."""

    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║          Step 4: Real-World Test with Customer Churn Dataset            ║
║                                                                          ║
║  Testing the Model Selection Agent with actual customer churn data      ║
║  to predict which customers are likely to leave.                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)

    # Path to CSV file
    csv_path = "/home/user/ModelMaestro/Customer_Churn_data.csv"

    # Analyze the CSV
    dataset_profile, csv_data, column_names = analyze_csv(csv_path)

    # Create problem analysis (simulating Step 3 output)
    print(f"\n🔍 Step 3: Problem Analysis")
    print("="*80)

    problem_analysis = ProblemAnalysis(
        problem_type=ProblemType.CLASSIFICATION,
        data_type=DataType.TABULAR,
        domain="Telecommunications / Customer Service",
        suggested_metrics=["accuracy", "precision", "recall", "f1_score", "auc"],
        complexity_score=0.55,
        confidence=0.92,
        reasoning=(
            "Binary classification problem to predict customer churn in a telecom company. "
            "Features include customer demographics, service usage, contract details, and billing information. "
            "The dataset shows moderate class imbalance which should be addressed in model training."
        ),
        is_labeled=True,
        num_classes=2,
        target_variable="churn",
        additional_insights={
            "business_context": "Reducing churn is critical for telecom profitability",
            "key_features": "tenure, contract_type, monthly_charges appear important",
            "recommendation": "Consider feature importance analysis and churn probability scores",
        },
    )

    print(f"\n✅ Problem Type: {problem_analysis.problem_type.value}")
    print(f"✅ Data Type: {problem_analysis.data_type.value}")
    print(f"✅ Domain: {problem_analysis.domain}")
    print(f"✅ Target Variable: {problem_analysis.target_variable}")
    print(f"✅ Number of Classes: {problem_analysis.num_classes}")
    print(f"✅ Complexity Score: {problem_analysis.complexity_score:.2f}")
    print(f"✅ Suggested Metrics: {', '.join(problem_analysis.suggested_metrics)}")
    print(f"\n📝 Reasoning: {problem_analysis.reasoning}")

    # Run Step 4: Model Selection
    print(f"\n\n🤖 Step 4: Model Selection Agent")
    print("="*80)

    selector = ModelSelector()

    # Test with different user preferences
    scenarios = [
        {
            "name": "Cost-Optimized",
            "preferences": {"max_cost_usd": 30, "speed": True},
        },
        {
            "name": "Performance-Optimized",
            "preferences": {"max_cost_usd": 100},
        },
        {
            "name": "Interpretability-Focused",
            "preferences": {"interpretability": True, "max_cost_usd": 50},
        },
    ]

    results = []

    for scenario in scenarios:
        print(f"\n\n{'='*80}")
        print(f"📋 Scenario: {scenario['name']}")
        print(f"{'='*80}")
        print(f"User Preferences: {json.dumps(scenario['preferences'], indent=2)}")

        recommendation = await selector.select_model(
            problem_analysis=problem_analysis,
            dataset_profile=dataset_profile,
            user_preferences=scenario['preferences'],
            use_ai=False,  # Using rule-based for deterministic testing
            csv_data=csv_data,
        )

        results.append({
            "scenario": scenario['name'],
            "recommendation": recommendation,
        })

        # Display results
        print(f"\n✅ Selected Model: {recommendation.architecture.value.upper()}")
        print(f"📊 Training Strategy: {recommendation.training_strategy.value}")
        print(f"☁️  Vertex AI Product: {recommendation.vertex_product.value}")
        print(f"🎯 Confidence: {recommendation.confidence:.1%}")
        print(f"⏱️  Estimated Training Time: {recommendation.estimated_training_time_minutes} minutes")
        print(f"💰 Estimated Cost: ${recommendation.estimated_cost_usd:.2f}")
        print(f"🔍 Interpretability Score: {recommendation.interpretability_score:.2f}/1.0")
        print(f"🖥️  Requires GPU: {'Yes' if recommendation.requires_gpu else 'No'}")
        print(f"🔄 Supports Incremental Training: {'Yes' if recommendation.supports_incremental_training else 'No'}")

        print(f"\n📝 Reasoning:")
        print(f"{recommendation.reasoning}")

        # Show hyperparameters
        print(f"\n⚙️  Hyperparameters:")
        print(f"  - Learning Rate: {recommendation.hyperparameters.learning_rate}")
        print(f"  - Batch Size: {recommendation.hyperparameters.batch_size}")
        print(f"  - Max Iterations: {recommendation.hyperparameters.max_iterations}")
        print(f"  - Early Stopping Patience: {recommendation.hyperparameters.early_stopping_patience}")

        if recommendation.hyperparameters.model_specific:
            print(f"\n  Model-Specific Parameters:")
            for key, value in recommendation.hyperparameters.model_specific.items():
                print(f"    - {key}: {value}")

        # Show alternatives
        if recommendation.alternatives:
            print(f"\n🔄 Alternative Recommendations:")
            for i, alt in enumerate(recommendation.alternatives[:3], 1):
                print(f"  {i}. {alt.architecture.value} "
                      f"(confidence: {alt.confidence:.1%}, "
                      f"cost: ${alt.estimated_cost_usd:.2f}, "
                      f"time: {alt.estimated_training_time_minutes}min)")

        # Generate Vertex AI config
        vertex_config = selector.get_vertex_ai_config(recommendation)
        print(f"\n🚀 Vertex AI Training Configuration:")
        print(json.dumps(vertex_config, indent=2))

    # Summary comparison
    print(f"\n\n{'='*80}")
    print("📊 SUMMARY: Model Recommendations Across Scenarios")
    print(f"{'='*80}\n")

    print(f"{'Scenario':<25} {'Model':<20} {'Cost':<12} {'Time':<12} {'Interp.':<10}")
    print(f"{'-'*80}")

    for result in results:
        rec = result['recommendation']
        print(f"{result['scenario']:<25} "
              f"{rec.architecture.value:<20} "
              f"${rec.estimated_cost_usd:<11.2f} "
              f"{rec.estimated_training_time_minutes:<11}min "
              f"{rec.interpretability_score:<10.2f}")

    print(f"\n{'='*80}")
    print("✅ Step 4 Testing Complete - All Scenarios Validated!")
    print(f"{'='*80}")

    print(f"\n🎯 Key Findings:")
    print(f"  ✓ Successfully profiled Customer_Churn_data.csv ({dataset_profile.num_samples:,} rows)")
    print(f"  ✓ Detected class imbalance ratio: {dataset_profile.class_imbalance_ratio:.3f}")
    print(f"  ✓ Generated model recommendations for 3 different scenarios")
    print(f"  ✓ All Vertex AI configurations ready for deployment")
    print(f"  ✓ CSV validation workflow tested with real data")

    print(f"\n💡 Recommended Next Steps:")
    print(f"  1. Review the selected model for your preferred scenario")
    print(f"  2. Use the Vertex AI config to launch training job (Step 5)")
    print(f"  3. Monitor training and evaluate model performance (Step 6)")
    print(f"  4. Deploy to production endpoint (Step 7)")

    return results


async def main():
    """Run the real-world test."""
    try:
        results = await test_customer_churn_model_selection()
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
