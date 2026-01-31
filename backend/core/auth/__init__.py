"""Authentication module for Clerk integration."""

from .client import ClerkClient
from .dependencies import (
    CurrentUser,
    RequiredUser,
    get_auth_provider,
    get_current_user,
    require_auth,
)
from .schemas import AuthenticatedUser

__all__ = [
    "AuthenticatedUser",
    "ClerkClient",
    "CurrentUser",
    "RequiredUser",
    "get_auth_provider",
    "get_current_user",
    "require_auth",
]
