"""API routes for document management."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.core.auth import RequiredUser
from backend.core.util import get_logger
from backend.features.document.schemas import AddDocumentResponse
from backend.features.document.service import DocumentServiceDep

logger = get_logger(__name__)

router = APIRouter()


@router.post("/add-document", response_model=AddDocumentResponse)
async def add_document(
    service: DocumentServiceDep,
    user: RequiredUser,
    fingerprint_hash: str = Form(...),
    image: UploadFile = File(...),
    document_type: str | None = Form(None),
):
    """
    Add a document to an identity from an uploaded image.

    The image is processed to extract document type, ID, and metadata.
    If the document_type already exists for this identity, it will be updated.
    Returns 404 if identity not found.
    
    Supported document_type values for tailored extraction:
    - drivers_license: Driver's license (looks for 9-digit number near DL/NDL/LDL)
    - bc_services: BC Services Card (looks for 10-digit PHN)
    - passport: Passport (looks for passport number in MRZ or header)
    - health_card: Generic health card

    Requires authentication.
    """
    logger.info(f"[ROUTER] add_document called - fingerprint: {fingerprint_hash[:8]}..., file: {image.filename}, content_type: {image.content_type}, document_type: {document_type}")
    
    result = await service.add_from_image(
        fingerprint_hash=fingerprint_hash,
        image=image,
        document_type=document_type,
    )

    if not result:
        logger.warning(f"[ROUTER] Identity not found for fingerprint: {fingerprint_hash[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Identity not found. Create identity first with /identity/create",
        )

    document, extracted = result
    
    logger.info(f"[ROUTER] Document processed successfully:")
    logger.info(f"  - document.document_type: {document.document_type}")
    logger.info(f"  - document.document_id: {document.document_id}")
    logger.info(f"  - extracted.document_type: {extracted.document_type}")
    logger.info(f"  - extracted.document_id: {extracted.document_id}")
    logger.info(f"  - extracted.confidence: {extracted.confidence}")
    logger.debug(f"  - extracted.metadata: {extracted.metadata}")

    # Filter metadata to only include user-relevant fields
    raw_metadata = document.doc_metadata or {}
    user_fields = {
        "first_name", "last_name", "date_of_birth", "expiry_date", "issue_date",
        "address", "sex", "issuing_authority", "nationality", "place_of_birth",
    }
    filtered_metadata = {k: v for k, v in raw_metadata.items() if k in user_fields}

    response = AddDocumentResponse(
        fingerprint_hash=fingerprint_hash,
        document_type=document.document_type,
        id=document.document_id,
        metadata=filtered_metadata,
        confidence=extracted.confidence,
    )
    
    logger.info(f"[ROUTER] Returning response - id: {response.id}, type: {response.document_type}")
    
    return response
