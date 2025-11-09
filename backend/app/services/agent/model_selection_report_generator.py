"""
Model Selection Report Generator with Gemini AI.

This module generates comprehensive reports explaining why a particular model
was selected, including data-driven insights powered by Gemini.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
from google.cloud import storage

from app.services.agent.gemini_client import GeminiClient
from app.services.agent.model_types import ModelRecommendation, DatasetProfile
from app.services.agent.types import ProblemAnalysis
from app.core.config import settings

logger = structlog.get_logger()


MODEL_SELECTION_REPORT_PROMPT = """You are an expert ML engineer explaining model selection decisions to stakeholders.

Given the following information about a machine learning project, generate a comprehensive, easy-to-understand report explaining why the selected model was chosen.

**Problem Analysis:**
{problem_analysis}

**Dataset Profile:**
{dataset_profile}

**Selected Model:**
{model_recommendation}

**Training Results:**
{training_results}

Generate a comprehensive model selection report with the following sections:

1. **Executive Summary** (2-3 sentences)
   - High-level explanation of the model choice
   - Key benefits of the selected approach

2. **Data Characteristics Analysis** (1 paragraph)
   - Describe the dataset characteristics that influenced the decision
   - Explain how the data properties align with the model's strengths

3. **Model Selection Rationale** (2-3 paragraphs)
   - Why this specific model architecture was chosen
   - What alternatives were considered and why they weren't selected
   - How the model addresses the specific problem type

4. **Performance Expectations** (1 paragraph)
   - Expected model performance based on dataset size and complexity
   - Key metrics to monitor
   - Potential limitations or caveats

5. **Training Configuration Justification** (1 paragraph)
   - Explain the training budget allocation
   - Justify hyperparameter choices
   - Discuss trade-offs made (if any)

6. **Recommendations for Production** (bullet points)
   - 3-5 practical recommendations for deploying this model
   - Monitoring suggestions
   - When to consider retraining

The report should be:
- Written in professional but accessible language
- Data-driven and specific
- Honest about limitations
- Actionable for ML engineers and stakeholders

