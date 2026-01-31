"""API routes for Clerk authentication proxy endpoints."""

from fastapi import APIRouter, HTTPException, status

from backend.core.auth.client import ClerkClient, ClerkSDKError
from backend.core.auth.dependencies import CurrentUser
from backend.core.config import settings

from .schemas import (
    CreateM2MTokenResponse,
    CreateUserRequest,
    CreateUserResponse,
    ValidateTokenResponse,
)

router = APIRouter()


def get_clerk_client() -> ClerkClient:
    """
    Get a ClerkClient instance.

    Raises:
        HTTPException: 503 if Clerk is not configured.
    """
    if not settings.clerk_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clerk authentication is not configured",
        )
    return ClerkClient(settings.clerk_secret_key)  # type: ignore


@router.post("/create-m2m", response_model=CreateM2MTokenResponse)
async def create_m2m_token():
    """
    Create an M2M (machine-to-machine) token via Clerk.

    This endpoint proxies the request to Clerk's Backend API using the
    server's secret key, creating a token with 365-day expiration.

    This is a backend-only endpoint secured by the server's Clerk secret.

    Returns:
        CreateM2MTokenResponse: The created token and expiration info.
    """
    client = get_clerk_client()

    try:
        # 365 days in seconds = 31536000
        result = await client.create_m2m_token(seconds_until_expiration=31536000)

        return CreateM2MTokenResponse(
            token=result.get("token", ""),
            expires_at=result.get("expires_at"),
        )
    except ClerkSDKError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Clerk API error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create M2M token: {str(e)}",
        )


@router.post("/create-user", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest):
    """
    Create a Clerk user with role metadata.

    This endpoint proxies the request to Clerk's Backend API using the
    server's secret key to create a new user with the specified role.

    This is a backend-only endpoint secured by the server's Clerk secret.

    Args:
        request: User creation request with name, email, password, and role.

    Returns:
        CreateUserResponse: The created user's info including ID and metadata.
    """
    client = get_clerk_client()

    try:
        result = await client.create_user(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            public_metadata={"role": request.role.value},
        )

        # Extract email from the response
        email_addresses = result.get("email_addresses", [])
        email = email_addresses[0]["email_address"] if email_addresses else request.email

        return CreateUserResponse(
            id=result["id"],
            email=email,
            first_name=result.get("first_name"),
            last_name=result.get("last_name"),
            public_metadata=result.get("public_metadata", {}),
        )
    except ClerkSDKError as e:
        # Forward Clerk's error response
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Clerk API error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.get("/validate", response_model=ValidateTokenResponse)
async def validate_token(user: CurrentUser):
    """
    Validate the current authentication token.

    This endpoint checks if the provided Bearer token is valid.
    Supports both API keys (for service providers) and Clerk JWTs.

    Returns:
        ValidateTokenResponse: Whether the token is valid and its type.
    """
    if user is None:
        return ValidateTokenResponse(valid=False, user_type=None)
    
    # Determine user type from claims
    user_type = "service" if user.claims.get("type") == "api_key" else "user"
    
    return ValidateTokenResponse(valid=True, user_type=user_type)
