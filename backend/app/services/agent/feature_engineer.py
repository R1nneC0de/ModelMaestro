"""
Feature Engineering pipelines for different data types.

This module handles feature engineering for image, text, and tabular data
with appropriate transformations and normalization.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np

from app.services.agent.types import ProblemAnalysis, DataType
from app.services.agent.data_splitter import DataSplit

logger = logging.getLogger(__name__)


@dataclass
class ProcessedData:
    """
    Result of complete data processing.
    
    Attributes:
        train_data: Processed training data
        val_data: Processed validation data
        test_data: Processed test data
        feature_info: Information about features and transformations
        preprocessing_pipeline: Serializable preprocessing pipeline
    """
    train_data: Any
    val_data: Any
    test_data: Any
    feature_info: Dict[str, Any]
    preprocessing_pipeline: Optional[Any] = None


class FeatureEngineer:
    """
    Handles feature engineering for different data types.
    
    Provides pipelines for image, text, and tabular data with
    appropriate transformations and normalization.
    """
    
    def __init__(self):
        """Initialize Feature Engineer."""
        logger.info("Initialized FeatureEngineer")
    
    async def process_features(
        self,
        data_split: DataSplit,
        analysis: ProblemAnalysis,
        target_column: Optional[str] = None
    ) -> ProcessedData:
        """
        Process features based on data type.
        
        Args:
            data_split: Split data (train/val/test)
            analysis: Problem analysis results
            target_column: Name of target column
            
        Returns:
            ProcessedData with engineered features
        """
        logger.info(f"Processing features for {analysis.data_type.value} data")
        
        if analysis.data_type == DataType.TABULAR:
            return await self._process_tabular_features(
                data_split, analysis, target_column
            )
        elif analysis.data_type == DataType.TEXT:
            return await self._process_text_features(
                data_split, analysis, target_column
            )
        elif analysis.data_type == DataType.IMAGE:
            return await self._process_image_features(
                data_split, analysis
            )
        else:
            # For unknown or multimodal, return as-is with basic info
            logger.warning(f"No specific processing for {analysis.data_type.value}")
            return ProcessedData(
                train_data=data_split.train_data,
                val_data=data_split.val_data,
                test_data=data_split.test_data,
                feature_info={"data_type": analysis.data_type.value}
            )
    
    async def _process_tabular_features(
        self,
        data_split: DataSplit,
        analysis: ProblemAnalysis,
        target_column: Optional[str]
    ) -> ProcessedData:
        """Process tabular data with normalization and encoding."""
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.compose import ColumnTransformer
        from sklearn.preprocessing import OneHotEncoder
        
        train_df = data_split.train_data
        val_df = data_split.val_data
        test_df = data_split.test_data
        
        # Identify feature types
        numeric_features = train_df.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        
        categorical_features = train_df.select_dtypes(
            include=['object', 'category']
        ).columns.tolist()
        
        # Remove target column from features
        if target_column:
            if target_column in numeric_features:
                numeric_features.remove(target_column)
            if target_column in categorical_features:
                categorical_features.remove(target_column)
        
        logger.info(
            f"Identified {len(numeric_features)} numeric and "
            f"{len(categorical_features)} categorical features"
        )
        
        # Create preprocessing pipeline
        transformers = []
        
        if numeric_features:
            transformers.append((
                'num',
                StandardScaler(),
                numeric_features
            ))
        
        if categorical_features:
            # Use one-hot encoding for low cardinality, label encoding for high
            low_card_features = []
            high_card_features = []
            
            for col in categorical_features:
                n_unique = train_df[col].nunique()
                if n_unique <= 10:
                    low_card_features.append(col)
                else:
                    high_card_features.append(col)
            
            if low_card_features:
                transformers.append((
                    'cat_onehot',
                    OneHotEncoder(handle_unknown='ignore', sparse_output=False),
                    low_card_features
                ))
            
            # For high cardinality, we'll use label encoding separately
            if high_card_features:
                logger.info(
                    f"High cardinality features: {high_card_features}. "
                    "Using label encoding."
                )
        
        # Create and fit the pipeline
        if transformers:
            preprocessor = ColumnTransformer(
                transformers=transformers,
                remainder='passthrough'
            )
            
            # Fit on training data only
            X_train = train_df.drop(columns=[target_column] if target_column else [])
            preprocessor.fit(X_train)
            
            # Transform all splits
            X_train_processed = preprocessor.transform(X_train)
            X_val_processed = preprocessor.transform(
                val_df.drop(columns=[target_column] if target_column else [])
            )
            X_test_processed = preprocessor.transform(
                test_df.drop(columns=[target_column] if target_column else [])
            )
            
            # Get feature names after transformation
            feature_names = self._get_feature_names(preprocessor)
            
        else:
            # No transformations needed
            X_train_processed = train_df.drop(
                columns=[target_column] if target_column else []
            ).values
            X_val_processed = val_df.drop(
                columns=[target_column] if target_column else []
            ).values
            X_test_processed = test_df.drop(
                columns=[target_column] if target_column else []
            ).values
            feature_names = train_df.columns.tolist()
            preprocessor = None
        
        # Extract target if present
        y_train = train_df[target_column].values if target_column else None
        y_val = val_df[target_column].values if target_column else None
        y_test = test_df[target_column].values if target_column else None
        
        feature_info = {
            "data_type": "tabular",
            "numeric_features": numeric_features,
            "categorical_features": categorical_features,
            "feature_names": feature_names,
            "n_features": X_train_processed.shape[1],
            "normalization": "StandardScaler",
            "encoding": "OneHotEncoder for low cardinality"
        }
        
        return ProcessedData(
            train_data={"X": X_train_processed, "y": y_train},
            val_data={"X": X_val_processed, "y": y_val},
            test_data={"X": X_test_processed, "y": y_test},
            feature_info=feature_info,
            preprocessing_pipeline=preprocessor
        )
    
    async def _process_text_features(
        self,
        data_split: DataSplit,
        analysis: ProblemAnalysis,
        target_column: Optional[str]
    ) -> ProcessedData:
        """Process text data with basic tokenization info."""
        # For text data, we'll primarily rely on Vertex AI's text processing
        # Just prepare the data structure and metadata
        
        train_df = data_split.train_data
        val_df = data_split.val_data
        test_df = data_split.test_data
        
        # Identify text column (assume first non-target column)
        text_columns = [
            col for col in train_df.columns
            if col != target_column and train_df[col].dtype == 'object'
        ]
        
        if not text_columns:
            raise ValueError("No text column found in dataset")
        
        text_column = text_columns[0]
        logger.info(f"Using text column: {text_column}")
        
        # Basic text statistics
        avg_length = train_df[text_column].str.len().mean()
        max_length = train_df[text_column].str.len().max()
        
        feature_info = {
            "data_type": "text",
            "text_column": text_column,
            "target_column": target_column,
            "avg_text_length": float(avg_length),
            "max_text_length": int(max_length),
            "preprocessing": "Vertex AI native text processing"
        }
        
        return ProcessedData(
            train_data=train_df,
            val_data=val_df,
            test_data=test_df,
            feature_info=feature_info,
            preprocessing_pipeline=None
        )
    
    async def _process_image_features(
        self,
        data_split: DataSplit,
        analysis: ProblemAnalysis
    ) -> ProcessedData:
        """Process image data metadata."""
        # For image data, Vertex AI handles the actual processing
        # We just need to prepare metadata and file paths
        
        feature_info = {
            "data_type": "image",
            "preprocessing": "Vertex AI native image processing",
            "normalization": "Automatic normalization by Vertex AI",
            "augmentation": "Automatic augmentation by Vertex AI AutoML"
        }
        
        return ProcessedData(
            train_data=data_split.train_data,
            val_data=data_split.val_data,
            test_data=data_split.test_data,
            feature_info=feature_info,
            preprocessing_pipeline=None
        )
    
    def _get_feature_names(self, preprocessor) -> List[str]:
        """Extract feature names from ColumnTransformer."""
        feature_names = []
        
        try:
            for name, transformer, columns in preprocessor.transformers_:
                if name == 'remainder':
                    continue
                
                if hasattr(transformer, 'get_feature_names_out'):
                    names = transformer.get_feature_names_out(columns)
                    feature_names.extend(names)
                else:
                    feature_names.extend(columns)
        except Exception as e:
            logger.warning(f"Could not extract feature names: {e}")
            feature_names = [f"feature_{i}" for i in range(100)]  # Fallback
        
        return feature_names
