"""E2E tests for document upload with document parsing.

These tests verify the full document upload flow including:
- Identity creation
- Document image upload
- Document parsing (via Document AI or LLM vision)
- Structured data extraction verification

To run these tests:
    # With Google Document AI:
    GCP_PROJECT_ID=xxx DOCUMENT_AI_PROCESSOR_ID=xxx pytest backend/tests/test_e2e_document_parsing.py -v
    
    # With OpenRouter LLM vision:
    OPENROUTER_API_KEY=sk-or-v1-xxx pytest backend/tests/test_e2e_document_parsing.py -v
"""

import os
import sys
import warnings

import pytest
from fastapi.testclient import TestClient


def has_document_ai_config() -> bool:
    """Check if Document AI is configured."""
    gcp_project = os.environ.get("GCP_PROJECT_ID")
    processor_id = os.environ.get("DOCUMENT_AI_PROCESSOR_ID")
    return bool(gcp_project and processor_id)


def has_llm_config() -> bool:
    """Check if LLM (OpenRouter) is configured."""
    return bool(os.environ.get("OPENROUTER_API_KEY"))


def get_config_summary() -> str:
    """Build configuration summary."""
    lines = [
        "",
        "=" * 60,
        "E2E Document Parsing Test Configuration:",
        "=" * 60,
        f"  GCP_PROJECT_ID: {os.environ.get('GCP_PROJECT_ID', '(not set)')}",
        f"  DOCUMENT_AI_PROCESSOR_ID: {os.environ.get('DOCUMENT_AI_PROCESSOR_ID', '(not set)')}",
        f"  DOCUMENT_READER_SERVICE: {os.environ.get('DOCUMENT_READER_SERVICE', 'ocr (default)')}",
        f"  OPENROUTER_API_KEY: {'set (' + os.environ.get('OPENROUTER_API_KEY', '')[:15] + '...)' if os.environ.get('OPENROUTER_API_KEY') else '(not set)'}",
        f"  Document AI configured: {has_document_ai_config()}",
        f"  LLM configured: {has_llm_config()}",
        f"  Tests will run: {has_document_ai_config() or has_llm_config()}",
        "=" * 60,
        "",
    ]
    return "\n".join(lines)


def get_skip_reason() -> str:
    """Build detailed skip reason showing what's missing."""
    lines = ["Document parsing not configured."]
    lines.append(get_config_summary())
    lines.append("Set either Document AI OR OpenRouter credentials to run these tests.")
    return "\n".join(lines)


# Log configuration status at import time (write to stderr to avoid pytest capture)
sys.stderr.write(get_config_summary())
sys.stderr.flush()

# Also emit as a warning so it shows in pytest output
if not has_document_ai_config() and not has_llm_config():
    warnings.warn(
        f"Skipping E2E document parsing tests - no parsing backend configured.\n{get_config_summary()}",
        UserWarning,
    )


# Skip all tests in this module if neither Document AI nor LLM is configured
pytestmark = pytest.mark.skipif(
    not has_document_ai_config() and not has_llm_config(),
    reason=get_skip_reason(),
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

        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()

        # Debug output - print full response
        print("\n" + "=" * 60)
        print("DOCUMENT UPLOAD RESPONSE:")
        print("=" * 60)
        import json
        print(json.dumps(data, indent=2))
        print("=" * 60 + "\n")

        # Basic structure assertions
        assert data["fingerprint_hash"] == sample_fingerprint
        assert "document_type" in data
        assert "id" in data
        assert "metadata" in data
        assert "confidence" in data

        # Document type should be detected as drivers_license
        assert data["document_type"] == "drivers_license", f"Expected 'drivers_license' but got '{data['document_type']}'. Full metadata: {data['metadata']}"

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
