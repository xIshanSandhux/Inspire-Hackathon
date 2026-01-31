"""Pydantic schemas for document endpoints."""

from typing import Any

from pydantic import BaseModel, Field


class AddDocumentResponse(BaseModel):
    """Response schema for document addition."""

    fingerprint_hash: str
    document_type: str
    id: str
    metadata: dict[str, Any]
    confidence: float = Field(description="Confidence score of document extraction")
