"""
Data Quality validation and assessment.

This module handles data quality validation, issue detection,
and strategy determination for data preprocessing.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from enum import Enum

from app.services.agent.types import ProblemAnalysis, ProblemType, DataType

logger = logging.getLogger(__name__)


class DataQualityIssue(str, Enum):
    """Types of data quality issues."""
    MISSING_VALUES = "missing_values"
    DUPLICATE_ROWS = "duplicate_rows"
    INVALID_VALUES = "invalid_values"
    IMBALANCED_CLASSES = "imbalanced_classes"
    INSUFFICIENT_SAMPLES = "insufficient_samples"
    HIGH_CARDINALITY = "high_cardinality"
    OUTLIERS = "outliers"


class MissingValueStrategy(str, Enum):
    """Strategies for handling missing values."""
    DROP_ROWS = "drop_rows"
    DROP_COLUMNS = "drop_columns"
    MEAN_IMPUTATION = "mean_imputation"
    MEDIAN_IMPUTATION = "median_imputation"
    MODE_IMPUTATION = "mode_imputation"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    CONSTANT_FILL = "constant_fill"
    INTERPOLATION = "interpolation"


@dataclass
class DataQualityReport:
    """
    Report of data quality assessment.
    
    Attributes:
        is_valid: Whether data meets minimum quality standards
        issues: List of identified quality issues
        missing_value_stats: Statistics about missing values
        duplicate_count: Number of duplicate rows
        recommendations: List of recommended actions
        severity_score: Overall severity from 0.0 (good) to 1.0 (critical)
    """
    is_valid: bool
    issues: List[DataQualityIssue]
    missing_value_stats: Dict[str, Any]
    duplicate_count: int
    recommendations: List[str]
    severity_score: float
    additional_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingStrategy:
    """
    Strategy for processing data based on quality assessment.
    
    Attributes:
        missing_value_strategy: How to handle missing values
        drop_columns: Columns to drop
        imputation_values: Values to use for imputation
        handle_duplicates: Whether to remove duplicates
        handle_outliers: Whether to handle outliers
        reasoning: Explanation of strategy choices
    """
    missing_value_strategy: MissingValueStrategy
    drop_columns: List[str] = field(default_factory=list)
    imputation_values: Dict[str, Any] = field(default_factory=dict)
    handle_duplicates: bool = True
    handle_outliers: bool = False
    reasoning: str = ""


class DataQualityValidator:
    """
    Validates data quality and identifies issues.
    
    Performs comprehensive quality checks including missing values,
    duplicates, class balance, and invalid values.
    """
    
    # Quality thresholds
    MAX_MISSING_RATIO = 0.3  # Max 30% missing values per column
    MIN_SAMPLES_PER_CLASS = 10  # Minimum samples per class
    MAX_DUPLICATE_RATIO = 0.1  # Max 10% duplicates
    
    def __init__(self):
        """Initialize Data Quality Validator."""
        logger.info("Initialized DataQualityValidator")
    
    async def validate_data_quality(
        self,
        data: Any,
        analysis: ProblemAnalysis,
        target_column: Optional[str] = None
    ) -> DataQualityReport:
        """
        Validate data quality and identify issues.
        
        Args:
            data: Dataset to validate (DataFrame, dict, or file path)
            analysis: Problem analysis results
            target_column: Name of target column for supervised learning
            
        Returns:
            DataQualityReport with validation results
        """
        logger.info("Starting data quality validation")
        
        # Convert data to DataFrame if needed
        df = self._to_dataframe(data, analysis.data_type)
        
        issues = []
        recommendations = []
        severity_score = 0.0
        
        # Check missing values
        missing_stats = self._check_missing_values(df)
        if missing_stats["total_missing"] > 0:
            issues.append(DataQualityIssue.MISSING_VALUES)
            missing_ratio = missing_stats["missing_ratio"]
            severity_score += min(missing_ratio, 0.3)
            
            if missing_ratio > self.MAX_MISSING_RATIO:
                recommendations.append(
                    f"High missing value ratio ({missing_ratio:.1%}). "
                    "Consider imputation or dropping columns."
                )
        
        # Check duplicates
        duplicate_count = self._check_duplicates(df)
        if duplicate_count > 0:
            issues.append(DataQualityIssue.DUPLICATE_ROWS)
            dup_ratio = duplicate_count / len(df)
            severity_score += min(dup_ratio, 0.2)
            
            if dup_ratio > self.MAX_DUPLICATE_RATIO:
                recommendations.append(
                    f"Found {duplicate_count} duplicate rows ({dup_ratio:.1%}). "
                    "Will remove duplicates."
                )
        
        # Check sample size
        if len(df) < 100:
            issues.append(DataQualityIssue.INSUFFICIENT_SAMPLES)
            severity_score += 0.3
            recommendations.append(
                f"Small dataset ({len(df)} samples). "
                "Consider data augmentation or collecting more data."
            )
        
        # Check class balance for classification
        if analysis.problem_type in [ProblemType.CLASSIFICATION, 
                                     ProblemType.TEXT_CLASSIFICATION]:
            if target_column and target_column in df.columns:
                balance_info = self._check_class_balance(df, target_column)
                if balance_info["is_imbalanced"]:
                    issues.append(DataQualityIssue.IMBALANCED_CLASSES)
                    severity_score += 0.2
                    recommendations.append(
                        f"Imbalanced classes detected. "
                        f"Smallest class: {balance_info['min_class_size']} samples. "
                        "Consider stratified splitting or resampling."
                    )
        
        # Check for invalid values (inf, extreme outliers)
        invalid_info = self._check_invalid_values(df)
        if invalid_info["has_invalid"]:
            issues.append(DataQualityIssue.INVALID_VALUES)
            severity_score += 0.15
            recommendations.append(
                f"Found invalid values: {invalid_info['details']}. "
                "Will clean during preprocessing."
            )
        
        # Determine if data is valid
        is_valid = severity_score < 0.7 and len(df) >= 10
        
        logger.info(
            f"Data quality validation complete: "
            f"{'PASS' if is_valid else 'FAIL'} "
            f"(severity: {severity_score:.2f})"
        )
        
        return DataQualityReport(
            is_valid=is_valid,
            issues=issues,
            missing_value_stats=missing_stats,
            duplicate_count=duplicate_count,
            recommendations=recommendations,
            severity_score=severity_score,
            additional_info={
                "num_samples": len(df),
                "num_features": len(df.columns),
                "invalid_values": invalid_info
            }
        )
    
    async def determine_processing_strategy(
        self,
        quality_report: DataQualityReport,
        analysis: ProblemAnalysis,
        data: Any
    ) -> ProcessingStrategy:
        """
        Determine the best strategy for processing data based on quality report.
        
        Args:
            quality_report: Data quality assessment results
            analysis: Problem analysis results
            data: The dataset
            
        Returns:
            ProcessingStrategy with recommended actions
        """
        logger.info("Determining data processing strategy")
        
        df = self._to_dataframe(data, analysis.data_type)
        
        # Determine missing value strategy
        missing_ratio = quality_report.missing_value_stats.get("missing_ratio", 0)
        
        if missing_ratio == 0:
            strategy = MissingValueStrategy.DROP_ROWS
            reasoning = "No missing values detected"
        elif missing_ratio < 0.05:
            strategy = MissingValueStrategy.DROP_ROWS
            reasoning = "Low missing value ratio (<5%), safe to drop rows"
        elif missing_ratio < 0.2:
            # Choose imputation based on data type
            if analysis.data_type == DataType.TABULAR:
                strategy = MissingValueStrategy.MEDIAN_IMPUTATION
                reasoning = "Moderate missing values, using median imputation for robustness"
            else:
                strategy = MissingValueStrategy.MEAN_IMPUTATION
                reasoning = "Moderate missing values, using mean imputation"
        else:
            # High missing values - need to drop columns
            strategy = MissingValueStrategy.DROP_COLUMNS
            reasoning = f"High missing value ratio ({missing_ratio:.1%}), will drop problematic columns"
        
        # Identify columns to drop
        drop_columns = []
        if strategy == MissingValueStrategy.DROP_COLUMNS:
            for col, ratio in quality_report.missing_value_stats.get("by_column", {}).items():
                if ratio > self.MAX_MISSING_RATIO:
                    drop_columns.append(col)
        
        # Determine if we should handle outliers
        handle_outliers = (
            analysis.problem_type in [ProblemType.REGRESSION, ProblemType.CLASSIFICATION]
            and analysis.data_type == DataType.TABULAR
            and quality_report.severity_score > 0.5
        )
        
        return ProcessingStrategy(
            missing_value_strategy=strategy,
            drop_columns=drop_columns,
            handle_duplicates=quality_report.duplicate_count > 0,
            handle_outliers=handle_outliers,
            reasoning=reasoning
        )
    
    def _to_dataframe(self, data: Any, data_type: DataType) -> pd.DataFrame:
        """Convert various data formats to DataFrame."""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame(data)
        elif isinstance(data, str):
            # Assume it's a file path
            if data.endswith('.csv'):
                return pd.read_csv(data)
            elif data.endswith('.json'):
                return pd.read_json(data)
            else:
                raise ValueError(f"Unsupported file format: {data}")
        elif isinstance(data, list):
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Cannot convert {type(data)} to DataFrame")
    
    def _check_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for missing values in DataFrame."""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        missing_ratio = missing_cells / total_cells if total_cells > 0 else 0
        
        # Per-column statistics
        by_column = {}
        for col in df.columns:
            col_missing = df[col].isnull().sum()
            if col_missing > 0:
                by_column[col] = col_missing / len(df)
        
        return {
            "total_missing": missing_cells,
            "missing_ratio": missing_ratio,
            "by_column": by_column,
            "columns_with_missing": list(by_column.keys())
        }
    
    def _check_duplicates(self, df: pd.DataFrame) -> int:
        """Check for duplicate rows."""
        return df.duplicated().sum()
    
    def _check_class_balance(
        self,
        df: pd.DataFrame,
        target_column: str
    ) -> Dict[str, Any]:
        """Check class balance for classification problems."""
        if target_column not in df.columns:
            return {"is_imbalanced": False, "min_class_size": 0}
        
        class_counts = df[target_column].value_counts()
        min_class_size = class_counts.min()
        max_class_size = class_counts.max()
        
        # Consider imbalanced if ratio > 3:1
        is_imbalanced = (max_class_size / min_class_size) > 3 if min_class_size > 0 else True
        
        return {
            "is_imbalanced": is_imbalanced,
            "min_class_size": int(min_class_size),
            "max_class_size": int(max_class_size),
            "class_distribution": class_counts.to_dict()
        }
    
    def _check_invalid_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for invalid values like inf, -inf."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        has_inf = False
        details = []
        
        for col in numeric_cols:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                has_inf = True
                details.append(f"{col}: {inf_count} infinite values")
        
        return {
            "has_invalid": has_inf,
            "details": ", ".join(details) if details else "None"
        }
