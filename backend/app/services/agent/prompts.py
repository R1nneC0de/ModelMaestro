"""
Prompt templates for agent operations.

This module contains all prompt templates used by the agent components
for interacting with Gemini models. Centralizing prompts makes them
easier to maintain, test, and version.
"""


class AnalyzerPrompts:
    """Prompt templates for the Problem Analyzer component."""

    PROBLEM_ANALYSIS = """You are an expert machine learning consultant analyzing a new ML problem.

Problem Description:
{problem_description}

Dataset Information:
- Data Type: {data_type_hint}
- Number of Samples: {num_samples}
- Is Labeled: {is_labeled}
- Sample Data Preview: {data_preview}

Analyze this problem and provide a comprehensive assessment. Consider:
1. What type of ML problem is this? (classification, regression, detection, etc.)
2. What is the data type? (image, text, tabular, time_series, multimodal)
3. What domain does this belong to? (medical, business, agriculture, finance, etc.)
4. What metrics would be most appropriate for evaluation?
5. How complex is this problem? (0.0 = very simple, 1.0 = very complex)
6. Is the data labeled? If not, what labeling strategy would work?
7. For classification: How many classes are there?
8. For regression/forecasting: What is the target variable?

Provide your analysis in the following JSON format:
{{
    "problem_type": "classification|regression|object_detection|image_segmentation|text_classification|sentiment_analysis|named_entity_recognition|time_series_forecasting|clustering|anomaly_detection|recommendation",
    "data_type": "image|text|tabular|time_series|multimodal",
    "domain": "brief domain description",
    "suggested_metrics": ["metric1", "metric2", "metric3"],
    "complexity_score": 0.0-1.0,
    "reasoning": "detailed explanation of your analysis",
    "confidence": 0.0-1.0,
    "is_labeled": true|false,
    "num_classes": number or null,
    "target_variable": "variable name" or null,
    "additional_insights": {{
        "key": "value"
    }}
}}"""

    DATA_TYPE_DETECTION = """Analyze the following dataset sample and determine the data type.

Sample Data:
{data_sample}

File Information:
- File Extensions: {file_extensions}
- Number of Files: {num_files}

Determine if this is:
- image: Photos, pictures, visual data
- text: Documents, articles, reviews, social media posts
- tabular: Structured data in rows/columns (CSV, database tables)
- time_series: Sequential data with timestamps
- multimodal: Combination of multiple data types

Respond with JSON:
{{
    "data_type": "image|text|tabular|time_series|multimodal",
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}}"""

    DOMAIN_IDENTIFICATION = """Based on the problem description and data characteristics, identify the domain.

Problem: {problem_description}
Data Type: {data_type}
Problem Type: {problem_type}

Common domains include:
- Healthcare/Medical
- Finance/Banking
- E-commerce/Retail
- Agriculture
- Manufacturing
- Education
- Transportation
- Social Media
- Entertainment
- Security/Fraud Detection
- Energy
- Real Estate
- Human Resources
- Marketing
- Customer Service

Respond with JSON:
{{
    "domain": "specific domain name",
    "confidence": 0.0-1.0,
    "reasoning": "why this domain"
}}"""

    PROBLEM_TYPE_CLASSIFICATION = """Classify this machine learning problem:

Problem: {problem_description}

Data Characteristics:
{data_characteristics}

What type of ML problem is this? Choose from:
- classification: Predicting discrete categories
- regression: Predicting continuous values
- object_detection: Detecting and locating objects in images
- image_segmentation: Segmenting images into regions
- text_classification: Categorizing text documents
- sentiment_analysis: Analyzing sentiment in text
- named_entity_recognition: Extracting entities from text
- time_series_forecasting: Predicting future values in sequences
- clustering: Grouping similar items
- anomaly_detection: Detecting unusual patterns
- recommendation: Recommending items to users

Respond with JSON:
{{
    "problem_type": "type",
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}}"""

    SYSTEM_INSTRUCTION = (
        "You are an expert ML consultant. Provide accurate, detailed analysis "
        "of machine learning problems. Be specific and actionable in your recommendations."
    )


