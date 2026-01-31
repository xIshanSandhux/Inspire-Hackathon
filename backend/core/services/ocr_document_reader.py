"""OCR-based document reader service implementation (stub)."""

from fastapi import UploadFile

from backend.core.services.document_reader import ExtractedDocument


class OCRDocumentReaderService:
    """
    Document reader service using OCR (Optical Character Recognition).
    
    TODO: Implement actual OCR logic using a library like pytesseract,
    EasyOCR, or a cloud OCR service.
    
    This is currently a stub that returns mock data.
    """

    def __init__(self):
        """Initialize OCR service."""
        pass

    async def extract_from_image(self, image: UploadFile) -> ExtractedDocument:
        """
        Extract document data from an uploaded image using OCR.

        Args:
            image: The uploaded document image file.

        Returns:
            ExtractedDocument with the extracted data.
        """
        # Read image bytes (simulating processing)
        image_bytes = await image.read()
        
        # STUB: Return mock data for now
        return ExtractedDocument(
            document_type="unknown",
            document_id="OCR-STUB-ID-12345",
            metadata={
                "service": "ocr",
                "stub": True,
                "filename": image.filename,
                "content_type": image.content_type,
                "size_bytes": len(image_bytes),
            },
            confidence=0.0,
        )
