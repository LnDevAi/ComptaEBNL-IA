from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.organizations import get_user_organization

router = APIRouter()

@router.get("/")
async def list_ecritures(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des écritures comptables"""
    organization, user_org = organization_details
    
    # TODO: Implémenter la liste complète des écritures
    return {
        "ecritures": [],
        "total": 0,
        "message": "Module écritures comptables en cours de développement"
    }