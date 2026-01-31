"""Tests for document endpoints."""

from fastapi.testclient import TestClient


class TestAddDocument:
    """Tests for POST /document/add-document endpoint."""

    def test_add_document_success(
        self, client: TestClient, sample_fingerprint: str, sample_image_bytes: bytes
    ):
        """Test adding a document to an existing identity."""
        # Create identity first
        client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        # Add document
        response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("passport.png", sample_image_bytes, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fingerprint_hash"] == sample_fingerprint
        assert "document_type" in data
        assert "id" in data
        assert "metadata" in data
        assert "confidence" in data

    def test_add_document_identity_not_found(
        self, client: TestClient, sample_image_bytes: bytes
    ):
        """Test adding document to non-existent identity returns 404."""
        response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": "non-existent-fingerprint"},
            files={"image": ("test.png", sample_image_bytes, "image/png")},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_add_document_missing_image(self, client: TestClient, sample_fingerprint: str):
        """Test that missing image returns validation error."""
        # Create identity first
        client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        # Try to add document without image
        response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
        )

        assert response.status_code == 422  # Validation error

    def test_add_document_missing_fingerprint(
        self, client: TestClient, sample_image_bytes: bytes
    ):
        """Test that missing fingerprint returns validation error."""
        response = client.post(
            "/document/add-document",
            files={"image": ("test.png", sample_image_bytes, "image/png")},
        )

        assert response.status_code == 422  # Validation error

    def test_add_multiple_documents(
        self, client: TestClient, sample_fingerprint: str, sample_image_bytes: bytes
    ):
        """Test adding multiple documents to same identity."""
        # Create identity
        client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        # Add first document
        response1 = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("doc1.png", sample_image_bytes, "image/png")},
        )
        assert response1.status_code == 200

        # Add second document
        response2 = client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("doc2.png", sample_image_bytes, "image/png")},
        )
        assert response2.status_code == 200
