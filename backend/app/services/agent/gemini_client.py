"""
Gemini API client for interacting with Google's Gemini models.

This module provides a production-grade client for Google's Gemini API with:
- Comprehensive error handling and retry logic
- Structured response parsing with validation
- Async/await support for non-blocking I/O
- Detailed logging and observability
- Type safety with full type hints

Example:
    >>> client = GeminiClient()
    >>> response = await client.generate_text("Analyze this problem...")
    >>> structured = await client.generate_structured_response(prompt)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.core.config import settings
from backend.app.services.agent.exceptions import (
    GeminiAPIError,
    GeminiClientError,
    GeminiRateLimitError,
    GeminiTimeoutError,
    GeminiValidationError,
)
from backend.app.services.agent.response_parser import ResponseParser

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Production-grade client for Google Gemini API.

    This client provides robust interaction with Gemini models including:
    - Automatic retry with exponential backoff
    - Comprehensive error handling
    - Structured response parsing
    - Request/response logging

    Attributes:
        api_key: Gemini API key for authentication
        model_name: Name of the Gemini model to use
        temperature: Sampling temperature (0.0 to 1.0)
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
    """

    # Default configuration constants
    DEFAULT_MODEL = "gemini-1.5-pro"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 60
    MAX_OUTPUT_TOKENS = 8192

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize Gemini client with configuration.

        Args:
            api_key: Gemini API key (defaults to settings.GEMINI_API_KEY)
            model_name: Name of the Gemini model to use
            temperature: Sampling temperature (0.0 to 1.0)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds

        Raises:
            ValueError: If temperature is not between 0.0 and 1.0
            GeminiClientError: If API key is missing or invalid
        """
        self._validate_temperature(temperature)

        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise GeminiClientError("Gemini API key is required")

        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout

        self._configure_api()
        self._model = self._create_model()

        logger.info(
            "Initialized GeminiClient",
            extra={
                "model": self.model_name,
                "temperature": self.temperature,
                "max_retries": self.max_retries,
            },
        )

    def _validate_temperature(self, temperature: float) -> None:
        """Validate temperature is within valid range."""
        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {temperature}")

    def _configure_api(self) -> None:
        """Configure the Gemini API with credentials."""
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise GeminiClientError("Failed to configure Gemini API", e) from e

    def _create_model(
        self,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> genai.GenerativeModel:
        """
        Create a GenerativeModel instance with specified configuration.

        Args:
            system_instruction: Optional system instruction for the model
            temperature: Optional temperature override

        Returns:
            Configured GenerativeModel instance
        """
        generation_config = {
            "temperature": temperature if temperature is not None else self.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": self.MAX_OUTPUT_TOKENS,
        }

        model_kwargs = {
            "model_name": self.model_name,
            "generation_config": generation_config,
        }

        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        return genai.GenerativeModel(**model_kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (GeminiRateLimitError, google_exceptions.ResourceExhausted)
        ),
        reraise=True,
    )
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text response from Gemini model with automatic retry.

        Args:
            prompt: The input prompt text
            system_instruction: Optional system instruction to guide the model
            temperature: Optional temperature override for this request
            **kwargs: Additional generation parameters

        Returns:
            Generated text response

        Raises:
            GeminiRateLimitError: When rate limit is exceeded after retries
            GeminiAPIError: When API returns an error
            GeminiTimeoutError: When request times out
            GeminiClientError: For other client errors
        """
        if not prompt or not prompt.strip():
            raise GeminiValidationError("Prompt cannot be empty")

        logger.debug(
            "Generating text",
            extra={
                "prompt_length": len(prompt),
                "has_system_instruction": system_instruction is not None,
            },
        )

        try:
            model = self._create_model(
                system_instruction=system_instruction,
                temperature=temperature,
            )

            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=self.timeout,
            )

            if not response or not response.text:
                raise GeminiAPIError("Empty response from Gemini API")

            logger.debug(
                "Generated text successfully",
                extra={"response_length": len(response.text)},
            )

            return response.text

        except asyncio.TimeoutError as e:
            logger.error(f"Request timed out after {self.timeout}s")
            raise GeminiTimeoutError(
                f"Request timed out after {self.timeout}s", e
            ) from e

        except google_exceptions.ResourceExhausted as e:
            logger.warning(f"Rate limit exceeded: {e}")
            raise GeminiRateLimitError(f"Rate limit exceeded: {e}", e) from e

        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"API error: {e}", e) from e

        except Exception as e:
            logger.error(f"Unexpected error in generate_text: {e}", exc_info=True)
            raise GeminiClientError(f"Unexpected error: {e}", e) from e

    async def generate_structured_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate structured response (JSON) from Gemini model.

        Args:
            prompt: The input prompt text
            system_instruction: Optional system instruction
            temperature: Optional temperature override
            **kwargs: Additional generation parameters

        Returns:
            Parsed JSON response as dictionary

        Raises:
            GeminiValidationError: When response cannot be parsed as JSON
        """
        json_prompt = ResponseParser.create_json_prompt(prompt)
        json_system_instruction = ResponseParser.create_json_system_instruction(
            system_instruction
        )

        response_text = await self.generate_text(
            json_prompt,
            system_instruction=json_system_instruction,
            temperature=temperature or 0.3,
            **kwargs,
        )

        parsed_json = ResponseParser.extract_json(response_text)

        logger.debug(
            "Parsed structured response",
            extra={"keys": list(parsed_json.keys())},
        )

        return parsed_json

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """
        Have a multi-turn conversation with Gemini.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system_instruction: Optional system instruction
            temperature: Optional temperature override
            **kwargs: Additional generation parameters

        Returns:
            Generated response text

        Raises:
            GeminiValidationError: If messages format is invalid
            GeminiClientError: For other errors
        """
        self._validate_messages(messages)

        logger.debug("Starting chat", extra={"num_messages": len(messages)})

        try:
            model = self._create_model(
                system_instruction=system_instruction,
                temperature=temperature,
            )

            chat = model.start_chat(history=[])

            # Send all messages except the last one
            for message in messages[:-1]:
                if message["role"] == "user":
                    await asyncio.to_thread(chat.send_message, message["content"])

            # Send final message and get response
            response = await asyncio.to_thread(
                chat.send_message, messages[-1]["content"]
            )

            return response.text

        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            raise GeminiClientError(f"Chat error: {e}", e) from e

    def _validate_messages(self, messages: List[Dict[str, str]]) -> None:
        """Validate chat messages format."""
        if not messages:
            raise GeminiValidationError("Messages list cannot be empty")

        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise GeminiValidationError(
                    "Each message must have 'role' and 'content' keys"
                )

    def update_temperature(self, temperature: float) -> None:
        """
        Update the temperature setting for generation.

        Args:
            temperature: New temperature value (0.0 to 1.0)

        Raises:
            ValueError: If temperature is not between 0.0 and 1.0
        """
        self._validate_temperature(temperature)
        self.temperature = temperature
        self._model = self._create_model()
        logger.info(f"Updated temperature to {temperature}")

    @asynccontextmanager
    async def with_temperature(
        self, temperature: float
    ) -> AsyncGenerator["GeminiClient", None]:
        """
        Context manager for temporarily changing temperature.

        Example:
            >>> async with client.with_temperature(0.2) as temp_client:
            ...     response = await temp_client.generate_text(prompt)

        Args:
            temperature: Temporary temperature value

        Yields:
            GeminiClient instance with modified temperature
        """
        original_temp = self.temperature
        try:
            self.update_temperature(temperature)
            yield self
        finally:
            self.update_temperature(original_temp)

    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"GeminiClient(model={self.model_name}, "
            f"temperature={self.temperature}, "
            f"max_retries={self.max_retries})"
        )
