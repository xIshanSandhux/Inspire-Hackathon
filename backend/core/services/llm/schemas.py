"""Pydantic schemas for LLM document parsing."""

from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types for identity verification."""

    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    BC_SERVICES = "bc_services"  # BC Services Card (health card)
    HEALTH_CARD = "health_card"
    BIRTH_CERTIFICATE = "birth_certificate"
    SIN_CARD = "sin_card"
    ID_CARD = "id_card"
    UNKNOWN = "unknown"


class ParsedDocument(BaseModel):
    """
    Structured data extracted from an identity document via LLM.
    
    This model is used with instructor to guide LLM extraction.
    """

    first_name: str | None = Field(
        None,
        description="First/given name as it appears on the document",
    )
    last_name: str | None = Field(
        None,
        description="Last/family/surname as it appears on the document",
    )
    unique_id: str | None = Field(
        None,
        description="Primary document identifier (driver's license number, passport number, PHN, SIN, etc.)",
    )
    document_type: DocumentType = Field(
        DocumentType.UNKNOWN,
        description="The type of identity document",
    )
    date_of_birth: str | None = Field(
        None,
        description="Date of birth in ISO format (YYYY-MM-DD) if possible",
    )
    expiry_date: str | None = Field(
        None,
        description="Document expiration date in ISO format (YYYY-MM-DD) if present",
    )
    issue_date: str | None = Field(
        None,
        description="Document issue date in ISO format (YYYY-MM-DD) if present",
    )
    address: str | None = Field(
        None,
        description="Full address as it appears on the document",
    )
    issuing_authority: str | None = Field(
        None,
        description="Authority that issued the document (state, country, agency)",
    )
    additional_metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Any other relevant fields extracted from the document",
    )
    confidence_notes: str | None = Field(
        None,
        description="Notes about extraction confidence or ambiguities",
    )
