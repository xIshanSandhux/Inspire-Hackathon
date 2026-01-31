"""Google Document AI-based document reader service implementation."""

from typing import Any

from fastapi import UploadFile

from backend.core.services.document_reader import ExtractedDocument


class DocumentAIReaderService:
    """
    Document reader service using Google Document AI.
    
    Uses specialized identity document processors (US Driver License, 
    US Passport, etc.) to extract structured data from document images.
    
    Prerequisites:
        1. Enable Document AI API in your GCP project
        2. Create an Identity Document processor in Cloud Console
        3. Set GCP_PROJECT_ID, GCP_LOCATION, and DOCUMENT_AI_PROCESSOR_ID
    """

    def __init__(
        self,
        project_id: str | None,
        location: str = "us",
        processor_id: str | None = None,
    ):
        """
        Initialize Document AI service.
        
        Args:
            project_id: GCP project ID.
            location: GCP region for Document AI ("us" or "eu").
            processor_id: The Document AI processor ID (created in Cloud Console).
        """
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self._client = None

    def _get_client(self):
        """Lazy-load the Document AI client."""
        if self._client is None:
            from google.api_core.client_options import ClientOptions
            from google.cloud import documentai_v1 as documentai

            if not self.project_id:
                raise ValueError("GCP_PROJECT_ID is required for Document AI service")
            if not self.processor_id:
                raise ValueError("DOCUMENT_AI_PROCESSOR_ID is required for Document AI service")

            # Set endpoint based on location
            opts = ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
            self._client = documentai.DocumentProcessorServiceClient(client_options=opts)

        return self._client

    def _get_processor_name(self) -> str:
        """Get the fully-qualified processor resource name."""
        return (
            f"projects/{self.project_id}/locations/{self.location}"
            f"/processors/{self.processor_id}"
        )

    async def extract_from_image(self, image: UploadFile) -> ExtractedDocument:
        """
        Extract document data from an uploaded image using Document AI.

        Args:
            image: The uploaded document image file.

        Returns:
            ExtractedDocument with the extracted data.
        """
        from google.cloud import documentai_v1 as documentai

        # Read image bytes
        image_bytes = await image.read()

        # Determine MIME type
        mime_type = image.content_type or "image/jpeg"

        try:
            client = self._get_client()

            # Create the raw document
            raw_document = documentai.RawDocument(
                content=image_bytes,
                mime_type=mime_type,
            )

            # Create and send the process request
            request = documentai.ProcessRequest(
                name=self._get_processor_name(),
                raw_document=raw_document,
            )

            result = client.process_document(request=request)
            document = result.document

            # Parse the extracted entities
            return self._parse_document_entities(document)

        except Exception as e:
            # Return error result on failure
            return ExtractedDocument(
                document_type="unknown",
                document_id="ERROR",
                metadata={
                    "error": str(e),
                    "service": "document_ai",
                    "filename": image.filename,
                },
                confidence=0.0,
            )

    def _parse_document_entities(self, document) -> ExtractedDocument:
        """
        Parse Document AI response entities into ExtractedDocument.
        
        Document AI identity processors return entities like:
        - document_id (driver license number, passport number)
        - given_name, family_name
        - date_of_birth, expiration_date, issue_date
        - address
        - portrait (face image)
        """
        entities = document.entities
        metadata: dict[str, Any] = {}
        document_type = "unknown"
        document_id = "UNKNOWN"
        total_confidence = 0.0
        confidence_count = 0

        # Map of Document AI entity types to our metadata fields
        entity_mapping = {
            "document_id": "document_id",
            "given_name": "first_name",
            "family_name": "last_name",
            "full_name": "name",
            "date_of_birth": "date_of_birth",
            "expiration_date": "expiry_date",
            "issue_date": "issue_date",
            "address": "address",
            "portrait": "has_portrait",
            "mrz_code": "mrz_code",
        }

        for entity in entities:
            entity_type = entity.type_
            mention_text = entity.mention_text
            confidence = entity.confidence

            # Track confidence for averaging
            if confidence > 0:
                total_confidence += confidence
                confidence_count += 1

            # Extract document ID
            if entity_type == "document_id":
                document_id = mention_text

            # Map entity to metadata
            if entity_type in entity_mapping:
                field_name = entity_mapping[entity_type]
                if field_name == "has_portrait":
                    metadata[field_name] = True
                else:
                    metadata[field_name] = mention_text

            # Store raw entity for debugging
            if entity_type not in ["portrait"]:  # Skip binary data
                metadata[f"raw_{entity_type}"] = mention_text

        # Detect document type from entities or text
        document_type = self._detect_document_type(document, entities)

        # Calculate average confidence
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0.0

        # Add service info
        metadata["service"] = "document_ai"

        return ExtractedDocument(
            document_type=document_type,
            document_id=document_id,
            metadata=metadata,
            confidence=avg_confidence,
        )

    def _detect_document_type(self, document, entities) -> str:
        """
        Detect document type from Document AI response.
        
        The processor type and extracted entities help determine
        the document type.
        """
        text_lower = document.text.lower() if document.text else ""
        entity_types = {e.type_ for e in entities}

        # Check for passport indicators
        if "mrz_code" in entity_types or "passport" in text_lower:
            return "passport"

        # Check for driver license indicators
        if "driver" in text_lower or "license" in text_lower or "dl" in text_lower:
            return "drivers_license"

        # Check for ID card indicators
        if "identification" in text_lower or "id card" in text_lower:
            return "id_card"

        # Check for birth certificate
        if "birth" in text_lower and "certificate" in text_lower:
            return "birth_certificate"

        # Check for health card
        if "health" in text_lower or "medical" in text_lower:
            return "health_card"

        # Check for SIN card
        if "social insurance" in text_lower or "sin" in text_lower:
            return "sin_card"

        # Default based on presence of common ID fields
        if "document_id" in entity_types:
            return "id_document"

        return "unknown"
