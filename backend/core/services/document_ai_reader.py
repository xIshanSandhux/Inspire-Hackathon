"""Google Document AI-based document reader service implementation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from fastapi import UploadFile

from backend.core.services.document_reader import ExtractedDocument
from backend.core.util import get_logger

if TYPE_CHECKING:
    from backend.core.services.llm.document_parser import DocumentLLMParser

logger = get_logger(__name__)


class DocumentAIReaderService:
    """
    Document reader service using Google Document AI.
    
    Uses specialized identity document processors (US Driver License, 
    US Passport, etc.) to extract structured data from document images.
    
    Can optionally use an LLM parser as fallback when Document AI
    entity extraction fails to find the document ID.
    
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
        llm_parser: "DocumentLLMParser | None" = None,
    ):
        """
        Initialize Document AI service.
        
        Args:
            project_id: GCP project ID.
            location: GCP region for Document AI ("us" or "eu").
            processor_id: The Document AI processor ID (created in Cloud Console).
            llm_parser: Optional LLM parser for fallback extraction.
        """
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.llm_parser = llm_parser
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

    async def extract_from_image(
        self, image: UploadFile, document_type: str | None = None
    ) -> ExtractedDocument:
        """
        Extract document data from an uploaded image using Document AI.

        Args:
            image: The uploaded document image file.
            document_type: Optional hint about document type (used for fallback detection).

        Returns:
            ExtractedDocument with the extracted data.
        """
        from google.cloud import documentai_v1 as documentai

        logger.info(f"[DOC_AI] extract_from_image called - file: {image.filename}, content_type: {image.content_type}, document_type_hint: {document_type}")
        self._document_type_hint = document_type  # Store for use in parsing

        # Read image bytes
        image_bytes = await image.read()
        logger.info(f"[DOC_AI] Image read - size: {len(image_bytes)} bytes")

        # Determine MIME type
        mime_type = image.content_type or "image/jpeg"

        try:
            client = self._get_client()
            logger.info(f"[DOC_AI] Client obtained, processor: {self._get_processor_name()}")

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

            logger.info(f"[DOC_AI] Sending request to Document AI...")
            result = client.process_document(request=request)
            document = result.document
            
            # Log raw extracted text
            raw_text = document.text if document.text else ""
            logger.info(f"[DOC_AI] Response received - text length: {len(raw_text)}, entities: {len(document.entities)}")
            logger.info(f"[DOC_AI] ========== RAW EXTRACTED TEXT START ==========")
            logger.info(f"[DOC_AI] {raw_text}")
            logger.info(f"[DOC_AI] ========== RAW EXTRACTED TEXT END ==========")

            # Parse the extracted entities
            extracted = await self._parse_document_entities(document)
            logger.info(f"[DOC_AI] Parsed result - type: {extracted.document_type}, id: {extracted.document_id}, confidence: {extracted.confidence}")
            return extracted

        except Exception as e:
            logger.error(f"[DOC_AI] ERROR during extraction: {type(e).__name__}: {e}")
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

    async def _parse_document_entities(self, document) -> ExtractedDocument:
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

        logger.info(f"[DOC_AI] Parsing {len(entities)} entities from Document AI response")
        
        # Log all entities for debugging
        logger.info(f"[DOC_AI] ========== ALL ENTITIES START ==========")
        for i, entity in enumerate(entities):
            entity_type = entity.type_
            mention_text = entity.mention_text if entity.mention_text else "(empty)"
            confidence = entity.confidence
            # Skip portrait binary data
            if entity_type != "portrait":
                logger.info(f"[DOC_AI] Entity[{i}]: type='{entity_type}', value='{mention_text}', confidence={confidence:.3f}")
            else:
                logger.info(f"[DOC_AI] Entity[{i}]: type='portrait', value='(binary data)', confidence={confidence:.3f}")
        logger.info(f"[DOC_AI] ========== ALL ENTITIES END ==========")

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
            
            logger.debug(f"[DOC_AI] Entity: type={entity_type}, text={mention_text[:50] if mention_text else 'None'}..., confidence={confidence}")

            # Track confidence for averaging
            if confidence > 0:
                total_confidence += confidence
                confidence_count += 1

            # Extract document ID
            if entity_type == "document_id":
                document_id = mention_text
                logger.info(f"[DOC_AI] Found document_id entity: {document_id}")

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

        # Detect document type from entities or text (use hint if available)
        document_type = getattr(self, '_document_type_hint', None) or self._detect_document_type(document, entities)
        logger.info(f"[DOC_AI] Detected document_type: {document_type}")

        # If no document_id found in entities, try LLM first (smarter), then regex fallback
        if document_id == "UNKNOWN" and document.text:
            logger.info(f"[DOC_AI] No document_id entity found, attempting LLM extraction first...")
            
            # First try LLM extraction (smarter, extracts more fields)
            if self.llm_parser:
                logger.info(f"[DOC_AI] ========== LLM EXTRACTION STARTING ==========")
                logger.info(f"[DOC_AI] self.llm_parser is set: {self.llm_parser is not None}")
                logger.info(f"[DOC_AI] document.text length: {len(document.text)}")
                logger.info(f"[DOC_AI] document_type for LLM: {document_type}")
                try:
                    # Use the raw text to get LLM to extract structured data
                    logger.info(f"[DOC_AI] Calling llm_parser.parse_async()...")
                    parsed = await self.llm_parser.parse_async(document.text, None, document_type)
                    logger.info(f"[DOC_AI] LLM parse completed!")
                    logger.info(f"[DOC_AI] LLM returned unique_id: {parsed.unique_id}")
                    logger.info(f"[DOC_AI] LLM returned document_type: {parsed.document_type}")
                    logger.info(f"[DOC_AI] LLM returned first_name: {parsed.first_name}")
                    logger.info(f"[DOC_AI] LLM returned last_name: {parsed.last_name}")
                    logger.info(f"[DOC_AI] LLM returned date_of_birth: {parsed.date_of_birth}")
                    logger.info(f"[DOC_AI] LLM returned expiry_date: {parsed.expiry_date}")
                    logger.info(f"[DOC_AI] LLM returned address: {parsed.address}")
                    
                    if parsed.unique_id:
                        document_id = parsed.unique_id
                        metadata["id_extraction_method"] = "llm"
                        logger.info(f"[DOC_AI] LLM extraction successful: {document_id}")
                        
                        # Grab all fields from LLM if we didn't get them from Document AI
                        if not metadata.get("first_name") and parsed.first_name:
                            metadata["first_name"] = parsed.first_name
                        if not metadata.get("last_name") and parsed.last_name:
                            metadata["last_name"] = parsed.last_name
                        if not metadata.get("date_of_birth") and parsed.date_of_birth:
                            metadata["date_of_birth"] = parsed.date_of_birth
                        if not metadata.get("expiry_date") and parsed.expiry_date:
                            metadata["expiry_date"] = parsed.expiry_date
                        if not metadata.get("address") and parsed.address:
                            metadata["address"] = parsed.address
                        if not metadata.get("sex") and parsed.sex:
                            metadata["sex"] = parsed.sex
                        if not metadata.get("issuing_authority") and parsed.issuing_authority:
                            metadata["issuing_authority"] = parsed.issuing_authority
                    else:
                        logger.warning(f"[DOC_AI] LLM returned but unique_id was None/empty")
                except Exception as e:
                    logger.error(f"[DOC_AI] LLM extraction EXCEPTION: {type(e).__name__}: {e}")
                    import traceback
                    logger.error(f"[DOC_AI] Traceback: {traceback.format_exc()}")
                logger.info(f"[DOC_AI] ========== LLM EXTRACTION ENDED ==========")
            else:
                logger.warning(f"[DOC_AI] self.llm_parser is None - LLM extraction not available")
            
            # If LLM failed or not available, fall back to regex
            if document_id == "UNKNOWN":
                logger.info(f"[DOC_AI] LLM didn't extract ID, trying regex fallback...")
                fallback_id = self._extract_id_from_text(document.text, document_type)
                if fallback_id:
                    document_id = fallback_id
                    metadata["id_extraction_method"] = "fallback_regex"
                    logger.info(f"[DOC_AI] Regex fallback extraction successful: {document_id}")
                else:
                    logger.warning(f"[DOC_AI] All extraction methods failed - no ID found")

        # Calculate average confidence
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0.0
        
        # Adjust confidence based on extraction method
        if metadata.get("id_extraction_method") == "llm":
            avg_confidence = max(avg_confidence, 0.9)  # High confidence for LLM extraction
        elif metadata.get("id_extraction_method") == "fallback_regex":
            avg_confidence = max(avg_confidence, 0.7)  # Decent confidence for regex match

        # Add service info and raw text for debugging
        metadata["service"] = "document_ai"
        metadata["raw_text"] = document.text if document.text else ""
        
        logger.info(f"[DOC_AI] Final parsed values - document_id: {document_id}, document_type: {document_type}, confidence: {avg_confidence}")
        logger.debug(f"[DOC_AI] Metadata keys: {list(metadata.keys())}")

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

    def _extract_id_from_text(self, raw_text: str, document_type: str) -> str | None:
        """
        Extract document ID from raw text using regex patterns.
        
        This is a fallback when Document AI doesn't extract a document_id entity.
        
        Args:
            raw_text: The raw OCR text from the document.
            document_type: The detected/hinted document type.
            
        Returns:
            Extracted ID string, or None if no pattern matched.
        """
        logger.info(f"[DOC_AI] Attempting fallback ID extraction for document_type: {document_type}")
        
        # Normalize text for searching
        text = raw_text.replace('\n', ' ').replace('\r', ' ')
        
        # Driver's License patterns (BC, Canadian, US)
        if document_type in ("drivers_license", "unknown"):
            # BC Driver's License: NDL, LDL, or DL followed by colon/space and digits
            # Pattern: NDL:01944956 or DL: 12345678 or LDL 12345678
            dl_patterns = [
                r'NDL[:\s]*(\d{7,9})',      # NDL:01944956
                r'LDL[:\s]*(\d{7,9})',      # LDL:12345678  
                r'DL[:\s]*(\d{7,9})',       # DL: 12345678
                r'DLN[:\s]*(\d{7,9})',      # DLN: 12345678
                r'LICENCE\s*(?:NO\.?|NUMBER|#)?[:\s]*(\d{7,9})',  # LICENCE NO: 12345678
                r'LICENSE\s*(?:NO\.?|NUMBER|#)?[:\s]*(\d{7,9})',  # LICENSE NO: 12345678
            ]
            
            for pattern in dl_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    dl_number = match.group(1)
                    logger.info(f"[DOC_AI] Found driver's license number with pattern '{pattern}': {dl_number}")
                    return dl_number
        
        # BC Services Card / Health Card patterns
        if document_type in ("bc_services", "health_card", "unknown"):
            # PHN is 10 digits, may have spaces: 9012 345 678
            phn_patterns = [
                r'PERSONAL\s*HEALTH\s*(?:NUMBER|NO\.?|#)?[:\s]*(\d[\d\s]{8,11}\d)',
                r'PHN[:\s]*(\d[\d\s]{8,11}\d)',
                r'HEALTH\s*(?:NUMBER|NO\.?|#)?[:\s]*(\d{10})',
            ]
            
            for pattern in phn_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Remove spaces from PHN
                    phn = re.sub(r'\s', '', match.group(1))
                    if len(phn) == 10:
                        logger.info(f"[DOC_AI] Found PHN with pattern '{pattern}': {phn}")
                        return phn
        
        # Passport patterns
        if document_type in ("passport", "unknown"):
            # Passport numbers are typically 8-9 alphanumeric characters
            passport_patterns = [
                r'PASSPORT\s*(?:NO\.?|NUMBER|#)?[:\s]*([A-Z]{1,2}\d{6,8})',
                r'PASSPORT\s*(?:NO\.?|NUMBER|#)?[:\s]*(\d{9})',
                # MRZ line 1 contains passport number after country code
                r'[A-Z]{3}([A-Z0-9]{9})',  # Very basic MRZ pattern
            ]
            
            for pattern in passport_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    passport_num = match.group(1).upper()
                    logger.info(f"[DOC_AI] Found passport number with pattern '{pattern}': {passport_num}")
                    return passport_num
        
        # Generic fallback: look for any labeled ID number
        generic_patterns = [
            r'(?:ID|CARD)\s*(?:NO\.?|NUMBER|#)?[:\s]*([A-Z0-9]{6,12})',
            r'(?:NO\.?|NUMBER|#)[:\s]*([A-Z0-9]{7,12})',
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                id_num = match.group(1)
                logger.info(f"[DOC_AI] Found generic ID with pattern '{pattern}': {id_num}")
                return id_num
        
        logger.warning(f"[DOC_AI] No ID pattern matched in text")
        return None
