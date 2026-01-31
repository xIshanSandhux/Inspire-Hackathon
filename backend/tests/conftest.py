"""Pytest fixtures for e2e tests."""

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Generate a valid Fernet key for testing
TEST_ENCRYPTION_KEY = Fernet.generate_key().decode()

# Set test environment before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENCRYPTION_KEY"] = TEST_ENCRYPTION_KEY

# Use Document AI reader for E2E tests (requires GCP credentials)
# Set DOCUMENT_READER_SERVICE=document_ai to use Google Document AI
# Otherwise falls back to OCR + LLM vision
if os.environ.get("GCP_PROJECT_ID") and os.environ.get("DOCUMENT_AI_PROCESSOR_ID"):
    os.environ.setdefault("DOCUMENT_READER_SERVICE", "document_ai")

from backend.core.auth.dependencies import require_auth
from backend.core.auth.schemas import AuthenticatedUser
from backend.core.db import Base, get_db
from backend.main import app

# Test resources directory
RESOURCES_DIR = Path(__file__).parent / "resources" / "documents"


# Create test database engine
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    # Import models to register them
    from backend.features.document.models import Document  # noqa: F401
    from backend.features.identity.models import Identity  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def mock_user() -> AuthenticatedUser:
    """Mock authenticated user for testing."""
    return AuthenticatedUser(
        user_id="test-user-123",
        session_id="test-session-456",
        claims={"email": "test@example.com"},
    )


@pytest.fixture(scope="function")
def client(db_session: Session, mock_user: AuthenticatedUser) -> Generator[TestClient, None, None]:
    """Create a test client with database and auth overrides."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_auth] = lambda: mock_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_fingerprint() -> str:
    """Sample fingerprint hash for testing."""
    return "test-fingerprint-hash-12345"


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Sample image bytes for testing document upload."""
    # Minimal valid PNG (1x1 transparent pixel)
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )


# =============================================================================
# Test Document Image Fixtures
# =============================================================================
# These fixtures load real document images from the resources folder.
# Place your test images in: backend/tests/resources/documents/


@pytest.fixture
def drivers_license_image() -> bytes:
    """Load driver's license test image from resources."""
    image_path = RESOURCES_DIR / "drivers_license.jpg"
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path.read_bytes()


@pytest.fixture
def passport_image() -> bytes:
    """Load passport test image from resources."""
    image_path = RESOURCES_DIR / "passport.jpg"
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path.read_bytes()


@pytest.fixture
def health_card_image() -> bytes:
    """Load health card test image from resources."""
    image_path = RESOURCES_DIR / "health_card.jpg"
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path.read_bytes()
