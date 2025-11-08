"""
End-to-End Pipeline Test (Local Mode - No GCS/Vertex AI)

Tests the complete ML pipeline from data upload through model selection:
1. Data Upload & Storage
2. Problem Analysis
3. Data Processing
4. Model Selection

This version runs locally without requiring Google Cloud credentials.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from app.services.agent import (
    ProblemAnalyzer,
    DataProcessor,
    GeminiClient
)
from app.services.agent.model_selector import ModelSelector
from app.services.agent.model_types import DatasetProfile


async def test_e2e_pipeline_local():
    """Test the complete pipeline end-to-end (local mode)."""

    print("=" * 80)
    print("🚀 STARTING END-TO-END PIPELINE TEST (LOCAL MODE)")
    print("=" * 80)

    # =========================================================================
    # STEP 1: Load Sample Data
    # =========================================================================
    print("\n📊 STEP 1: Loading sample data...")

    # Try multiple possible paths - using 50rows.csv for faster testing
    possible_paths = [
        "50rows.csv",  # From workspace root
        "../50rows.csv",  # From backend dir
        str(Path(__file__).parent.parent / "50rows.csv")  # Absolute from script
    ]

    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break

    if not csv_path:
        print(f"❌ Error: 50rows.csv not found")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Tried paths: {possible_paths}")
        return

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {', '.join(df.columns.tolist()[:5])}...")

    # Prepare data sample for analysis
    data_sample = df.head(10).to_dict('records')

    # =========================================================================
    # STEP 2: Problem Analysis
    # =========================================================================
    print("\n🔍 STEP 2: Analyzing problem with Gemini...")

    try:
        gemini_client = GeminiClient(temperature=0.3)
        analyzer = ProblemAnalyzer(gemini_client=gemini_client)

        problem_description = """
        Predict customer churn for a telecommunications company.
        The dataset contains customer information including tenure, services,
        contract type, and whether they churned (left the company).
        """

        analysis = await analyzer.analyze_problem(
            problem_description=problem_description,
            data_sample=data_sample,
            num_samples=len(df),
            is_labeled=True,
            data_type_hint="tabular",
            file_extensions=[".csv"]
        )

        print(f"✅ Problem Analysis Complete:")
        print(f"   Problem Type: {analysis.problem_type.value}")
        print(f"   Data Type: {analysis.data_type.value}")
        print(f"   Domain: {analysis.domain}")
        print(f"   Confidence: {analysis.confidence:.2%}")
        print(f"   Complexity Score: {analysis.complexity_score:.2f}")
        print(f"   Suggested Metrics: {', '.join(analysis.suggested_metrics[:3])}")
        print(f"   Reasoning: {analysis.reasoning[:150]}...")

    except Exception as e:
        print(f"❌ Problem Analysis Failed: {e}")
        print("   Continuing with fallback analysis...")

        # Create fallback analysis
        from app.services.agent.types import ProblemAnalysis, ProblemType, DataType
        analysis = ProblemAnalysis(
            problem_type=ProblemType.CLASSIFICATION,
            data_type=DataType.TABULAR,
            domain="Telecommunications",
            suggested_metrics=["accuracy", "precision", "recall", "f1_score", "roc_auc"],
            complexity_score=0.6,
            reasoning="Fallback analysis: Binary classification problem",
            confidence=0.7,
            is_labeled=True,
            num_classes=2,
            target_variable="churn"
        )
        print(f"✅ Using fallback analysis: {analysis.problem_type.value}")

    # =========================================================================
    # STEP 3: Data Quality Validation
    # =========================================================================
    print("\n🔬 STEP 3: Validating data quality...")

    try:
        from app.services.agent.data_quality import DataQualityValidator

        validator = DataQualityValidator()
        quality_report = await validator.validate_data_quality(
            data=df,
            analysis=analysis,
            target_column="churn"
        )

        print(f"✅ Data Quality Report:")
        print(f"   Valid: {quality_report.is_valid}")
        print(f"   Severity Score: {quality_report.severity_score:.2f}")
        print(f"   Issues Found: {len(quality_report.issues)}")
        if quality_report.issues:
            print(f"   Issues: {', '.join([i.value for i in quality_report.issues])}")
        print(f"   Missing Values: {quality_report.missing_value_stats['total_missing']}")
        print(f"   Duplicates: {quality_report.duplicate_count}")

        if quality_report.recommendations:
            print(f"   Recommendations:")
            for rec in quality_report.recommendations[:2]:
                print(f"     - {rec}")

        # Determine processing strategy
        strategy = await validator.determine_processing_strategy(
            quality_report, analysis, df
        )
        print(f"\n   Processing Strategy: {strategy.missing_value_strategy.value}")
        print(f"   Reasoning: {strategy.reasoning}")

    except Exception as e:
        print(f"❌ Data Quality Validation Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # STEP 4: Data Splitting
    # =========================================================================
    print("\n✂️  STEP 4: Splitting data into train/val/test...")

    try:
        from app.services.agent.data_splitter import DataSplitter

        splitter = DataSplitter(
            train_ratio=0.70,
            val_ratio=0.15,
            test_ratio=0.15,
            random_state=42
        )

        data_split = await splitter.split_data(
            data=df,
            analysis=analysis,
            target_column="churn",
            stratify=True
        )

        print(f"✅ Data Split Complete:")
        print(f"   Train: {data_split.split_info['train_size']} samples ({data_split.split_info['train_ratio']:.1%})")
        print(f"   Val:   {data_split.split_info['val_size']} samples ({data_split.split_info['val_ratio']:.1%})")
        print(f"   Test:  {data_split.split_info['test_size']} samples ({data_split.split_info['test_ratio']:.1%})")
        print(f"   Stratified: {data_split.split_info['stratified']}")

        if data_split.split_info.get('class_distribution'):
            print(f"   Class Distribution (Train): {data_split.split_info['class_distribution']['train']}")

    except Exception as e:
        print(f"❌ Data Splitting Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # STEP 5: Feature Engineering
    # =========================================================================
    print("\n⚙️  STEP 5: Engineering features...")

    try:
        from app.services.agent.feature_engineer import FeatureEngineer

        feature_engineer = FeatureEngineer()

        processed_data = await feature_engineer.process_features(
            data_split=data_split,
            analysis=analysis,
            target_column="churn"
        )

        print(f"✅ Feature Engineering Complete:")
        print(f"   Data Type: {processed_data.feature_info['data_type']}")
        print(f"   Number of Features: {processed_data.feature_info.get('n_features', 'N/A')}")

        if 'numeric_features' in processed_data.feature_info:
            print(f"   Numeric Features: {len(processed_data.feature_info['numeric_features'])}")
        if 'categorical_features' in processed_data.feature_info:
            print(f"   Categorical Features: {len(processed_data.feature_info['categorical_features'])}")

        print(f"   Normalization: {processed_data.feature_info.get('normalization', 'None')}")
        print(f"   Encoding: {processed_data.feature_info.get('encoding', 'None')}")

        # Check processed data shape
        if isinstance(processed_data.train_data, dict) and 'X' in processed_data.train_data:
            import numpy as np
            X_train = processed_data.train_data['X']
            y_train = processed_data.train_data['y']
            print(f"   Train X shape: {X_train.shape if hasattr(X_train, 'shape') else 'N/A'}")
            print(f"   Train y shape: {y_train.shape if hasattr(y_train, 'shape') else 'N/A'}")

    except Exception as e:
        print(f"❌ Feature Engineering Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # STEP 6: Create Dataset Profile for Model Selection
    # =========================================================================
    print("\n📋 STEP 6: Creating dataset profile...")

    try:
        # Calculate dataset statistics
        num_numeric = len(df.select_dtypes(include=['number']).columns)
        num_categorical = len(df.select_dtypes(include=['object', 'category']).columns)
        missing_ratio = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])

        # Class imbalance for classification
        class_imbalance_ratio = None
        if analysis.problem_type.value in ['classification', 'text_classification']:
            if 'churn' in df.columns:
                class_counts = df['churn'].value_counts()
                class_imbalance_ratio = class_counts.min() / class_counts.max()

        dataset_profile = DatasetProfile(
            num_samples=len(df),
            num_features=len(df.columns) - 1,  # Exclude target
            num_classes=analysis.num_classes,
            num_numeric_features=num_numeric,
            num_categorical_features=num_categorical,
            num_text_features=0,
            num_datetime_features=0,
            missing_value_ratio=missing_ratio,
            class_imbalance_ratio=class_imbalance_ratio,
            has_high_cardinality_categoricals=False,
            has_sparse_features=False,
            dimensionality_ratio=(len(df.columns) - 1) / len(df),
            dataset_size_mb=df.memory_usage(deep=True).sum() / (1024 * 1024),
            estimated_memory_gb=df.memory_usage(deep=True).sum() / (1024 * 1024 * 1024)
        )

        print(f"✅ Dataset Profile Created:")
        print(f"   Samples: {dataset_profile.num_samples}")
        print(f"   Features: {dataset_profile.num_features}")
        print(f"   Numeric: {dataset_profile.num_numeric_features}")
        print(f"   Categorical: {dataset_profile.num_categorical_features}")
        print(f"   Missing Ratio: {dataset_profile.missing_value_ratio:.2%}")
        if dataset_profile.class_imbalance_ratio:
            print(f"   Class Imbalance: {dataset_profile.class_imbalance_ratio:.2f}")
        print(f"   Size: {dataset_profile.dataset_size_mb:.2f} MB")

    except Exception as e:
        print(f"❌ Dataset Profile Creation Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # STEP 7: Model Selection
    # =========================================================================
    print("\n🤖 STEP 7: Selecting optimal model...")

    try:
        model_selector = ModelSelector(gemini_client=gemini_client)

        # Prepare CSV data for model selector
        csv_data = {
            "column_names": df.columns.tolist(),
            "data_sample": df.head(5).to_dict('records'),
            "total_rows": len(df),
            "total_columns": len(df.columns)
        }

        recommendation = await model_selector.select_model(
            problem_analysis=analysis,
            dataset_profile=dataset_profile,
            user_preferences={
                "interpretability": "medium",
                "cost_sensitivity": "medium",
                "training_time": "fast"
            },
            use_ai=True,
            csv_data=csv_data
        )

        print(f"✅ Model Selection Complete:")
        print(f"   Architecture: {recommendation.architecture.value}")
        print(f"   Training Strategy: {recommendation.training_strategy.value}")
        print(f"   Vertex AI Product: {recommendation.vertex_product.value}")
        print(f"   Confidence: {recommendation.confidence:.2%}")
        print(f"   Requires GPU: {recommendation.requires_gpu}")
        print(f"   Interpretability Score: {recommendation.interpretability_score:.2f}")

        if recommendation.estimated_training_time_minutes:
            print(f"   Est. Training Time: {recommendation.estimated_training_time_minutes} minutes")
        if recommendation.estimated_cost_usd:
            print(f"   Est. Cost: ${recommendation.estimated_cost_usd:.2f}")

        print(f"\n   Hyperparameters:")
        print(f"     Learning Rate: {recommendation.hyperparameters.learning_rate}")
        print(f"     Batch Size: {recommendation.hyperparameters.batch_size}")
        print(f"     Max Iterations: {recommendation.hyperparameters.max_iterations}")

        # Show budget
        budget = recommendation.hyperparameters.model_specific.get('train_budget_milli_node_hours', 0)
        if budget:
            print(f"     Training Budget: {budget} milli-node-hours ({budget/1000:.1f} hours = {budget/1000*60:.0f} minutes)")

        print(f"\n   Reasoning: {recommendation.reasoning[:200]}...")

        if recommendation.alternatives:
            print(f"\n   Alternatives ({len(recommendation.alternatives)}):")
            for i, alt in enumerate(recommendation.alternatives[:2], 1):
                print(f"     {i}. {alt.architecture.value} (confidence: {alt.confidence:.2%})")

        # Get Vertex AI configuration
        vertex_config = model_selector.get_vertex_ai_config(recommendation)
        print(f"\n   Vertex AI Config:")
        print(f"     Display Name: {vertex_config['display_name']}")
        print(f"     Product: {vertex_config['vertex_product']}")

    except Exception as e:
        print(f"❌ Model Selection Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ END-TO-END PIPELINE TEST COMPLETE (LOCAL MODE)!")
    print("=" * 80)
    print("\n📊 Pipeline Summary:")
    print(f"   1. ✅ Data Loaded: {len(df)} samples")
    print(f"   2. ✅ Problem Analyzed: {analysis.problem_type.value}")
    print(f"   3. ✅ Data Quality: {'Valid' if quality_report.is_valid else 'Issues Found'}")
    print(f"   4. ✅ Data Split: {data_split.split_info['train_size']}/{data_split.split_info['val_size']}/{data_split.split_info['test_size']}")
    print(f"   5. ✅ Features Engineered: {processed_data.feature_info.get('n_features', 'N/A')} features")
    print(f"   6. ✅ Model Selected: {recommendation.architecture.value}")
    print(f"   7. ✅ Training Budget: {budget/1000*60:.0f} minutes (optimized for dataset size!)")
    print(f"\n🎉 All pipeline steps executed successfully!")
    print(f"\n💡 Next Steps:")
    print(f"   - Set up Google Cloud credentials to enable GCS upload and Vertex AI training")
    print(f"   - Run full E2E test with: python test_e2e_pipeline.py")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(test_e2e_pipeline_local())
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
