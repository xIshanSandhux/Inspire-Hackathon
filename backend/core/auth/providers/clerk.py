"""Clerk authentication provider implementation using the official SDK."""

from typing import Any

import jwt
from clerk_backend_api import Clerk
from jwt import PyJWKClient

from .base import AuthProvider

# Handle different versions of clerk_backend_api SDK
try:
    from clerk_backend_api.models import errors as clerk_errors

    ClerkSDKError = clerk_errors.SDKError
except ImportError:
    try:
        from clerk_backend_api import errors as clerk_errors

        ClerkSDKError = clerk_errors.SDKError
    except (ImportError, AttributeError):
        # Fallback to generic Exception if SDK errors not available
        ClerkSDKError = Exception  # type: ignore


class ClerkAuthProvider(AuthProvider):
    """
    Clerk authentication provider using JWKS for JWT validation.

    This provider validates Clerk JWTs by fetching public keys from
    Clerk's JWKS endpoint and verifying token signatures.
    Uses the official Clerk SDK for user operations.
    """

    def __init__(self, secret_key: str, jwks_url: str):
        """
        Initialize the Clerk auth provider.

        Args:
            secret_key: Clerk secret key for API calls.
            jwks_url: URL to Clerk's JWKS endpoint for JWT validation.
        """
        self.secret_key = secret_key
        self.jwks_url = jwks_url
        self._jwk_client = PyJWKClient(jwks_url, cache_keys=True)
        self._clerk = Clerk(bearer_auth=secret_key)

    async def validate_token(self, token: str) -> dict[str, Any] | None:
        """
        Validate a Clerk JWT token using JWKS.

        Note: JWT validation still uses PyJWT with JWKS as the Clerk SDK
        doesn't provide direct JWT validation - it expects you to use
        their frontend SDKs or validate JWTs yourself.

        Args:
            token: The JWT token to validate (without Bearer prefix).

        Returns:
            Dictionary with user_id, session_id, and claims if valid,
            or None if invalid.
        """
        try:
            # Get the signing key from JWKS
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)

            # Decode and validate the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_aud": False,  # Clerk doesn't always set audience
                    "verify_exp": True,
                    "verify_iat": True,
                },
            )

            return {
                "user_id": payload.get("sub"),
                "session_id": payload.get("sid"),
                "claims": payload,
            }
        except jwt.exceptions.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.exceptions.InvalidTokenError:
            # Invalid token (bad signature, malformed, etc.)
            return None
        except Exception:
            # Any other error during validation
            return None

    async def get_user_info(self, user_id: str) -> dict[str, Any] | None:
        """
        Fetch user details from Clerk by user ID using the SDK.

        Args:
            user_id: The Clerk user ID.

        Returns:
            User details dictionary, or None if not found.
        """
        try:
            user = await self._clerk.users.get_async(user_id=user_id)
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
        except ClerkSDKError:
            return None
