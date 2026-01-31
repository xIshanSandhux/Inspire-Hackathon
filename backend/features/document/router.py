"""API routes for document management."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.core.auth import RequiredUser
from backend.features.document.schemas import AddDocumentResponse
from backend.features.document.service import DocumentServiceDep

router = APIRouter()


@router.post("/add-document", response_model=AddDocumentResponse)
async def add_document(
    service: DocumentServiceDep,
    user: RequiredUser,
    fingerprint_hash: str = Form(...),
    image: UploadFile = File(...),
):
    """
    Add a document to an identity from an uploaded image.

    The image is processed to extract document type, ID, and metadata.
    If the document_type already exists for this identity, it will be updated.
    Returns 404 if identity not found.

    Requires authentication.
    """
    result = await service.add_from_image(
        fingerprint_hash=fingerprint_hash,
        image=image,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity not found. Create identity first with /identity/create",
        )

    document, extracted = result

    return AddDocumentResponse(
        fingerprint_hash=fingerprint_hash,
        document_type=document.document_type,
        id=document.document_id,
        metadata=document.doc_metadata or {},
        confidence=extracted.confidence,
    )
