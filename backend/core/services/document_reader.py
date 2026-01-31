"""Document reader service protocol and factory."""

from dataclasses import dataclass
from typing import Annotated, Any, Protocol, runtime_checkable

from fastapi import Depends, UploadFile

from backend.core.config import settings


@dataclass
class ExtractedDocument:
    """Data extracted from a document image."""

    document_type: str  # e.g., "passport", "drivers_license", "birth_certificate"
    document_id: str  # The ID/number on the document
    metadata: dict[str, Any]  # Additional extracted fields (name, expiry, etc.)
    confidence: float  # Confidence score 0-1


@runtime_checkable
class DocumentReaderService(Protocol):
    """Protocol for document reader services."""

    async def extract_from_image(self, image: UploadFile) -> ExtractedDocument:
        """
        Extract document data from an uploaded image.

        Args:
            image: The uploaded document image file.

        Returns:
            ExtractedDocument with the extracted data.
        """
        ...


def get_document_reader_service() -> DocumentReaderService:
    """
    Factory function to get the configured document reader service.
    
    Returns the appropriate implementation based on settings.document_reader_service.
    """
    from backend.core.services.document_ai_reader import DocumentAIReaderService
    from backend.core.services.ocr_document_reader import OCRDocumentReaderService

    service_type = settings.document_reader_service.lower()

    if service_type == "document_ai":
        return DocumentAIReaderService(
            project_id=settings.gcp_project_id,
            location=settings.gcp_location,
            processor_id=settings.document_ai_processor_id,
        )
    else:
        # Default to OCR stub
        return OCRDocumentReaderService()


# Type alias for dependency injection
DocumentReaderServiceDep = Annotated[DocumentReaderService, Depends(get_document_reader_service)]
