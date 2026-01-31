"""Clerk API client for backend operations using the official SDK."""

from typing import Any

from clerk_backend_api import Clerk
from clerk_backend_api.models import errors as clerk_errors


class ClerkClient:
    """
    Client for Clerk Backend API operations using the official SDK.

    Handles API calls to Clerk for creating users, M2M tokens,
    and other backend operations that require the secret key.
    """

    def __init__(self, secret_key: str):
        """
        Initialize the Clerk client.

        Args:
            secret_key: Clerk secret key (sk_test_xxx or sk_live_xxx).
        """
        self.secret_key = secret_key
        self._client = Clerk(bearer_auth=secret_key)

    async def create_m2m_token(
        self,
        seconds_until_expiration: int = 31536000,
        claims: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create an M2M token via Clerk SDK.

        Args:
            seconds_until_expiration: Token expiration in seconds.
                                      Default is 365 days (31536000 seconds).
            claims: Optional additional custom claims for the token.

        Returns:
            Dictionary containing the token and metadata.

        Raises:
            clerk_errors.SDKError: If the API request fails.
        """
        result = await self._client.m2m_tokens.create_async(
            seconds_until_expiration=seconds_until_expiration,
            claims=claims,
        )

        # Convert SDK response to dict
        return {
            "token": result.token if hasattr(result, "token") else str(result),
            "expires_at": getattr(result, "expires_at", None),
        }

    async def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        public_metadata: dict[str, Any] | None = None,
        private_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a Clerk user via the SDK.

        Args:
            email: User's email address.
            password: User's password (min 8 characters).
            first_name: User's first name.
            last_name: User's last name.
            public_metadata: Public metadata (readable from frontend).
            private_metadata: Private metadata (backend only).

        Returns:
            Dictionary containing the created user data.

        Raises:
            clerk_errors.SDKError: If the API request fails.
        """
        user = await self._client.users.create_async(
            email_address=[email],
            password=password,
            first_name=first_name,
            last_name=last_name,
            public_metadata=public_metadata or {},
            private_metadata=private_metadata or {},
        )

        # Convert SDK User object to dict for consistent response
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email_addresses": [
                {"email_address": ea.email_address} for ea in (user.email_addresses or [])
            ],
            "public_metadata": user.public_metadata or {},
            "private_metadata": user.private_metadata or {},
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """
        Get a user by ID from Clerk.

        Args:
            user_id: The Clerk user ID.

        Returns:
            User data dictionary, or None if not found.
        """
        try:
            user = await self._client.users.get_async(user_id=user_id)
            return {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email_addresses": [
                    {"email_address": ea.email_address}
                    for ea in (user.email_addresses or [])
                ],
                "public_metadata": user.public_metadata or {},
                "private_metadata": user.private_metadata or {},
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
        except clerk_errors.SDKError:
            return None

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user from Clerk.

        Args:
            user_id: The Clerk user ID.

        Returns:
            True if deleted successfully, False otherwise.
        """
        try:
            await self._client.users.delete_async(user_id=user_id)
            return True
        except clerk_errors.SDKError:
            return False
