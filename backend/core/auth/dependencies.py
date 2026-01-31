"""FastAPI dependencies for authentication."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from backend.core.auth.providers.clerk import ClerkAuthProvider
from backend.core.auth.schemas import AuthenticatedUser
from backend.core.config import settings
from backend.core.util import get_logger

logger = get_logger(__name__)

# Singleton provider instance (lazily initialized)
_auth_provider: ClerkAuthProvider | None = None


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
            # Extract the instance ID from the publishable key
            # pk_test_xxx or pk_live_xxx -> xxx.clerk.accounts.dev
            key_parts = settings.clerk_publishable_key.replace("pk_test_", "").replace(
                "pk_live_", ""
            )
            jwks_url = f"https://{key_parts}.clerk.accounts.dev/.well-known/jwks.json"
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
        logger.debug(f"[AUTH] No bearer token in authorization header")
        return None

    # Extract the token
    token = authorization.replace("Bearer ", "")
    
    # Debug: show what we're checking
    logger.info(f"[AUTH] Token received: {token[:20]}...")
    logger.info(f"[AUTH] API keys configured: {settings.api_keys_list}")
    logger.info(f"[AUTH] Token in api_keys_list: {token in settings.api_keys_list}")

    # Check if it's a static API key first
    if token in settings.api_keys_list:
        logger.info(f"[AUTH] API key matched! Returning service user")
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
        return None

    # Validate as JWT
    user_info = await provider.validate_token(token)

    if user_info:
        return AuthenticatedUser(**user_info)

    return None


async def require_auth(
    user: Annotated[AuthenticatedUser | None, Depends(get_current_user)],
) -> AuthenticatedUser:
    """
    FastAPI dependency that requires authentication.

    Raises 401 Unauthorized if user is not authenticated.

    Args:
        user: The current user from get_current_user dependency.

    Returns:
        AuthenticatedUser if authenticated.

    Raises:
        HTTPException: 401 if not authenticated.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Type aliases for clean dependency injection
CurrentUser = Annotated[AuthenticatedUser | None, Depends(get_current_user)]
RequiredUser = Annotated[AuthenticatedUser, Depends(require_auth)]
