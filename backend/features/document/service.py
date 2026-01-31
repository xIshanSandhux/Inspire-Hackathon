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
from backend.features.document.models import Document
from backend.features.identity.service import IdentityService, get_identity_service


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
    ) -> tuple[Document, ExtractedDocument] | None:
        """
        Add a document from an uploaded image.

        Extracts document data from the image and stores it.
        Returns None if identity not found.
        """
        identity = self.identity_service.get_by_fingerprint(fingerprint_hash)
        if not identity:
            return None

        # Extract document data from image (validation is implicit)
        extracted = await self.document_reader.extract_from_image(image)

        # Store the document
        document = self._upsert_document(
            identity_id=identity.id,
            document_type=extracted.document_type,
            document_id=extracted.document_id,
            metadata=extracted.metadata,
        )

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
