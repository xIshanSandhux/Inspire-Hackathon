"""Document reader service for extracting data from document images."""

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import Depends, UploadFile


@dataclass
class ExtractedDocument:
    """Data extracted from a document image."""

    document_type: str  # e.g., "passport", "drivers_license", "birth_certificate"
    document_id: str  # The ID/number on the document
    metadata: dict[str, Any]  # Additional extracted fields (name, expiry, etc.)
    confidence: float  # Confidence score 0-1


class DocumentReaderService:
    """
    Service for reading and extracting data from document images.
    
    TODO: Implement actual document reading using OCR/AI.
    This is a stub that returns mock data.
    """

    def __init__(self):
        # TODO: Initialize any ML models, API clients, etc.
        pass

    async def extract_from_image(self, image: UploadFile) -> ExtractedDocument:
        """
        Extract document data from an uploaded image.
        
        Args:
            image: The uploaded document image file.
            
        Returns:
            ExtractedDocument with the extracted data.
            
        TODO: Implement actual extraction logic:
            - Read image bytes from UploadFile
            - Run OCR / document AI
            - Parse and validate extracted fields
            - Determine document type
        """
        # STUB: Return mock data for now
        _ = await image.read()  # Read to simulate processing
        
        return ExtractedDocument(
            document_type="unknown",
            document_id="STUB-ID-12345",
            metadata={
                "stub": True,
                "filename": image.filename,
                "content_type": image.content_type,
            },
            confidence=0.0,
        )


def get_document_reader_service() -> DocumentReaderService:
    """FastAPI dependency for DocumentReaderService."""
    return DocumentReaderService()


# Type alias for dependency injection
DocumentReaderServiceDep = Annotated[DocumentReaderService, Depends(get_document_reader_service)]
