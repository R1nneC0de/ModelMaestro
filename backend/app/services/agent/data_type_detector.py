"""
Data type detection utilities for problem analysis.

This module handles detection of data types (image, text, tabular, etc.)
using both heuristic and AI-based approaches.
"""

import logging
from typing import Any, List, Optional

from app.services.agent.gemini_client import GeminiClient
from app.services.agent.prompts import AnalyzerPrompts

logger = logging.getLogger(__name__)


class DataTypeDetector:
    """Detects data types from samples and file extensions."""

    # File extension mappings for quick data type detection
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}
    TEXT_EXTENSIONS = {".txt", ".json", ".csv", ".tsv"}

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        """
        Initialize Data Type Detector.

        Args:
            gemini_client: Optional GeminiClient instance for AI-based detection
        """
        self.gemini_client = gemini_client

    async def detect_data_type(
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
        heuristic_type = self._heuristic_detection(file_extensions)
        if heuristic_type != "unknown":
            logger.debug(f"Detected data type via heuristics: {heuristic_type}")
            return heuristic_type

        # Use Gemini for more complex detection if available
        if self.gemini_client:
            return await self._gemini_detection(data_sample, file_extensions)
        
        return "unknown"

    def _heuristic_detection(self, file_extensions: List[str]) -> str:
        """
        Quick heuristic-based data type detection.
        
        Args:
            file_extensions: List of file extensions
            
        Returns:
            Detected data type or "unknown"
        """
        if any(ext.lower() in self.IMAGE_EXTENSIONS for ext in file_extensions):
            return "image"

        if ".csv" in file_extensions or ".tsv" in file_extensions:
            return "tabular"

        if ".txt" in file_extensions:
            return "text"

        return "unknown"

    async def _gemini_detection(
        self, data_sample: Any, file_extensions: List[str]
    ) -> str:
        """
        Use Gemini for complex data type detection.
        
        Args:
            data_sample: Sample of the data
            file_extensions: List of file extensions
            
        Returns:
            Detected data type or "unknown"
        """
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

    @staticmethod
    def format_data_preview(data_sample: Any, data_type: str) -> str:
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
