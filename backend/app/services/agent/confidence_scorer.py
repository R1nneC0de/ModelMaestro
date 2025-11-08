"""
Confidence scoring utilities for problem analysis.

This module calculates confidence scores for ML problem analysis results
based on multiple factors including completeness, specificity, and consistency.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Calculates confidence scores for analysis results."""

    @staticmethod
    def calculate_confidence_score(
        result: Dict[str, Any], is_labeled: bool
    ) -> float:
        """
        Calculate adjusted confidence score based on multiple factors.
        
        Considers:
        - Base confidence from Gemini
        - Completeness of analysis
        - Consistency of results
        - Data quality indicators
        
        Args:
            result: Raw analysis result from Gemini
            is_labeled: Whether data is labeled
            
        Returns:
            Adjusted confidence score between 0.0 and 1.0
        """
        # Start with Gemini's confidence
        base_confidence = float(result.get("confidence", 0.5))
        
        # Factor 1: Completeness (are all expected fields present?)
        completeness_score = ConfidenceScorer._calculate_completeness_score(result)
        
        # Factor 2: Problem type specificity (is it a specific type or unknown?)
        problem_type = result.get("problem_type", "unknown")
        specificity_score = 1.0 if problem_type != "unknown" else 0.3
        
        # Factor 3: Data type clarity
        data_type = result.get("data_type", "unknown")
        data_clarity_score = 1.0 if data_type != "unknown" else 0.4
        
        # Factor 4: Reasoning quality (is there detailed reasoning?)
        reasoning = result.get("reasoning", "")
        reasoning_score = min(1.0, len(reasoning) / 200.0) if reasoning else 0.5
        
        # Factor 5: Label consistency
        label_consistency = 1.0 if result.get("is_labeled") == is_labeled else 0.8
        
        # Weighted combination of factors
        adjusted_confidence = (
            base_confidence * 0.40 +  # Gemini's assessment is most important
            completeness_score * 0.20 +
            specificity_score * 0.15 +
            data_clarity_score * 0.10 +
            reasoning_score * 0.10 +
            label_consistency * 0.05
        )
        
        # Ensure confidence is within valid range
        return max(0.0, min(1.0, adjusted_confidence))
    
    @staticmethod
    def _calculate_completeness_score(result: Dict[str, Any]) -> float:
        """
        Calculate completeness score based on presence of expected fields.
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Completeness score between 0.0 and 1.0
        """
        required_fields = [
            "problem_type",
            "data_type",
            "domain",
            "suggested_metrics",
            "complexity_score",
            "reasoning",
            "confidence",
        ]
        
        optional_fields = [
            "num_classes",
            "target_variable",
            "additional_insights",
        ]
        
        # Count present required fields
        required_present = sum(
            1 for field in required_fields if result.get(field) is not None
        )
        required_score = required_present / len(required_fields)
        
        # Count present optional fields (bonus)
        optional_present = sum(
            1 for field in optional_fields if result.get(field) is not None
        )
        optional_score = optional_present / len(optional_fields) * 0.2
        
        return min(1.0, required_score + optional_score)
    
    @staticmethod
    def get_confidence_level_description(confidence: float) -> str:
        """
        Get human-readable confidence level description.
        
        Args:
            confidence: Confidence score between 0.0 and 1.0
            
        Returns:
            Descriptive string for confidence level
        """
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.75:
            return "High"
        elif confidence >= 0.6:
            return "Moderate"
        elif confidence >= 0.4:
            return "Low"
        else:
            return "Very Low"
    
    @staticmethod
    def get_confidence_explanation(
        confidence: float, result: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for the confidence score.
        
        Args:
            confidence: Confidence score
            result: Analysis result
            
        Returns:
            Explanation string
        """
        if confidence >= 0.8:
            return (
                "The analysis is highly confident based on clear problem "
                "characteristics and sufficient data information."
            )
        elif confidence >= 0.6:
            return (
                "The analysis is reasonably confident, though some aspects "
                "may benefit from additional clarification."
            )
        elif confidence >= 0.4:
            return (
                "The analysis has moderate confidence. Consider providing more "
                "details about the problem or data for improved accuracy."
            )
        else:
            # Identify specific issues
            issues = []
            if result.get("problem_type") == "unknown":
                issues.append("unclear problem type")
            if result.get("data_type") == "unknown":
                issues.append("unclear data type")
            if not result.get("reasoning"):
                issues.append("limited analysis details")
            
            issue_str = ", ".join(issues) if issues else "limited information"
            return (
                f"The analysis has low confidence due to {issue_str}. "
                f"Additional context would significantly improve the assessment."
            )
