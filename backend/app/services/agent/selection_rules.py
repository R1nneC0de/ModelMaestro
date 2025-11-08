"""
Rule-based model selection logic.

This module contains the core decision logic for selecting optimal models
based on problem type, data characteristics, and resource constraints.
"""
from typing import List, Optional, Tuple
import math

from .types import ProblemType, DataType
from .model_types import (
    ModelArchitecture,
    TrainingStrategy,
    VertexAIProduct,
    HyperparameterConfig,
    ModelRecommendation,
    DatasetProfile,
)


class ModelSelectionRules:
    """
    Rule-based model selection engine.

    This class encapsulates the decision logic for choosing optimal models
    based on problem characteristics and data profiles.
    """

    # Thresholds for decision making
    SMALL_DATASET_THRESHOLD = 1000
    MEDIUM_DATASET_THRESHOLD = 100000
    HIGH_DIMENSIONAL_RATIO = 0.1  # features/samples
    SIMPLE_PROBLEM_FEATURES = 10

    @staticmethod
    def select_model(
        problem_type: ProblemType,
        data_type: DataType,
        dataset_profile: DatasetProfile,
        domain: str,
        complexity_score: float,
        user_preferences: Optional[dict] = None,
    ) -> ModelRecommendation:
        """
        Select the optimal model based on problem and data characteristics.

        Args:
            problem_type: Type of ML problem
            data_type: Type of data
            dataset_profile: Dataset characteristics
            domain: Problem domain
            complexity_score: Problem complexity (0.0-1.0)
            user_preferences: Optional user preferences (e.g., interpretability, cost)

        Returns:
            ModelRecommendation with primary and alternative models
        """
        # Route to specialized selection methods
        if data_type == DataType.TABULAR:
            return ModelSelectionRules._select_tabular_model(
                problem_type, dataset_profile, complexity_score, user_preferences
            )
        elif data_type == DataType.TEXT:
            return ModelSelectionRules._select_text_model(
                problem_type, dataset_profile, complexity_score
            )
        elif data_type == DataType.IMAGE:
            return ModelSelectionRules._select_image_model(
                problem_type, dataset_profile, complexity_score
            )
        elif data_type == DataType.TIME_SERIES:
            return ModelSelectionRules._select_timeseries_model(
                problem_type, dataset_profile, complexity_score
            )
        else:
            # Fallback to AutoML
            return ModelSelectionRules._create_automl_recommendation(
                problem_type, data_type, dataset_profile
            )

    @staticmethod
    def _select_tabular_model(
        problem_type: ProblemType,
        dataset_profile: DatasetProfile,
        complexity_score: float,
        user_preferences: Optional[dict] = None,
    ) -> ModelRecommendation:
        """Select model for tabular data."""

        preferences = user_preferences or {}
        prefer_interpretability = preferences.get("interpretability", False)
        prefer_speed = preferences.get("speed", False)
        budget_constraint = preferences.get("max_cost_usd", float('inf'))

        # Decision factors
        is_small_dataset = dataset_profile.num_samples < ModelSelectionRules.SMALL_DATASET_THRESHOLD
        is_large_dataset = dataset_profile.num_samples > ModelSelectionRules.MEDIUM_DATASET_THRESHOLD
        is_simple = (
            dataset_profile.num_features < ModelSelectionRules.SIMPLE_PROBLEM_FEATURES
            and complexity_score < 0.3
        )
        is_high_dimensional = (
            dataset_profile.dimensionality_ratio > ModelSelectionRules.HIGH_DIMENSIONAL_RATIO
        )
        is_imbalanced = (
            dataset_profile.class_imbalance_ratio is not None
            and dataset_profile.class_imbalance_ratio < 0.2
        )

        # Classification problems
        if problem_type == ProblemType.CLASSIFICATION:
            if is_simple and (prefer_interpretability or prefer_speed):
                # Logistic Regression for simple interpretable problems
                return ModelRecommendation(
                    architecture=ModelArchitecture.LOGISTIC_REGRESSION,
                    training_strategy=TrainingStrategy.CUSTOM,
                    vertex_product=VertexAIProduct.CUSTOM_TRAINING,
                    hyperparameters=HyperparameterConfig(
                        learning_rate=0.01,
                        max_iterations=1000,
                        model_specific={
                            "regularization": "l2",
                            "C": 1.0,
                            "solver": "lbfgs",
                        }
                    ),
                    confidence=0.85,
                    reasoning=(
                        f"Simple classification with {dataset_profile.num_features} features. "
                        f"Logistic regression provides high interpretability and fast training."
                    ),
                    estimated_training_time_minutes=5,
                    estimated_cost_usd=2.0,
                    requires_gpu=False,
                    supports_incremental_training=True,
                    interpretability_score=0.95,
                    alternatives=[
                        ModelSelectionRules._create_xgboost_recommendation(
                            problem_type, dataset_profile, is_imbalanced
                        ),
                    ]
                )

            elif is_small_dataset or budget_constraint < 50:
                # XGBoost for small-medium datasets with limited budget
                return ModelSelectionRules._create_xgboost_recommendation(
                    problem_type, dataset_profile, is_imbalanced
                )

            else:
                # AutoML Tabular for complex problems or large datasets
                return ModelSelectionRules._create_automl_tabular_recommendation(
                    problem_type, dataset_profile, is_imbalanced
                )

        # Regression problems
        elif problem_type == ProblemType.REGRESSION:
            if is_simple and prefer_interpretability:
                # Linear Regression for simple problems
                return ModelRecommendation(
                    architecture=ModelArchitecture.LINEAR_REGRESSION,
                    training_strategy=TrainingStrategy.CUSTOM,
                    vertex_product=VertexAIProduct.CUSTOM_TRAINING,
                    hyperparameters=HyperparameterConfig(
                        learning_rate=0.01,
                        max_iterations=1000,
                        model_specific={
                            "fit_intercept": True,
                            "normalize": True,
                        }
                    ),
                    confidence=0.80,
                    reasoning=(
                        f"Simple regression with {dataset_profile.num_features} features. "
                        f"Linear regression is interpretable and sufficient for linear relationships."
                    ),
                    estimated_training_time_minutes=3,
                    estimated_cost_usd=1.5,
                    requires_gpu=False,
                    supports_incremental_training=True,
                    interpretability_score=0.98,
                    alternatives=[
                        ModelSelectionRules._create_xgboost_recommendation(
                            problem_type, dataset_profile, False
                        ),
                    ]
                )

            elif is_small_dataset or budget_constraint < 50:
                # XGBoost regressor
                return ModelSelectionRules._create_xgboost_recommendation(
                    problem_type, dataset_profile, False
                )

            else:
                # AutoML Tabular
                return ModelSelectionRules._create_automl_tabular_recommendation(
                    problem_type, dataset_profile, False
                )

        # Fallback to AutoML
        return ModelSelectionRules._create_automl_tabular_recommendation(
            problem_type, dataset_profile, False
        )

    @staticmethod
    def _select_text_model(
        problem_type: ProblemType,
        dataset_profile: DatasetProfile,
        complexity_score: float,
    ) -> ModelRecommendation:
        """Select model for text data."""

        is_small_dataset = dataset_profile.num_samples < 5000

        # Calculate budget based on dataset size for text models
        if dataset_profile.num_samples < 500:
            text_budget_hours = 0.5  # 30 minutes
        elif dataset_profile.num_samples < 5000:
            text_budget_hours = 2.0  # 2 hours
        else:
            text_budget_hours = 8.0  # 8 hours

        if is_small_dataset or complexity_score > 0.7:
            # Use AutoML Text for small datasets or complex problems
            return ModelRecommendation(
                architecture=ModelArchitecture.AUTOML_TEXT,
                training_strategy=TrainingStrategy.AUTOML,
                vertex_product=VertexAIProduct.AUTOML_TEXT,
                hyperparameters=HyperparameterConfig(
                    model_specific={
                        "train_budget_milli_node_hours": int(text_budget_hours * 1000),
                        "optimization_objective": "maximize-au-prc",
                    }
                ),
                confidence=0.90,
                reasoning=(
                    f"Text classification with {dataset_profile.num_samples} samples. "
                    f"AutoML Text will automatically select between BERT variants and optimize."
                ),
                estimated_training_time_minutes=120,
                estimated_cost_usd=76.0,  # ~$9.50/node hour * 8 hours
                requires_gpu=True,
                supports_incremental_training=False,
                interpretability_score=0.3,
            )
        else:
            # Use DistilBERT for larger datasets
            return ModelRecommendation(
                architecture=ModelArchitecture.DISTILBERT,
                training_strategy=TrainingStrategy.CUSTOM,
                vertex_product=VertexAIProduct.CUSTOM_TRAINING,
                hyperparameters=HyperparameterConfig(
                    learning_rate=2e-5,
                    batch_size=16,
                    max_iterations=10000,
                    early_stopping_patience=3,
                    model_specific={
                        "model_name": "distilbert-base-uncased",
                        "max_seq_length": 512,
                        "warmup_steps": 500,
                        "weight_decay": 0.01,
                    }
                ),
                confidence=0.85,
                reasoning=(
                    f"Large text dataset ({dataset_profile.num_samples} samples). "
                    f"DistilBERT provides good performance with faster training than BERT."
                ),
                estimated_training_time_minutes=240,
                estimated_cost_usd=45.0,
                requires_gpu=True,
                supports_incremental_training=True,
                interpretability_score=0.4,
            )

    @staticmethod
    def _select_image_model(
        problem_type: ProblemType,
        dataset_profile: DatasetProfile,
        complexity_score: float,
    ) -> ModelRecommendation:
        """Select model for image data."""

        is_small_dataset = dataset_profile.num_samples < 1000

        # Calculate budget based on dataset size for image models
        if dataset_profile.num_samples < 100:
            image_budget_hours = 0.5  # 30 minutes
        elif dataset_profile.num_samples < 500:
            image_budget_hours = 1.0  # 1 hour
        elif dataset_profile.num_samples < 5000:
            image_budget_hours = 4.0  # 4 hours
        else:
            image_budget_hours = 8.0  # 8 hours

        # Default to AutoML Image for most cases
        return ModelRecommendation(
            architecture=ModelArchitecture.AUTOML_IMAGE,
            training_strategy=TrainingStrategy.AUTOML,
            vertex_product=VertexAIProduct.AUTOML_IMAGE,
            hyperparameters=HyperparameterConfig(
                model_specific={
                    "train_budget_milli_node_hours": int(image_budget_hours * 1000),
                    "model_type": "CLOUD",  # vs MOBILE_TF_LOW_LATENCY, etc.
                }
            ),
            confidence=0.92,
            reasoning=(
                f"Image {problem_type.value} with {dataset_profile.num_samples} samples. "
                f"AutoML Image will select optimal architecture (EfficientNet, ResNet, etc.)."
            ),
            estimated_training_time_minutes=180,
            estimated_cost_usd=96.0,
            requires_gpu=True,
            supports_incremental_training=False,
            interpretability_score=0.2,
        )

    @staticmethod
    def _select_timeseries_model(
        problem_type: ProblemType,
        dataset_profile: DatasetProfile,
        complexity_score: float,
    ) -> ModelRecommendation:
        """Select model for time series data."""

        # Calculate budget based on dataset size for timeseries models
        if dataset_profile.num_samples < 100:
            ts_budget_hours = 0.3  # 18 minutes
        elif dataset_profile.num_samples < 1000:
            ts_budget_hours = 0.5  # 30 minutes
        elif dataset_profile.num_samples < 10000:
            ts_budget_hours = 2.0  # 2 hours
        else:
            ts_budget_hours = 8.0  # 8 hours

        return ModelRecommendation(
            architecture=ModelArchitecture.AUTOML_FORECASTING,
            training_strategy=TrainingStrategy.AUTOML,
            vertex_product=VertexAIProduct.AUTOML_FORECASTING,
            hyperparameters=HyperparameterConfig(
                model_specific={
                    "train_budget_milli_node_hours": int(ts_budget_hours * 1000),
                    "optimization_objective": "minimize-rmse",
                }
            ),
            confidence=0.88,
            reasoning=(
                f"Time series forecasting with {dataset_profile.num_samples} samples. "
                f"AutoML Forecasting handles seasonality and trends automatically."
            ),
            estimated_training_time_minutes=90,
            estimated_cost_usd=60.0,
            requires_gpu=False,
            supports_incremental_training=True,
            interpretability_score=0.6,
        )

    @staticmethod
    def _create_xgboost_recommendation(
        problem_type: ProblemType,
        dataset_profile: DatasetProfile,
        is_imbalanced: bool,
    ) -> ModelRecommendation:
        """Create XGBoost recommendation."""

        model_specific = {
            "objective": "binary:logistic" if problem_type == ProblemType.CLASSIFICATION else "reg:squarederror",
            "max_depth": 6,
            "n_estimators": 100,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 1,
            "gamma": 0,
        }

        if is_imbalanced and dataset_profile.class_imbalance_ratio:
            # Adjust for class imbalance
            model_specific["scale_pos_weight"] = 1.0 / dataset_profile.class_imbalance_ratio

        return ModelRecommendation(
            architecture=ModelArchitecture.XGBOOST,
            training_strategy=TrainingStrategy.CUSTOM,
            vertex_product=VertexAIProduct.CUSTOM_TRAINING,
            hyperparameters=HyperparameterConfig(
                learning_rate=0.1,
                batch_size=32,
                max_iterations=100,
                early_stopping_patience=10,
                model_specific=model_specific,
            ),
            confidence=0.88,
            reasoning=(
                f"XGBoost is ideal for tabular {problem_type.value} with "
                f"{dataset_profile.num_samples} samples and {dataset_profile.num_features} features. "
                f"Provides excellent performance-to-cost ratio."
                + (" Configured for class imbalance." if is_imbalanced else "")
            ),
            estimated_training_time_minutes=15,
            estimated_cost_usd=8.0,
            requires_gpu=False,
            supports_incremental_training=True,
            interpretability_score=0.7,
        )

    @staticmethod
    def _create_automl_tabular_recommendation(
        problem_type: ProblemType,
        dataset_profile: DatasetProfile,
        is_imbalanced: bool,
    ) -> ModelRecommendation:
        """Create AutoML Tabular recommendation."""

        # Estimate budget based on dataset size - use smaller budgets for smaller datasets
        if dataset_profile.num_samples < 100:
            budget_hours = 0.1  # 6 minutes - very small datasets
        elif dataset_profile.num_samples < 1000:
            budget_hours = 0.2  # 12 minutes - small datasets
        elif dataset_profile.num_samples < 10000:
            budget_hours = 0.5  # 30 minutes - medium-small datasets
        elif dataset_profile.num_samples < 100000:
            budget_hours = 1.0  # 1 hour - medium datasets
        elif dataset_profile.num_samples < 1000000:
            budget_hours = 4.0  # 4 hours - large datasets
        else:
            budget_hours = 24.0  # 24 hours - very large datasets

        optimization_objective = "maximize-au-roc" if problem_type == ProblemType.CLASSIFICATION else "minimize-rmse"

        return ModelRecommendation(
            architecture=ModelArchitecture.AUTOML_TABULAR,
            training_strategy=TrainingStrategy.AUTOML,
            vertex_product=VertexAIProduct.AUTOML_TABLES,
            hyperparameters=HyperparameterConfig(
                model_specific={
                    "train_budget_milli_node_hours": int(budget_hours * 1000),
                    "optimization_objective": optimization_objective,
                    "disable_early_stopping": False,
                }
            ),
            confidence=0.93,
            reasoning=(
                f"AutoML Tabular is optimal for this {problem_type.value} problem with "
                f"{dataset_profile.num_samples} samples. It will automatically search through "
                f"multiple algorithms (XGBoost, TabNet, Wide & Deep) and find the best configuration."
                + (" Class imbalance will be handled automatically." if is_imbalanced else "")
            ),
            estimated_training_time_minutes=int(budget_hours * 60),
            estimated_cost_usd=budget_hours * 19.50,  # $19.50/node hour for AutoML Tables
            requires_gpu=True,
            supports_incremental_training=False,
            interpretability_score=0.5,
        )

    @staticmethod
    def _create_automl_recommendation(
        problem_type: ProblemType,
        data_type: DataType,
        dataset_profile: DatasetProfile,
    ) -> ModelRecommendation:
        """Fallback AutoML recommendation."""

        return ModelRecommendation(
            architecture=ModelArchitecture.CUSTOM,
            training_strategy=TrainingStrategy.AUTOML,
            vertex_product=VertexAIProduct.CUSTOM_TRAINING,
            hyperparameters=HyperparameterConfig(),
            confidence=0.60,
            reasoning=(
                f"Complex {data_type.value} {problem_type.value} problem. "
                f"Recommending AutoML for automatic model selection."
            ),
            estimated_training_time_minutes=120,
            estimated_cost_usd=80.0,
            requires_gpu=True,
            supports_incremental_training=False,
            interpretability_score=0.5,
        )
