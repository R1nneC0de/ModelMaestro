"""
AI-powered model selection agent.

Combines rule-based logic with Gemini AI for intelligent model selection.
"""
import asyncio
from typing import Optional, Dict, Any
import structlog

from .types import ProblemType, DataType, ProblemAnalysis
from .model_types import ModelRecommendation, DatasetProfile, ModelArchitecture
from .selection_rules import ModelSelectionRules
from .gemini_client import GeminiClient
from .prompts import MODEL_SELECTION_PROMPT
from .response_parser import parse_json_response

logger = structlog.get_logger()


class ModelSelector:
    """
    Intelligent model selection agent.

    This agent combines rule-based heuristics with AI-powered reasoning
    to select the optimal model architecture and training strategy.
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize the model selector.

        Args:
            gemini_client: Optional Gemini client for AI-powered selection
        """
        self.gemini_client = gemini_client
        self.rules_engine = ModelSelectionRules()

    async def select_model(
        self,
        problem_analysis: ProblemAnalysis,
        dataset_profile: DatasetProfile,
        user_preferences: Optional[Dict[str, Any]] = None,
        use_ai: bool = True,
        csv_data: Optional[Dict[str, Any]] = None,
    ) -> ModelRecommendation:
        """
        Select the optimal model for the given problem and dataset.

        Args:
            problem_analysis: Analysis from Step 3
            dataset_profile: Dataset characteristics
            user_preferences: Optional user preferences (interpretability, cost, etc.)
            use_ai: Whether to use AI-powered selection (requires Gemini)
            csv_data: Optional CSV data with column_names, data_sample, total_rows, total_columns

        Returns:
            ModelRecommendation with selected model and configuration
        """
        logger.info(
            "selecting_model",
            problem_type=problem_analysis.problem_type,
            data_type=problem_analysis.data_type,
            num_samples=dataset_profile.num_samples,
            num_features=dataset_profile.num_features,
        )

        # Get rule-based recommendation
        rule_based_recommendation = self.rules_engine.select_model(
            problem_type=problem_analysis.problem_type,
            data_type=problem_analysis.data_type,
            dataset_profile=dataset_profile,
            domain=problem_analysis.domain,
            complexity_score=problem_analysis.complexity_score,
            user_preferences=user_preferences,
        )

        # If AI is disabled or no Gemini client, return rule-based
        if not use_ai or self.gemini_client is None:
            logger.info(
                "model_selected_by_rules",
                architecture=rule_based_recommendation.architecture,
                confidence=rule_based_recommendation.confidence,
            )
            return rule_based_recommendation

        # Use AI to validate and potentially improve the recommendation
        try:
            ai_recommendation = await self._get_ai_recommendation(
                problem_analysis=problem_analysis,
                dataset_profile=dataset_profile,
                rule_based_recommendation=rule_based_recommendation,
                user_preferences=user_preferences,
                csv_data=csv_data,
            )

            # Combine insights from both
            final_recommendation = self._merge_recommendations(
                rule_based=rule_based_recommendation,
                ai_based=ai_recommendation,
            )

            logger.info(
                "model_selected_with_ai",
                architecture=final_recommendation.architecture,
                confidence=final_recommendation.confidence,
            )

            return final_recommendation

        except Exception as e:
            logger.warning(
                "ai_selection_failed_falling_back_to_rules",
                error=str(e),
            )
            return rule_based_recommendation

    async def _get_ai_recommendation(
        self,
        problem_analysis: ProblemAnalysis,
        dataset_profile: DatasetProfile,
        rule_based_recommendation: ModelRecommendation,
        user_preferences: Optional[Dict[str, Any]],
        csv_data: Optional[Dict[str, Any]] = None,
    ) -> ModelRecommendation:
        """
        Get AI-powered model recommendation using Gemini.
        """
        # Prepare context for AI
        context = {
            "problem_analysis": {
                "problem_type": problem_analysis.problem_type.value,
                "data_type": problem_analysis.data_type.value,
                "domain": problem_analysis.domain,
                "complexity_score": problem_analysis.complexity_score,
                "confidence": problem_analysis.confidence,
                "reasoning": problem_analysis.reasoning,
                "is_labeled": problem_analysis.is_labeled,
                "num_classes": problem_analysis.num_classes,
                "target_variable": problem_analysis.target_variable,
            },
            "dataset_profile": {
                "num_samples": dataset_profile.num_samples,
                "num_features": dataset_profile.num_features,
                "num_classes": dataset_profile.num_classes,
                "num_numeric_features": dataset_profile.num_numeric_features,
                "num_categorical_features": dataset_profile.num_categorical_features,
                "missing_value_ratio": dataset_profile.missing_value_ratio,
                "class_imbalance_ratio": dataset_profile.class_imbalance_ratio,
                "dimensionality_ratio": dataset_profile.dimensionality_ratio,
                "dataset_size_mb": dataset_profile.dataset_size_mb,
            },
            "rule_based_recommendation": rule_based_recommendation.to_dict(),
            "user_preferences": user_preferences or {},
        }

        # Prepare CSV data for prompt
        if csv_data:
            column_names = csv_data.get("column_names", "Not provided")
            data_sample = csv_data.get("data_sample", "Not provided")
            total_rows = csv_data.get("total_rows", "Unknown")
            total_columns = csv_data.get("total_columns", "Unknown")
        else:
            column_names = "Not provided"
            data_sample = "Not provided"
            total_rows = "Unknown"
            total_columns = "Unknown"

        # Generate AI recommendation
        prompt = MODEL_SELECTION_PROMPT.format(
            context=str(context),
            column_names=column_names,
            data_sample=data_sample,
            total_rows=total_rows,
            total_columns=total_columns,
        )

        response = await self.gemini_client.generate_structured_response(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more consistent selection
        )

        # Parse AI response
        ai_data = parse_json_response(response)

        # Convert to ModelRecommendation
        return self._parse_ai_recommendation(ai_data)

    def _parse_ai_recommendation(self, ai_data: Dict[str, Any]) -> ModelRecommendation:
        """Parse AI response into ModelRecommendation."""

        # Parse architecture
        architecture_str = ai_data.get("architecture", "automl_tabular")
        try:
            architecture = ModelArchitecture(architecture_str)
        except ValueError:
            architecture = ModelArchitecture.AUTOML_TABULAR

        # Parse hyperparameters
        from .model_types import HyperparameterConfig, TrainingStrategy, VertexAIProduct

        hp_data = ai_data.get("hyperparameters", {})
        hyperparameters = HyperparameterConfig(
            learning_rate=hp_data.get("learning_rate", 0.01),
            batch_size=hp_data.get("batch_size", 32),
            max_iterations=hp_data.get("max_iterations", 1000),
            early_stopping_patience=hp_data.get("early_stopping_patience", 10),
            model_specific=hp_data.get("model_specific", {}),
        )

        # Parse training strategy
        strategy_str = ai_data.get("training_strategy", "automl")
        try:
            training_strategy = TrainingStrategy(strategy_str)
        except ValueError:
            training_strategy = TrainingStrategy.AUTOML

        # Parse Vertex AI product
        product_str = ai_data.get("vertex_product", "automl_tables")
        try:
            vertex_product = VertexAIProduct(product_str)
        except ValueError:
            vertex_product = VertexAIProduct.AUTOML_TABLES

        return ModelRecommendation(
            architecture=architecture,
            training_strategy=training_strategy,
            vertex_product=vertex_product,
            hyperparameters=hyperparameters,
            confidence=ai_data.get("confidence", 0.75),
            reasoning=ai_data.get("reasoning", ""),
            estimated_training_time_minutes=ai_data.get("estimated_training_time_minutes"),
            estimated_cost_usd=ai_data.get("estimated_cost_usd"),
            requires_gpu=ai_data.get("requires_gpu", False),
            supports_incremental_training=ai_data.get("supports_incremental_training", False),
            interpretability_score=ai_data.get("interpretability_score", 0.5),
        )

    def _merge_recommendations(
        self,
        rule_based: ModelRecommendation,
        ai_based: ModelRecommendation,
    ) -> ModelRecommendation:
        """
        Merge rule-based and AI recommendations.

        Strategy: If AI and rules agree, use AI's recommendation with higher confidence.
        If they disagree, prefer rules but include AI suggestion as alternative.
        """
        if rule_based.architecture == ai_based.architecture:
            # Agreement - use AI with boosted confidence
            merged = ai_based
            merged.confidence = min(0.98, (rule_based.confidence + ai_based.confidence) / 1.5)
            merged.reasoning = (
                f"[Rule-based & AI Agreement] {ai_based.reasoning}\n\n"
                f"Rule-based reasoning: {rule_based.reasoning}"
            )
            merged.alternatives = rule_based.alternatives
            return merged

        else:
            # Disagreement - use rules but add AI as alternative
            merged = rule_based
            merged.alternatives.insert(0, ai_based)
            merged.reasoning = (
                f"[Rule-based Selection] {rule_based.reasoning}\n\n"
                f"Alternative AI suggestion: {ai_based.architecture.value} "
                f"(confidence: {ai_based.confidence:.2f})\n"
                f"AI reasoning: {ai_based.reasoning}"
            )
            return merged

    def get_vertex_ai_config(
        self,
        recommendation: ModelRecommendation,
    ) -> Dict[str, Any]:
        """
        Generate Vertex AI configuration for the recommended model.

        This prepares the configuration dict needed to launch training jobs.

        Args:
            recommendation: Model recommendation

        Returns:
            Dictionary with Vertex AI configuration
        """
        from .model_types import VertexAIProduct, TrainingStrategy

        config = {
            "display_name": f"{recommendation.architecture.value}_training",
            "training_strategy": recommendation.training_strategy.value,
            "vertex_product": recommendation.vertex_product.value,
        }

        # AutoML-specific configuration
        if recommendation.training_strategy == TrainingStrategy.AUTOML:
            config["automl_config"] = {
                "optimization_objective": recommendation.hyperparameters.model_specific.get(
                    "optimization_objective", "maximize-au-roc"
                ),
                "budget_milli_node_hours": recommendation.hyperparameters.model_specific.get(
                    "train_budget_milli_node_hours", 8000
                ),
                "disable_early_stopping": recommendation.hyperparameters.model_specific.get(
                    "disable_early_stopping", False
                ),
            }

        # Custom training configuration
        else:
            config["custom_config"] = {
                "machine_type": "n1-standard-8" if not recommendation.requires_gpu else "n1-highmem-8",
                "accelerator_type": "NVIDIA_TESLA_T4" if recommendation.requires_gpu else None,
                "accelerator_count": 1 if recommendation.requires_gpu else 0,
                "replica_count": 1,
                "hyperparameters": {
                    "learning_rate": recommendation.hyperparameters.learning_rate,
                    "batch_size": recommendation.hyperparameters.batch_size,
                    "max_iterations": recommendation.hyperparameters.max_iterations,
                    "early_stopping_patience": recommendation.hyperparameters.early_stopping_patience,
                    **recommendation.hyperparameters.model_specific,
                },
            }

        return config
