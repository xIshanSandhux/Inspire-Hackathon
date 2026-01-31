"""Auth-related Pydantic models for authentication."""

from typing import Any

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """Represents an authenticated user from JWT validation."""

    user_id: str
    session_id: str | None = None
    claims: dict[str, Any] = {}

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return bool(self.user_id)
