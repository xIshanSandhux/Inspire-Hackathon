"""Business logic for document operations."""

from typing import Annotated

from fastapi import Depends, UploadFile
from sqlalchemy.orm import Session

from backend.core.db import get_db
from backend.core.services.document_reader import (
    DocumentReaderService,
    ExtractedDocument,
    get_document_reader_service,
)
from backend.core.util import get_logger
from backend.features.document.models import Document
from backend.features.identity.service import IdentityService, get_identity_service

logger = get_logger(__name__)


class DocumentService:
    """Service class for document operations."""

    def __init__(
        self,
        db: Session,
        identity_service: IdentityService,
        document_reader: DocumentReaderService,
    ):
        self.db = db
        self.identity_service = identity_service
        self.document_reader = document_reader

    async def add_from_image(
        self,
        fingerprint_hash: str,
        image: UploadFile,
        document_type: str | None = None,
    ) -> tuple[Document, ExtractedDocument] | None:
        """
        Add a document from an uploaded image.

        Extracts document data from the image and stores it.
        Returns None if identity not found.
        
        Args:
            fingerprint_hash: The identity's fingerprint hash.
            image: The uploaded document image.
            document_type: Optional hint about the document type for better extraction.
        """
        logger.info(f"[SERVICE] add_from_image called - fingerprint: {fingerprint_hash[:8]}..., document_type: {document_type}")
        
        identity = self.identity_service.get_by_fingerprint(fingerprint_hash)
        if not identity:
            logger.warning(f"[SERVICE] Identity not found for fingerprint: {fingerprint_hash[:8]}...")
            return None
        
        logger.info(f"[SERVICE] Identity found - id: {identity.id}")

        # Extract document data from image with document type hint
        logger.info(f"[SERVICE] Calling document_reader.extract_from_image with document_type: {document_type}")
        extracted = await self.document_reader.extract_from_image(image, document_type)
        
        logger.info(f"[SERVICE] Extraction result:")
        logger.info(f"  - extracted.document_type: {extracted.document_type}")
        logger.info(f"  - extracted.document_id: {extracted.document_id}")
        logger.info(f"  - extracted.confidence: {extracted.confidence}")
        logger.debug(f"  - extracted.metadata keys: {list(extracted.metadata.keys())}")

        # Use the provided document_type if extraction didn't determine one
        final_document_type = extracted.document_type
        if final_document_type == "unknown" and document_type:
            final_document_type = document_type
            logger.info(f"[SERVICE] Using provided document_type: {final_document_type}")

        # Store the document
        logger.info(f"[SERVICE] Upserting document...")
        document = self._upsert_document(
            identity_id=identity.id,
            document_type=final_document_type,
            document_id=extracted.document_id,
            metadata=extracted.metadata,
        )
        
        logger.info(f"[SERVICE] Document upserted - db_id: {document.id}, document_id: {document.document_id}")

        return document, extracted

    def _upsert_document(
        self,
        identity_id: int,
        document_type: str,
        document_id: str,
        metadata: dict | None = None,
    ) -> Document:
        """Create or update a document for an identity."""
        # Check if document type already exists for this identity
        existing_doc = self.db.query(Document).filter(
            Document.identity_id == identity_id,
            Document.document_type == document_type,
        ).first()

        if existing_doc:
            # Update existing document
            existing_doc.document_id = document_id
            existing_doc.doc_metadata = metadata
            self.db.commit()
            self.db.refresh(existing_doc)
            return existing_doc

        # Create new document
        document = Document(
            identity_id=identity_id,
            document_type=document_type,
            document_id=document_id,
            doc_metadata=metadata,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_for_identity(self, fingerprint_hash: str) -> list[Document]:
        """Get all documents for an identity."""
        identity = self.identity_service.get_by_fingerprint(fingerprint_hash)
        if not identity:
            return []
        return identity.documents


def get_document_service(
    db: Session = Depends(get_db),
    identity_service: IdentityService = Depends(get_identity_service),
    document_reader: DocumentReaderService = Depends(get_document_reader_service),
) -> DocumentService:
    """FastAPI dependency for DocumentService."""
    return DocumentService(db, identity_service, document_reader)


# Type alias for dependency injection
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
