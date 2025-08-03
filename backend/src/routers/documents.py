from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.organizations import get_user_organization

router = APIRouter()

@router.get("/")
async def list_documents(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des documents"""
    organization, user_org = organization_details
    
    # TODO: Implémenter la gestion complète des documents et OCR
    return {
        "documents": [],
        "total": 0,
        "message": "Module documents et OCR en cours de développement"
    }