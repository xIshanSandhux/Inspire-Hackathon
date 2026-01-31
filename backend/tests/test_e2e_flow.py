"""End-to-end flow tests simulating real usage scenarios."""

from fastapi.testclient import TestClient


class TestFullUserFlow:
    """Test complete user registration and document upload flow."""

    def test_complete_registration_flow(
        self, client: TestClient, sample_image_bytes: bytes
    ):
        """
        Test the complete flow:
        1. User registers with fingerprint
        2. User uploads documents
        3. User retrieves their identity with documents
        """
        fingerprint = "user-abc-fingerprint-hash"

        # Step 1: Register identity
        create_response = client.post(
            "/identity/create",
            json={"fingerprint_hash": fingerprint},
        )
        assert create_response.status_code == 200
        assert create_response.json()["fingerprint_hash"] == fingerprint

        # Step 2: Upload a document
        upload_response = client.post(
            "/document/add-document",
            data={"fingerprint_hash": fingerprint},
            files={"image": ("passport.png", sample_image_bytes, "image/png")},
        )
        assert upload_response.status_code == 200

        # Step 3: Retrieve identity with documents
        retrieve_response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": fingerprint},
        )
        assert retrieve_response.status_code == 200

        data = retrieve_response.json()
        assert data["fingerprint_hash"] == fingerprint
        assert len(data["documents"]) >= 1

    def test_multiple_users_isolation(
        self, client: TestClient, sample_image_bytes: bytes
    ):
        """Test that different users' data is properly isolated."""
        user1_fingerprint = "user-1-fingerprint"
        user2_fingerprint = "user-2-fingerprint"

        # Create both users
        client.post("/identity/create", json={"fingerprint_hash": user1_fingerprint})
        client.post("/identity/create", json={"fingerprint_hash": user2_fingerprint})

        # Add document only to user 1
        client.post(
            "/document/add-document",
            data={"fingerprint_hash": user1_fingerprint},
            files={"image": ("doc.png", sample_image_bytes, "image/png")},
        )

        # Verify user 1 has document
        user1_response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": user1_fingerprint},
        )
        assert len(user1_response.json()["documents"]) >= 1

        # Verify user 2 has no documents
        user2_response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": user2_fingerprint},
        )
        assert len(user2_response.json()["documents"]) == 0

    def test_return_visitor_flow(self, client: TestClient, sample_image_bytes: bytes):
        """Test flow for a returning user adding more documents."""
        fingerprint = "returning-user-fingerprint"

        # Initial registration
        client.post("/identity/create", json={"fingerprint_hash": fingerprint})
        client.post(
            "/document/add-document",
            data={"fingerprint_hash": fingerprint},
            files={"image": ("initial.png", sample_image_bytes, "image/png")},
        )

        # User returns later - try to create again (idempotent)
        create_again = client.post(
            "/identity/create",
            json={"fingerprint_hash": fingerprint},
        )
        assert create_again.status_code == 200

        # Can still retrieve their data
        retrieve_response = client.post(
            "/identity/retrieve",
            json={"fingerprint_hash": fingerprint},
        )
        assert retrieve_response.status_code == 200
        assert len(retrieve_response.json()["documents"]) >= 1
