# Confusion Matrix & Model Selection Report Guide

## Overview

This guide explains how to use the new **Confusion Matrix Generator** and **Model Selection Report Generator** to create comprehensive evaluation artifacts after training completes.

## What's Been Added

### 1. **Confusion Matrix Generator** (`confusion_matrix_generator.py`)
- Loads trained models from GCS or local storage
- Generates confusion matrices and classification reports
- Creates professional visualizations (confusion matrix, normalized, ROC curves)
- Calculates accuracy, precision, recall, F1-score
- Uploads results to GCS automatically

### 2. **Model Selection Report Generator** (`model_selection_report_generator.py`)
- AI-powered explanations using Gemini
- Generates comprehensive Markdown reports explaining:
  - Why the model was selected
  - Data characteristics that influenced the decision
  - Performance expectations
  - Production deployment recommendations
- Displays beautifully formatted reports in terminal
- Uploads to GCS for stakeholder review

### 3. **Test Script** (`test_confusion_matrix_and_report.py`)
- Complete end-to-end testing
- Works without GCS credentials (local mode)
- Creates synthetic data for testing
- Clear examples for production usage

---

## Quick Start - Test Locally

### Step 1: Install Dependencies (if not already done)

```powershell
cd backend
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

Create or update `backend/.env`:

```
GEMINI_API_KEY=your-actual-api-key-here
GOOGLE_CLOUD_PROJECT=test-project
GCS_BUCKET_NAME=test-bucket
ENVIRONMENT=development
```

### Step 3: Run the Test Script

```powershell
cd backend
python test_confusion_matrix_and_report.py
```

### Expected Output

The script will:
1. ✅ Create a test model and synthetic data
2. ✅ Generate confusion matrix with visualizations
3. ✅ Create AI-powered model selection report
4. ✅ Save all outputs to `./test_outputs/` directory
5. ✅ Display formatted reports in terminal

### Generated Files

After running, check `backend/test_outputs/`:
- `model.pkl` - Test trained model
- `test_data.pkl` - Test dataset
- `metadata.json` - Metadata file
- `confusion_matrix_results.json` - Metrics and confusion matrix
- `plots/confusion_matrix.png` - Confusion matrix visualization
- `plots/confusion_matrix_normalized.png` - Normalized version
- `plots/roc_curve.png` - ROC curve (if binary classification)
- `model_selection_report.md` - AI-generated explanation report
- `model_selection_report.json` - Report metadata

---

## Production Usage

### After Training Completes

When your E2E pipeline completes training, you'll have:
- `metadata.json` with paths to model and test data
- Trained model stored in GCS
- Test data stored in GCS

### Generate Confusion Matrix

```python
import asyncio
from app.services.agent.confusion_matrix_generator import ConfusionMatrixGenerator

async def generate_cm():
    generator = ConfusionMatrixGenerator(gcs_bucket_name="your-bucket")

    results = await generator.generate_confusion_matrix(
        metadata_path="path/to/metadata.json",  # or GCS path
        upload_to_gcs=True
    )

    print(f"Accuracy: {results['metrics']['accuracy']:.3f}")
    print(f"Confusion Matrix:\n{results['confusion_matrix']}")
    print(f"Plots uploaded to: {results['gcs_uris']}")

asyncio.run(generate_cm())
```

### Generate Model Selection Report

```python
import asyncio
from app.services.agent.model_selection_report_generator import ModelSelectionReportGenerator
from app.services.agent.model_types import ModelRecommendation, DatasetProfile
from app.services.agent.types import ProblemAnalysis

async def generate_report():
    report_gen = ModelSelectionReportGenerator(gcs_bucket_name="your-bucket")

    # These come from your training pipeline
    problem_analysis = ...  # From Step 3
    dataset_profile = ...   # From Step 6
    model_recommendation = ...  # From Step 7
    training_results = ...  # From training completion

    report = await report_gen.generate_report(
        dataset_id="churn_prediction_001",
        problem_analysis=problem_analysis,
        dataset_profile=dataset_profile,
        model_recommendation=model_recommendation,
        training_results=training_results,
        upload_to_gcs=True
    )

    # Report automatically displayed in terminal
    # Also uploaded to GCS
    print(f"Report uploaded to: {report['gcs_uri']}")

asyncio.run(generate_report())
```

### Integration with E2E Pipeline

Add to the end of `test_e2e_pipeline.py`:

```python
# After training completes...

print("\n📊 STEP 10: Generating Evaluation Artifacts...")

# Generate confusion matrix
from app.services.agent.confusion_matrix_generator import ConfusionMatrixGenerator

cm_generator = ConfusionMatrixGenerator()
cm_results = await cm_generator.generate_confusion_matrix(
    metadata_path=metadata_path,
    upload_to_gcs=True,
    dataset_id=dataset_id
)

print(f"✅ Confusion Matrix Generated:")
print(f"   Accuracy: {cm_results['metrics']['accuracy']:.3f}")
print(f"   GCS URI: {cm_results['gcs_uris']['metrics']}")

# Generate model selection report
from app.services.agent.model_selection_report_generator import ModelSelectionReportGenerator

