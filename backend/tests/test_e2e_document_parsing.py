"""E2E tests for document upload with LLM parsing.

These tests verify the full document upload flow including:
- Identity creation
- Document image upload
- LLM-based document parsing (when OPENROUTER_API_KEY is set)
- Structured data extraction verification

To run these tests with LLM parsing:
    OPENROUTER_API_KEY=sk-or-v1-xxx pytest backend/tests/test_e2e_document_parsing.py -v
"""

import os

import pytest
from fastapi.testclient import TestClient


# Skip all tests in this module if OPENROUTER_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"),
    reason="Requires OPENROUTER_API_KEY for LLM parsing",
)


class TestDocumentParsing:
    """E2E tests for document upload and LLM extraction."""

    def test_upload_drivers_license(
        self,
        client: TestClient,
        sample_fingerprint: str,
        drivers_license_image: bytes,
    ):
        """Test uploading a driver's license extracts expected fields."""
        # Create identity first
        create_response = client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )
        assert create_response.status_code == 200

        # Upload document
        response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("drivers_license.jpg", drivers_license_image, "image/jpeg")},
        )

        assert response.status_code == 200
        data = response.json()

        # Basic structure assertions
        assert data["fingerprint_hash"] == sample_fingerprint
        assert "document_type" in data
        assert "id" in data
        assert "metadata" in data
        assert "confidence" in data

        # Document type should be detected as drivers_license
        assert data["document_type"] == "drivers_license"

        # LLM parsing should have been used
        assert data["metadata"].get("llm_parsing") is True

        # Assertions for extracted data (fill in expected values based on test image)
        # assert data["metadata"]["first_name"] == ""
        # assert data["metadata"]["last_name"] == ""
        # assert data["id"] == ""

    def test_upload_passport(
        self,
        client: TestClient,
        sample_fingerprint: str,
        passport_image: bytes,
    ):
        """Test uploading a passport extracts expected fields."""
        # Create identity first
        create_response = client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )
        assert create_response.status_code == 200

        # Upload document
        response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("passport.jpg", passport_image, "image/jpeg")},
        )

        assert response.status_code == 200
        data = response.json()

        # Basic structure assertions
        assert data["fingerprint_hash"] == sample_fingerprint
        assert "document_type" in data
        assert "id" in data
        assert "metadata" in data

        # Document type should be detected as passport
        assert data["document_type"] == "passport"

        # Assertions for extracted data (fill in expected values based on test image)
        # assert data["metadata"]["first_name"] == ""
        # assert data["metadata"]["last_name"] == ""
        # assert data["id"] == ""

    def test_upload_health_card(
        self,
        client: TestClient,
        sample_fingerprint: str,
        health_card_image: bytes,
    ):
        """Test uploading a health card extracts expected fields."""
        # Create identity first
        create_response = client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )
        assert create_response.status_code == 200

        # Upload document
        response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("health_card.jpg", health_card_image, "image/jpeg")},
        )

        assert response.status_code == 200
        data = response.json()

        # Basic structure assertions
        assert data["fingerprint_hash"] == sample_fingerprint
        assert "document_type" in data
        assert "id" in data
        assert "metadata" in data

        # Document type should be detected as health_card
        assert data["document_type"] == "health_card"

        # Assertions for extracted data (fill in expected values based on test image)
        # assert data["metadata"]["first_name"] == ""
        # assert data["metadata"]["last_name"] == ""
        # assert data["id"] == ""  # PHN


class TestDocumentParsingFlow:
    """E2E tests for complete document parsing workflows."""

    def test_full_identity_with_multiple_documents(
        self,
        client: TestClient,
        drivers_license_image: bytes,
        passport_image: bytes,
    ):
        """Test creating identity and uploading multiple documents."""
        fingerprint = "multi-doc-test-fingerprint"

        # Create identity
        create_response = client.post(
            "/identity/create",
            json={"fingerprint_hash": fingerprint},
        )
        assert create_response.status_code == 200

        # Upload driver's license
        dl_response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": fingerprint},
            files={"image": ("drivers_license.jpg", drivers_license_image, "image/jpeg")},
        )
        assert dl_response.status_code == 200
        assert dl_response.json()["document_type"] == "drivers_license"

        # Upload passport
        passport_response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": fingerprint},
            files={"image": ("passport.jpg", passport_image, "image/jpeg")},
        )
        assert passport_response.status_code == 200
        assert passport_response.json()["document_type"] == "passport"

        # Retrieve identity and verify both documents are present
        retrieve_response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": fingerprint},
        )
        assert retrieve_response.status_code == 200

        data = retrieve_response.json()
        assert data["fingerprint_hash"] == fingerprint
        assert "drivers_license" in data["documents"]
        assert "passport" in data["documents"]

    def test_document_data_persists_after_retrieval(
        self,
        client: TestClient,
        sample_fingerprint: str,
        drivers_license_image: bytes,
    ):
        """Test that extracted document data persists correctly."""
        # Create identity and upload document
        client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        upload_response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("drivers_license.jpg", drivers_license_image, "image/jpeg")},
        )
        assert upload_response.status_code == 200
        uploaded_data = upload_response.json()

        # Retrieve identity
        retrieve_response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": sample_fingerprint},
        )
        assert retrieve_response.status_code == 200

        retrieved_data = retrieve_response.json()
        doc = retrieved_data["documents"].get("drivers_license")
        assert doc is not None

        # Verify the document ID matches what was uploaded
        assert doc["id"] == uploaded_data["id"]

        # Verify metadata was persisted
        # assert doc["metadata"]["first_name"] == uploaded_data["metadata"]["first_name"]
        # assert doc["metadata"]["last_name"] == uploaded_data["metadata"]["last_name"]
