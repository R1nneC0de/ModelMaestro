"""
Response parsing utilities for Gemini API responses.

This module handles parsing and extracting structured data from
Gemini API text responses, particularly JSON extraction.
"""

import json
import logging
import re
from typing import Any, Dict

from .exceptions import GeminiValidationError

logger = logging.getLogger(__name__)


class ResponseParser:
    """Utility class for parsing Gemini API responses."""

    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from text response.

        Handles various formats:
        - JSON in code blocks (```json ... ```)
        - Plain JSON objects
        - JSON with surrounding text

        Args:
            text: Response text potentially containing JSON

        Returns:
            Parsed JSON dictionary

        Raises:
            GeminiValidationError: If JSON cannot be parsed
        """
        try:
            # Try to find JSON in code blocks first
            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    json_text = json_match.group(0)
                else:
                    # Assume entire text is JSON
                    json_text = text

            # Parse JSON
            return json.loads(json_text.strip())

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse JSON: {e}",
                extra={"text_preview": text[:500]},
            )
            raise GeminiValidationError(f"Failed to parse JSON: {e}", e) from e

    @staticmethod
    def create_json_prompt(prompt: str) -> str:
        """
        Enhance prompt to request JSON format.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt with JSON instructions
        """
        return f"""{prompt}

IMPORTANT: Respond with valid JSON only. Do not include any text before or after the JSON object.
Format your response as a JSON object enclosed in curly braces."""

    @staticmethod
    def create_json_system_instruction(system_instruction: str | None) -> str:
        """
        Create system instruction that emphasizes JSON output.

        Args:
            system_instruction: Optional base system instruction

        Returns:
            Enhanced system instruction
        """
        json_instruction = (
            "You are a precise AI assistant that responds with valid JSON only. "
            "Always format your responses as valid JSON objects."
        )

        if system_instruction:
            return f"{system_instruction}\n\n{json_instruction}"
        return json_instruction


# Convenience function for backward compatibility
def parse_json_response(text: str) -> Dict[str, Any]:
    """
    Parse JSON from a text response.

    Convenience wrapper around ResponseParser.extract_json for easier imports.

    Args:
        text: Response text potentially containing JSON

    Returns:
        Parsed JSON dictionary

    Raises:
        GeminiValidationError: If JSON cannot be parsed
    """
    return ResponseParser.extract_json(text)
