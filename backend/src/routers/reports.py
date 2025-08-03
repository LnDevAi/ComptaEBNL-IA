from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.organizations import get_user_organization

router = APIRouter()

@router.get("/")
async def list_reports(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des rapports disponibles"""
    organization, user_org = organization_details
    
    # TODO: Implémenter les rapports et états financiers OHADA
    return {
        "reports": [
            {"name": "bilan", "label": "Bilan"},
            {"name": "compte_resultat", "label": "Compte de résultat"},
            {"name": "flux_tresorerie", "label": "Flux de trésorerie"},
            {"name": "annexes", "label": "Annexes"}
        ],
        "message": "Module rapports OHADA en cours de développement"
    }