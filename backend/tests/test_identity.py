"""Tests for identity endpoints."""

from fastapi.testclient import TestClient


class TestCreateIdentity:
    """Tests for POST /identity/create endpoint."""

    def test_create_identity_success(self, client: TestClient, sample_fingerprint: str):
        """Test creating a new identity."""
        response = client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fingerprint_hash"] == sample_fingerprint

    def test_create_identity_idempotent(self, client: TestClient, sample_fingerprint: str):
        """Test that creating the same identity twice is idempotent."""
        # Create first time
        response1 = client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )
        assert response1.status_code == 200

        # Create second time (should succeed, not error)
        response2 = client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )
        assert response2.status_code == 200
        assert response2.json()["fingerprint_hash"] == sample_fingerprint

    def test_create_identity_missing_fingerprint(self, client: TestClient):
        """Test that missing fingerprint returns validation error."""
        response = client.post(
            "/identity/create",
            json={},
        )

        assert response.status_code == 422  # Validation error


class TestRetrieveIdentity:
    """Tests for POST /identity/retrieve endpoint."""

    def test_retrieve_identity_success(self, client: TestClient, sample_fingerprint: str):
        """Test retrieving an existing identity."""
        # Create identity first
        client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        # Retrieve it
        response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": sample_fingerprint},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fingerprint_hash"] == sample_fingerprint
        assert data["documents"] == {}

    def test_retrieve_identity_not_found(self, client: TestClient):
        """Test retrieving a non-existent identity returns 404."""
        response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": "non-existent-fingerprint"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_retrieve_identity_with_documents(
        self, client: TestClient, sample_fingerprint: str, sample_image_bytes: bytes
    ):
        """Test retrieving identity includes associated documents."""
        # Create identity
        client.post(
            "/identity/create",
            json={"fingerprint_hash": sample_fingerprint},
        )

        # Add a document
        client.post(
            "/document/add-document",
            data={"fingerprint_hash": sample_fingerprint},
            files={"image": ("test.png", sample_image_bytes, "image/png")},
        )

        # Retrieve identity with documents
        response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": sample_fingerprint},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fingerprint_hash"] == sample_fingerprint
        assert len(data["documents"]) > 0
