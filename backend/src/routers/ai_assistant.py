from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.organizations import get_user_organization

router = APIRouter()

@router.get("/")
async def ai_assistant_info(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Informations sur l'assistant IA"""
    organization, user_org = organization_details
    
    # TODO: Implémenter l'assistant IA complet
    return {
        "ai_features": [
            "OCR automatique",
            "Génération d'écritures",
            "Analyse de documents",
            "Suggestions comptables",
            "Détection d'anomalies"
        ],
        "status": "available",
        "message": "Assistant IA ComptaOHADA en cours de développement"
    }