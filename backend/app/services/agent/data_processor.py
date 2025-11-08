"""
Data Processor orchestrator with GCS integration.

This module orchestrates the complete data processing pipeline including
validation, splitting, feature engineering, and storage to GCS.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np

from app.services.agent.types import ProblemAnalysis
from app.services.agent.data_quality import (
    DataQualityValidator,
    DataQualityReport,
    ProcessingStrategy,
    MissingValueStrategy
)
from app.services.agent.data_splitter import DataSplitter, DataSplit
from app.services.agent.feature_engineer import FeatureEngineer, ProcessedData

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Complete data processor with GCS integration.
    
    Orchestrates data validation, splitting, feature engineering,
    and storage to Google Cloud Storage.
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize Data Processor.
        
        Args:
            bucket_name: GCS bucket name (defaults to settings)
        """
        from app.core.config import settings
        from google.cloud import storage
        
        self.bucket_name = bucket_name or settings.GCS_BUCKET_NAME
        self.storage_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        self.bucket = self.storage_client.bucket(self.bucket_name)
        
        self.validator = DataQualityValidator()
        self.splitter = DataSplitter()
        self.feature_engineer = FeatureEngineer()
        
        logger.info(
            f"Initialized DataProcessor with bucket: {self.bucket_name}"
        )
    
    async def process_and_store(
        self,
        dataset_id: str,
        data: Any,
        analysis: ProblemAnalysis,
        target_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete data processing pipeline with GCS storage.
        
        Args:
            dataset_id: Unique identifier for the dataset
            data: Raw dataset
            analysis: Problem analysis results
            target_column: Name of target column
            
        Returns:
            Dictionary with processing results and GCS paths
        """
        logger.info(f"Starting complete data processing for dataset {dataset_id}")
        
        # Step 1: Validate data quality
        quality_report = await self.validator.validate_data_quality(
            data, analysis, target_column
        )
        
        if not quality_report.is_valid:
            logger.error(
                f"Data quality validation failed: "
                f"severity={quality_report.severity_score:.2f}"
            )
            raise ValueError(
                f"Data quality issues detected: {quality_report.issues}. "
                f"Recommendations: {quality_report.recommendations}"
            )
        
        # Step 2: Determine processing strategy
        strategy = await self.validator.determine_processing_strategy(
            quality_report, analysis, data
        )
        
        logger.info(f"Processing strategy: {strategy.reasoning}")
        
        # Step 3: Apply preprocessing based on strategy
        cleaned_data = await self._apply_preprocessing(
            data, strategy, analysis
        )
        
        # Step 4: Split data
        data_split = await self.splitter.split_data(
            cleaned_data, analysis, target_column, stratify=True
        )
        
        # Step 5: Feature engineering
        processed_data = await self.feature_engineer.process_features(
            data_split, analysis, target_column
        )
        
        # Step 6: Upload to GCS
        gcs_paths = await self._upload_to_gcs(
            dataset_id, processed_data, data_split
        )
        
        # Step 7: Store metadata
        metadata = await self._store_metadata(
            dataset_id,
            quality_report,
            strategy,
            data_split,
            processed_data,
            gcs_paths
        )
        
        logger.info(
            f"Data processing complete for dataset {dataset_id}. "
            f"Files uploaded to GCS."
        )
        
        return {
            "dataset_id": dataset_id,
            "quality_report": quality_report,
            "processing_strategy": strategy,
            "split_info": data_split.split_info,
            "feature_info": processed_data.feature_info,
            "gcs_paths": gcs_paths,
            "metadata": metadata
        }
    
    async def _apply_preprocessing(
        self,
        data: Any,
        strategy: ProcessingStrategy,
        analysis: ProblemAnalysis
    ) -> pd.DataFrame:
        """Apply preprocessing based on strategy."""
        df = self.validator._to_dataframe(data, analysis.data_type)
        
        # Handle duplicates
        if strategy.handle_duplicates:
            initial_size = len(df)
            df = df.drop_duplicates()
            removed = initial_size - len(df)
            if removed > 0:
                logger.info(f"Removed {removed} duplicate rows")
        
        # Handle missing values
        if strategy.missing_value_strategy == MissingValueStrategy.DROP_ROWS:
            initial_size = len(df)
            df = df.dropna()
            removed = initial_size - len(df)
            if removed > 0:
                logger.info(f"Dropped {removed} rows with missing values")
        
        elif strategy.missing_value_strategy == MissingValueStrategy.DROP_COLUMNS:
            if strategy.drop_columns:
                df = df.drop(columns=strategy.drop_columns)
                logger.info(f"Dropped columns: {strategy.drop_columns}")
        
        elif strategy.missing_value_strategy == MissingValueStrategy.MEAN_IMPUTATION:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    mean_val = df[col].mean()
                    df[col].fillna(mean_val, inplace=True)
                    logger.debug(f"Imputed {col} with mean: {mean_val:.2f}")
        
        elif strategy.missing_value_strategy == MissingValueStrategy.MEDIAN_IMPUTATION:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    median_val = df[col].median()
                    df[col].fillna(median_val, inplace=True)
                    logger.debug(f"Imputed {col} with median: {median_val:.2f}")
        
        elif strategy.missing_value_strategy == MissingValueStrategy.MODE_IMPUTATION:
            for col in df.columns:
                if df[col].isnull().any():
                    mode_val = df[col].mode()[0]
                    df[col].fillna(mode_val, inplace=True)
                    logger.debug(f"Imputed {col} with mode: {mode_val}")
        
        # Handle outliers if needed
        if strategy.handle_outliers:
            df = self._handle_outliers(df)
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using IQR method."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            # Cap outliers instead of removing
            initial_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if initial_outliers > 0:
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                logger.debug(f"Capped {initial_outliers} outliers in {col}")
        
        return df
    
    async def _upload_to_gcs(
        self,
        dataset_id: str,
        processed_data: ProcessedData,
        data_split: DataSplit
    ) -> Dict[str, str]:
        """Upload processed data to GCS."""
        import pickle
        
        gcs_paths = {}
        base_path = f"data/{dataset_id}/processed"
        
        # Upload train data (pickle for custom training)
        train_path = f"{base_path}/train.pkl"
        train_blob = self.bucket.blob(train_path)
        train_blob.upload_from_string(
            pickle.dumps(processed_data.train_data),
            content_type='application/octet-stream'
        )
        gcs_paths["train"] = f"gs://{self.bucket_name}/{train_path}"
        logger.info(f"Uploaded train data to {gcs_paths['train']}")
        
        # Upload validation data (pickle for custom training)
        val_path = f"{base_path}/val.pkl"
        val_blob = self.bucket.blob(val_path)
        val_blob.upload_from_string(
            pickle.dumps(processed_data.val_data),
            content_type='application/octet-stream'
        )
        gcs_paths["val"] = f"gs://{self.bucket_name}/{val_path}"
        logger.info(f"Uploaded validation data to {gcs_paths['val']}")
        
        # Upload test data (pickle for custom training)
        test_path = f"{base_path}/test.pkl"
        test_blob = self.bucket.blob(test_path)
        test_blob.upload_from_string(
            pickle.dumps(processed_data.test_data),
            content_type='application/octet-stream'
        )
        gcs_paths["test"] = f"gs://{self.bucket_name}/{test_path}"
        logger.info(f"Uploaded test data to {gcs_paths['test']}")
        
        # Upload combined CSV for AutoML (with split column)
        combined_csv_path = f"{base_path}/combined_automl.csv"
        combined_df = self._create_combined_csv_for_automl(
            data_split.train_data,
            data_split.val_data,
            data_split.test_data
        )
        combined_blob = self.bucket.blob(combined_csv_path)
        combined_blob.upload_from_string(
            combined_df.to_csv(index=False),
            content_type='text/csv'
        )
        gcs_paths["automl_csv"] = f"gs://{self.bucket_name}/{combined_csv_path}"
        logger.info(f"Uploaded AutoML CSV to {gcs_paths['automl_csv']}")
        
        # Upload preprocessing pipeline if exists
        if processed_data.preprocessing_pipeline:
            pipeline_path = f"{base_path}/pipeline.pkl"
            pipeline_blob = self.bucket.blob(pipeline_path)
            pipeline_blob.upload_from_string(
                pickle.dumps(processed_data.preprocessing_pipeline),
                content_type='application/octet-stream'
            )
            gcs_paths["pipeline"] = f"gs://{self.bucket_name}/{pipeline_path}"
            logger.info(f"Uploaded preprocessing pipeline to {gcs_paths['pipeline']}")
        
        return gcs_paths
    
    def _create_combined_csv_for_automl(
        self,
        train_data: pd.DataFrame,
        val_data: pd.DataFrame,
        test_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create a combined CSV with split column for AutoML.
        
        AutoML expects a single CSV with a column indicating train/val/test split.
        """
        # Add split column to each dataset
        train_df = train_data.copy()
        train_df['ml_use'] = 'TRAIN'
        
        val_df = val_data.copy()
        val_df['ml_use'] = 'VALIDATE'
        
        test_df = test_data.copy()
        test_df['ml_use'] = 'TEST'
        
        # Combine all splits
        combined_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
        
        logger.info(
            f"Created combined CSV: {len(train_df)} train, "
            f"{len(val_df)} val, {len(test_df)} test"
        )
        
        return combined_df
    
    class NumpyEncoder(json.JSONEncoder):
        """Custom JSON encoder for numpy types."""
        def default(self, obj):
            if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
    
    async def _store_metadata(
        self,
        dataset_id: str,
        quality_report: DataQualityReport,
        strategy: ProcessingStrategy,
        data_split: DataSplit,
        processed_data: ProcessedData,
        gcs_paths: Dict[str, str]
    ) -> Dict[str, Any]:
        """Store processing metadata to GCS."""
        metadata = {
            "dataset_id": dataset_id,
            "processed_at": datetime.utcnow().isoformat(),
            "quality_report": {
                "is_valid": quality_report.is_valid,
                "issues": [issue.value for issue in quality_report.issues],
                "severity_score": float(quality_report.severity_score),
                "recommendations": quality_report.recommendations,
                "missing_value_stats": quality_report.missing_value_stats,
                "duplicate_count": int(quality_report.duplicate_count)
            },
            "processing_strategy": {
                "missing_value_strategy": strategy.missing_value_strategy.value,
                "drop_columns": strategy.drop_columns,
                "handle_duplicates": strategy.handle_duplicates,
                "handle_outliers": strategy.handle_outliers,
                "reasoning": strategy.reasoning
            },
            "split_info": data_split.split_info,
            "feature_info": processed_data.feature_info,
            "gcs_paths": gcs_paths
        }
        
        # Upload metadata
        metadata_path = f"data/{dataset_id}/processed/metadata.json"
        metadata_blob = self.bucket.blob(metadata_path)
        metadata_blob.upload_from_string(
            json.dumps(metadata, indent=2, cls=self.NumpyEncoder),
            content_type='application/json'
        )
        
        logger.info(f"Stored metadata at gs://{self.bucket_name}/{metadata_path}")
        
        return metadata
