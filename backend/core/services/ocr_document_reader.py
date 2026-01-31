"""OCR-based document reader service implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import UploadFile

from backend.core.services.document_reader import ExtractedDocument
from backend.core.util import get_logger

if TYPE_CHECKING:
    from backend.core.services.llm.document_parser import DocumentLLMParser
    from backend.core.services.llm.schemas import ParsedDocument

logger = get_logger(__name__)


class OCRDocumentReaderService:
    """
    Document reader service using OCR (Optical Character Recognition).
    
    This reader extracts raw text from images and optionally uses an LLM
    parser to extract structured data from the text.
    
    TODO: Implement actual OCR logic using a library like pytesseract,
    EasyOCR, or a cloud OCR service. Currently uses stub text extraction.
    """

    def __init__(self, llm_parser: DocumentLLMParser | None = None):
        """
        Initialize OCR service.
        
        Args:
            llm_parser: Optional LLM parser for structured data extraction.
                        If not provided, returns raw text in metadata.
        """
        self.llm_parser = llm_parser

    def _extract_raw_text(self, image_bytes: bytes) -> str:
        """
        Extract raw text from image bytes using OCR.
        
        TODO: Implement actual OCR using pytesseract, EasyOCR, etc.
        Currently returns placeholder text for testing.
        
        Args:
            image_bytes: Raw image data.
            
        Returns:
            Extracted text string.
        """
        # STUB: Return placeholder text
        # In production, use:
        # import pytesseract
        # from PIL import Image
        # import io
        # image = Image.open(io.BytesIO(image_bytes))
        # return pytesseract.image_to_string(image)
        return "[OCR STUB] No text extracted - implement OCR library"

    async def extract_from_image(
        self, image: UploadFile, document_type: str | None = None
    ) -> ExtractedDocument:
        """
        Extract document data from an uploaded image.

        Uses vision LLM to extract structured data directly from the image.
        Falls back to OCR + text parsing if vision fails.

        Args:
            image: The uploaded document image file.
            document_type: Optional hint about document type for tailored extraction.

        Returns:
            ExtractedDocument with the extracted data.
        """
        logger.info(f"[OCR] extract_from_image called - file: {image.filename}, content_type: {image.content_type}, document_type: {document_type}")
        
        # Read image bytes
        image_bytes = await image.read()
        mime_type = image.content_type or "image/jpeg"
        logger.info(f"[OCR] Image read - size: {len(image_bytes)} bytes, mime_type: {mime_type}")
        
        # If LLM parser is available, use vision to parse image directly
        if self.llm_parser:
            logger.info(f"[OCR] LLM parser available, attempting vision-based parsing with document_type: {document_type}")
            try:
                # Try vision-based parsing first (sends image directly to LLM)
                parsed = await self.llm_parser.parse_image_async(
                    image_bytes, mime_type, image.filename, document_type
                )
                logger.info(f"[OCR] Vision parsing successful - document_type: {parsed.document_type}, unique_id: {parsed.unique_id}")
                logger.debug(f"[OCR] Parsed fields: first_name={parsed.first_name}, last_name={parsed.last_name}, dob={parsed.date_of_birth}")
                extracted = self._convert_parsed_to_extracted(parsed, "[vision]", image)
                logger.info(f"[OCR] Converted to ExtractedDocument - document_id: {extracted.document_id}")
                return extracted
            except Exception as e:
                logger.error(f"[OCR] Vision parsing failed: {type(e).__name__}: {e}")
                # Fallback: try OCR + text parsing
                try:
                    raw_text = self._extract_raw_text(image_bytes)
                    logger.info(f"[OCR] Fallback OCR text: {raw_text[:100]}...")
                    if not raw_text.startswith("[OCR STUB]"):
                        parsed = await self.llm_parser.parse_async(raw_text, image.filename, document_type)
                        logger.info(f"[OCR] Text parsing successful - unique_id: {parsed.unique_id}")
                        return self._convert_parsed_to_extracted(parsed, raw_text, image)
                except Exception as e2:
                    logger.error(f"[OCR] Fallback text parsing also failed: {type(e2).__name__}: {e2}")
                
                # Return error response
                logger.warning(f"[OCR] Returning PARSE_ERROR result")
                return ExtractedDocument(
                    document_type=document_type or "unknown",
                    document_id="PARSE_ERROR",
                    metadata={
                        "service": "ocr",
                        "llm_error": str(e),
                        "filename": image.filename,
                        "content_type": image.content_type,
                        "size_bytes": len(image_bytes),
                    },
                    confidence=0.0,
                )
        
        # No LLM parser - try OCR only
        logger.warning(f"[OCR] No LLM parser available, returning raw OCR result")
        raw_text = self._extract_raw_text(image_bytes)
        return ExtractedDocument(
            document_type=document_type or "unknown",
            document_id="UNKNOWN",
            metadata={
                "service": "ocr",
                "raw_text": raw_text,
                "filename": image.filename,
                "content_type": image.content_type,
                "size_bytes": len(image_bytes),
                "llm_parsing": False,
            },
            confidence=0.0,
        )

    def _convert_parsed_to_extracted(
        self,
        parsed: "ParsedDocument",
        raw_text: str,
        image: UploadFile,
    ) -> ExtractedDocument:
        """
        Convert ParsedDocument from LLM to ExtractedDocument.
        
        Args:
            parsed: Structured data from LLM parser.
            raw_text: Original OCR text.
            image: Original upload file for metadata.
            
        Returns:
            ExtractedDocument with structured data.
        """
        logger.info(f"[OCR] Converting ParsedDocument to ExtractedDocument")
        logger.info(f"[OCR] ParsedDocument values:")
        logger.info(f"  - document_type: {parsed.document_type}")
        logger.info(f"  - unique_id: {parsed.unique_id}")
        logger.info(f"  - first_name: {parsed.first_name}")
        logger.info(f"  - last_name: {parsed.last_name}")
        
        # Build metadata from parsed fields
        metadata: dict = {
            "service": "ocr",
            "llm_parsing": True,
            "filename": image.filename,
        }
        
        # Add parsed fields to metadata
        if parsed.first_name:
            metadata["first_name"] = parsed.first_name
        if parsed.last_name:
            metadata["last_name"] = parsed.last_name
        if parsed.date_of_birth:
            metadata["date_of_birth"] = parsed.date_of_birth
        if parsed.expiry_date:
            metadata["expiry_date"] = parsed.expiry_date
        if parsed.issue_date:
            metadata["issue_date"] = parsed.issue_date
        if parsed.address:
            metadata["address"] = parsed.address
        if parsed.issuing_authority:
            metadata["issuing_authority"] = parsed.issuing_authority
        if parsed.confidence_notes:
            metadata["confidence_notes"] = parsed.confidence_notes
        
        # Merge additional metadata
        metadata.update(parsed.additional_metadata)
        
        document_id = parsed.unique_id or "UNKNOWN"
        confidence = 0.8 if parsed.unique_id else 0.5
        
        logger.info(f"[OCR] Final document_id: {document_id}, confidence: {confidence}")
        
        return ExtractedDocument(
            document_type=parsed.document_type.value,
            document_id=document_id,
            metadata=metadata,
            confidence=confidence,
        )
