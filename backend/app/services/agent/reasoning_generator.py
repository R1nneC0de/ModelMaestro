"""
Reasoning generation utilities for problem analysis.

This module generates human-readable explanations for ML problem analysis
results, combining AI insights with structured reasoning.
"""

import logging
from typing import Any, Dict

from app.services.agent.confidence_scorer import ConfidenceScorer

logger = logging.getLogger(__name__)


class ReasoningGenerator:
    """Generates enhanced reasoning explanations for analysis results."""

    @staticmethod
    def generate_enhanced_reasoning(
        result: Dict[str, Any],
        gemini_confidence: float,
        adjusted_confidence: float,
    ) -> str:
        """
        Generate enhanced human-readable reasoning explanation.
        
        Combines Gemini's reasoning with additional context about confidence
        and analysis quality.
        
        Args:
            result: Analysis result from Gemini
            gemini_confidence: Original confidence from Gemini
            adjusted_confidence: Calculated adjusted confidence
            
        Returns:
            Enhanced reasoning string
        """
        base_reasoning = result.get("reasoning", "")
        
        # Build enhanced reasoning sections
        reasoning_parts = []
        
        # Add base reasoning
        if base_reasoning:
            reasoning_parts.append(f"Analysis: {base_reasoning}")
        
        # Add problem type explanation
        problem_type = result.get("problem_type", "unknown")
        data_type = result.get("data_type", "unknown")
        
        if problem_type != "unknown" and data_type != "unknown":
            reasoning_parts.append(
                f"This appears to be a {problem_type} problem working with "
                f"{data_type} data."
            )
        
        # Add domain context
        domain = result.get("domain", "General")
        if domain and domain != "General":
            reasoning_parts.append(
                f"The problem domain is identified as {domain}, which helps "
                f"inform appropriate model selection and evaluation metrics."
            )
        
        # Add complexity insight
        complexity = float(result.get("complexity_score", 0.5))
        complexity_desc = ReasoningGenerator._get_complexity_description(complexity)
        
        reasoning_parts.append(
            f"The problem is assessed as {complexity_desc} "
            f"(complexity score: {complexity:.2f})."
        )
        
        # Add metrics recommendation
        metrics = result.get("suggested_metrics", [])
        if metrics:
            metrics_str = ", ".join(metrics[:3])  # Show top 3
            reasoning_parts.append(
                f"Recommended evaluation metrics include: {metrics_str}."
            )
        
        # Add confidence explanation
        confidence_level = ConfidenceScorer.get_confidence_level_description(
            adjusted_confidence
        )
        confidence_explanation = ConfidenceScorer.get_confidence_explanation(
            adjusted_confidence, result
        )
        reasoning_parts.append(
            f"Confidence Level: {confidence_level} ({adjusted_confidence:.2f}). "
            f"{confidence_explanation}"
        )
        
        # Add any additional insights
        insights = result.get("additional_insights", {})
        if insights:
            insight_items = [
                f"{k}: {v}" for k, v in list(insights.items())[:2]
            ]
            if insight_items:
                reasoning_parts.append(
                    f"Additional insights: {'; '.join(insight_items)}."
                )
        
        return " ".join(reasoning_parts)
    
    @staticmethod
    def _get_complexity_description(complexity: float) -> str:
        """
        Get human-readable complexity description.
        
        Args:
            complexity: Complexity score between 0.0 and 1.0
            
        Returns:
            Descriptive string for complexity level
        """
        if complexity < 0.3:
            return "relatively straightforward"
        elif complexity < 0.6:
            return "moderately complex"
        else:
            return "highly complex"
