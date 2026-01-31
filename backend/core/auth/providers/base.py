"""Abstract base class for authentication providers."""

from abc import ABC, abstractmethod
from typing import Any


class AuthProvider(ABC):
    """
    Abstract base for authentication providers (Clerk, Auth0, Firebase, etc.).

    This allows for easy swapping or adding of authentication providers
    in the future without changing the core authentication logic.
    """

    @abstractmethod
    async def validate_token(self, token: str) -> dict[str, Any] | None:
        """
        Validate a JWT token and return user info or None if invalid.

        Args:
            token: The JWT token to validate (without Bearer prefix).

        Returns:
            A dictionary containing user_id, session_id, and claims if valid,
            or None if the token is invalid.
        """
        pass

    @abstractmethod
    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        """
        Fetch user details by ID from the auth provider.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            A dictionary containing user details, or None if not found.
        """
        pass
