"""OpenRouter API client for LLM interactions."""

from typing import Any

import instructor
from openai import OpenAI

from backend.core.util import get_logger

logger = get_logger(__name__)


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
        logger.info(f"[OPENROUTER] Initializing OpenRouterClient")
        logger.info(f"[OPENROUTER] api_key: {api_key[:20]}..." if api_key else "[OPENROUTER] api_key: NOT SET")
        logger.info(f"[OPENROUTER] model: {model}")
        logger.info(f"[OPENROUTER] base_url: {self.OPENROUTER_BASE_URL}")
        
        self.api_key = api_key
        self.model = model
        self.default_headers = default_headers or {}
        self._instructor_client: Any | None = None

    def get_instructor_client(self) -> Any:
        """
        Return an instructor-patched OpenAI client configured for OpenRouter.
        
        The client is lazily initialized and cached.
        """
        logger.info(f"[OPENROUTER] get_instructor_client() called")
        
        if self._instructor_client is None:
            logger.info(f"[OPENROUTER] Creating new instructor client...")
            logger.info(f"[OPENROUTER] Base URL: {self.OPENROUTER_BASE_URL}")
            logger.info(f"[OPENROUTER] API Key: {self.api_key[:20]}...")
            
            base_client = OpenAI(
                base_url=self.OPENROUTER_BASE_URL,
                api_key=self.api_key,
                default_headers=self.default_headers,
            )
            logger.info(f"[OPENROUTER] Base OpenAI client created")
            
            self._instructor_client = instructor.from_openai(base_client)
            logger.info(f"[OPENROUTER] Instructor client created successfully")
        else:
            logger.info(f"[OPENROUTER] Returning cached instructor client")

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
