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
