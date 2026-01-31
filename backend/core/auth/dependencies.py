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
# Set when Clerk secret is present but JWKS URL cannot be derived (avoids retrying on every request)
_jwks_unavailable: bool = False


def get_auth_provider() -> ClerkAuthProvider | None:
    """
    Get the singleton ClerkAuthProvider instance.

    Returns:
        ClerkAuthProvider if Clerk is configured and JWKS URL is available, None otherwise.
    """
    global _auth_provider, _jwks_unavailable

    if not settings.clerk_configured:
        return None

    if _jwks_unavailable:
        return None

    if _auth_provider is None:
        # Derive JWKS URL from publishable key if not explicitly set
        jwks_url: str | None = None
        if settings.clerk_jwks_url:
            jwks_url = settings.clerk_jwks_url
        elif settings.clerk_publishable_key:
            # The publishable key is base64 encoded: pk_test_<base64> or pk_live_<base64>
            # Decode it to get the Clerk frontend API domain
            import base64

            key_parts = settings.clerk_publishable_key.replace("pk_test_", "").replace(
                "pk_live_", ""
            )
            try:
                # Add padding if needed (base64 requires length to be multiple of 4)
                padding_needed = 4 - (len(key_parts) % 4)
                if padding_needed != 4:
                    key_parts += "=" * padding_needed
                
                # Decode base64 to get domain (e.g., "first-duckling-82.clerk.accounts.dev$")
                decoded = base64.b64decode(key_parts).decode("utf-8")
                # Remove trailing $ if present
                clerk_domain = decoded.rstrip("$")
                jwks_url = f"https://{clerk_domain}/.well-known/jwks.json"
                logger.info(f"[AUTH] Derived JWKS URL: {jwks_url}")
            except Exception as e:
                logger.warning(
                    "[AUTH] Clerk JWKS URL could not be derived from publishable key: %s. "
                    "Set CLERK_JWKS_URL or fix CLERK_PUBLISHABLE_KEY. Clerk JWT validation disabled.",
                    e,
                )
                _jwks_unavailable = True
                return None
        else:
            logger.warning(
                "[AUTH] Clerk JWKS URL could not be derived. "
                "Set CLERK_JWKS_URL or CLERK_PUBLISHABLE_KEY in .env to enable Clerk JWT validation. "
                "API key auth still works if API_KEYS is set."
            )
            _jwks_unavailable = True
            return None

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

    # If Clerk is not configured (e.g. missing CLERK_PUBLISHABLE_KEY), we can't validate JWTs
    if provider is None:
        # In debug mode, accept any Bearer token as a dev user so local dev works without full Clerk setup
        if settings.debug:
            logger.debug("[AUTH] Clerk not configured; debug mode: accepting token as dev user")
            return AuthenticatedUser(
                user_id="dev",
                session_id=None,
                claims={"type": "dev", "sub": "dev"},
            )
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
