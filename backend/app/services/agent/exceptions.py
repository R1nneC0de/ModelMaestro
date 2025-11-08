"""
Custom exceptions for Gemini client operations.

This module defines a hierarchy of exceptions for better error handling
and more specific error reporting in the Gemini client.
"""

from typing import Optional


class GeminiClientError(Exception):
    """Base exception for all Gemini client errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            original_error: Optional original exception that caused this error
        """
        super().__init__(message)
        self.original_error = original_error
        self.message = message


class GeminiRateLimitError(GeminiClientError):
    """Raised when API rate limit is exceeded."""

    pass


class GeminiAPIError(GeminiClientError):
    """Raised when API returns an error response."""

    pass


class GeminiValidationError(GeminiClientError):
    """Raised when response validation fails."""

    pass


class GeminiTimeoutError(GeminiClientError):
    """Raised when API request times out."""

    pass
