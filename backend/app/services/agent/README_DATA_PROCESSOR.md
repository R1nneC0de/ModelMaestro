# Data Processor Module

The Data Processor component has been modularized into four focused modules for better maintainability and clarity.

## Module Structure

### 1. `data_quality.py` (359 lines)
**Purpose**: Data quality validation and preprocessing strategy determination

**Key Classes**:
- `DataQualityValidator`: Validates data quality and identifies issues
- `DataQualityReport`: Report of quality assessment results
- `ProcessingStrategy`: Strategy for handling data issues
- `DataQualityIssue`: Enum of possible quality issues
- `MissingValueStrategy`: Enum of missing value handling strategies

**Responsibilities**:
- Check for missing values, duplicates, invalid values
- Assess class balance for classification problems
- Determine optimal preprocessing strategy based on data characteristics
- Calculate severity scores and provide recommendations

### 2. `data_splitter.py` (214 lines)
**Purpose**: Split data into train/validation/test sets

**Key Classes**:
- `DataSplitter`: Handles data splitting with stratification support
- `DataSplit`: Container for split data and metadata

**Responsibilities**:
- Random splitting for general cases
- Stratified splitting for classification tasks (maintains class distribution)
- Default 70/15/15 train/val/test split
- Configurable ratios and random seed for reproducibility

### 3. `feature_engineer.py` (313 lines)
**Purpose**: Feature engineering pipelines for different data types

**Key Classes**:
- `FeatureEngineer`: Processes features based on data type
- `ProcessedData`: Container for processed data and metadata

**Responsibilities**:
- **Tabular data**: StandardScaler normalization, OneHotEncoder for categorical features
- **Text data**: Metadata preparation for Vertex AI processing
- **Image data**: Metadata preparation for Vertex AI processing
- Pipeline creation and feature name extraction

### 4. `data_processor.py` (323 lines)
**Purpose**: Main orchestrator with GCS integration

**Key Classes**:
- `DataProcessor`: Complete pipeline orchestrator

**Responsibilities**:
- Orchestrate the complete processing pipeline
- Apply preprocessing strategies (imputation, outlier handling, duplicate removal)
- Upload processed data to Google Cloud Storage
- Store processing metadata as JSON
- Coordinate between validator, splitter, and feature engineer

## Usage Example

```python
from app.services.agent import DataProcessor, ProblemAnalysis

# Initialize processor
processor = DataProcessor(bucket_name="my-bucket")

# Process and store data
result = await processor.process_and_store(
    dataset_id="ds_123",
    data=my_dataframe,
    analysis=problem_analysis,
    target_column="target"
)

# Access results
print(f"Quality: {result['quality_report'].is_valid}")
print(f"Split: {result['split_info']}")
print(f"GCS paths: {result['gcs_paths']}")
```

## Benefits of Modularization

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Easier Testing**: Individual components can be tested in isolation
3. **Better Maintainability**: Smaller files are easier to understand and modify
4. **Reusability**: Components can be used independently if needed
5. **Clearer Dependencies**: Import structure shows relationships between components

## Requirements

The data processor requires the following requirements from task 5:

- **Requirement 7.1**: Data quality validation and train/val/test splitting
- **Requirement 8.1**: Missing value handling and GCS integration
- **Requirement 8.2**: Image data pipeline support
- **Requirement 8.3**: Text data pipeline support
- **Requirement 8.4**: Tabular data pipeline with normalization
