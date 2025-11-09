"""
Test script for Confusion Matrix Generator and Model Selection Report Generator.

This script demonstrates how to:
1. Generate confusion matrices from trained models
2. Create AI-powered model selection explanation reports
3. Upload both to GCS

Can run in local mode (without GCS) for testing.
"""

import asyncio
import os
import sys
from pathlib import Path
import pickle
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for testing
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("GCS_BUCKET_NAME", "test-bucket")
os.environ.setdefault("ENVIRONMENT", "test")


async def create_test_model_and_data():
    """Create a test model and test data for demonstration."""
    print("\n🔧 Creating test model and data...")

    # Generate synthetic classification data
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        random_state=42
    )

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train a simple model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)

    print(f"✅ Model trained:")
    print(f"   Training accuracy: {train_acc:.3f}")
    print(f"   Test accuracy: {test_acc:.3f}")

    # Save model and test data locally
    test_dir = Path("./test_outputs")
    test_dir.mkdir(exist_ok=True)

    model_path = test_dir / "model.pkl"
    test_data_path = test_dir / "test_data.pkl"
    metadata_path = test_dir / "metadata.json"

    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    # Save test data
    with open(test_data_path, 'wb') as f:
        pickle.dump({'X': X_test, 'y': y_test}, f)

    # Create metadata
    metadata = {
        "dataset_id": "test_classification_001",
        "model_uri": str(model_path),
        "gcs_paths": {
            "test": str(test_data_path)
        },
        "num_samples": len(y),
        "num_features": X.shape[1],
        "num_classes": len(np.unique(y))
    }

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✅ Test files created:")
    print(f"   Model: {model_path}")
    print(f"   Test data: {test_data_path}")
    print(f"   Metadata: {metadata_path}")

    return str(metadata_path), str(model_path), str(test_data_path)


async def test_confusion_matrix_generator(metadata_path, model_path, test_data_path):
    """Test the confusion matrix generator."""
    print("\n" + "=" * 80)
    print("📊 TESTING CONFUSION MATRIX GENERATOR")
    print("=" * 80)

    try:
        from app.services.agent.confusion_matrix_generator import ConfusionMatrixGenerator

        # Create generator (will fail if no GCS credentials, that's OK for testing)
        try:
            generator = ConfusionMatrixGenerator(gcs_bucket_name="test-bucket")
            has_gcs = True
        except Exception as e:
            print(f"⚠️  GCS not available: {e}")
            print("   Running in local-only mode")
            has_gcs = False
            # For local testing, we'll mock the GCS parts
            return await test_confusion_matrix_local(metadata_path, model_path, test_data_path)

        # Generate confusion matrix
        print("\n🔄 Generating confusion matrix...")
        results = await generator.generate_confusion_matrix(
            metadata_path=metadata_path,
            model_path=model_path,
            test_data_path=test_data_path,
            upload_to_gcs=has_gcs,
            dataset_id="test_classification_001"
        )

        # Display results
        print("\n✅ Confusion Matrix Generated:")
        print(f"   Accuracy: {results['metrics']['accuracy']:.3f}")
        print(f"   Precision: {results['metrics']['precision']:.3f}")
        print(f"   Recall: {results['metrics']['recall']:.3f}")
        print(f"   F1-Score: {results['metrics']['f1_score']:.3f}")

        print("\n📊 Confusion Matrix:")
        cm = np.array(results['confusion_matrix'])
        print(cm)

        print(f"\n🎨 Generated {len(results['plots'])} visualization plots")
        for plot_name in results['plots'].keys():
            print(f"   - {plot_name}")

        if 'gcs_uris' in results:
            print("\n☁️  Uploaded to GCS:")
            for name, uri in results['gcs_uris'].items():
                print(f"   {name}: {uri}")

        # Save results locally
        results_path = Path("./test_outputs/confusion_matrix_results.json")
        with open(results_path, 'w') as f:
            # Remove plots from JSON (they're binary)
            results_for_json = {
                k: v for k, v in results.items() if k != 'plots'
            }
            json.dump(results_for_json, f, indent=2)
        print(f"\n💾 Results saved to: {results_path}")

        # Save plots
        plots_dir = Path("./test_outputs/plots")
        plots_dir.mkdir(exist_ok=True)
        for plot_name, plot_bytes in results['plots'].items():
            plot_path = plots_dir / f"{plot_name}.png"
            with open(plot_path, 'wb') as f:
                f.write(plot_bytes)
            print(f"   Plot saved: {plot_path}")

        return results

    except Exception as e:
        print(f"\n❌ Confusion Matrix Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_confusion_matrix_local(metadata_path, model_path, test_data_path):
    """Test confusion matrix generation in local mode (without GCS)."""
    print("\n🔄 Running confusion matrix generation in local mode...")

    import pickle
    from sklearn.metrics import (
        confusion_matrix, accuracy_score,
        precision_recall_fscore_support, classification_report
    )

    # Load model and data
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)

    X_test = test_data['X']
    y_test = test_data['y']

    # Generate predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)

    # Calculate metrics
    cm = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average='weighted'
    )

    print("\n✅ Local Confusion Matrix Results:")
    print(f"   Accuracy: {accuracy:.3f}")
    print(f"   Precision: {precision:.3f}")
    print(f"   Recall: {recall:.3f}")
    print(f"   F1-Score: {f1:.3f}")
    print("\n📊 Confusion Matrix:")
    print(cm)

    # Generate plots
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay

    plots_dir = Path("./test_outputs/plots")
    plots_dir.mkdir(exist_ok=True)

    # Confusion matrix plot
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(ax=ax, cmap='Blues')
    plt.title('Confusion Matrix')
    plt.savefig(plots_dir / 'confusion_matrix.png', dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n💾 Plot saved to: {plots_dir / 'confusion_matrix.png'}")

    return {
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1)
        },
        "confusion_matrix": cm.tolist()
    }


