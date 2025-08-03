from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.organizations import get_user_organization

router = APIRouter()

@router.get("/")
async def list_tiers(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des tiers (adhérents, donateurs, etc.)"""
    organization, user_org = organization_details
    
    # TODO: Implémenter la gestion complète des tiers
    return {
        "tiers": [],
        "total": 0,
        "message": "Module tiers EBNL en cours de développement"
    }