"""Document database model."""

from typing import Any

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base


class Document(Base):
    """
    Document entity associated with an identity.
    
    Stores document information like passport, SIN card, birth certificate, etc.
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
    document_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Document ID/number
    document_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Additional metadata as JSON (named doc_metadata to avoid SQLAlchemy reserved name)
    doc_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationship back to identity
    identity: Mapped["Identity"] = relationship("Identity", back_populates="documents")
