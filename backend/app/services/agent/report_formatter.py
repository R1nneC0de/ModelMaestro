"""
Report formatting utilities.

Formats evaluation results into markdown, HTML, and JSON formats.
"""

import base64
import json
from datetime import datetime
from typing import Dict, Any
import structlog

from .evaluator import EvaluationResult, EvaluationDecision
from .types import ProblemType
from .training_config import TrainingOutput

logger = structlog.get_logger()


class MarkdownReportFormatter:
    """Format evaluation results as markdown."""
    
    @staticmethod
    def format(
        evaluation_result: EvaluationResult,
        training_output: TrainingOutput,
        problem_type: ProblemType,
        plots: Dict[str, bytes]
    ) -> str:
        """Generate markdown report."""
        lines = []
        
        # Header
        lines.extend(MarkdownReportFormatter._format_header(
            evaluation_result, training_output, problem_type
        ))
        
        # Metrics
        lines.extend(MarkdownReportFormatter._format_metrics(evaluation_result))
        
        # Threshold checks
        lines.extend(MarkdownReportFormatter._format_threshold_checks(
            evaluation_result, training_output
        ))
        
        # Baseline comparison
        lines.extend(MarkdownReportFormatter._format_baseline_comparison(evaluation_result))
        
        # Sanity checks
        if evaluation_result.sanity_checks:
            lines.extend(MarkdownReportFormatter._format_sanity_checks(evaluation_result))
        
        # Reasoning and recommendations
        lines.extend(MarkdownReportFormatter._format_reasoning(evaluation_result))
        lines.extend(MarkdownReportFormatter._format_recommendations(evaluation_result))
        
        # Training details
        lines.extend(MarkdownReportFormatter._format_training_details(training_output))
        
        # Plots
        if plots:
            lines.extend(MarkdownReportFormatter._format_plots_section(plots))
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_header(result, training_output, problem_type):
        """Format report header."""
        decision_emoji = "✅" if result.decision == EvaluationDecision.ACCEPT else "❌"
        return [
            "# Model Evaluation Report",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}Z",
            f"**Problem Type:** {problem_type.value}",
            f"**Architecture:** {training_output.strategy_config.architecture}",
            "",
            f"## {decision_emoji} Decision: {result.decision.value.upper()}",
            "",
        ]
    
    @staticmethod
    def _format_metrics(result):
        """Format metrics section."""
        lines = [
            "## Primary Metric",
            "",
            f"**{result.primary_metric_name}:** {result.primary_metric_value:.4f}",
            "",
            "## All Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
        ]
        for metric_name, value in sorted(result.all_metrics.items()):
            lines.append(f"| {metric_name} | {value:.4f} |")
        lines.append("")
        return lines
    
    @staticmethod
    def _format_threshold_checks(result, training_output):
        """Format threshold checks section."""
        lines = [
            "## Threshold Checks",
            "",
            "| Metric | Status | Value | Threshold |",
            "|--------|--------|-------|-----------|",
        ]
        for metric_name, passed in result.threshold_checks.items():
            status = "✓ Pass" if passed else "✗ Fail"
            value = result.all_metrics.get(metric_name, 0.0)
            threshold = training_output.strategy_config.acceptance_thresholds.get(metric_name, 0.0)
            lines.append(f"| {metric_name} | {status} | {value:.4f} | {threshold:.4f} |")
        lines.append("")
        return lines
    
    @staticmethod
    def _format_baseline_comparison(result):
        """Format baseline comparison section."""
        lines = [
            "## Baseline Comparison",
            "",
            "| Metric | Model | Baseline | Improvement |",
            "|--------|-------|----------|-------------|",
        ]
        for metric_name, baseline_info in result.baseline_metrics.items():
            if metric_name in result.all_metrics:
                model_value = result.all_metrics[metric_name]
                baseline_value = baseline_info.baseline_value
                
                if metric_name in ['rmse', 'mae', 'mse']:
                    improvement = ((baseline_value - model_value) / baseline_value) * 100
                else:
                    improvement = ((model_value - baseline_value) / baseline_value) * 100 if baseline_value > 0 else 0
                
                lines.append(f"| {metric_name} | {model_value:.4f} | {baseline_value:.4f} | {improvement:+.1f}% |")
        lines.append("")
        return lines
    
    @staticmethod
    def _format_sanity_checks(result):
        """Format sanity checks section."""
        lines = [
            "## Sanity Checks",
            "",
            "| Check | Status |",
            "|-------|--------|",
        ]
        for check_name, passed in result.sanity_checks.items():
            status = "✓ Pass" if passed else "✗ Fail"
            lines.append(f"| {check_name} | {status} |")
        lines.append("")
        return lines
    
    @staticmethod
    def _format_reasoning(result):
        """Format reasoning section."""
        return [
            "## Detailed Reasoning",
            "",
            "```",
            result.reasoning,
            "```",
            "",
        ]
    
    @staticmethod
    def _format_recommendations(result):
        """Format recommendations section."""
        if not result.recommendations:
            return []
        
        lines = ["## Recommendations", ""]
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        return lines
    
    @staticmethod
    def _format_training_details(training_output):
        """Format training details section."""
        return [
            "## Training Details",
            "",
            f"**Duration:** {training_output.training_duration_seconds:.1f} seconds",
            f"**Random Seed:** {training_output.random_seed}",
            f"**Job ID:** {training_output.job_id}",
            "",
        ]
    
    @staticmethod
    def _format_plots_section(plots):
        """Format plots section."""
        lines = [
            "## Visualizations",
            "",
            "See accompanying plot files:",
        ]
        for plot_name in plots.keys():
            lines.append(f"- {plot_name}.png")
        lines.append("")
        return lines


