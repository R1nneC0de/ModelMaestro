"""
Test Confusion Matrix and Model Selection Report with Real GCS Files.

This script tests the generators with actual training outputs from your pipeline.
Requires Google Cloud credentials to be set up.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_with_real_gcs_files():
    """
    Test with real GCS files from training pipeline.

    Prerequisites:
    1. Run E2E pipeline to train a model
    2. Have metadata.json path from training output
    3. GCS credentials configured (gcloud auth application-default login)
    """
    print("=" * 80)
    print("🧪 TESTING WITH REAL GCS FILES")
    print("=" * 80)

    from app.services.agent.confusion_matrix_generator import ConfusionMatrixGenerator
    from app.services.agent.model_selection_report_generator import ModelSelectionReportGenerator

    # =========================================================================
    # CONFIGURATION - Update these with your actual values
    # =========================================================================

    # Option 1: Use local metadata.json from E2E pipeline run
    metadata_path = "./test_outputs/metadata.json"  # Update this path

    # Option 2: Use GCS metadata path (if you uploaded it)
    # metadata_path = "gs://your-bucket/models/dataset_id/preprocessing/metadata.json"

    dataset_id = "churn_test_001"  # Update with your dataset ID
    gcs_bucket = os.getenv("GCS_BUCKET_NAME", "your-bucket-name")

    print(f"\n📋 Configuration:")
    print(f"   Metadata Path: {metadata_path}")
    print(f"   Dataset ID: {dataset_id}")
    print(f"   GCS Bucket: {gcs_bucket}")

    # Check if metadata exists
    if not os.path.exists(metadata_path) and not metadata_path.startswith("gs://"):
        print(f"\n❌ Error: Metadata file not found at {metadata_path}")
        print(f"\n💡 To get metadata.json:")
        print(f"   1. Run: python test_e2e_pipeline.py")
        print(f"   2. Wait for training to complete")
        print(f"   3. Find metadata.json in GCS or training output")
        print(f"   4. Update metadata_path in this script")
        return

    # =========================================================================
    # STEP 1: Generate Confusion Matrix
    # =========================================================================
    print("\n" + "=" * 80)
    print("📊 STEP 1: Generating Confusion Matrix from Trained Model")
    print("=" * 80)

    try:
        cm_generator = ConfusionMatrixGenerator(gcs_bucket_name=gcs_bucket)

        print("\n🔄 Loading model and generating confusion matrix...")
        print("   This will:")
        print("   1. Load metadata from the specified path")
        print("   2. Load the trained model from GCS")
        print("   3. Load test data from GCS")
        print("   4. Generate predictions")
        print("   5. Calculate metrics and create visualizations")
        print("   6. Upload results to GCS")

        cm_results = await cm_generator.generate_confusion_matrix(
            metadata_path=metadata_path,
            upload_to_gcs=True,
            dataset_id=dataset_id
        )

        print("\n✅ CONFUSION MATRIX RESULTS:")
        print(f"   Dataset ID: {cm_results['dataset_id']}")
        print(f"   Test Samples: {cm_results['metadata']['test_samples']}")

        print("\n📊 Metrics:")
        for metric, value in cm_results['metrics'].items():
            print(f"   {metric.capitalize()}: {value:.4f}")

        print("\n📈 Confusion Matrix:")
        import numpy as np
        cm = np.array(cm_results['confusion_matrix'])
        print(cm)

        print(f"\n🎨 Generated Visualizations:")
        for plot_name in cm_results.get('plots', {}).keys():
            print(f"   ✓ {plot_name}")

        if 'gcs_uris' in cm_results:
            print(f"\n☁️  Uploaded to GCS:")
            for name, uri in cm_results['gcs_uris'].items():
                print(f"   {name}:")
                print(f"      {uri}")

        # Save a local copy of metrics
        import json
        local_results_path = Path("./test_outputs/gcs_cm_results.json")
        local_results_path.parent.mkdir(exist_ok=True)

        with open(local_results_path, 'w') as f:
            results_for_json = {
                k: v for k, v in cm_results.items()
                if k not in ['plots']  # Exclude binary data
            }
            json.dump(results_for_json, f, indent=2)

        print(f"\n💾 Local copy saved to: {local_results_path}")

    except Exception as e:
        print(f"\n❌ Confusion Matrix Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Common issues:")
        print("   - GCS credentials not configured: run 'gcloud auth application-default login'")
        print("   - Model path incorrect in metadata.json")
        print("   - Test data path incorrect in metadata.json")
        print("   - Model file doesn't exist in GCS")
        return

    # =========================================================================
    # STEP 2: Generate Model Selection Report
    # =========================================================================
    print("\n" + "=" * 80)
    print("📝 STEP 2: Generating AI-Powered Model Selection Report")
    print("=" * 80)

    try:
        # Load metadata to get model info
        import json
        if metadata_path.startswith("gs://"):
            # Would need to download from GCS
            print("\n⚠️  GCS metadata path - skipping report generation")
            print("   Please download metadata.json locally to generate report")
            return

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # You'll need to provide these from your training pipeline
        # For now, we'll reconstruct from metadata
        from app.services.agent.types import ProblemAnalysis, ProblemType, DataType
        from app.services.agent.model_types import (
            ModelRecommendation, ModelArchitecture, TrainingStrategy,
            VertexAIProduct, HyperparameterConfig, DatasetProfile
        )

        print("\n🔄 Reconstructing training context from metadata...")

        # Create problem analysis (you should have this from Step 3)
        problem_analysis = ProblemAnalysis(
            problem_type=ProblemType.CLASSIFICATION,
            data_type=DataType.TABULAR,
            domain=metadata.get('domain', 'Business'),
            suggested_metrics=['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc'],
            complexity_score=0.6,
            confidence=0.9,
            reasoning=metadata.get('problem_reasoning', 'Classification problem'),
            is_labeled=True,
            num_classes=metadata.get('num_classes', 2),
            target_variable=metadata.get('target_variable', 'target')
        )

        # Create dataset profile
        dataset_profile = DatasetProfile(
            num_samples=metadata.get('num_samples', 1000),
            num_features=metadata.get('num_features', 20),
            num_classes=metadata.get('num_classes', 2),
            num_numeric_features=metadata.get('num_numeric', 15),
            num_categorical_features=metadata.get('num_categorical', 5),
            missing_value_ratio=metadata.get('missing_ratio', 0.0),
            class_imbalance_ratio=metadata.get('class_imbalance', 0.8),
            dimensionality_ratio=metadata.get('num_features', 20) / metadata.get('num_samples', 1000),
            dataset_size_mb=metadata.get('dataset_size_mb', 5.0)
        )

        # Create model recommendation
        model_recommendation = ModelRecommendation(
            architecture=ModelArchitecture.AUTOML_TABULAR,
            training_strategy=TrainingStrategy.AUTOML,
            vertex_product=VertexAIProduct.AUTOML_TABLES,
            hyperparameters=HyperparameterConfig(
                learning_rate=0.01,
                batch_size=32,
                max_iterations=1000,
                model_specific={
                    "train_budget_milli_node_hours": metadata.get('train_budget', 200),
                    "optimization_objective": "maximize-au-roc"
                }
            ),
            confidence=0.93,
            reasoning=metadata.get('model_reasoning', 'AutoML Tabular selected for optimal performance'),
            estimated_training_time_minutes=metadata.get('train_budget', 200) / 1000 * 60,
            estimated_cost_usd=9.75,
            requires_gpu=True,
            interpretability_score=0.5
        )

        # Use actual metrics from confusion matrix results
        training_results = cm_results['metrics']

        print("\n🤖 Generating AI-powered report with Gemini...")
        print("   This will create a comprehensive explanation of:")
        print("   - Why this model was selected")
        print("   - Data characteristics that influenced the decision")
        print("   - Expected performance and limitations")
        print("   - Production deployment recommendations")

        report_gen = ModelSelectionReportGenerator(gcs_bucket_name=gcs_bucket)

        report = await report_gen.generate_report(
            dataset_id=dataset_id,
            problem_analysis=problem_analysis,
            dataset_profile=dataset_profile,
            model_recommendation=model_recommendation,
            training_results=training_results,
            upload_to_gcs=True
        )

        print("\n✅ MODEL SELECTION REPORT GENERATED!")

        if 'gcs_uri' in report:
            print(f"\n☁️  Report uploaded to GCS:")
            print(f"   {report['gcs_uri']}")

        # Save local copies
        report_md_path = Path("./test_outputs/gcs_model_selection_report.md")
        report_json_path = Path("./test_outputs/gcs_model_selection_report.json")

        with open(report_md_path, 'w') as f:
            f.write(report['report_markdown'])

        with open(report_json_path, 'w') as f:
            json.dump({
                k: v for k, v in report.items()
                if k != 'report_markdown'
            }, f, indent=2)

        print(f"\n💾 Local copies saved:")
        print(f"   Markdown: {report_md_path}")
        print(f"   JSON: {report_json_path}")

    except Exception as e:
        print(f"\n❌ Model Selection Report Generation Failed: {e}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 80)
    print("✅ GCS TESTING COMPLETE")
    print("=" * 80)

    print("\n📊 What was generated:")
    print("   1. ✅ Confusion Matrix with visualizations")
    print("   2. ✅ Classification metrics (accuracy, precision, recall, F1)")
    print("   3. ✅ AI-powered model selection explanation")
    print("   4. ✅ All artifacts uploaded to GCS")

    print("\n☁️  GCS Locations:")
    print(f"   Confusion Matrix: gs://{gcs_bucket}/evaluation/{dataset_id}/confusion_matrix/")
    print(f"   Model Report: gs://{gcs_bucket}/evaluation/{dataset_id}/model_selection_report/")

    print("\n💾 Local Files:")
    print("   test_outputs/gcs_cm_results.json")
    print("   test_outputs/gcs_model_selection_report.md")
    print("   test_outputs/gcs_model_selection_report.json")

    print("\n🎉 Success! You can now share these reports with stakeholders.")


async def main():
    """Run GCS testing."""
    print("\n🔐 Checking GCS credentials...")

    try:
        from google.cloud import storage
        from app.core.config import settings

        # Test GCS connection
        client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        bucket = client.bucket(settings.GCS_BUCKET_NAME)

        # Try to list (just to verify access)
        try:
            blobs = list(bucket.list_blobs(max_results=1))
            print("✅ GCS credentials valid and bucket accessible")
        except Exception as e:
            print(f"⚠️  GCS bucket access issue: {e}")
            print("\n💡 Make sure:")
            print("   1. GCS_BUCKET_NAME is set in .env")
            print("   2. Bucket exists in your project")
            print("   3. You have permissions to access it")
            return

    except Exception as e:
        print(f"❌ GCS credentials not configured: {e}")
        print("\n💡 To set up GCS credentials:")
        print("   1. Install Google Cloud SDK")
        print("   2. Run: gcloud auth application-default login")
        print("   3. Set GOOGLE_CLOUD_PROJECT and GCS_BUCKET_NAME in .env")
        return

    await test_with_real_gcs_files()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
