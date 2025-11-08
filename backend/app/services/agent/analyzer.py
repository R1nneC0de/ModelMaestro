"""
Problem Analyzer component for analyzing ML problems and datasets.

This module uses Gemini to understand problem types, data characteristics,
and domains to guide the ML pipeline. It provides comprehensive analysis
including problem classification, data type detection, and domain identification.
"""

import logging
from typing import Any, Dict, List, Optional

from app.services.agent.confidence_scorer import ConfidenceScorer
from app.services.agent.data_type_detector import DataTypeDetector
from app.services.agent.gemini_client import GeminiClient
from app.services.agent.prompts import AnalyzerPrompts
from app.services.agent.reasoning_generator import ReasoningGenerator
from app.services.agent.types import DataType, ProblemAnalysis, ProblemType

logger = logging.getLogger(__name__)


class ProblemAnalyzer:
    """
    Analyzes ML problems using Gemini to understand:
    - Problem type (classification, regression, detection, etc.)
    - Data type (image, text, tabular, multimodal)
    - Domain (medical, business, agriculture, etc.)
    - Success criteria and metrics
    """
    
    # Default temperature for analysis (lower for more consistent results)
    ANALYSIS_TEMPERATURE = 0.3

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize Problem Analyzer.

        Args:
            gemini_client: Optional GeminiClient instance (creates new one if not provided)
        """
        self.gemini_client = gemini_client or GeminiClient(
            temperature=self.ANALYSIS_TEMPERATURE
        )
        self.data_type_detector = DataTypeDetector(self.gemini_client)
        self.confidence_scorer = ConfidenceScorer()
        self.reasoning_generator = ReasoningGenerator()
        logger.info("Initialized ProblemAnalyzer")

    async def analyze_problem(
        self,
        problem_description: str,
        data_sample: Any,
        num_samples: int,
        is_labeled: bool,
        data_type_hint: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
    ) -> ProblemAnalysis:
        """
        Perform comprehensive problem analysis.

        Args:
            problem_description: User's description of the problem
            data_sample: Sample of the dataset for analysis
            num_samples: Total number of samples in dataset
            is_labeled: Whether the data has labels
            data_type_hint: Optional hint about data type
            file_extensions: List of file extensions in dataset

        Returns:
            ProblemAnalysis object with complete analysis

        Raises:
            GeminiClientError: If analysis fails
        """
        logger.info("Starting comprehensive problem analysis")

        # Detect data type if not provided
        if not data_type_hint:
            data_type_hint = await self.data_type_detector.detect_data_type(
                data_sample, file_extensions or []
            )

        # Format data preview for prompt
        data_preview = DataTypeDetector.format_data_preview(
            data_sample, data_type_hint
        )

        # Generate comprehensive analysis using Gemini
        try:
            analysis_result = await self._generate_analysis(
                problem_description=problem_description,
                data_type_hint=data_type_hint,
                num_samples=num_samples,
                is_labeled=is_labeled,
                data_preview=data_preview,
            )

            # Parse and validate the analysis
            analysis = self._parse_analysis_result(analysis_result, is_labeled)

            logger.info(
                f"Analysis complete: {analysis.problem_type.value} / "
                f"{analysis.data_type.value} (confidence: {analysis.confidence:.2f})"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error during problem analysis: {e}", exc_info=True)
            # Return fallback analysis
            return self._create_fallback_analysis(
                problem_description, data_type_hint, is_labeled
            )

    async def _generate_analysis(
        self,
        problem_description: str,
        data_type_hint: str,
        num_samples: int,
        is_labeled: bool,
        data_preview: str,
    ) -> Dict[str, Any]:
        """Generate analysis using Gemini."""
        prompt = AnalyzerPrompts.PROBLEM_ANALYSIS.format(
            problem_description=problem_description,
            data_type_hint=data_type_hint,
            num_samples=num_samples,
            is_labeled=is_labeled,
            data_preview=data_preview,
        )

        return await self.gemini_client.generate_structured_response(
            prompt=prompt,
            system_instruction=AnalyzerPrompts.SYSTEM_INSTRUCTION,
            temperature=self.ANALYSIS_TEMPERATURE,
        )

    def _parse_analysis_result(
        self, result: Dict[str, Any], is_labeled: bool
    ) -> ProblemAnalysis:
        """
        Parse Gemini response into ProblemAnalysis object.
        
        Enhances the raw Gemini response with additional confidence scoring
        and reasoning validation.
        """
        # Extract base confidence from Gemini
        gemini_confidence = float(result.get("confidence", 0.5))
        
        # Calculate adjusted confidence based on multiple factors
        adjusted_confidence = self.confidence_scorer.calculate_confidence_score(
            result, is_labeled
        )
        
        # Generate enhanced reasoning
        enhanced_reasoning = self.reasoning_generator.generate_enhanced_reasoning(
            result, gemini_confidence, adjusted_confidence
        )
        
        return ProblemAnalysis(
            problem_type=ProblemType(result.get("problem_type", "unknown")),
            data_type=DataType(result.get("data_type", "unknown")),
            domain=result.get("domain", "General"),
            suggested_metrics=result.get("suggested_metrics", []),
            complexity_score=float(result.get("complexity_score", 0.5)),
            reasoning=enhanced_reasoning,
            confidence=adjusted_confidence,
            is_labeled=result.get("is_labeled", is_labeled),
            num_classes=result.get("num_classes"),
            target_variable=result.get("target_variable"),
            additional_insights=result.get("additional_insights", {}),
        )



    async def identify_domain(
        self, problem_description: str, data_type: str, problem_type: str
    ) -> Dict[str, Any]:
        """
        Identify the domain of the ML problem.

        Args:
            problem_description: Description of the problem
            data_type: Type of data
            problem_type: Type of ML problem

        Returns:
            Dictionary with domain, confidence, and reasoning
        """
        logger.debug("Identifying problem domain")

        try:
            prompt = AnalyzerPrompts.DOMAIN_IDENTIFICATION.format(
                problem_description=problem_description,
                data_type=data_type,
                problem_type=problem_type,
            )

            response = await self.gemini_client.generate_structured_response(
                prompt=prompt, temperature=0.2
            )

            return {
                "domain": response.get("domain", "General"),
                "confidence": response.get("confidence", 0.5),
                "reasoning": response.get("reasoning", ""),
            }

        except Exception as e:
            logger.warning(f"Error identifying domain: {e}")
            return {
                "domain": "General",
                "confidence": 0.3,
                "reasoning": "Could not determine specific domain",
            }

    async def classify_problem_type(
        self, problem_description: str, data_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify the type of ML problem.

        Args:
            problem_description: Description of the problem
            data_characteristics: Dictionary with data characteristics

        Returns:
            Dictionary with problem_type, confidence, and reasoning
        """
        try:
            prompt = AnalyzerPrompts.PROBLEM_TYPE_CLASSIFICATION.format(
                problem_description=problem_description,
                data_characteristics=self._format_dict(data_characteristics),
            )

            response = await self.gemini_client.generate_structured_response(
                prompt=prompt, temperature=0.2
            )

            return response

        except Exception as e:
            logger.error(f"Error classifying problem type: {e}")
            return {
                "problem_type": "unknown",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
            }

    def _create_fallback_analysis(
        self, problem_description: str, data_type_hint: str, is_labeled: bool
    ) -> ProblemAnalysis:
        """
        Create a basic fallback analysis when Gemini analysis fails.

        Uses simple heuristics based on keywords in the problem description.

        Args:
            problem_description: Problem description
            data_type_hint: Hint about data type
            is_labeled: Whether data is labeled

        Returns:
            Basic ProblemAnalysis object
        """
        logger.warning("Creating fallback analysis using heuristics")

        description_lower = problem_description.lower()

        # Simple keyword-based heuristics
        if "classify" in description_lower or "category" in description_lower:
            problem_type = ProblemType.CLASSIFICATION
            metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc", "pr_auc"]
        elif "predict" in description_lower or "forecast" in description_lower:
            problem_type = ProblemType.REGRESSION
            metrics = ["mse", "rmse", "mae", "r2_score"]
        elif "detect" in description_lower and data_type_hint == "image":
            problem_type = ProblemType.OBJECT_DETECTION
            metrics = ["map", "precision", "recall", "roc_auc", "pr_auc"]
        else:
            problem_type = ProblemType.UNKNOWN
            metrics = ["accuracy", "roc_auc", "pr_auc"]

        return ProblemAnalysis(
            problem_type=problem_type,
            data_type=DataType(data_type_hint) if data_type_hint else DataType.UNKNOWN,
            domain="General",
            suggested_metrics=metrics,
            complexity_score=0.5,
            reasoning="Fallback analysis based on keyword heuristics",
            confidence=0.3,
            is_labeled=is_labeled,
        )

    def _format_dict(self, d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for display in prompts."""
        lines = []
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{'  ' * indent}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            else:
                lines.append(f"{'  ' * indent}{key}: {value}")
        return "\n".join(lines)
