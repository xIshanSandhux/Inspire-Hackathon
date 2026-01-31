"""LLM-based document parsing service."""

import base64

from backend.core.services.llm.client import OpenRouterClient
from backend.core.services.llm.schemas import ParsedDocument
from backend.core.util import get_logger

logger = get_logger(__name__)


# Base prompt template - used for unknown/generic documents
BASE_EXTRACTION_PROMPT = """You are an expert document analyst specializing in identity document data extraction.

Your task is to extract structured information from this identity document image.

CRITICAL REQUIREMENTS:
1. The 'unique_id' field is MANDATORY - you MUST find and extract the document's primary identifier number
2. Look carefully for any ID numbers, license numbers, card numbers, or reference codes
3. Extract names EXACTLY as they appear (preserve capitalization)
4. Convert ALL dates to ISO format: YYYY-MM-DD

EXTRACTION PRIORITY:
1. unique_id - The document's main identifier (license number, passport number, card number, etc.)
2. Names (first_name, last_name)
3. Dates (date_of_birth, expiry_date, issue_date)
4. Other fields (address, issuing_authority, etc.)

If you cannot find a clear document ID, look for ANY prominent number that could serve as an identifier."""


# Tailored prompt for Driver's License
DRIVERS_LICENSE_PROMPT = """You are an expert at extracting data from driver's licenses. Your extraction must be precise and complete.

TASK: Extract all information from this driver's license image.

## CRITICAL: Finding the License Number (unique_id)

The license number is the MOST IMPORTANT field. Search carefully for it:

COMMON LABELS (the number appears RIGHT AFTER these):
- "NDL:" followed by digits → e.g., "NDL:01944956" means unique_id = "01944956"
- "LDL:" followed by digits → e.g., "LDL:12345678" means unique_id = "12345678"  
- "DL:" or "DL " followed by digits → e.g., "DL: 1234567" means unique_id = "1234567"
- "DLN:" followed by digits
- "LICENCE NO" or "LICENSE NO" followed by digits

FORMAT: Usually 7-9 digits. Examples: "01944956", "1234567", "123456789"

IMPORTANT: Extract ONLY the number, not the label. If you see "NDL:01944956", return "01944956".

## Other Required Fields

| Field | What to Look For | Format |
|-------|------------------|--------|
| first_name | Given name, usually after last name | Exactly as shown (e.g., "ROBERT") |
| last_name | Family/surname, often first name shown | Exactly as shown (e.g., "THOMLINSON") |
| date_of_birth | "DOB", "Birth", "BD" + date | Convert to YYYY-MM-DD |
| expiry_date | "Expires", "Exp" + date | Convert to YYYY-MM-DD |
| issue_date | "Issued", "Iss" + date | Convert to YYYY-MM-DD |
| address | Street, city, province, postal code | Full address string |
| issuing_authority | Province/State name | e.g., "British Columbia" |
| sex | "Sex", "M/F" | "M", "F", or "X" |

## Additional Metadata
In additional_metadata, include: license class, restrictions, height, weight, eye color, hair color.

Set document_type to "drivers_license"."""


# Tailored prompt for BC Services Card
BC_SERVICES_PROMPT = """You are an expert at extracting data from BC Services Cards (British Columbia health cards).

TASK: Extract all information from this BC Services Card image.

## CRITICAL: Finding the Personal Health Number (unique_id)

The PHN is the MOST IMPORTANT field. It is a 10-DIGIT number.

WHERE TO FIND IT:
- Look for "PERSONAL HEALTH NUMBER" label
- Look for "PHN" label
- It may be formatted with spaces: "9012 345 678"

FORMAT: Always 10 digits. Examples: "9012345678", "9876543210"

IMPORTANT: Remove any spaces. If you see "9012 345 678", return "9012345678".

## Other Required Fields

| Field | What to Look For | Format |
|-------|------------------|--------|
| first_name | Given name | Exactly as shown |
| last_name | Family/surname | Exactly as shown |
| date_of_birth | "DATE OF BIRTH", "DOB" | Convert to YYYY-MM-DD |
| expiry_date | Card expiry date if shown | Convert to YYYY-MM-DD |
| issuing_authority | Should be "British Columbia" | |

Set document_type to "bc_services"."""


