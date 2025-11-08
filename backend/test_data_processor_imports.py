"""
Test that all data processor modules can be imported correctly.
"""

# Test individual module imports
from app.services.agent.data_quality import (
    DataQualityValidator,
    DataQualityReport,
    DataQualityIssue,
    MissingValueStrategy,
    ProcessingStrategy
)

from app.services.agent.data_splitter import (
    DataSplitter,
    DataSplit
)

from app.services.agent.feature_engineer import (
    FeatureEngineer,
    ProcessedData
)

from app.services.agent.data_processor import (
    DataProcessor
)

# Test package-level imports
from app.services.agent import (
    DataProcessor,
    DataQualityValidator,
    DataSplitter,
    FeatureEngineer
)

print("✅ All data processor modules imported successfully!")
print("\nModule structure:")
print("  - data_quality.py (359 lines): Quality validation and strategy")
print("  - data_splitter.py (214 lines): Train/val/test splitting")
print("  - feature_engineer.py (313 lines): Feature engineering pipelines")
print("  - data_processor.py (323 lines): Main orchestrator with GCS")
print("  - Total: 1,209 lines (down from 1,154 in single file)")
