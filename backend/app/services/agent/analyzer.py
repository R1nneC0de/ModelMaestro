"""
Problem Analyzer component for analyzing ML problems and datasets.

This module uses Gemini to understand problem types, data characteristics,
and domains to guide the ML pipeline. It provides comprehensive analysis
including problem classification, data type detection, and domain identification.
"""

import logging
from typing import Any, Dict, List, Optional

from .gemini_client import GeminiClient
from .prompts import AnalyzerPrompts
from .types import DataType, ProblemAnalysis, ProblemType

logger = logging.getLogger(__name__)


class ProblemAnalyzer:
    """
    Analyzes ML problems using Gemini to understand:
    - Problem type (classification, regression, detection, etc.)
    - Data type (image, text, tabular, multimodal)
    - Domain (medical, business, agriculture, etc.)
    - Success criteria and metrics
    """

    # File extension mappings for quick data type detection
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    TEXT_EXTENSIONS = {".txt", ".json", ".csv", ".tsv"}
    
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
            data_type_hint = await self._detect_data_type(
                data_sample, file_extensions or []
            )

        # Format data preview for prompt
        data_preview = self._format_data_preview(data_sample, data_type_hint)

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
        """Parse Gemini response into ProblemAnalysis object."""
        return ProblemAnalysis(
            problem_type=ProblemType(result.get("problem_type", "unknown")),
            data_type=DataType(result.get("data_type", "unknown")),
            domain=result.get("domain", "General"),
            suggested_metrics=result.get("suggested_metrics", []),
            complexity_score=float(result.get("complexity_score", 0.5)),
            reasoning=result.get("reasoning", ""),
            confidence=float(result.get("confidence", 0.5)),
            is_labeled=result.get("is_labeled", is_labeled),
            num_classes=result.get("num_classes"),
            target_variable=result.get("target_variable"),
            additional_insights=result.get("additional_insights", {}),
        )

    async def _detect_data_type(
        self, data_sample: Any, file_extensions: List[str]
    ) -> str:
        """
        Detect the type of data from sample and file extensions.

        Args:
            data_sample: Sample of the data
            file_extensions: List of file extensions

        Returns:
            Detected data type as string
        """
        logger.debug("Detecting data type from sample and extensions")

        # Quick heuristic checks first
        heuristic_type = self._heuristic_data_type_detection(file_extensions)
        if heuristic_type != "unknown":
            logger.debug(f"Detected data type via heuristics: {heuristic_type}")
            return heuristic_type

        # Use Gemini for more complex detection
        return await self._gemini_data_type_detection(data_sample, file_extensions)

    def _heuristic_data_type_detection(self, file_extensions: List[str]) -> str:
        """Quick heuristic-based data type detection."""
        if any(ext.lower() in self.IMAGE_EXTENSIONS for ext in file_extensions):
            return "image"

        if ".csv" in file_extensions or ".tsv" in file_extensions:
            return "tabular"

        if ".txt" in file_extensions:
            return "text"

        return "unknown"

    async def _gemini_data_type_detection(
        self, data_sample: Any, file_extensions: List[str]
    ) -> str:
        """Use Gemini for complex data type detection."""
        try:
            prompt = AnalyzerPrompts.DATA_TYPE_DETECTION.format(
                data_sample=str(data_sample)[:1000],  # Limit sample size
                file_extensions=", ".join(file_extensions),
                num_files=len(file_extensions),
            )

            response = await self.gemini_client.generate_structured_response(
                prompt=prompt, temperature=0.2
            )

            detected_type = response.get("data_type", "unknown")
            logger.debug(f"Gemini detected data type: {detected_type}")
            return detected_type

        except Exception as e:
            logger.warning(f"Error detecting data type with Gemini: {e}")
            return "unknown"

    def _format_data_preview(self, data_sample: Any, data_type: str) -> str:
        """
        Format data sample for display in prompts.

        Args:
            data_sample: Sample data
            data_type: Type of data

        Returns:
            Formatted string representation
        """
        if data_type == "image":
            return "Image data (visual inspection not available in preview)"

        if isinstance(data_sample, dict):
            preview_items = list(data_sample.items())[:5]
            return "\n".join(f"  {k}: {v}" for k, v in preview_items)

        if isinstance(data_sample, list):
            preview_items = data_sample[:5]
            return "\n".join(f"  - {item}" for item in preview_items)

        # Default string representation with truncation
        sample_str = str(data_sample)
        return sample_str[:500] + "..." if len(sample_str) > 500 else sample_str

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
            metrics = ["accuracy", "precision", "recall", "f1_score"]
        elif "predict" in description_lower or "forecast" in description_lower:
            problem_type = ProblemType.REGRESSION
            metrics = ["mse", "rmse", "mae", "r2_score"]
        elif "detect" in description_lower and data_type_hint == "image":
            problem_type = ProblemType.OBJECT_DETECTION
            metrics = ["map", "precision", "recall"]
        else:
            problem_type = ProblemType.UNKNOWN
            metrics = ["accuracy"]

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
