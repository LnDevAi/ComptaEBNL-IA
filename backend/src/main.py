import os
import logging
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from models import Base, Organization, User, PlanComptable
from database import get_db, init_db
from routers import (
    auth, organizations, plan_comptable, 
    ecritures, tiers, projets, documents, 
    reports, ai_assistant
)

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Démarrage de ComptaOHADA-IA API Server...")
    logger.info("🏛️ Plateforme de comptabilité OHADA avec IA intégrée")
    
    # Initialisation de la base de données
    await init_db()
    
    # Chargement du plan comptable SYSCEBNL
    # await load_syscebnl_plan()
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt de ComptaOHADA-IA API Server")


# Création de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.comptaohada.ai"]
)


# ============================================================================
# ROUTES PRINCIPALES
# ============================================================================

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "ComptaOHADA-IA API Server",
        "version": settings.app_version,
        "description": "Plateforme de comptabilité OHADA avec IA intégrée",
        "docs": "/docs" if settings.debug else "Documentation disponible pour les utilisateurs autorisés",
        "status": "active",
        "ohada_countries": settings.ohada_countries,
        "syscebnl_version": settings.syscebnl_version
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Vérification de l'état de santé du système"""
    try:
        # Test de connexion à la base de données
        organizations_count = db.query(Organization).count()
        users_count = db.query(User).count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "statistics": {
                "organizations": organizations_count,
                "users": users_count
            },
            "services": {
                "database": "ok",
                "ai_assistant": "ok" if settings.openai_api_key else "not_configured",
                "ocr": "ok" if settings.tesseract_path else "not_configured",
                "email": "ok" if settings.mail_username else "not_configured",
                "stripe": "ok" if settings.stripe_secret_key else "not_configured"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "status": "unhealthy",
            "error": str(e)
        })


@app.get("/info")
async def api_info():
    """Informations sur l'API"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "description": settings.description,
        "features": {
            "multi_tenant": True,
            "ai_integration": True,
            "ocr_support": True,
            "syscebnl_compliance": True,
            "ohada_standards": True,
            "subscription_plans": list(settings.subscription_plans.keys())
        },
        "supported_countries": settings.ohada_countries,
        "compliance": {
            "syscebnl": settings.syscebnl_version,
            "ohada": "2024",
            "ifrs": "partial_support"
        }
    }


# ============================================================================
# INCLUSION DES ROUTERS
# ============================================================================

# Authentification et utilisateurs
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Gestion des organisations
app.include_router(
    organizations.router,
    prefix="/api/organizations",
    tags=["Organizations"]
)

# Plan comptable SYSCEBNL
app.include_router(
    plan_comptable.router,
    prefix="/api/plan-comptable",
    tags=["Plan Comptable"]
)

# Écritures comptables
app.include_router(
    ecritures.router,
    prefix="/api/ecritures",
    tags=["Écritures Comptables"]
)

# Gestion des tiers (spécifique EBNL)
app.include_router(
    tiers.router,
    prefix="/api/tiers",
    tags=["Tiers & EBNL"]
)

# Projets et fonds affectés
app.include_router(
    projets.router,
    prefix="/api/projets",
    tags=["Projets EBNL"]
)

# Gestion documentaire et OCR
app.include_router(
    documents.router,
    prefix="/api/documents",
    tags=["Documents & OCR"]
)

# Rapports et états financiers
app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["Rapports & États Financiers"]
)

# Assistant IA
app.include_router(
    ai_assistant.router,
    prefix="/api/ai",
    tags=["Assistant IA"]
)


# ============================================================================
# GESTION DES ERREURS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'erreurs HTTP personnalisé"""
    return {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code,
        "timestamp": "2024-01-01T00:00:00Z"  # Remplacer par datetime.utcnow()
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire d'erreurs général"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": True,
        "message": "Une erreur interne s'est produite",
        "status_code": 500,
        "timestamp": "2024-01-01T00:00:00Z"  # Remplacer par datetime.utcnow()
    }


# ============================================================================
# ENDPOINTS SPÉCIAUX POUR LE DÉVELOPPEMENT
# ============================================================================

if settings.debug:
    @app.get("/debug/models")
    async def debug_models():
        """Liste tous les modèles de données (debug only)"""
        return {
            "models": [
                "User", "Organization", "UserOrganization",
                "PlanComptable", "Journal", "ExerciceComptable",
                "EcritureComptable", "LigneEcriture", "Tiers",
                "Projet", "FondsAffecte", "Cotisation", "Don",
                "Document", "AuditLog"
            ],
            "total": 14
        }
    
    @app.get("/debug/config")
    async def debug_config():
        """Configuration actuelle (debug only, données sensibles masquées)"""
        return {
            "app_name": settings.app_name,
            "debug": settings.debug,
            "database_type": "sqlite" if "sqlite" in settings.database_url else "postgresql",
            "ai_configured": bool(settings.openai_api_key),
            "email_configured": bool(settings.mail_username),
            "stripe_configured": bool(settings.stripe_secret_key),
            "upload_path": settings.upload_path,
            "max_file_size": f"{settings.max_file_size / 1024 / 1024}MB"
        }


# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("🚀 Démarrage de ComptaOHADA-IA API Server...")
    print("🏛️ Plateforme de comptabilité OHADA avec IA intégrée")
    print("🌍 Support des 17 pays de l'espace OHADA")
    print("📊 Conformité SYSCEBNL et normes OHADA")
    print("🤖 Intelligence artificielle intégrée")
    print(f"🔗 API disponible sur: http://localhost:8000")
    print(f"📚 Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