async def test_model_selection_report():
    """Test the model selection report generator."""
    print("\n" + "=" * 80)
    print("📝 TESTING MODEL SELECTION REPORT GENERATOR")
    print("=" * 80)

    try:
        from app.services.agent.model_selection_report_generator import ModelSelectionReportGenerator
        from app.services.agent.model_types import (
            ModelRecommendation, ModelArchitecture, TrainingStrategy,
            VertexAIProduct, HyperparameterConfig, DatasetProfile
        )
        from app.services.agent.types import ProblemAnalysis, ProblemType, DataType

        # Create test problem analysis
        problem_analysis = ProblemAnalysis(
            problem_type=ProblemType.CLASSIFICATION,
            data_type=DataType.TABULAR,
            domain="Healthcare",
            suggested_metrics=["accuracy", "precision", "recall", "f1_score", "roc_auc"],
            complexity_score=0.65,
            confidence=0.92,
            reasoning="Binary classification problem to predict disease diagnosis based on patient vitals and lab results.",
            is_labeled=True,
            num_classes=2,
            target_variable="diagnosis"
        )

        # Create test dataset profile
        dataset_profile = DatasetProfile(
            num_samples=1000,
            num_features=20,
            num_classes=2,
            num_numeric_features=15,
            num_categorical_features=5,
            missing_value_ratio=0.02,
            class_imbalance_ratio=0.65,
            dimensionality_ratio=0.02,
            dataset_size_mb=5.2
        )

        # Create test model recommendation
        model_recommendation = ModelRecommendation(
            architecture=ModelArchitecture.XGBOOST,
            training_strategy=TrainingStrategy.CUSTOM,
            vertex_product=VertexAIProduct.CUSTOM_TRAINING,
            hyperparameters=HyperparameterConfig(
                learning_rate=0.1,
                batch_size=32,
                max_iterations=100,
                early_stopping_patience=10,
                model_specific={
                    "train_budget_milli_node_hours": 200,  # 12 minutes
                    "max_depth": 6,
                    "n_estimators": 100
                }
            ),
            confidence=0.88,
            reasoning="XGBoost is ideal for tabular classification with 1000 samples. Provides excellent performance-to-cost ratio.",
            estimated_training_time_minutes=12,
            estimated_cost_usd=8.0,
            requires_gpu=False,
            supports_incremental_training=True,
            interpretability_score=0.7
        )

        # Create test training results
        training_results = {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87,
            "roc_auc": 0.92,
            "training_duration_seconds": 680
        }

        # Create report generator
        try:
            report_gen = ModelSelectionReportGenerator(gcs_bucket_name="test-bucket")
            has_gcs = True
        except Exception as e:
            print(f"⚠️  GCS not available: {e}")
            print("   Running in local-only mode")
            has_gcs = False

        print("\n🔄 Generating model selection report...")
        print("   (This uses Gemini AI - requires GEMINI_API_KEY)")

        report = await report_gen.generate_report(
            dataset_id="test_classification_001",
            problem_analysis=problem_analysis,
            dataset_profile=dataset_profile,
            model_recommendation=model_recommendation,
            training_results=training_results,
            upload_to_gcs=has_gcs
        )

        # Save report locally
        report_path = Path("./test_outputs/model_selection_report.md")
        with open(report_path, 'w') as f:
            f.write(report['report_markdown'])

        report_json_path = Path("./test_outputs/model_selection_report.json")
        with open(report_json_path, 'w') as f:
            json.dump({
                k: v for k, v in report.items() if k != 'report_markdown'
            }, f, indent=2)

        print(f"\n💾 Report saved to:")
        print(f"   Markdown: {report_path}")
        print(f"   JSON: {report_json_path}")

        if 'gcs_uri' in report:
            print(f"\n☁️  Report uploaded to: {report['gcs_uri']}")

        return report

    except Exception as e:
        print(f"\n❌ Model Selection Report Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests."""
    print("=" * 80)
    print("🧪 CONFUSION MATRIX & MODEL SELECTION REPORT TESTING")
    print("=" * 80)

    # Create test data
    metadata_path, model_path, test_data_path = await create_test_model_and_data()

    # Test 1: Confusion Matrix Generator
    cm_results = await test_confusion_matrix_generator(
        metadata_path, model_path, test_data_path
    )

    # Test 2: Model Selection Report Generator
    report_results = await test_model_selection_report()

    # Summary
    print("\n" + "=" * 80)
    print("✅ TESTING COMPLETE")
    print("=" * 80)
    print("\n📂 All outputs saved to: ./test_outputs/")
    print("\n📊 Generated Files:")
    print("   - test_outputs/model.pkl (test model)")
    print("   - test_outputs/test_data.pkl (test data)")
    print("   - test_outputs/metadata.json (metadata)")
    print("   - test_outputs/confusion_matrix_results.json (metrics)")
    print("   - test_outputs/plots/confusion_matrix.png (visualization)")
    print("   - test_outputs/model_selection_report.md (AI report)")
    print("   - test_outputs/model_selection_report.json (report metadata)")

    print("\n💡 Next Steps:")
    print("   1. Review the generated reports in ./test_outputs/")
    print("   2. Check the confusion matrix visualization")
    print("   3. Read the AI-generated model selection explanation")
    print("   4. Set up GCS credentials to enable cloud uploads")

    print("\n🚀 To use with real models:")
    print("   1. Run your E2E pipeline to train a model")
    print("   2. Get the metadata.json path from training output")
    print("   3. Use ConfusionMatrixGenerator.generate_confusion_matrix()")
    print("   4. Use ModelSelectionReportGenerator.generate_report()")

    return cm_results, report_results


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