class ModelSelectionPrompts:
    """Prompt templates for the Model Selector component."""

    MODEL_SELECTION = """You are an expert machine learning engineer selecting the optimal model for a training task.

## CRITICAL INSTRUCTIONS - CSV Data Analysis
Before making any model recommendation, you MUST:
1. **Carefully read ALL column titles** from the CSV dataset
2. **Examine a representative sample** (approximately 1/10) of the dataset rows
3. **Verify alignment** between the user's prompt and the actual data structure
4. **Ensure the suggested model** directly matches the user's stated goals and the data characteristics

Example: If the user asks to "predict house prices" but the CSV contains customer reviews, FLAG this mismatch and ask for clarification before proceeding.

## Context
{context}

## Dataset Sample Information
Column Names: {column_names}
Sample Data (10% of dataset):
{data_sample}

Total Rows: {total_rows}
Total Columns: {total_columns}

## Your Task
Review the problem analysis, dataset profile, actual CSV data sample, and rule-based recommendation. Then:

1. **VALIDATE DATA ALIGNMENT**: Confirm the user's prompt matches the CSV data structure
2. Determine if the rule-based recommendation is optimal given the ACTUAL data
3. Consider any user preferences for interpretability, cost, speed
4. Select the best model architecture and training strategy
5. Provide hyperparameter recommendations tailored to the specific dataset characteristics
6. Estimate training time and cost

## Available Model Architectures

### Tabular Data:
- **automl_tabular**: Fully automated with Vertex AI (best for complex problems, higher cost ~$19.50/hr)
- **xgboost**: Gradient boosting (excellent for most tabular tasks, cost-effective)
- **linear_regression/logistic_regression**: Simple, highly interpretable models
- **random_forest**: Ensemble method (good baseline, interpretable)
- **feedforward_nn**: Neural network for non-linear patterns

### Text Data:
- **automl_text**: Automated text model selection (~$9.50/hr)
- **bert/distilbert**: Transformer models for NLP

### Image Data:
- **automl_image**: Automated image model selection
- **resnet/efficientnet**: CNN architectures

### Time Series:
- **automl_forecasting**: Automated forecasting
- **arima**: Statistical forecasting
- **lstm**: Deep learning for sequences

## Training Strategies
- **automl**: Fully automated (hands-off, higher cost, best performance)
- **custom**: Manual configuration (more control, lower cost)
- **hybrid**: AutoML with custom preprocessing

## Decision Factors to Consider
1. **Dataset Size**: Small (<1K) → simpler models; Large (>100K) → AutoML or complex models
2. **Feature Count**: Few features (<10) → linear models; Many features → ensemble/neural methods
3. **Problem Complexity**: Simple → interpretable models; Complex → AutoML
4. **User Preferences**: Interpretability, cost constraints, training time
5. **Data Quality**: Missing values, class imbalance, feature types
6. **ALIGNMENT**: Does the data actually support what the user is trying to achieve?

## Respond in this exact JSON format:
```json
{{
  "data_validation": {{
    "user_prompt_matches_data": true|false,
    "issues_found": ["list any mismatches or concerns"],
    "confidence_in_alignment": 0.0-1.0
  }},
  "architecture": "model_architecture_enum_value",
  "training_strategy": "automl|custom|hybrid",
  "vertex_product": "vertex_ai_product_enum_value",
  "hyperparameters": {{
    "learning_rate": 0.01,
    "batch_size": 32,
    "max_iterations": 1000,
    "early_stopping_patience": 10,
    "model_specific": {{
      "param1": "value1"
    }}
  }},
  "confidence": 0.85,
  "reasoning": "Detailed explanation of your selection based on ACTUAL data analysis...",
  "estimated_training_time_minutes": 60,
  "estimated_cost_usd": 20.0,
  "requires_gpu": false,
  "supports_incremental_training": true,
  "interpretability_score": 0.7
}}
```

**IMPORTANT**: If you detect ANY mismatch between the user's stated goal and the actual CSV data, set "user_prompt_matches_data" to false and explain the issues clearly. Do not proceed with a full recommendation until alignment is confirmed.

Be thoughtful and consider trade-offs between performance, cost, interpretability, and training time.
"""

    SYSTEM_INSTRUCTION = (
        "You are an expert ML model selection specialist. Analyze datasets carefully, "
        "validate alignment with user goals, and recommend optimal models with clear reasoning. "
        "Always prioritize data validation before making recommendations."
    )


# Legacy compatibility - expose MODEL_SELECTION_PROMPT at module level
MODEL_SELECTION_PROMPT = ModelSelectionPrompts.MODEL_SELECTION
