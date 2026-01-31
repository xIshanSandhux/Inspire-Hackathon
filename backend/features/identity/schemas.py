"""Pydantic schemas for identity endpoints."""

from typing import Any

from pydantic import BaseModel, Field


class CreateIdentityRequest(BaseModel):
    """Request schema for creating an identity."""

    fingerprint_hash: str = Field(..., description="The fingerprint hash to register")


class CreateIdentityResponse(BaseModel):
    """Response schema for identity creation."""

    fingerprint_hash: str = Field(..., description="The same fingerprint hash as input")


class DocumentInfo(BaseModel):
    """Document info within retrieve response."""

    id: str
    metadata: dict[str, Any]


class RetrieveRequest(BaseModel):
    """Request schema for retrieving identity and documents."""

    fingerprint_hash: str


class RetrieveResponse(BaseModel):
    """Response schema for identity retrieval with documents."""

    fingerprint_hash: str
    documents: dict[str, DocumentInfo] = Field(
        default_factory=dict,
        description="Documents keyed by document_type"
    )
