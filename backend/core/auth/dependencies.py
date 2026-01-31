from typing import Annotated

from fastapi import Header


async def get_current_identity(
    authorization: Annotated[str | None, Header()] = None,
) -> dict | None:
    """
    FastAPI dependency to get the current authenticated identity.

    TODO: Implement Clerk JWT validation when auth is needed.
    For now, returns None (no auth).
    """
    # No auth yet - just return None or a placeholder
    if authorization is None:
        return None

    # TODO: Validate JWT token with Clerk
    # token = authorization.replace("Bearer ", "")
    # return verify_clerk_token(token)

    return {"placeholder": True}


# Type alias for dependency injection
CurrentIdentity = Annotated[dict | None, Header()]
