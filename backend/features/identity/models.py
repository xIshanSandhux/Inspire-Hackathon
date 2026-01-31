"""Identity database model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base


class Identity(Base):
    """
    Identity entity representing a user identified by fingerprint.
    
    The fingerprint_hash_lookup is a SHA-256 hash used for indexed lookups.
    The fingerprint_hash_encrypted stores the encrypted original value.
    """

    __tablename__ = "identities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # SHA-256 hash for fast lookups (indexed)
    fingerprint_hash_lookup: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    
    # Encrypted fingerprint hash (for secure storage)
    fingerprint_hash_encrypted: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    # Relationship to documents
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="identity", cascade="all, delete-orphan"
    )