# Tailored prompt for Passport
PASSPORT_PROMPT = """You are an expert at extracting data from passports.

TASK: Extract all information from this passport image.

## CRITICAL: Finding the Passport Number (unique_id)

The passport number is the MOST IMPORTANT field.

WHERE TO FIND IT:
- Near "PASSPORT NO" or "PASSPORT NUMBER" label
- In the MRZ (Machine Readable Zone) - the two lines of text at the bottom
- MRZ Line 1 format: P<COUNTRY_CODE<SURNAME<<GIVEN_NAMES then passport number

FORMAT: Usually 8-9 alphanumeric characters. Examples: "AB1234567", "GA1234567", "123456789"

## Other Required Fields

| Field | What to Look For | Format |
|-------|------------------|--------|
| first_name | Given names | Exactly as shown |
| last_name | Surname | Exactly as shown |
| date_of_birth | "DATE OF BIRTH" | Convert to YYYY-MM-DD |
| expiry_date | "DATE OF EXPIRY" | Convert to YYYY-MM-DD |
| issue_date | "DATE OF ISSUE" | Convert to YYYY-MM-DD |
| issuing_authority | Country name | e.g., "Canada", "United States" |
| sex | Sex/Gender | "M", "F", or "X" |

## Additional Metadata
In additional_metadata, include: nationality, place_of_birth, country_code.

Set document_type to "passport"."""


# Tailored prompt for generic health cards
HEALTH_CARD_PROMPT = """You are an expert at extracting data from health cards.

TASK: Extract all information from this health card image.

## CRITICAL: Finding the Health Number (unique_id)

The health card number is the MOST IMPORTANT field.

WHERE TO FIND IT:
- "HEALTH NUMBER", "HEALTH CARD NUMBER"
- "PHN" (Personal Health Number)
- "OHIP" (Ontario Health Insurance Plan)
- Any prominent 9-12 digit number

FORMAT: Usually 9-12 digits depending on province/state.

## Other Required Fields

| Field | What to Look For | Format |
|-------|------------------|--------|
| first_name | Given name | Exactly as shown |
| last_name | Family/surname | Exactly as shown |
| date_of_birth | DOB, Date of Birth | Convert to YYYY-MM-DD |
| expiry_date | Expiry, Valid Until | Convert to YYYY-MM-DD |
| issuing_authority | Province/State | e.g., "Ontario", "British Columbia" |

Set document_type to "health_card"."""


# Map document types to their tailored prompts
DOCUMENT_TYPE_PROMPTS = {
    "drivers_license": DRIVERS_LICENSE_PROMPT,
    "bc_services": BC_SERVICES_PROMPT,
    "passport": PASSPORT_PROMPT,
    "health_card": HEALTH_CARD_PROMPT,
}


def get_prompt_for_document_type(document_type: str | None) -> str:
    """
    Get the tailored extraction prompt for a document type.
    
    Args:
        document_type: The type of document (e.g., "drivers_license", "bc_services")
        
    Returns:
        Tailored prompt string, or base prompt if type not recognized
    """
    if document_type and document_type.lower() in DOCUMENT_TYPE_PROMPTS:
        return DOCUMENT_TYPE_PROMPTS[document_type.lower()]
    return BASE_EXTRACTION_PROMPT


