from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.organizations import get_user_organization

router = APIRouter()

@router.get("/")
async def list_projets(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des projets et fonds affectés"""
    organization, user_org = organization_details
    
    # TODO: Implémenter la gestion complète des projets
    return {
        "projets": [],
        "total": 0,
        "message": "Module projets EBNL en cours de développement"
    }