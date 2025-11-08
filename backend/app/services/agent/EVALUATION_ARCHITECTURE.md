# Model Evaluation Architecture

## Overview

The model evaluation system is designed with a modular architecture that separates concerns into focused, reusable components. This design follows SOLID principles and makes the codebase maintainable and testable.

## Module Structure

### Core Evaluation Module

**`evaluator.py`** - Main orchestrator
- `ModelEvaluator`: Coordinates the evaluation process
- `EvaluationResult`: Data class containing complete evaluation results
- Delegates to specialized modules for specific tasks

### Metrics Calculation

**`metrics_calculator.py`** - Metric computation
- `ClassificationMetricsCalculator`: Computes accuracy, precision, recall, F1, ROC-AUC, etc.
- `RegressionMetricsCalculator`: Computes RMSE, MAE, R², residual statistics, etc.
- Pure functions with no side effects

### Baseline Calculation

**`baseline_calculator.py`** - Baseline metrics
- `BaselineCalculator`: Computes baseline metrics for comparison
- `BaselineMetrics`: Data class for baseline information
- Classification: Majority class baseline
- Regression: Mean prediction baseline

### Threshold Checking

**`threshold_checker.py`** - Validation logic
- `ThresholdChecker`: Validates metrics against acceptance thresholds
- `SanityChecker`: Performs problem-specific sanity checks
- Handles baseline-relative thresholds (e.g., "0.9*baseline_rmse")

### Decision Making

**`evaluation_decision.py`** - Decision logic and reasoning
- `EvaluationDecision`: Enum for ACCEPT/REJECT outcomes
- `DecisionMaker`: Makes final evaluation decision
- `ReasoningGenerator`: Generates human-readable explanations
- `RecommendationGenerator`: Provides improvement suggestions

### Report Generation

**`evaluation_report.py`** - Report orchestrator
- `EvaluationReportGenerator`: Coordinates report generation and storage
- Delegates to plot generators and formatters
- Handles GCS storage

**`plot_generator.py`** - Visualization
- `ClassificationPlotGenerator`: Confusion matrix, ROC curve, PR curve
- `RegressionPlotGenerator`: Residual plots, predicted vs actual, distributions
- Returns plots as bytes for storage

**`report_formatter.py`** - Report formatting
- `MarkdownReportFormatter`: Generates markdown reports
- `HTMLReportFormatter`: Generates styled HTML reports with embedded plots
- `JSONReportFormatter`: Generates JSON summaries
- Each formatter is independent and reusable

## Data Flow

```
ModelEvaluator.evaluate_model()
    ↓
1. Calculate Metrics
    → ClassificationMetricsCalculator or RegressionMetricsCalculator
    ↓
2. Calculate Baselines
    → BaselineCalculator
    ↓
3. Check Thresholds
    → ThresholdChecker.check_thresholds()
    ↓
4. Perform Sanity Checks
    → SanityChecker.perform_sanity_checks()
    ↓
5. Make Decision
    → DecisionMaker.make_decision()
    ↓
6. Generate Reasoning
    → ReasoningGenerator.generate_reasoning()
    ↓
7. Generate Recommendations
    → RecommendationGenerator.generate_recommendations()
    ↓
Return EvaluationResult

EvaluationReportGenerator.generate_report()
    ↓
1. Generate Plots
    → ClassificationPlotGenerator or RegressionPlotGenerator
    ↓
2. Format Reports
    → MarkdownReportFormatter
    → HTMLReportFormatter
    → JSONReportFormatter
    ↓
3. Store in GCS
    → _store_report()
    ↓
Return report URI
```

## Design Principles

### Single Responsibility
Each module has one clear purpose:
- Metrics calculation
- Baseline computation
- Threshold checking
- Decision making
- Plot generation
- Report formatting

### Open/Closed Principle
Easy to extend without modifying existing code:
- Add new metric calculators for different problem types
- Add new plot generators for custom visualizations
- Add new report formatters (e.g., PDF, LaTeX)

### Dependency Inversion
High-level modules depend on abstractions:
- `ModelEvaluator` uses calculator interfaces
- `EvaluationReportGenerator` uses formatter interfaces
- Easy to mock for testing

### Testability
Each module can be tested independently:
- Pure functions for calculations
- Static methods for stateless operations
- Clear inputs and outputs

## Usage Examples

### Basic Evaluation

```python
from app.services.agent import ModelEvaluator, ProblemType

evaluator = ModelEvaluator()
result = evaluator.evaluate_model(
    training_output=training_output,
    y_true=y_true,
    y_pred=y_pred,
    y_pred_proba=y_pred_proba,
    problem_type=ProblemType.CLASSIFICATION
)

print(f"Decision: {result.decision}")
print(f"Primary Metric: {result.primary_metric_value}")
```

### Generate Report

```python
from app.services.agent import EvaluationReportGenerator

report_gen = EvaluationReportGenerator(storage_client=gcs_client)
report_uri = await report_gen.generate_report(
    evaluation_result=result,
    training_output=training_output,
    problem_type=ProblemType.CLASSIFICATION,
    dataset_id="dataset_123",
    y_true=y_true,
    y_pred=y_pred,
    y_pred_proba=y_pred_proba
)
```

### Use Individual Components

```python
from app.services.agent import (
    ClassificationMetricsCalculator,
    ThresholdChecker,
    ClassificationPlotGenerator
)

# Calculate metrics
metrics = ClassificationMetricsCalculator.calculate(y_true, y_pred, y_pred_proba)

# Check thresholds
checks = ThresholdChecker.check_thresholds(metrics, thresholds, baseline)

# Generate plots
plots = ClassificationPlotGenerator.generate_plots(y_true, y_pred, y_pred_proba)
```

## Benefits

1. **Maintainability**: Each module is small and focused
2. **Testability**: Easy to unit test individual components
3. **Reusability**: Components can be used independently
4. **Extensibility**: Easy to add new functionality
5. **Readability**: Clear separation of concerns
6. **Performance**: Can optimize individual components
7. **Debugging**: Easy to isolate issues

## Future Enhancements

Potential additions that fit the modular design:

1. **New Metrics**: Add domain-specific metrics
2. **Custom Plots**: Add specialized visualizations
3. **Report Formats**: Add PDF, LaTeX, or interactive reports
4. **Threshold Strategies**: Add adaptive threshold logic
5. **Decision Policies**: Add custom decision-making rules
6. **Comparison Reports**: Compare multiple models
7. **Time-Series Metrics**: Add forecasting-specific metrics
