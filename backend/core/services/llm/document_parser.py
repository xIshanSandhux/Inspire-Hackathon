"""LLM-based document parsing service."""

from backend.core.services.llm.client import OpenRouterClient
from backend.core.services.llm.schemas import ParsedDocument


DOCUMENT_EXTRACTION_PROMPT = """You are an expert at extracting structured data from identity documents.

Given the raw text extracted from a document image, extract all relevant identity information.

Guidelines:
- Extract names exactly as they appear on the document
- For dates, convert to ISO format (YYYY-MM-DD) when possible
- The unique_id should be the primary identifier (driver's license number, passport number, PHN, SIN, etc.)
- Identify the document type based on content and formatting cues
- Include any additional relevant fields in additional_metadata
- Note any ambiguities or low-confidence extractions in confidence_notes
- If a field is not present or cannot be determined, leave it as null

Common document types:
- drivers_license: Contains DL number, usually has address, photo, class
- passport: Contains passport number, nationality, MRZ code
- health_card: Contains PHN (Personal Health Number), provincial health info
- birth_certificate: Contains registration number, place of birth, parents' names
- sin_card: Contains Social Insurance Number (9 digits)
- id_card: Generic government ID card"""


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

    def parse(self, raw_text: str, filename: str | None = None) -> ParsedDocument:
        """
        Extract structured document data from raw text using LLM.
        
        Args:
            raw_text: The raw text extracted from the document image.
            filename: Optional filename for context (may hint at document type).
            
        Returns:
            ParsedDocument with extracted structured data.
        """
        instructor_client = self.client.get_instructor_client()

        # Build user message with context
        user_content = f"Document text:\n{raw_text}"
        if filename:
            user_content = f"Filename: {filename}\n\n{user_content}"

        return instructor_client.chat.completions.create(
            model=self.client.model,
            response_model=ParsedDocument,
            messages=[
                {"role": "system", "content": DOCUMENT_EXTRACTION_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )

    async def parse_async(
        self, raw_text: str, filename: str | None = None
    ) -> ParsedDocument:
        """
        Async version of parse for use in async contexts.
        
        Note: instructor's sync client is used here as OpenAI's async
        client has different semantics. For true async, consider using
        asyncio.to_thread or the async OpenAI client.
        
        Args:
            raw_text: The raw text extracted from the document image.
            filename: Optional filename for context.
            
        Returns:
            ParsedDocument with extracted structured data.
        """
        # For now, use sync client - instructor handles this well
        # In production, consider using AsyncOpenAI with instructor
        import asyncio

        return await asyncio.to_thread(self.parse, raw_text, filename)
