"""LLM-based document parsing service."""

import base64

from backend.core.services.llm.client import OpenRouterClient
from backend.core.services.llm.schemas import ParsedDocument
from backend.core.util import get_logger

logger = get_logger(__name__)


# Base prompt template - used for unknown/generic documents
BASE_EXTRACTION_PROMPT = """You are an expert at extracting structured data from identity documents.

Analyze this document image and extract all relevant identity information.

Guidelines:
- Extract names exactly as they appear on the document
- For dates, convert to ISO format (YYYY-MM-DD) when possible
- The unique_id should be the primary identifier on the document
- Include any additional relevant fields in additional_metadata
- Note any ambiguities or low-confidence extractions in confidence_notes
- If a field is not present or cannot be determined, leave it as null"""


# Tailored prompt for Driver's License
DRIVERS_LICENSE_PROMPT = """You are an expert at extracting structured data from driver's licenses.

Analyze this driver's license image and extract the identity information.

CRITICAL - Finding the Driver's License Number (unique_id):
- Look for a 9-DIGIT NUMBER near labels like "DL", "NDL", "LDL", "DLN", "DRIVER LICENSE", or "LIC NO"
- The number format is typically 7-9 digits (e.g., "123456789" or "1234567")
- It may appear after "DL:" or "DL " or on its own line
- This is the MOST IMPORTANT field - search carefully for any 7-9 digit number
- If you see multiple numbers, the one near "DL", "NDL", "LDL" labels is the license number

Other fields to extract:
- first_name: Given name / first name
- last_name: Family name / surname  
- date_of_birth: Look for "DOB", "BIRTH", "BD" - convert to YYYY-MM-DD
- expiry_date: Look for "EXP", "EXPIRY", "EXPIRES" - convert to YYYY-MM-DD
- issue_date: Look for "ISS", "ISSUED" - convert to YYYY-MM-DD
- address: Full address on the license
- issuing_authority: State/Province that issued (e.g., "British Columbia", "California")

Set document_type to "drivers_license"."""


# Tailored prompt for BC Services Card
BC_SERVICES_PROMPT = """You are an expert at extracting structured data from BC Services Cards (British Columbia health cards).

Analyze this BC Services Card image and extract the identity information.

CRITICAL - Finding the Personal Health Number (unique_id):
- Look for "PERSONAL HEALTH NUMBER" or "PHN" label
- The PHN is a 10-DIGIT NUMBER (e.g., "9012 345 678" or "9012345678")
- It may be formatted with spaces: "9012 345 678"
- Remove any spaces and return just the digits as unique_id
- This is the MOST IMPORTANT field - the 10-digit number is the PHN

Other fields to extract:
- first_name: Given name
- last_name: Family name / surname
- date_of_birth: Look for "DATE OF BIRTH" or "DOB" - convert to YYYY-MM-DD
- expiry_date: Card expiry if shown - convert to YYYY-MM-DD
- address: Not typically on BC Services Cards, leave null if not present
- issuing_authority: Should be "British Columbia" or "BC"

Set document_type to "bc_services"."""


# Tailored prompt for Passport
PASSPORT_PROMPT = """You are an expert at extracting structured data from passports.

Analyze this passport image and extract the identity information.

CRITICAL - Finding the Passport Number (unique_id):
- Look for "PASSPORT NO", "PASSPORT NUMBER", or just the alphanumeric code
- Passport numbers are typically 8-9 characters, mix of letters and numbers
- Common formats: "AB123456", "123456789", "A12345678"
- Check the MRZ (Machine Readable Zone) at the bottom - the passport number is in the first line
- MRZ format: First 2 chars are country code, next 9 chars include the passport number
- This is the MOST IMPORTANT field

Other fields to extract:
- first_name: Given names
- last_name: Surname / family name
- date_of_birth: Convert to YYYY-MM-DD format
- expiry_date: "DATE OF EXPIRY" - convert to YYYY-MM-DD
- issue_date: "DATE OF ISSUE" - convert to YYYY-MM-DD  
- issuing_authority: Country that issued the passport
- In additional_metadata: nationality, place_of_birth, sex

Set document_type to "passport"."""


# Tailored prompt for generic health cards
HEALTH_CARD_PROMPT = """You are an expert at extracting structured data from health cards.

Analyze this health card image and extract the identity information.

CRITICAL - Finding the Health Number (unique_id):
- Look for "HEALTH NUMBER", "HEALTH CARD NUMBER", "PHN", "OHIP" or similar labels
- Health numbers vary by province/state but are typically 9-12 digits
- This is the MOST IMPORTANT field

Other fields to extract:
- first_name: Given name
- last_name: Family name / surname
- date_of_birth: Convert to YYYY-MM-DD format
- expiry_date: Card expiry if shown
- issuing_authority: Province/State that issued the card

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
        instructor_client = self.client.get_instructor_client()
        prompt = get_prompt_for_document_type(document_type)

        # Build user message with context
        user_content = f"Document text:\n{raw_text}"
        if filename:
            user_content = f"Filename: {filename}\n\n{user_content}"

        return instructor_client.chat.completions.create(
            model=self.client.model,
            response_model=ParsedDocument,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
            ],
        )

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
        user_text = "Extract structured data from this identity document."
        if document_type:
            user_text = f"This is a {document_type.replace('_', ' ')}. {user_text}"
        if filename:
            user_text += f" Filename: {filename}"
            
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
