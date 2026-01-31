"""Business logic for identity operations."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.core.crypto import decrypt_json, decrypt_value, encrypt_value, hash_for_lookup
from backend.core.db import get_db
from backend.features.identity.models import Identity
from backend.features.identity.schemas import DocumentInfo, RetrieveResponse


class IdentityService:
    """Service class for identity operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_fingerprint(self, fingerprint_hash: str) -> Identity | None:
        """Find an identity by fingerprint hash."""
        lookup_hash = hash_for_lookup(fingerprint_hash)
        return self.db.query(Identity).filter(
            Identity.fingerprint_hash_lookup == lookup_hash
        ).first()

    def create(self, fingerprint_hash: str) -> Identity:
        """
        Create a new identity if it doesn't exist.
        Returns existing identity if already exists.
        """
        # Check if identity already exists
        existing = self.get_by_fingerprint(fingerprint_hash)
        if existing:
            return existing

        # Create new identity with encrypted storage
        identity = Identity(
            fingerprint_hash_lookup=hash_for_lookup(fingerprint_hash),
            fingerprint_hash_encrypted=encrypt_value(fingerprint_hash),
        )
        self.db.add(identity)
        self.db.commit()
        self.db.refresh(identity)
        return identity

    def retrieve_with_documents(self, fingerprint_hash: str) -> RetrieveResponse | None:
        """
        Retrieve an identity with all associated documents.
        
        All encrypted document data (document_id, metadata) is decrypted
        before being returned.
        """
        identity = self.get_by_fingerprint(fingerprint_hash)
        if not identity:
            return None

        # Build documents dict keyed by document_type, decrypting sensitive fields
        documents: dict[str, DocumentInfo] = {}
        for doc in identity.documents:
            # Decrypt the document_id and metadata
            decrypted_id = decrypt_value(doc.document_id)
            decrypted_metadata = decrypt_json(doc.doc_metadata)
            
            documents[doc.document_type] = DocumentInfo(
                id=decrypted_id,
                metadata=decrypted_metadata or {},
            )

        return RetrieveResponse(
            fingerprint_hash=fingerprint_hash,
            documents=documents,
        )

    def get_decrypted_fingerprint(self, identity: Identity) -> str:
        """
        Decrypt and return the original fingerprint hash for an identity.
        
        Use sparingly - prefer using the lookup hash where possible.
        """
        return decrypt_value(identity.fingerprint_hash_encrypted)


def get_identity_service(db: Session = Depends(get_db)) -> IdentityService:
    """FastAPI dependency for IdentityService."""
    return IdentityService(db)


# Type alias for dependency injection
IdentityServiceDep = Annotated[IdentityService, Depends(get_identity_service)]
