from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings


def get_engine():
    """Create and return SQLAlchemy engine."""
    connect_args = {}
    
    # SQLite needs check_same_thread=False for FastAPI
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    
    return create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args=connect_args,
    )


engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
