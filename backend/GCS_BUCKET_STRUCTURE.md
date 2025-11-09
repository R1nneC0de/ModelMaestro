# GCS Bucket File Structure

## Overview

Your GCS bucket: `gs://agentic-workflow-477603-data/`

All files are organized by dataset ID (timestamp-based) for easy tracking and cleanup.

## Complete File Structure

```
gs://agentic-workflow-477603-data/
│
└── data/
    └── {dataset_id}/                    # e.g., churn_test_20251108_183410
        │
        ├── raw/                          # Original uploaded data
        │   └── original.csv              # Raw CSV file as uploaded
        │
        └── processed/                    # Processed data for training
            ├── train.pkl                 # Training data (features + labels)
            ├── val.pkl                   # Validation data (features + labels)
            ├── test.pkl                  # Test data (features + labels)
            ├── pipeline.pkl              # Preprocessing pipeline (scalers, encoders)
            └── combined_automl.csv       # Combined dataset for AutoML with ml_use column
```

## File Details

### 1. Raw Data Files

#### `raw/original.csv`
- **Purpose**: Backup of the original uploaded CSV file
- **Format**: CSV (comma-separated values)
- **Contains**: Unprocessed data exactly as uploaded
- **Used for**: 
  - Audit trail
  - Reprocessing if needed
  - Data lineage tracking
- **Size**: ~1-2 MB for your churn dataset

---

### 2. Processed Data Files

#### `processed/train.pkl`
- **Purpose**: Training dataset (70% of data)
- **Format**: Python pickle file
- **Contains**: 
  - `X_train`: Feature matrix (1139 samples × 27 features)
  - `y_train`: Target labels (1139 samples)
  - Preprocessed and ready for training
- **Used for**: 
  - Training the ML model
  - Custom training jobs
- **Size**: ~500 KB - 1 MB
- **Note**: Not used by AutoML (uses combined_automl.csv instead)

#### `processed/val.pkl`
- **Purpose**: Validation dataset (15% of data)
- **Format**: Python pickle file
- **Contains**: 
  - `X_val`: Feature matrix (245 samples × 27 features)
  - `y_val`: Target labels (245 samples)
- **Used for**: 
  - Hyperparameter tuning
  - Model selection during training
  - Early stopping decisions
- **Size**: ~100-200 KB
- **Note**: Not used by AutoML (uses combined_automl.csv instead)

#### `processed/test.pkl`
- **Purpose**: Test dataset (15% of data)
- **Format**: Python pickle file
- **Contains**: 
  - `X_test`: Feature matrix (245 samples × 27 features)
  - `y_test`: Target labels (245 samples)
- **Used for**: 
  - Final model evaluation
  - Unbiased performance metrics
  - Acceptance gate testing
- **Size**: ~100-200 KB
- **Note**: Not used by AutoML (uses combined_automl.csv instead)

#### `processed/pipeline.pkl`
- **Purpose**: Preprocessing pipeline
- **Format**: Python pickle file (scikit-learn Pipeline object)
- **Contains**: 
  - StandardScaler (for numeric features)
  - OneHotEncoder (for categorical features)
  - Feature names and transformations
  - All fitted parameters
- **Used for**: 
  - Transforming new data for predictions
  - Ensuring consistent preprocessing
  - Deployment (must be loaded with model)
- **Size**: ~50-100 KB
- **Critical**: Must be saved with model for production use

#### `processed/combined_automl.csv`
- **Purpose**: Combined dataset for AutoML training
- **Format**: CSV file
- **Contains**: 
  - All features (original, not preprocessed)
  - Target column (`churn`)
  - `ml_use` column: "TRAIN", "VALIDATE", or "TEST"
  - All 1629 rows (after dropping missing values)
- **Used for**: 
  - AutoML Tabular training
  - Vertex AI reads this file directly
  - Predefined data splits via `ml_use` column
- **Size**: ~200-300 KB
- **Why CSV**: AutoML requires CSV format, not pickle
- **Special**: Contains split information in `ml_use` column

---

## File Usage by Training Type

### AutoML Training (Current)
```
Uses:
✅ combined_automl.csv  → Main training file
❌ train.pkl           → Not used
❌ val.pkl             → Not used  
❌ test.pkl            → Not used
❌ pipeline.pkl        → Not used (AutoML does its own preprocessing)
```