class DocumentLLMParser:
    """
    Parses raw document text into structured data using LLM.
    
    Uses instructor for type-safe structured extraction with pydantic models.
    """

    def __init__(self, client: OpenRouterClient):
        """
        Initialize document parser.
        
        Args:
            client: Configured OpenRouterClient instance.
        """
        self.client = client

    def parse(
        self, raw_text: str, filename: str | None = None, document_type: str | None = None
    ) -> ParsedDocument:
        """
        Extract structured document data from raw text using LLM.
        
        Args:
            raw_text: The raw text extracted from the document image.
            filename: Optional filename for context (may hint at document type).
            document_type: Optional document type for tailored extraction.
            
        Returns:
            ParsedDocument with extracted structured data.
        """
        logger.info(f"[LLM_PARSER] ========== parse() CALLED ==========")
        logger.info(f"[LLM_PARSER] raw_text length: {len(raw_text)}")
        logger.info(f"[LLM_PARSER] raw_text preview: {raw_text[:200]}...")
        logger.info(f"[LLM_PARSER] filename: {filename}")
        logger.info(f"[LLM_PARSER] document_type: {document_type}")
        logger.info(f"[LLM_PARSER] model: {self.client.model}")
        
        instructor_client = self.client.get_instructor_client()
        prompt = get_prompt_for_document_type(document_type)
        logger.info(f"[LLM_PARSER] Using prompt for type: {document_type or 'base'}")
        logger.debug(f"[LLM_PARSER] Prompt preview: {prompt[:300]}...")

        # Build user message with context
        user_content = f"Document text:\n{raw_text}"
        if filename:
            user_content = f"Filename: {filename}\n\n{user_content}"
        
        logger.info(f"[LLM_PARSER] User content preview: {user_content[:200]}...")
        logger.info(f"[LLM_PARSER] Making API call to OpenRouter...")

        try:
            result = instructor_client.chat.completions.create(
                model=self.client.model,
                response_model=ParsedDocument,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content},
                ],
            )
            logger.info(f"[LLM_PARSER] API call SUCCESS!")
            logger.info(f"[LLM_PARSER] Result: unique_id={result.unique_id}, document_type={result.document_type}")
            logger.info(f"[LLM_PARSER] Result: first_name={result.first_name}, last_name={result.last_name}")
            return result
        except Exception as e:
            logger.error(f"[LLM_PARSER] API call FAILED: {type(e).__name__}: {e}")
            raise

    async def parse_async(
        self, raw_text: str, filename: str | None = None, document_type: str | None = None
    ) -> ParsedDocument:
        """
        Async version of parse for use in async contexts.
        
        Args:
            raw_text: The raw text extracted from the document image.
            filename: Optional filename for context.
            document_type: Optional document type for tailored extraction.
            
        Returns:
            ParsedDocument with extracted structured data.
        """
        import asyncio
        
        logger.info(f"[LLM_PARSER] parse_async() called - delegating to parse()")

        return await asyncio.to_thread(self.parse, raw_text, filename, document_type)

    def parse_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        filename: str | None = None,
        document_type: str | None = None,
    ) -> ParsedDocument:
        """
        Extract structured document data directly from an image using vision LLM.
        
        This method sends the image directly to a vision-capable LLM (like Claude)
        instead of relying on OCR text extraction.
        
        Args:
            image_bytes: Raw image data.
            mime_type: MIME type of the image (e.g., "image/jpeg", "image/png").
            filename: Optional filename for context.
            document_type: Optional document type for tailored extraction prompt.
            
        Returns:
            ParsedDocument with extracted structured data.
        """
        logger.info(f"[LLM_PARSER] parse_image called - size: {len(image_bytes)} bytes, mime_type: {mime_type}, filename: {filename}, document_type: {document_type}")
        logger.info(f"[LLM_PARSER] Using model: {self.client.model}")
        
        # Get tailored prompt for document type
        prompt = get_prompt_for_document_type(document_type)
        logger.info(f"[LLM_PARSER] Using {'tailored' if document_type else 'base'} prompt for document_type: {document_type or 'unknown'}")
        logger.debug(f"[LLM_PARSER] Prompt: {prompt[:200]}...")
        
        instructor_client = self.client.get_instructor_client()

        # Encode image as base64 for the API
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        logger.debug(f"[LLM_PARSER] Image encoded to base64 - length: {len(image_b64)}")

        # Build user message with image and document type hint
        doc_type_label = document_type.replace('_', ' ').title() if document_type else "identity document"
        
        user_text = f"""Analyze this {doc_type_label} image and extract all the information.

IMPORTANT: You MUST find and extract the unique_id (document number). This is critical.
- Look carefully for any ID numbers, license numbers, or card numbers
- The unique_id is usually near labels like "DL", "NDL", "LDL", "PHN", "Passport No", etc.
- Extract ONLY the number itself, not the label

Return the extracted data in the structured format requested."""
        
        if filename:
            user_text += f"\n\nFilename hint: {filename}"
            
        user_content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_b64}",
                },
            },
            {
                "type": "text",
                "text": user_text,
            },
        ]

        logger.info(f"[LLM_PARSER] Sending request to LLM with user text: {user_text}")
        result = instructor_client.chat.completions.create(
            model=self.client.model,
            response_model=ParsedDocument,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
            ],
        )
        
        logger.info(f"[LLM_PARSER] LLM response received:")
        logger.info(f"  - document_type: {result.document_type}")
        logger.info(f"  - unique_id: {result.unique_id}")
        logger.info(f"  - first_name: {result.first_name}")
        logger.info(f"  - last_name: {result.last_name}")
        logger.info(f"  - date_of_birth: {result.date_of_birth}")
        logger.info(f"  - confidence_notes: {result.confidence_notes}")
        logger.debug(f"  - additional_metadata: {result.additional_metadata}")
        
        return result

    async def parse_image_async(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        filename: str | None = None,
        document_type: str | None = None,
    ) -> ParsedDocument:
        """
        Async version of parse_image for use in async contexts.
        
        Args:
            image_bytes: Raw image data.
            mime_type: MIME type of the image.
            filename: Optional filename for context.
            document_type: Optional document type for tailored extraction prompt.
            
        Returns:
            ParsedDocument with extracted structured data.
        """
        import asyncio

        return await asyncio.to_thread(self.parse_image, image_bytes, mime_type, filename, document_type)
