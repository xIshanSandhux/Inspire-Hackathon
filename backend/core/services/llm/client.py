"""OpenRouter API client for LLM interactions."""

from typing import Any

import instructor
from openai import OpenAI


class OpenRouterClient:
    """
    Thin wrapper around OpenRouter API for instructor compatibility.
    
    OpenRouter provides a unified API for multiple LLM providers,
    using the OpenAI-compatible interface.
    """

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        default_headers: dict[str, str] | None = None,
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (sk-or-v1-xxx).
            model: Model identifier (e.g., "anthropic/claude-3.5-sonnet").
            default_headers: Optional headers (e.g., HTTP-Referer, X-Title).
        """
        self.api_key = api_key
        self.model = model
        self.default_headers = default_headers or {}
        self._instructor_client: Any | None = None

    def get_instructor_client(self) -> Any:
        """
        Return an instructor-patched OpenAI client configured for OpenRouter.
        
        The client is lazily initialized and cached.
        """
        if self._instructor_client is None:
            base_client = OpenAI(
                base_url=self.OPENROUTER_BASE_URL,
                api_key=self.api_key,
                default_headers=self.default_headers,
            )
            self._instructor_client = instructor.from_openai(base_client)

        return self._instructor_client

    def get_raw_client(self) -> OpenAI:
        """
        Return the raw OpenAI client without instructor patching.
        
        Useful for non-structured completions.
        """
        return OpenAI(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=self.api_key,
            default_headers=self.default_headers,
        )