report_gen = ModelSelectionReportGenerator()
report = await report_gen.generate_report(
    dataset_id=dataset_id,
    problem_analysis=analysis,
    dataset_profile=dataset_profile,
    model_recommendation=recommendation,
    training_results={"accuracy": cm_results['metrics']['accuracy']},
    upload_to_gcs=True
)

print(f"✅ Model Selection Report Generated:")
print(f"   GCS URI: {report['gcs_uri']}")
```

---

## What the Reports Include

### Confusion Matrix Report

**Metrics:**
- Accuracy
- Precision (weighted)
- Recall (weighted)
- F1-Score (weighted)
- Per-class metrics

**Visualizations:**
- Confusion matrix (counts)
- Normalized confusion matrix (percentages)
- ROC curve (binary classification)
- Precision-Recall curve (if available)

**Uploaded to GCS:**
- `evaluation/{dataset_id}/confusion_matrix/{timestamp}/metrics.json`
- `evaluation/{dataset_id}/confusion_matrix/{timestamp}/plots/*.png`

### Model Selection Report

**Sections:**
1. **Executive Summary** - High-level explanation
2. **Data Characteristics Analysis** - What about the data influenced the decision
3. **Model Selection Rationale** - Why this model vs alternatives
4. **Performance Expectations** - What to expect from the model
5. **Training Configuration Justification** - Why these hyperparameters
6. **Recommendations for Production** - Deployment best practices

**AI-Powered Insights:**
- Written by Gemini in professional, accessible language
- Data-driven and specific to your use case
- Includes practical recommendations
- Honest about limitations

**Uploaded to GCS:**
- `evaluation/{dataset_id}/model_selection_report/{timestamp}/report.md`
- `evaluation/{dataset_id}/model_selection_report/{timestamp}/report.json`

---

## Example Output

### Confusion Matrix Terminal Output

```
📊 Confusion Matrix Generated:
   Accuracy: 0.874
   Precision: 0.865
   Recall: 0.884
   F1-Score: 0.874

📊 Confusion Matrix:
[[85  7]
 [18 90]]

🎨 Generated 3 visualization plots
   - confusion_matrix
   - confusion_matrix_normalized
   - roc_curve

☁️  Uploaded to GCS:
   metrics: gs://your-bucket/evaluation/test_001/confusion_matrix/20231108_120000/metrics.json
   plot_confusion_matrix: gs://your-bucket/evaluation/test_001/confusion_matrix/20231108_120000/plots/confusion_matrix.png
```

### Model Selection Report Terminal Output

```
================================================================================
📊 MODEL SELECTION REPORT
================================================================================

# Model Selection Report

## Executive Summary

Selected **xgboost** for classification on a dataset with 1,000 samples and
20 features. This model was chosen based on dataset characteristics and optimal
performance-cost trade-offs, providing excellent accuracy with fast training times.

## Data Characteristics Analysis

The dataset contains 1,000 samples with 20 features (15 numeric, 5 categorical).
The problem complexity score of 0.65 indicates a moderately complex task. A class
imbalance ratio of 0.65 was detected, which XGBoost handles well through its
built-in class weighting mechanisms.

...

## Recommendations for Production

- **Monitor primary metrics**: Track accuracy on validation set weekly
- **Set up alerts**: Configure alerts if performance drops below 0.85
- **Regular retraining**: Consider retraining when data distribution shifts
- **A/B testing**: Compare against baseline model before full deployment
- **Explainability**: Use SHAP values for model interpretability

---
*Report generated automatically by ModelMaestro Agentic Platform*
================================================================================
```

---

## Troubleshooting

### Issue: "GCS credentials not found"

**Solution:** The generators work in two modes:

1. **Local Mode** (no GCS): Set `upload_to_gcs=False`
2. **Cloud Mode**: Set up GCS credentials:
   ```powershell
   gcloud auth application-default login
   ```

### Issue: "Model loading failed"

**Solution:** Check model path format:
- GCS: `gs://bucket-name/path/to/model.pkl`
- Local: `./path/to/model.pkl`
- The generator auto-detects the format

### Issue: "Gemini API error"

**Solution:**
1. Verify your `GEMINI_API_KEY` in `.env`
2. Get a key from: https://aistudio.google.com/app/apikey
3. The report generator falls back to template-based report if Gemini fails

### Issue: "Test script fails with import errors"

**Solution:**
```powershell
cd backend
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ **Test Locally**: Run `python test_confusion_matrix_and_report.py`
2. ✅ **Review Outputs**: Check `./test_outputs/` directory
3. ✅ **Set Up GCS**: Configure Google Cloud credentials for production
4. ✅ **Integrate**: Add generators to your E2E pipeline
5. ✅ **Share Reports**: Send stakeholders the GCS links to reports

---

## Files Added

```
backend/
├── app/services/agent/
│   ├── confusion_matrix_generator.py         # NEW
│   └── model_selection_report_generator.py   # NEW
└── test_confusion_matrix_and_report.py        # NEW
```

## Questions?

- Check the inline documentation in the source files
- Run the test script to see examples
- All functions have detailed docstrings

Happy model evaluation! 🎉