class HTMLReportFormatter:
    """Format evaluation results as HTML."""
    
    @staticmethod
    def format(
        evaluation_result: EvaluationResult,
        training_output: TrainingOutput,
        problem_type: ProblemType,
        plots: Dict[str, bytes]
    ) -> str:
        """Generate HTML report."""
        # Convert plots to base64
        plot_html = {}
        for plot_name, plot_bytes in plots.items():
            b64 = base64.b64encode(plot_bytes).decode('utf-8')
            plot_html[plot_name] = f'<img src="data:image/png;base64,{b64}" style="max-width: 100%; height: auto;">'
        
        decision_color = "#28a745" if evaluation_result.decision == EvaluationDecision.ACCEPT else "#dc3545"
        decision_emoji = "✅" if evaluation_result.decision == EvaluationDecision.ACCEPT else "❌"
        
        # Build HTML sections
        header = HTMLReportFormatter._build_header(
            evaluation_result, training_output, problem_type, decision_color, decision_emoji
        )
        metrics_section = HTMLReportFormatter._build_metrics_section(evaluation_result)
        thresholds_section = HTMLReportFormatter._build_thresholds_section(
            evaluation_result, training_output
        )
        reasoning_section = HTMLReportFormatter._build_reasoning_section(evaluation_result)
        recommendations_section = HTMLReportFormatter._build_recommendations_section(evaluation_result)
        plots_section = HTMLReportFormatter._build_plots_section(plot_html)
        training_section = HTMLReportFormatter._build_training_section(training_output)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Evaluation Report</title>
    {HTMLReportFormatter._get_styles()}
</head>
<body>
    <div class="container">
        {header}
        {metrics_section}
        {thresholds_section}
        {reasoning_section}
        {recommendations_section}
        {plots_section}
        {training_section}
    </div>