Format the response as a well-structured Markdown document.
"""


class ModelSelectionReportGenerator:
    """
    Generate comprehensive model selection reports powered by Gemini AI.

    Creates detailed explanations of why specific models were selected,
    with data-driven insights and recommendations.
    """

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        gcs_bucket_name: Optional[str] = None
    ):
        """
        Initialize the report generator.

        Args:
            gemini_client: Gemini client for AI-powered insights
            gcs_bucket_name: GCS bucket for storing reports
        """
        self.gemini_client = gemini_client or GeminiClient(temperature=0.3)
        self.bucket_name = gcs_bucket_name or settings.GCS_BUCKET_NAME
        self.storage_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        self.bucket = self.storage_client.bucket(self.bucket_name)

        logger.info(
            "model_selection_report_generator_initialized",
            bucket=self.bucket_name
        )

    async def generate_report(
        self,
        dataset_id: str,
        problem_analysis: ProblemAnalysis,
        dataset_profile: DatasetProfile,
        model_recommendation: ModelRecommendation,
        training_results: Optional[Dict[str, Any]] = None,
        upload_to_gcs: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive model selection report.

        Args:
            dataset_id: Dataset identifier
            problem_analysis: Problem analysis from Step 3
            dataset_profile: Dataset profiling information
            model_recommendation: Model selection recommendation
            training_results: Optional training results/metrics
            upload_to_gcs: Whether to upload report to GCS

        Returns:
            Dictionary with report content and metadata
        """
        logger.info(
            "generating_model_selection_report",
            dataset_id=dataset_id,
            model=model_recommendation.architecture.value
        )

        # Step 1: Prepare context
        context = self._prepare_context(
            problem_analysis,
            dataset_profile,
            model_recommendation,
            training_results
        )

        # Step 2: Generate AI-powered report
        try:
            ai_report = await self._generate_ai_report(context)
        except Exception as e:
            logger.warning(
                "ai_report_generation_failed_using_template",
                error=str(e)
            )
            ai_report = self._generate_template_report(context)

        # Step 3: Add metadata section
        full_report = self._add_metadata_section(
            ai_report, dataset_id, model_recommendation, training_results
        )

        # Step 4: Generate summary dict
        report_dict = {
            "dataset_id": dataset_id,
            "generated_at": datetime.utcnow().isoformat(),
            "model_architecture": model_recommendation.architecture.value,
            "report_markdown": full_report,
            "metadata": {
                "problem_type": problem_analysis.problem_type.value,
                "data_type": problem_analysis.data_type.value,
                "num_samples": dataset_profile.num_samples,
                "num_features": dataset_profile.num_features,
                "training_budget_minutes":
                    model_recommendation.hyperparameters.model_specific.get(
                        "train_budget_milli_node_hours", 0
                    ) / 1000 * 60,
                "estimated_cost_usd": model_recommendation.estimated_cost_usd,
                "confidence": model_recommendation.confidence
            }
        }

        # Step 5: Upload to GCS if requested
        if upload_to_gcs:
            gcs_uri = await self._upload_report(
                dataset_id, full_report, report_dict
            )
            report_dict["gcs_uri"] = gcs_uri

        # Step 6: Print to terminal
        print("\n" + "=" * 80)
        print("📊 MODEL SELECTION REPORT")
        print("=" * 80)
        print(full_report)
        print("=" * 80)

        logger.info(
            "model_selection_report_generated",
            dataset_id=dataset_id,
            uploaded=upload_to_gcs
        )

        return report_dict

    def _prepare_context(
        self,
        problem_analysis: ProblemAnalysis,
        dataset_profile: DatasetProfile,
        model_recommendation: ModelRecommendation,
        training_results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare context for report generation."""
        return {
            "problem_analysis": {
                "problem_type": problem_analysis.problem_type.value,
                "data_type": problem_analysis.data_type.value,
                "domain": problem_analysis.domain,
                "complexity_score": problem_analysis.complexity_score,
                "confidence": problem_analysis.confidence,
                "reasoning": problem_analysis.reasoning,
                "target_variable": problem_analysis.target_variable,
                "num_classes": problem_analysis.num_classes
            },
            "dataset_profile": {
                "num_samples": dataset_profile.num_samples,
                "num_features": dataset_profile.num_features,
                "num_classes": dataset_profile.num_classes,
                "num_numeric": dataset_profile.num_numeric_features,
                "num_categorical": dataset_profile.num_categorical_features,
                "missing_ratio": dataset_profile.missing_value_ratio,
                "class_imbalance": dataset_profile.class_imbalance_ratio,
                "dimensionality_ratio": dataset_profile.dimensionality_ratio,
                "dataset_size_mb": dataset_profile.dataset_size_mb
            },
            "model_recommendation": {
                "architecture": model_recommendation.architecture.value,
                "training_strategy": model_recommendation.training_strategy.value,
                "vertex_product": model_recommendation.vertex_product.value,
                "confidence": model_recommendation.confidence,
                "reasoning": model_recommendation.reasoning,
                "hyperparameters": {
                    "learning_rate": model_recommendation.hyperparameters.learning_rate,
                    "batch_size": model_recommendation.hyperparameters.batch_size,
                    "max_iterations": model_recommendation.hyperparameters.max_iterations,
                    "model_specific": model_recommendation.hyperparameters.model_specific
                },
                "estimated_training_time": model_recommendation.estimated_training_time_minutes,
                "estimated_cost": model_recommendation.estimated_cost_usd,
                "interpretability_score": model_recommendation.interpretability_score,
                "alternatives": [
                    {
                        "architecture": alt.architecture.value,
                        "confidence": alt.confidence
                    } for alt in (model_recommendation.alternatives or [])[:3]
                ]
            },
            "training_results": training_results or {}
        }

    async def _generate_ai_report(self, context: Dict[str, Any]) -> str:
        """Generate AI-powered report using Gemini."""
        prompt = MODEL_SELECTION_REPORT_PROMPT.format(
            problem_analysis=json.dumps(context["problem_analysis"], indent=2),
            dataset_profile=json.dumps(context["dataset_profile"], indent=2),
            model_recommendation=json.dumps(context["model_recommendation"], indent=2),
            training_results=json.dumps(context["training_results"], indent=2)
        )

        logger.info("generating_ai_report_with_gemini")

        response = await self.gemini_client.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000
        )

        return response

    def _generate_template_report(self, context: Dict[str, Any]) -> str:
        """Generate fallback template-based report."""
        problem = context["problem_analysis"]
        dataset = context["dataset_profile"]
        model = context["model_recommendation"]

        budget_minutes = model["hyperparameters"]["model_specific"].get(
            "train_budget_milli_node_hours", 0
        ) / 1000 * 60

        report = f"""# Model Selection Report

## Executive Summary

Selected **{model['architecture']}** for {problem['problem_type']} on a dataset with {dataset['num_samples']:,} samples and {dataset['num_features']} features. This model was chosen based on dataset characteristics and optimal performance-cost trade-offs.

## Data Characteristics Analysis

The dataset contains {dataset['num_samples']:,} samples with {dataset['num_features']} features ({dataset['num_numeric']} numeric, {dataset['num_categorical']} categorical). The problem complexity score of {problem['complexity_score']:.2f} indicates a {'relatively simple' if problem['complexity_score'] < 0.5 else 'moderately complex'} task. {"Class imbalance ratio of " + f"{dataset['class_imbalance']:.2f}" if dataset['class_imbalance'] else "Balanced dataset"} was detected.

## Model Selection Rationale

**Selected Model:** {model['architecture'].upper()}
**Confidence:** {model['confidence']:.1%}

{model['reasoning']}

The model was selected using {model['training_strategy']} training strategy via Vertex AI's {model['vertex_product']} product.

**Alternatives Considered:**
"""

        for i, alt in enumerate(model['alternatives'], 1):
            report += f"\n{i}. {alt['architecture']} (confidence: {alt['confidence']:.1%})"

        report += f"""

## Performance Expectations

Based on dataset size and complexity, expect:
- Training time: ~{model['estimated_training_time']} minutes
- Estimated cost: ${model['estimated_cost']:.2f}
- Interpretability score: {model['interpretability_score']:.2f}/1.0

Key metrics to monitor: {', '.join(problem.get('suggested_metrics', ['accuracy', 'precision', 'recall'])[:3])}

## Training Configuration Justification

**Training Budget:** {budget_minutes:.0f} minutes ({model['hyperparameters']['model_specific'].get('train_budget_milli_node_hours', 0)} milli-node-hours)

The training budget was automatically calculated based on dataset size:
- Smaller datasets (< 1,000 samples): 12 minutes
- Medium datasets (1,000-10,000 samples): 30 minutes
- Large datasets (> 10,000 samples): 60+ minutes

**Key Hyperparameters:**
- Learning Rate: {model['hyperparameters']['learning_rate']}
- Batch Size: {model['hyperparameters']['batch_size']}
- Max Iterations: {model['hyperparameters']['max_iterations']}

## Recommendations for Production

- **Monitor primary metrics**: Track {problem.get('suggested_metrics', ['accuracy'])[0]} on validation set
- **Set up alerts**: Configure alerts if performance drops below acceptable thresholds
- **Regular retraining**: Consider retraining when data distribution shifts or every 3-6 months
- **A/B testing**: Compare against baseline model before full deployment
- **Explainability**: Use SHAP or LIME for model interpretability (interpretability score: {model['interpretability_score']:.2f})

---
*Report generated automatically by ModelMaestro Agentic Platform*
"""

        return report

    def _add_metadata_section(
        self,
        report: str,
        dataset_id: str,
        model_recommendation: ModelRecommendation,
        training_results: Optional[Dict[str, Any]]
    ) -> str:
        """Add metadata section to report."""
        metadata_section = f"""

---

## Technical Metadata

**Dataset ID:** `{dataset_id}`
**Model Architecture:** `{model_recommendation.architecture.value}`
**Training Strategy:** `{model_recommendation.training_strategy.value}`
**Vertex AI Product:** `{model_recommendation.vertex_product.value}`
**Report Generated:** `{datetime.utcnow().isoformat()}Z`

"""

        if training_results:
            metadata_section += f"""
**Training Results:**
```json
{json.dumps(training_results, indent=2)}
```
"""

        return report + metadata_section

    async def _upload_report(
        self,
        dataset_id: str,
        report_markdown: str,
        report_dict: Dict[str, Any]
    ) -> str:
        """Upload report to GCS."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base_path = f"evaluation/{dataset_id}/model_selection_report/{timestamp}"

        # Upload markdown
        md_path = f"{base_path}/report.md"
        md_blob = self.bucket.blob(md_path)
        md_blob.upload_from_string(
            report_markdown,
            content_type="text/markdown"
        )

        # Upload JSON
        json_path = f"{base_path}/report.json"
        json_blob = self.bucket.blob(json_path)
        json_blob.upload_from_string(
            json.dumps(report_dict, indent=2),
            content_type="application/json"
        )

        gcs_uri = f"gs://{self.bucket_name}/{base_path}"

        logger.info(
            "report_uploaded_to_gcs",
            gcs_uri=gcs_uri
        )

        return gcs_uri
