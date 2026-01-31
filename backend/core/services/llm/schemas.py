"""Pydantic schemas for LLM document parsing."""

from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Supported document types for identity verification."""

    DRIVERS_LICENSE = "drivers_license"
    PASSPORT = "passport"
    BC_SERVICES = "bc_services"  # BC Services Card (health card)
    BCID = "bcid"  # BC ID Card (ID format: BCID: <string>)
    HEALTH_CARD = "health_card"
    BIRTH_CERTIFICATE = "birth_certificate"
    SIN_CARD = "sin_card"
    ID_CARD = "id_card"
    UNKNOWN = "unknown"


class ParsedDocument(BaseModel):
    """
    Structured data extracted from an identity document via LLM.
    
    This model is used with instructor to guide LLM extraction.
    The unique_id field is THE MOST CRITICAL field - it must be extracted.
    """

    unique_id: str | None = Field(
        None,
        description=(
            "CRITICAL - MUST EXTRACT: The primary document identifier. This is the MOST IMPORTANT field. "
            "For driver's license: the license number (7-9 digits) found near 'DL', 'NDL', 'LDL' labels. "
            "Example: if you see 'NDL:01944956', extract '01944956'. "
            "For BC Services Card: the 10-digit PHN found near 'Personal Health Number'. "
            "Example: if you see '9012 345 678', extract '9012345678' (no spaces). "
            "For BCID (BC ID Card): the string after 'BCID:' on the card. "
            "Example: if you see 'BCID: ABC123456', extract 'ABC123456' (the value only, not the 'BCID:' prefix). "
            "For passport: the passport number (8-9 alphanumeric chars) found near 'Passport No' or in MRZ. "
            "IMPORTANT: Extract ONLY the number/code/string, NOT the label."
        ),
    )
    document_type: DocumentType = Field(
        DocumentType.UNKNOWN,
        description=(
            "The type of identity document: 'drivers_license' for driver's license, "
            "'bc_services' for BC Services Card/PHN card, 'bcid' for BC ID Card, "
            "'passport' for passports, 'health_card' for other health cards, 'id_card' for generic IDs."
        ),
    )
    first_name: str | None = Field(
        None,
        description="The person's first/given name exactly as shown on the document (e.g., 'ROBERT', 'JOHN').",
    )
    last_name: str | None = Field(
        None,
        description="The person's last/family/surname exactly as shown on the document (e.g., 'THOMLINSON', 'SMITH').",
    )
    date_of_birth: str | None = Field(
        None,
        description=(
            "Date of birth converted to ISO format YYYY-MM-DD. "
            "If document shows '2003-Aug-15' or 'Aug 15, 2003' or '15/08/2003', convert to '2003-08-15'."
        ),
    )
    expiry_date: str | None = Field(
        None,
        description=(
            "Document expiration date in ISO format YYYY-MM-DD. "
            "Look for 'Expires', 'Expiry', 'EXP' labels. Convert to YYYY-MM-DD format."
        ),
    )
    issue_date: str | None = Field(
        None,
        description=(
            "Document issue date in ISO format YYYY-MM-DD. "
            "Look for 'Issued', 'Issue Date', 'ISS' labels. Convert to YYYY-MM-DD format."
        ),
    )
    address: str | None = Field(
        None,
        description="Full mailing address as shown on the document, including street, city, province/state, postal code.",
    )
    issuing_authority: str | None = Field(
        None,
        description="The authority that issued the document (e.g., 'British Columbia', 'Canada', 'California DMV').",
    )
    sex: str | None = Field(
        None,
        description="Sex/gender as shown on document ('M', 'F', or 'X').",
    )
    additional_metadata: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Any other relevant fields from the document as key-value pairs. "
            "Include: license class, restrictions, height, weight, eye color, hair color, etc."
        ),
    )
    confidence_notes: str | None = Field(
        None,
        description="Brief notes about extraction quality or any fields that were unclear or ambiguous.",
    )
