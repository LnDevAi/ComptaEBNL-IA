from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from config import settings
from models import Base
import logging

logger = logging.getLogger(__name__)

# Configuration du moteur de base de données
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )
else:
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.debug
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialisation de la base de données"""
    try:
        logger.info("🗄️ Initialisation de la base de données...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise e


async def drop_all_tables():
    """Suppression de toutes les tables (pour les tests)"""
    if settings.debug:
        logger.warning("🗑️ Suppression de toutes les tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Toutes les tables supprimées")
    else:
        raise Exception("Suppression des tables non autorisée en production")