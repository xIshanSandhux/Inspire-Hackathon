"""API routes for identity management."""

from fastapi import APIRouter, HTTPException, status

from backend.core.auth import RequiredUser
from backend.features.identity.schemas import (
    CreateIdentityRequest,
    CreateIdentityResponse,
    RetrieveRequest,
    RetrieveResponse,
)
from backend.features.identity.service import IdentityServiceDep

router = APIRouter()


@router.post("/create", response_model=CreateIdentityResponse)
def create_identity(
    request: CreateIdentityRequest,
    service: IdentityServiceDep,
    user: RequiredUser,
):
    """
    Create a new identity if it doesn't exist.

    The fingerprint_hash is encrypted before storage.
    Returns the same fingerprint_hash as provided.

    Requires authentication.
    """
    service.create(request.fingerprint_hash)
    return CreateIdentityResponse(fingerprint_hash=request.fingerprint_hash)


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_identity(
    request: RetrieveRequest,
    service: IdentityServiceDep,
    user: RequiredUser,
):
    """
    Retrieve an identity and all associated documents.

    Returns 404 if identity not found.

    Requires authentication.
    """
    result = service.retrieve_with_documents(request.fingerprint_hash)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity not found",
        )
    return result
