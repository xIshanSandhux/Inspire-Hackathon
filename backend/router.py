from fastapi import APIRouter

from backend.features.identity.router import router as identity_router
from backend.features.document.router import router as document_router

# Main router that aggregates all feature routers
router = APIRouter()

# Include feature routers
router.include_router(identity_router, prefix="/identity", tags=["identity"])
router.include_router(document_router, prefix="/document", tags=["document"])
