"""FastAPI dependencies for LLM services."""

from typing import Annotated

from fastapi import Depends

from backend.core.config import settings
from backend.core.services.llm.client import OpenRouterClient
from backend.core.services.llm.document_parser import DocumentLLMParser


# Singleton instances (lazily initialized)
_openrouter_client: OpenRouterClient | None = None
_document_llm_parser: DocumentLLMParser | None = None


def get_openrouter_client() -> OpenRouterClient | None:
    """
    Get the singleton OpenRouterClient instance.
    
    Returns:
        OpenRouterClient if configured, None otherwise.
    """
    global _openrouter_client

    if not settings.llm_configured:
        return None

    if _openrouter_client is None:
        _openrouter_client = OpenRouterClient(
            api_key=settings.openrouter_api_key,  # type: ignore
            model=settings.llm_model,
        )

    return _openrouter_client


def get_document_llm_parser() -> DocumentLLMParser | None:
    """
    Get the singleton DocumentLLMParser instance.
    
    Returns:
        DocumentLLMParser if OpenRouter is configured, None otherwise.
    """
    global _document_llm_parser

    client = get_openrouter_client()
    if client is None:
        return None

    if _document_llm_parser is None:
        _document_llm_parser = DocumentLLMParser(client)

    return _document_llm_parser


# Type aliases for dependency injection
OpenRouterClientDep = Annotated[OpenRouterClient | None, Depends(get_openrouter_client)]
DocumentLLMParserDep = Annotated[DocumentLLMParser | None, Depends(get_document_llm_parser)]
