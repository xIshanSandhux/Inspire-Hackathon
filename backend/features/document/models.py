"""Document database model."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base


class Document(Base):
    """
    Document entity associated with an identity.
    
    Stores document information like passport, SIN card, birth certificate, etc.
    
    SECURITY: document_id and doc_metadata are stored encrypted.
    - document_id: Fernet-encrypted document number (e.g., passport number)
    - doc_metadata: Fernet-encrypted JSON string containing document metadata
    
    Only document_type is stored in plaintext for querying purposes.
    Use DocumentService methods to properly encrypt/decrypt data.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Foreign key to identity (using the lookup hash)
    identity_id: Mapped[int] = mapped_column(
        ForeignKey("identities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Document type (e.g., "passport", "sin_card", "birth_certificate")
    # NOTE: Not encrypted - needed for queries
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Document ID/number (ENCRYPTED - Fernet ciphertext)
    document_id: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Additional metadata (ENCRYPTED - Fernet-encrypted JSON string)
    # Using Text for potentially large encrypted metadata payloads
    doc_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship back to identity
    identity: Mapped["Identity"] = relationship("Identity", back_populates="documents")
