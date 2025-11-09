"""
Confusion Matrix Generator for trained models.

This module generates confusion matrices and model evaluation visualizations
from trained models and test data stored in GCS.
"""

import io
import json
import pickle
from typing import Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
import structlog
from google.cloud import storage
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score,
    precision_recall_fscore_support
)

from app.core.config import settings

logger = structlog.get_logger()


class ConfusionMatrixGenerator:
    """
    Generate confusion matrices and classification reports for trained models.

    This class handles loading models from GCS, making predictions on test data,
    and generating comprehensive evaluation visualizations.
    """

    def __init__(self, gcs_bucket_name: Optional[str] = None):
        """
        Initialize the confusion matrix generator.

        Args:
            gcs_bucket_name: GCS bucket name. If None, uses settings.
        """
        self.bucket_name = gcs_bucket_name or settings.GCS_BUCKET_NAME
        self.storage_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        self.bucket = self.storage_client.bucket(self.bucket_name)

        logger.info(
            "confusion_matrix_generator_initialized",
            bucket=self.bucket_name
        )

    async def generate_confusion_matrix(
        self,
        metadata_path: str,
        model_path: Optional[str] = None,
        test_data_path: Optional[str] = None,
        upload_to_gcs: bool = True,
        dataset_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate confusion matrix and evaluation metrics.

        Args:
            metadata_path: Path to metadata.json (local or GCS)
            model_path: Optional GCS path to model. If None, extracted from metadata.
            test_data_path: Optional path to test data. If None, extracted from metadata.
            upload_to_gcs: Whether to upload results to GCS
            dataset_id: Optional dataset ID for naming output files

        Returns:
            Dictionary containing:
                - confusion_matrix: numpy array
                - classification_report: dict
                - metrics: dict with accuracy, precision, recall, f1
                - plots: dict with plot data
                - gcs_uris: dict with GCS paths (if uploaded)
        """
        logger.info(
            "generating_confusion_matrix",
            metadata_path=metadata_path,
            model_path=model_path,
            test_data_path=test_data_path
        )

        # Step 1: Load metadata
        metadata = await self._load_metadata(metadata_path)

        # Step 2: Extract paths from metadata if not provided
        if not model_path:
            model_path = metadata.get("model_uri")
        if not test_data_path:
            test_data_path = metadata.get("gcs_paths", {}).get("test")

        if not dataset_id:
            dataset_id = metadata.get("dataset_id", "unknown")

        logger.info(
            "paths_resolved",
            model_path=model_path,
            test_data_path=test_data_path,
            dataset_id=dataset_id
        )

        # Step 3: Load model and test data
        model = await self._load_model(model_path)
        X_test, y_test = await self._load_test_data(test_data_path)

        # Step 4: Generate predictions
        y_pred = model.predict(X_test)
        y_pred_proba = None
        if hasattr(model, 'predict_proba'):
            y_pred_proba = model.predict_proba(X_test)

        logger.info(
            "predictions_generated",
            test_samples=len(y_test),
            unique_predictions=len(np.unique(y_pred))
        )

        # Step 5: Calculate metrics
        cm = confusion_matrix(y_test, y_pred)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_test, y_pred, average='weighted'
        )

        # Generate detailed classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)

        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "support": int(np.sum(support))
        }

        logger.info(
            "metrics_calculated",
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1
        )

        # Step 6: Generate plots
        plots = await self._generate_plots(
            cm, y_test, y_pred, y_pred_proba, metadata
        )

        # Step 7: Compile results
        results = {
            "dataset_id": dataset_id,
            "confusion_matrix": cm.tolist(),
            "classification_report": class_report,
            "metrics": metrics,
            "plots": plots,
            "metadata": {
                "test_samples": len(y_test),
                "classes": np.unique(y_test).tolist(),
                "model_path": model_path,
                "test_data_path": test_data_path
            }
        }

        # Step 8: Upload to GCS if requested
        if upload_to_gcs:
            gcs_uris = await self._upload_results(
                dataset_id, results, plots, metadata
            )
            results["gcs_uris"] = gcs_uris

        logger.info(
            "confusion_matrix_generated",
            dataset_id=dataset_id,
            accuracy=accuracy,
            uploaded=upload_to_gcs
        )

        return results

    async def _load_metadata(self, metadata_path: str) -> Dict[str, Any]:
        """Load metadata from local file or GCS."""
        if metadata_path.startswith("gs://"):
            # Load from GCS
            gcs_path = metadata_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(gcs_path)
            content = blob.download_as_string()
            return json.loads(content)
        else:
            # Load from local file
            with open(metadata_path, 'r') as f:
                return json.load(f)

    async def _load_model(self, model_path: str):
        """Load model from GCS."""
        if not model_path:
            raise ValueError("Model path is required")

        logger.info("loading_model", model_path=model_path)

        if model_path.startswith("gs://"):
            # Extract bucket and path
            gcs_path = model_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(gcs_path)
            model_bytes = blob.download_as_bytes()
            return pickle.loads(model_bytes)
        elif model_path.startswith("projects/"):
            # Vertex AI managed model - would need different loading logic
            raise NotImplementedError(
                "Loading Vertex AI managed models not yet implemented. "
                "Please export model to GCS first."
            )
        else:
            # Local file
            with open(model_path, 'rb') as f:
                return pickle.load(f)

    async def _load_test_data(
        self, test_data_path: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Load test data from GCS."""
        if not test_data_path:
            raise ValueError("Test data path is required")

        logger.info("loading_test_data", test_data_path=test_data_path)

        if test_data_path.startswith("gs://"):
            gcs_path = test_data_path.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(gcs_path)
            data_bytes = blob.download_as_bytes()
            data = pickle.loads(data_bytes)
        else:
            with open(test_data_path, 'rb') as f:
                data = pickle.load(f)

        # Extract X and y
        if isinstance(data, dict):
            X_test = data['X']
            y_test = data['y']
        elif isinstance(data, tuple):
            X_test, y_test = data
        else:
            raise ValueError(f"Unexpected test data format: {type(data)}")

        return X_test, y_test

    async def _generate_plots(
        self,
        cm: np.ndarray,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray],
        metadata: Dict[str, Any]
    ) -> Dict[str, bytes]:
        """Generate visualization plots."""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from sklearn.metrics import ConfusionMatrixDisplay

        plots = {}

        # 1. Confusion Matrix
        fig, ax = plt.subplots(figsize=(10, 8))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(ax=ax, cmap='Blues', values_format='d')
        ax.set_title('Confusion Matrix', fontsize=16, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plots['confusion_matrix'] = buf.getvalue()
        plt.close(fig)

        # 2. Normalized Confusion Matrix
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        fig, ax = plt.subplots(figsize=(10, 8))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm_normalized)
        disp.plot(ax=ax, cmap='Blues', values_format='.2f')
        ax.set_title('Normalized Confusion Matrix', fontsize=16, fontweight='bold')
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plots['confusion_matrix_normalized'] = buf.getvalue()
        plt.close(fig)

        # 3. ROC Curve (if probabilities available and binary classification)
        if y_pred_proba is not None and len(np.unique(y_true)) == 2:
            from sklearn.metrics import roc_curve, auc

            if y_pred_proba.ndim == 2:
                y_pred_proba_pos = y_pred_proba[:, 1]
            else:
                y_pred_proba_pos = y_pred_proba

            fpr, tpr, _ = roc_curve(y_true, y_pred_proba_pos)
            roc_auc = auc(fpr, tpr)

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(fpr, tpr, color='darkorange', lw=2,
                   label=f'ROC curve (AUC = {roc_auc:.3f})')
            ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                   label='Random classifier')
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('False Positive Rate')
            ax.set_ylabel('True Positive Rate')
            ax.set_title('ROC Curve')
            ax.legend(loc="lower right")
            ax.grid(alpha=0.3)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            plots['roc_curve'] = buf.getvalue()
            plt.close(fig)

        logger.info("plots_generated", num_plots=len(plots))
        return plots

    async def _upload_results(
        self,
        dataset_id: str,
        results: Dict[str, Any],
        plots: Dict[str, bytes],
        metadata: Dict[str, Any]
    ) -> Dict[str, str]:
        """Upload results to GCS."""
        from datetime import datetime

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base_path = f"evaluation/{dataset_id}/confusion_matrix/{timestamp}"

        gcs_uris = {}

        # Upload metrics JSON
        metrics_path = f"{base_path}/metrics.json"
        metrics_blob = self.bucket.blob(metrics_path)
        metrics_blob.upload_from_string(
            json.dumps({
                "confusion_matrix": results["confusion_matrix"],
                "metrics": results["metrics"],
                "classification_report": results["classification_report"],
                "metadata": results["metadata"]
            }, indent=2),
            content_type="application/json"
        )
        gcs_uris["metrics"] = f"gs://{self.bucket_name}/{metrics_path}"

        # Upload plots
        for plot_name, plot_bytes in plots.items():
            plot_path = f"{base_path}/plots/{plot_name}.png"
            plot_blob = self.bucket.blob(plot_path)
            plot_blob.upload_from_string(plot_bytes, content_type="image/png")
            gcs_uris[f"plot_{plot_name}"] = f"gs://{self.bucket_name}/{plot_path}"

        logger.info(
            "results_uploaded_to_gcs",
            base_path=base_path,
            num_files=len(gcs_uris)
        )

        return gcs_uris
