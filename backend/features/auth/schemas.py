"""Request/response schemas for auth endpoints."""

from enum import Enum

from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    """User role for public_metadata."""

    GOV = "gov"
    ADMIN = "admin"


class CreateUserRequest(BaseModel):
    """Request body for creating a Clerk user."""

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: Role


class CreateUserResponse(BaseModel):
    """Response from creating a Clerk user."""

    id: str
    email: str
    first_name: str | None
    last_name: str | None
    public_metadata: dict


class CreateM2MTokenResponse(BaseModel):
    """Response from creating an M2M token."""

    token: str
    expires_at: str | None
