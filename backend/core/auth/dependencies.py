"""FastAPI dependencies for authentication."""

import base64
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from backend.core.auth.providers.clerk import ClerkAuthProvider
from backend.core.auth.schemas import AuthenticatedUser
from backend.core.config import settings
from backend.core.util import get_logger

logger = get_logger(__name__)

# Singleton provider instance (lazily initialized)
_auth_provider: ClerkAuthProvider | None = None


def _decode_clerk_publishable_key(publishable_key: str) -> str:
    """
    Decode Clerk publishable key to extract the frontend API domain.
    
    Clerk publishable keys are formatted as: pk_test_<base64> or pk_live_<base64>
    The base64 portion decodes to the Clerk domain (e.g., "example.clerk.accounts.dev$")
    
    Args:
        publishable_key: The full Clerk publishable key.
        
    Returns:
        The Clerk frontend API domain.
        
    Raises:
        ValueError: If the key cannot be decoded.
    """
    # Remove prefix
    key_parts = publishable_key.replace("pk_test_", "").replace("pk_live_", "")
    
    # Add padding if needed (base64 requires length to be multiple of 4)
    padding_needed = 4 - (len(key_parts) % 4)
    if padding_needed != 4:
        key_parts += "=" * padding_needed
    
    # Decode and clean up
    decoded = base64.b64decode(key_parts).decode("utf-8")
    return decoded.rstrip("$")


def get_auth_provider() -> ClerkAuthProvider | None:
    """
    Get the singleton ClerkAuthProvider instance.

    Returns:
        ClerkAuthProvider if Clerk is configured, None otherwise.
    """
    global _auth_provider

    if not settings.clerk_configured:
        return None

    if _auth_provider is None:
        # Derive JWKS URL from publishable key if not explicitly set
        if settings.clerk_jwks_url:
            jwks_url = settings.clerk_jwks_url
        elif settings.clerk_publishable_key:
            try:
                clerk_domain = _decode_clerk_publishable_key(settings.clerk_publishable_key)
                jwks_url = f"https://{clerk_domain}/.well-known/jwks.json"
                logger.info(f"[AUTH] Derived JWKS URL: {jwks_url}")
            except Exception as e:
                logger.error(f"[AUTH] Failed to decode publishable key: {e}")
                raise RuntimeError(
                    "Clerk JWKS URL could not be derived from publishable key. "
                    "Set CLERK_JWKS_URL explicitly."
                )
        else:
            raise RuntimeError(
                "Clerk JWKS URL could not be derived. "
                "Set CLERK_JWKS_URL or CLERK_PUBLISHABLE_KEY."
            )

        _auth_provider = ClerkAuthProvider(
            secret_key=settings.clerk_secret_key,  # type: ignore
            jwks_url=jwks_url,
        )

    return _auth_provider


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser | None:
    """
    FastAPI dependency to get the current authenticated user.

    This is an optional auth dependency - returns None if no token
    is provided or if Clerk is not configured.

    Supports both:
    - Clerk JWT tokens (validated via JWKS)
    - Static API keys (configured via API_KEYS env var)

    Args:
        authorization: The Authorization header value.

    Returns:
        AuthenticatedUser if valid token, None otherwise.
    """
    # No authorization header provided
    if not authorization or not authorization.startswith("Bearer "):
        logger.debug("[AUTH] No bearer token in authorization header")
        return None

    # Extract the token
    token = authorization.replace("Bearer ", "")

    # Check if it's a static API key first (for M2M / service dashboard auth)
    if token in settings.api_keys_list:
        logger.debug("[AUTH] API key matched - returning service user")
        # Return a service user for API key auth
        return AuthenticatedUser(
            user_id="service",
            session_id=None,
            claims={"type": "api_key"},
        )

    # Try Clerk JWT validation
    provider = get_auth_provider()

    # If Clerk is not configured, allow unauthenticated access
    if provider is None:
        logger.debug("[AUTH] Clerk not configured, returning None")
        return None

    # Validate as JWT
    logger.debug("[AUTH] Attempting Clerk JWT validation")
    user_info = await provider.validate_token(token)

    if user_info:
        logger.debug(f"[AUTH] JWT validated successfully for user: {user_info.get('user_id')}")
        return AuthenticatedUser(**user_info)

    logger.debug("[AUTH] JWT validation failed")
    return None


async def require_auth(
    user: Annotated[AuthenticatedUser | None, Depends(get_current_user)],
) -> AuthenticatedUser:
    """
    FastAPI dependency that requires authentication.

    Raises HTTPException 401 if not authenticated.
    Supports both:
    - Clerk JWT tokens (for gov/admin dashboards)
    - Static API keys (for service dashboard M2M auth)
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Type aliases for clean dependency injection
CurrentUser = Annotated[AuthenticatedUser | None, Depends(get_current_user)]
RequiredUser = Annotated[AuthenticatedUser, Depends(require_auth)]
