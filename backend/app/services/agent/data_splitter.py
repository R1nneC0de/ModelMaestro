"""
Data Splitter for train/validation/test splits.

This module handles splitting data into train/validation/test sets
with support for stratification.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import numpy as np

from app.services.agent.types import ProblemAnalysis, ProblemType

logger = logging.getLogger(__name__)


@dataclass
class DataSplit:
    """
    Result of data splitting operation.
    
    Attributes:
        train_data: Training dataset
        val_data: Validation dataset
        test_data: Test dataset
        split_info: Information about the split (sizes, ratios, etc.)
    """
    train_data: Any
    val_data: Any
    test_data: Any
    split_info: Dict[str, Any]


class DataSplitter:
    """
    Handles splitting data into train/validation/test sets.
    
    Supports stratification for classification tasks and ensures
    proper distribution across splits.
    """
    
    # Default split ratios
    TRAIN_RATIO = 0.70
    VAL_RATIO = 0.15
    TEST_RATIO = 0.15
    
    def __init__(
        self,
        train_ratio: float = TRAIN_RATIO,
        val_ratio: float = VAL_RATIO,
        test_ratio: float = TEST_RATIO,
        random_state: int = 42
    ):
        """
        Initialize Data Splitter.
        
        Args:
            train_ratio: Proportion of data for training (default 0.70)
            val_ratio: Proportion of data for validation (default 0.15)
            test_ratio: Proportion of data for testing (default 0.15)
            random_state: Random seed for reproducibility
        """
        # Validate ratios sum to 1.0
        total = train_ratio + val_ratio + test_ratio
        if not np.isclose(total, 1.0):
            raise ValueError(
                f"Split ratios must sum to 1.0, got {total} "
                f"({train_ratio} + {val_ratio} + {test_ratio})"
            )
        
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.random_state = random_state
        
        logger.info(
            f"Initialized DataSplitter with ratios: "
            f"train={train_ratio:.0%}, val={val_ratio:.0%}, test={test_ratio:.0%}"
        )
    
    async def split_data(
        self,
        data: Any,
        analysis: ProblemAnalysis,
        target_column: Optional[str] = None,
        stratify: bool = True
    ) -> DataSplit:
        """
        Split data into train/validation/test sets.
        
        Args:
            data: Dataset to split (DataFrame or compatible format)
            analysis: Problem analysis results
            target_column: Name of target column for stratification
            stratify: Whether to use stratified splitting (for classification)
            
        Returns:
            DataSplit object with train/val/test sets
        """
        logger.info("Starting data splitting")
        
        # Convert to DataFrame if needed
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            df = pd.DataFrame(data)
        
        # Determine if we should stratify
        should_stratify = (
            stratify
            and target_column is not None
            and target_column in df.columns
            and analysis.problem_type in [
                ProblemType.CLASSIFICATION,
                ProblemType.TEXT_CLASSIFICATION
            ]
        )
        
        if should_stratify:
            logger.info(f"Using stratified split on column: {target_column}")
            train_df, val_df, test_df = self._stratified_split(
                df, target_column
            )
        else:
            logger.info("Using random split")
            train_df, val_df, test_df = self._random_split(df)
        
        # Prepare split info
        split_info = {
            "train_size": len(train_df),
            "val_size": len(val_df),
            "test_size": len(test_df),
            "train_ratio": len(train_df) / len(df),
            "val_ratio": len(val_df) / len(df),
            "test_ratio": len(test_df) / len(df),
            "stratified": should_stratify,
            "target_column": target_column,
            "random_state": self.random_state
        }
        
        # Add class distribution for classification
        if should_stratify and target_column:
            split_info["class_distribution"] = {
                "train": train_df[target_column].value_counts().to_dict(),
                "val": val_df[target_column].value_counts().to_dict(),
                "test": test_df[target_column].value_counts().to_dict()
            }
        
        logger.info(
            f"Data split complete: "
            f"train={split_info['train_size']}, "
            f"val={split_info['val_size']}, "
            f"test={split_info['test_size']}"
        )
        
        return DataSplit(
            train_data=train_df,
            val_data=val_df,
            test_data=test_df,
            split_info=split_info
        )
    
    def _random_split(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Perform random split without stratification."""
        # Shuffle the data
        df_shuffled = df.sample(frac=1, random_state=self.random_state).reset_index(drop=True)
        
        n = len(df_shuffled)
        train_end = int(n * self.train_ratio)
        val_end = train_end + int(n * self.val_ratio)
        
        train_df = df_shuffled[:train_end]
        val_df = df_shuffled[train_end:val_end]
        test_df = df_shuffled[val_end:]
        
        return train_df, val_df, test_df
    
    def _stratified_split(
        self,
        df: pd.DataFrame,
        target_column: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Perform stratified split maintaining class distribution.
        
        Uses sklearn's train_test_split for proper stratification.
        """
        from sklearn.model_selection import train_test_split
        
        # First split: separate test set
        train_val_df, test_df = train_test_split(
            df,
            test_size=self.test_ratio,
            stratify=df[target_column],
            random_state=self.random_state
        )
        
        # Second split: separate train and validation
        # Adjust validation ratio relative to remaining data
        val_ratio_adjusted = self.val_ratio / (self.train_ratio + self.val_ratio)
        
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_ratio_adjusted,
            stratify=train_val_df[target_column],
            random_state=self.random_state
        )
        
        return train_df, val_df, test_df
