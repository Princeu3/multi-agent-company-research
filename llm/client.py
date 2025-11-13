"""
LLM Client Wrapper

This module provides a clean interface for making LLM (Language Model) calls.
Instead of repeating OpenAI setup code everywhere, we centralize it here.

Student Guide:
--------------
Why a wrapper?
- Single place to configure API settings
- Easy to swap LLM providers (OpenAI → Anthropic → etc)
- Consistent error handling
- Easier to add logging, retries, rate limiting

Usage:
    from llm.client import LLMClient

    client = LLMClient()
    response = client.complete(prompt, temperature=0.2)
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Wrapper for OpenAI API calls with consistent configuration.

    This class handles:
    - API client initialization
    - Common parameters (temperature, max_tokens)
    - Error handling
    - Response parsing

    Example usage:
        client = LLMClient()

        # Simple completion
        response = client.complete("What is sustainability?")

        # With custom settings
        response = client.complete(
            prompt="Extract metrics...",
            temperature=0.1,
            max_tokens=2000
        )

        # JSON mode
        response = client.complete_json(
            system_message="You are a JSON extractor",
            user_message=prompt
        )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env variable

        Raises:
            ValueError: If API key is not found
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables")

        # Create OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Default model (fast and cost-effective)
        self.default_model = "gpt-4o-mini"

        logger.info("LLM Client initialized successfully")

    def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        model: Optional[str] = None
    ) -> str:
        """
        Get a text completion from the LLM.

        Args:
            prompt: The prompt/question to send to the LLM
            system_message: Optional system message to set AI behavior
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response length
            model: Model to use (defaults to gpt-4o-mini)

        Returns:
            The LLM's response as a string

        Example:
            response = client.complete(
                prompt="What is ESG?",
                system_message="You are a sustainability expert",
                temperature=0.1
            )
            print(response)  # "ESG stands for Environmental, Social, and Governance..."
        """
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract and return the response text
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM completion error: {str(e)}")
            raise

    def complete_json(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        model: Optional[str] = None
    ) -> str:
        """
        Get a JSON completion from the LLM.

        Same as complete() but forces JSON output format.
        Useful for structured data extraction.

        Args:
            prompt: The prompt/question to send to the LLM
            system_message: Optional system message
            temperature: Randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response length
            model: Model to use (defaults to gpt-4o-mini)

        Returns:
            The LLM's response as a JSON string

        Example:
            response = client.complete_json(
                prompt="Extract metrics from: ...",
                system_message="You are a JSON extractor"
            )
            data = json.loads(response)  # Parse the JSON
        """
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            # Call OpenAI API with JSON mode
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Extract and return the JSON response
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM JSON completion error: {str(e)}")
            raise


# Singleton instance for easy importing
_client_instance = None


def get_llm_client() -> LLMClient:
    """
    Get a singleton LLM client instance.

    This ensures we only create one client instance throughout the app,
    which is more efficient.

    Returns:
        LLMClient instance

    Example:
        from llm.client import get_llm_client

        client = get_llm_client()
        response = client.complete("Hello!")
    """
    global _client_instance

    if _client_instance is None:
        _client_instance = LLMClient()

    return _client_instance