</body>
</html>"""
    
    @staticmethod
    def _get_styles():
        """Get CSS styles."""
        return """<style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }
        .decision { padding: 20px; border-radius: 8px; color: white; font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }
        .metric-box { display: inline-block; padding: 15px 25px; margin: 10px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
        .metric-label { font-size: 14px; color: #666; }
        .metric-value { font-size: 28px; font-weight: bold; color: #333; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #007bff; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .pass { color: #28a745; font-weight: bold; }
        .fail { color: #dc3545; font-weight: bold; }
        .plot { margin: 20px 0; text-align: center; }
        .recommendation { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .reasoning { background-color: #f8f9fa; padding: 20px; border-radius: 5px; white-space: pre-wrap; font-family: monospace; }
        .info { color: #666; font-size: 14px; }
    </style>"""
    
    @staticmethod
    def _build_header(result, training_output, problem_type, decision_color, decision_emoji):
        """Build header section."""
        return f"""<h1>Model Evaluation Report</h1>
        <p class="info"><strong>Generated:</strong> {datetime.utcnow().isoformat()}Z</p>
        <p class="info"><strong>Problem Type:</strong> {problem_type.value}</p>
        <p class="info"><strong>Architecture:</strong> {training_output.strategy_config.architecture}</p>
        <div class="decision" style="background-color: {decision_color};">{decision_emoji} {result.decision.value.upper()}</div>"""
    
    @staticmethod
    def _build_metrics_section(result):
        """Build metrics section."""
        rows = "".join([
            f"<tr><td>{name}</td><td>{value:.4f}</td></tr>"
            for name, value in sorted(result.all_metrics.items())
        ])
        return f"""<h2>Primary Metric</h2>
        <div class="metric-box">
            <div class="metric-label">{result.primary_metric_name}</div>
            <div class="metric-value">{result.primary_metric_value:.4f}</div>
        </div>
        <h2>All Metrics</h2>
        <table><tr><th>Metric</th><th>Value</th></tr>{rows}</table>"""
    
    @staticmethod
    def _build_thresholds_section(result, training_output):
        """Build thresholds section."""
        rows = ""
        for metric_name, passed in result.threshold_checks.items():
            status_class = "pass" if passed else "fail"
            status_text = "✓ Pass" if passed else "✗ Fail"
            value = result.all_metrics.get(metric_name, 0.0)
            threshold = training_output.strategy_config.acceptance_thresholds.get(metric_name, 0.0)
            rows += f'<tr><td>{metric_name}</td><td class="{status_class}">{status_text}</td><td>{value:.4f}</td><td>{threshold:.4f}</td></tr>'
        
        return f"""<h2>Threshold Checks</h2>
        <table><tr><th>Metric</th><th>Status</th><th>Value</th><th>Threshold</th></tr>{rows}</table>"""
    
    @staticmethod
    def _build_reasoning_section(result):
        """Build reasoning section."""
        return f'<h2>Detailed Reasoning</h2><div class="reasoning">{result.reasoning}</div>'
    
    @staticmethod
    def _build_recommendations_section(result):
        """Build recommendations section."""
        if not result.recommendations:
            return ""
        
        recs = "".join([
            f'<div class="recommendation">{i}. {rec}</div>'
            for i, rec in enumerate(result.recommendations, 1)
        ])
        return f"<h2>Recommendations</h2>{recs}"
    
    @staticmethod
    def _build_plots_section(plot_html):
        """Build plots section."""
        if not plot_html:
            return ""
        
        plots = "".join([
            f'<div class="plot"><h3>{name.replace("_", " ").title()}</h3>{img}</div>'
            for name, img in plot_html.items()
        ])
        return f"<h2>Visualizations</h2>{plots}"
    
    @staticmethod
    def _build_training_section(training_output):
        """Build training details section."""
        return f"""<h2>Training Details</h2>
        <p><strong>Duration:</strong> {training_output.training_duration_seconds:.1f} seconds</p>
        <p><strong>Random Seed:</strong> {training_output.random_seed}</p>
        <p><strong>Job ID:</strong> {training_output.job_id}</p>"""


class JSONReportFormatter:
    """Format evaluation results as JSON."""
    
    @staticmethod
    def format(
        evaluation_result: EvaluationResult,
        training_output: TrainingOutput
    ) -> Dict[str, Any]:
        """Generate JSON summary."""
        return {
            "decision": evaluation_result.decision.value,
            "primary_metric": {
                "name": evaluation_result.primary_metric_name,
                "value": evaluation_result.primary_metric_value
            },
            "all_metrics": evaluation_result.all_metrics,
            "threshold_checks": evaluation_result.threshold_checks,
            "sanity_checks": evaluation_result.sanity_checks,
            "baseline_metrics": {
                k: {
                    "metric_name": v.metric_name,
                    "baseline_value": v.baseline_value,
                    "description": v.description
                }
                for k, v in evaluation_result.baseline_metrics.items()
            },
            "reasoning": evaluation_result.reasoning,
            "recommendations": evaluation_result.recommendations,
            "confidence": evaluation_result.confidence,
            "training_details": {
                "architecture": training_output.strategy_config.architecture,
                "duration_seconds": training_output.training_duration_seconds,
                "random_seed": training_output.random_seed,
                "job_id": training_output.job_id
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
