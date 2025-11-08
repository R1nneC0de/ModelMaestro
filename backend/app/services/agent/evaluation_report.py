"""
Diagnostic report generator for model evaluation.

This module generates comprehensive evaluation reports with plots,
metrics, and recommendations, and stores them in GCS.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np
import structlog

from .evaluator import EvaluationResult
from .types import ProblemType
from .training_config import TrainingOutput
from .plot_generator import ClassificationPlotGenerator, RegressionPlotGenerator
from .report_formatter import MarkdownReportFormatter, HTMLReportFormatter, JSONReportFormatter

logger = structlog.get_logger()


class EvaluationReportGenerator:
    """
    Generate diagnostic reports for model evaluation.
    
    Creates comprehensive reports with metrics, plots, and recommendations.
    """
    
    def __init__(self, storage_client=None):
        """
        Initialize report generator.
        
        Args:
            storage_client: GCS storage client
        """
        self.storage_client = storage_client
        logger.info("evaluation_report_generator_initialized")
    
    async def generate_report(
        self,
        evaluation_result: EvaluationResult,
        training_output: TrainingOutput,
        problem_type: ProblemType,
        dataset_id: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None
    ) -> str:
        """
        Generate complete evaluation report.
        
        Args:
            evaluation_result: Evaluation result
            training_output: Training output
            problem_type: Type of problem
            dataset_id: Dataset identifier
            y_true: True labels/values
            y_pred: Predicted labels/values
            y_pred_proba: Predicted probabilities (optional)
            
        Returns:
            GCS URI to the report
        """
        logger.info(
            "generating_evaluation_report",
            dataset_id=dataset_id,
            decision=evaluation_result.decision.value
        )
        
        # Generate plots
        plots = {}
        if problem_type in [ProblemType.CLASSIFICATION, ProblemType.TEXT_CLASSIFICATION]:
            plots = ClassificationPlotGenerator.generate_plots(
                y_true, y_pred, y_pred_proba
            )
        elif problem_type in [ProblemType.REGRESSION, ProblemType.TIME_SERIES_FORECASTING]:
            plots = RegressionPlotGenerator.generate_plots(y_true, y_pred)
        
        # Generate reports
        markdown_report = MarkdownReportFormatter.format(
            evaluation_result, training_output, problem_type, plots
        )
        html_report = HTMLReportFormatter.format(
            evaluation_result, training_output, problem_type, plots
        )
        json_summary = JSONReportFormatter.format(
            evaluation_result, training_output
        )
        
        # Store in GCS
        report_uri = await self._store_report(
            dataset_id, markdown_report, html_report, json_summary, plots
        )
        
        logger.info("evaluation_report_generated", report_uri=report_uri)
        return report_uri
    
    async def _store_report(
        self,
        dataset_id: str,
        markdown_report: str,
        html_report: str,
        json_summary: Dict[str, Any],
        plots: Dict[str, bytes]
    ) -> str:
        """
        Store report and plots in GCS.
        
        Args:
            dataset_id: Dataset identifier
            markdown_report: Markdown report content
            html_report: HTML report content
            json_summary: JSON summary
            plots: Dictionary of plot names to bytes
            
        Returns:
            GCS URI to the report directory
        """
        if not self.storage_client:
            logger.warning("no_storage_client_report_not_stored")
            return f"local://evaluation_reports/{dataset_id}"
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        base_path = f"evaluation_reports/{dataset_id}/{timestamp}"
        
        try:
            # Store markdown
            markdown_path = f"{base_path}/report.md"
            await self._upload_text(markdown_path, markdown_report)
            
            # Store HTML
            html_path = f"{base_path}/report.html"
            await self._upload_text(html_path, html_report)
            
            # Store JSON
            json_path = f"{base_path}/summary.json"
            await self._upload_text(json_path, json.dumps(json_summary, indent=2))
            
            # Store plots
            for plot_name, plot_bytes in plots.items():
                plot_path = f"{base_path}/plots/{plot_name}.png"
                await self._upload_bytes(plot_path, plot_bytes)
            
            report_uri = f"gs://{self.storage_client.bucket_name}/{base_path}"
            logger.info("report_stored_in_gcs", uri=report_uri)
            return report_uri
            
        except Exception as e:
            logger.error("failed_to_store_report", error=str(e))
            return f"error://failed_to_store/{dataset_id}"
    
    async def _upload_text(self, path: str, content: str):
        """Upload text content to GCS."""
        if hasattr(self.storage_client, 'upload_text'):
            await self.storage_client.upload_text(path, content)
        else:
            # Fallback for sync client
            blob = self.storage_client.bucket.blob(path)
            blob.upload_from_string(content)
    
    async def _upload_bytes(self, path: str, content: bytes):
        """Upload bytes content to GCS."""
        if hasattr(self.storage_client, 'upload_bytes'):
            await self.storage_client.upload_bytes(path, content)
        else:
            # Fallback for sync client
            blob = self.storage_client.bucket.blob(path)
            blob.upload_from_string(content, content_type='image/png')
