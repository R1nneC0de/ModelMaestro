# Data Processor Architecture

## Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                      types.py                                │
│  (ProblemAnalysis, ProblemType, DataType)                   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼──────┐
│ data_quality.py│  │data_splitter.py│  │             │
│   (359 lines)  │  │  (214 lines)   │  │             │
│                │  │                │  │             │
│ - Validator    │  │ - Splitter     │  │             │
│ - Report       │  │ - DataSplit    │  │             │
│ - Strategy     │  │                │  │             │
└────────────────┘  └────────┬───────┘  │             │
                             │          │             │
                             │          │             │
                    ┌────────▼──────────▼─────┐       │
                    │  feature_engineer.py    │       │
                    │     (313 lines)         │       │
                    │                         │       │
                    │  - FeatureEngineer      │       │
                    │  - ProcessedData        │       │
                    └────────┬────────────────┘       │
                             │                        │
                             │                        │
                    ┌────────▼────────────────────────▼─┐
                    │     data_processor.py             │
                    │        (323 lines)                │
                    │                                   │
                    │  - DataProcessor (orchestrator)   │
                    │  - GCS integration                │
                    │  - Complete pipeline              │
                    └───────────────────────────────────┘
```

## Processing Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DataProcessor.process_and_store()         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Validate Data Quality                                │
│ → DataQualityValidator.validate_data_quality()               │
│   - Check missing values, duplicates, invalid values         │
│   - Assess class balance                                     │
│   - Calculate severity score                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Determine Processing Strategy                        │
│ → DataQualityValidator.determine_processing_strategy()       │
│   - Choose imputation method                                 │
│   - Identify columns to drop                                 │
│   - Decide on outlier handling                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Apply Preprocessing                                  │
│ → DataProcessor._apply_preprocessing()                       │
│   - Remove duplicates                                        │
│   - Handle missing values (drop/impute)                      │
│   - Cap outliers                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Split Data                                           │
│ → DataSplitter.split_data()                                  │
│   - 70/15/15 train/val/test split                           │
│   - Stratified for classification                            │
│   - Random for other tasks                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Feature Engineering                                  │
│ → FeatureEngineer.process_features()                         │
│   - Tabular: StandardScaler + OneHotEncoder                  │
│   - Text: Metadata preparation                               │
│   - Image: Metadata preparation                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Upload to GCS                                        │
│ → DataProcessor._upload_to_gcs()                             │
│   - Upload train.pkl, val.pkl, test.pkl                     │
│   - Upload preprocessing pipeline                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 7: Store Metadata                                       │
│ → DataProcessor._store_metadata()                            │
│   - Save quality report, strategy, split info               │
│   - Save feature info and GCS paths                          │
└─────────────────────────────────────────────────────────────┘
```

## File Organization

```
backend/app/services/agent/
├── data_quality.py          # Quality validation (359 lines)
│   ├── DataQualityValidator
│   ├── DataQualityReport
│   ├── ProcessingStrategy
│   ├── DataQualityIssue (enum)
│   └── MissingValueStrategy (enum)
│
├── data_splitter.py         # Data splitting (214 lines)
│   ├── DataSplitter
│   └── DataSplit
│
├── feature_engineer.py      # Feature engineering (313 lines)
│   ├── FeatureEngineer
│   └── ProcessedData
│
└── data_processor.py        # Main orchestrator (323 lines)
    └── DataProcessor
```

## Key Design Decisions

1. **Single Responsibility**: Each module handles one aspect of data processing
2. **Hierarchical Dependencies**: Clean dependency tree with no circular imports
3. **Reusability**: Components can be used independently
4. **Testability**: Each module can be unit tested in isolation
5. **Maintainability**: Smaller files (~200-350 lines each) are easier to understand

## Total Lines of Code

- **Before modularization**: 1,154 lines in single file
- **After modularization**: 1,209 lines across 4 files
- **Overhead**: 55 lines (4.5%) for better organization
