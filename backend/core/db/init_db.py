from .base import Base
from .engine import engine


def init_db() -> None:
    """Initialize the database by creating all tables."""
    # Import models here to ensure they're registered with Base.metadata
    from backend.features.identity.models import Identity  # noqa: F401
    from backend.features.document.models import Document  # noqa: F401

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all tables. Use with caution!"""
    from backend.features.identity.models import Identity  # noqa: F401
    from backend.features.document.models import Document  # noqa: F401

    Base.metadata.drop_all(bind=engine)
