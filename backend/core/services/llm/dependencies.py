"""FastAPI dependencies for LLM services."""

from typing import Annotated

from fastapi import Depends

from backend.core.config import settings
from backend.core.services.llm.client import OpenRouterClient
from backend.core.services.llm.document_parser import DocumentLLMParser
from backend.core.util import get_logger

logger = get_logger(__name__)

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

    logger.info(f"[LLM_DEP] get_openrouter_client called")
    logger.info(f"[LLM_DEP] settings.llm_configured: {settings.llm_configured}")
    logger.info(f"[LLM_DEP] settings.openrouter_api_key: {'set (' + settings.openrouter_api_key[:20] + '...)' if settings.openrouter_api_key else 'NOT SET'}")
    logger.info(f"[LLM_DEP] settings.llm_model: {settings.llm_model}")

    if not settings.llm_configured:
        logger.warning(f"[LLM_DEP] LLM not configured - returning None")
        return None

    if _openrouter_client is None:
        logger.info(f"[LLM_DEP] Creating new OpenRouterClient with model: {settings.llm_model}")
        _openrouter_client = OpenRouterClient(
            api_key=settings.openrouter_api_key,  # type: ignore
            model=settings.llm_model,
        )
        logger.info(f"[LLM_DEP] OpenRouterClient created successfully")
    else:
        logger.info(f"[LLM_DEP] Returning cached OpenRouterClient")

    return _openrouter_client


def get_document_llm_parser() -> DocumentLLMParser | None:
    """
    Get the singleton DocumentLLMParser instance.
    
    Returns:
        DocumentLLMParser if OpenRouter is configured, None otherwise.
    """
    global _document_llm_parser

    logger.info(f"[LLM_DEP] get_document_llm_parser called")

    client = get_openrouter_client()
    if client is None:
        logger.warning(f"[LLM_DEP] OpenRouter client is None - returning None for parser")
        return None

    if _document_llm_parser is None:
        logger.info(f"[LLM_DEP] Creating new DocumentLLMParser")
        _document_llm_parser = DocumentLLMParser(client)
        logger.info(f"[LLM_DEP] DocumentLLMParser created successfully")
    else:
        logger.info(f"[LLM_DEP] Returning cached DocumentLLMParser")

    return _document_llm_parser


# Type aliases for dependency injection
OpenRouterClientDep = Annotated[OpenRouterClient | None, Depends(get_openrouter_client)]
DocumentLLMParserDep = Annotated[DocumentLLMParser | None, Depends(get_document_llm_parser)]