### Custom Training (Future)
```
Uses:
❌ combined_automl.csv  → Not used
✅ train.pkl           → Training data
✅ val.pkl             → Validation data
✅ test.pkl            → Test data
✅ pipeline.pkl        → Preprocessing
```

---

## Data Flow

```
1. Upload CSV
   ↓
2. Save to: raw/original.csv
   ↓
3. Data Quality Check
   ↓
4. Split Data (70/15/15)
   ↓
5. Feature Engineering
   ↓
6. Save Processed Files:
   ├── train.pkl (for custom training)
   ├── val.pkl (for custom training)
   ├── test.pkl (for evaluation)
   ├── pipeline.pkl (for deployment)
   └── combined_automl.csv (for AutoML)
   ↓
7. Training (AutoML reads combined_automl.csv)
   ↓
8. Model saved by Vertex AI (separate location)
```

---

## Storage Costs

**Your current dataset (~1,600 rows)**:
- Total storage per training run: ~2-3 MB
- Monthly cost: < $0.01 USD
- Storage is very cheap!

**Cleanup Strategy**:
- Keep recent datasets (last 30 days)
- Delete old datasets to save space
- Each dataset folder is independent

---

## File Formats Explained

### Pickle (.pkl)
- **Pros**: 
  - Fast to read/write
  - Preserves Python objects exactly
  - Includes numpy arrays, pandas DataFrames
- **Cons**: 
  - Python-specific (can't use in other languages)
  - Not human-readable
  - Version-sensitive
- **Used for**: Internal Python processing

### CSV (.csv)
- **Pros**: 
  - Human-readable
  - Universal format
  - Easy to inspect
  - Required by AutoML
- **Cons**: 
  - Slower to read/write
  - Loses data types
  - Larger file size
- **Used for**: AutoML training, data inspection

---

## Special: The `ml_use` Column

In `combined_automl.csv`, the `ml_use` column tells AutoML how to split data:

```csv
customer_id,tenure,churn,ml_use
CUST001,12,No,TRAIN      ← Used for training
CUST002,24,Yes,TRAIN     ← Used for training
CUST003,6,No,VALIDATE    ← Used for validation
CUST004,36,Yes,TEST      ← Used for final testing
```

**Values**:
- `TRAIN`: 70% of data (1139 rows)
- `VALIDATE`: 15% of data (245 rows)
- `TEST`: 15% of data (245 rows)

**Why**: Ensures AutoML uses the exact same splits we defined, maintaining consistency.

---

## Accessing Files

### Via gsutil (Command Line)
```bash
# List all files
gsutil ls -r gs://agentic-workflow-477603-data/data/churn_test_20251108_183410/

# Download a file
gsutil cp gs://agentic-workflow-477603-data/data/churn_test_20251108_183410/processed/combined_automl.csv .

# View file size
gsutil du -h gs://agentic-workflow-477603-data/data/churn_test_20251108_183410/
```

### Via Python
```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('agentic-workflow-477603-data')

# List files
blobs = bucket.list_blobs(prefix='data/churn_test_20251108_183410/')
for blob in blobs:
    print(f"{blob.name} - {blob.size} bytes")

# Download a file
blob = bucket.blob('data/churn_test_20251108_183410/processed/combined_automl.csv')
blob.download_to_filename('local_file.csv')
```

### Via Google Cloud Console
1. Go to: https://console.cloud.google.com/storage/browser/agentic-workflow-477603-data
2. Navigate to: `data/churn_test_20251108_183410/`
3. Click any file to view or download

---

## Cleanup

### Delete Old Datasets
```bash
# Delete a specific dataset
gsutil -m rm -r gs://agentic-workflow-477603-data/data/churn_test_20251108_183410/

# Delete all datasets older than 30 days (be careful!)
# Use lifecycle rules in GCS console instead
```

### Lifecycle Rules (Recommended)
Set up automatic deletion in GCS console:
1. Go to bucket settings
2. Add lifecycle rule
3. Delete objects older than 30 days
4. Saves money automatically

---

## Summary

**Essential Files**:
1. `combined_automl.csv` - Used by AutoML for training
2. `test.pkl` - Used for final evaluation
3. `pipeline.pkl` - Needed for deployment

**Backup Files**:
4. `original.csv` - Original data backup
5. `train.pkl` - For custom training (future)
6. `val.pkl` - For custom training (future)

**Total Storage**: ~2-3 MB per dataset
**Cost**: Negligible (< $0.01/month)
