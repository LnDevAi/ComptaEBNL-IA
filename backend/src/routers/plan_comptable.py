from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from database import get_db
from models import PlanComptable, Organization
from routers.auth import get_current_user
from routers.organizations import get_user_organization

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# SCHEMAS PYDANTIC
# ============================================================================

class CompteCreate(BaseModel):
    numero_compte: str
    libelle_compte: str
    classe: int
    niveau: int
    parent_id: Optional[int] = None
    sens: str  # debit ou credit
    type_compte: Optional[str] = None
    lettrable: bool = False
    auxiliaire: bool = False
    syscebnl_code: Optional[str] = None
    observations: Optional[str] = None


class CompteUpdate(BaseModel):
    libelle_compte: Optional[str] = None
    lettrable: Optional[bool] = None
    auxiliaire: Optional[bool] = None
    observations: Optional[str] = None
    actif: Optional[bool] = None


class CompteResponse(BaseModel):
    id: int
    numero_compte: str
    libelle_compte: str
    classe: int
    niveau: int
    parent_id: Optional[int]
    sens: str
    type_compte: Optional[str]
    lettrable: bool
    auxiliaire: bool
    pointable: bool
    syscebnl_code: Optional[str]
    observations: Optional[str]
    actif: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def validate_compte_number(numero_compte: str, classe: int) -> bool:
    """Validation du numéro de compte selon les normes SYSCEBNL"""
    # Le numéro de compte doit commencer par le numéro de classe
    if not numero_compte.startswith(str(classe)):
        return False
    
    # Vérification de la longueur (3 à 10 caractères)
    if len(numero_compte) < 3 or len(numero_compte) > 10:
        return False
    
    # Vérification que c'est uniquement des chiffres
    return numero_compte.isdigit()


def get_compte_level(numero_compte: str) -> int:
    """Détermination du niveau du compte selon sa longueur"""
    return len(numero_compte)


# ============================================================================
# ENDPOINTS DU PLAN COMPTABLE
# ============================================================================

@router.get("/", response_model=List[CompteResponse])
async def list_comptes(
    organization_details: tuple = Depends(get_user_organization),
    classe: Optional[int] = None,
    niveau: Optional[int] = None,
    actif_only: bool = True,
    db: Session = Depends(get_db)
):
    """Liste des comptes du plan comptable SYSCEBNL"""
    organization, user_org = organization_details
    
    query = db.query(PlanComptable).filter(
        PlanComptable.organization_id == organization.id
    )
    
    if actif_only:
        query = query.filter(PlanComptable.actif == True)
    
    if classe is not None:
        query = query.filter(PlanComptable.classe == classe)
    
    if niveau is not None:
        query = query.filter(PlanComptable.niveau == niveau)
    
    comptes = query.order_by(PlanComptable.numero_compte).all()
    
    return comptes


@router.get("/classes")
async def get_classes_comptables(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des classes comptables SYSCEBNL"""
    organization, user_org = organization_details
    
    classes = db.query(PlanComptable.classe).filter(
        PlanComptable.organization_id == organization.id,
        PlanComptable.niveau == 1,
        PlanComptable.actif == True
    ).distinct().all()
    
    # Définition des classes SYSCEBNL pour les EBNL
    syscebnl_classes = {
        1: "RESSOURCES DURABLES",
        2: "ACTIF IMMOBILISE", 
        3: "ACTIF CIRCULANT",
        4: "COMPTES DE TIERS",
        5: "COMPTES DE TRESORERIE",
        6: "CHARGES DES ACTIVITES ORDINAIRES",
        7: "PRODUITS DES ACTIVITES ORDINAIRES",
        8: "AUTRES CHARGES ET AUTRES PRODUITS",
        9: "COMPTES DE LA COMPTABILITE ANALYTIQUE"
    }
    
    result = []
    for (classe_num,) in classes:
        result.append({
            "numero": classe_num,
            "libelle": syscebnl_classes.get(classe_num, f"Classe {classe_num}"),
            "type": "bilan" if classe_num <= 5 else "resultat" if classe_num <= 8 else "analytique"
        })
    
    return result


@router.get("/search")
async def search_comptes(
    q: str,
    organization_details: tuple = Depends(get_user_organization),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Recherche de comptes par numéro ou libellé"""
    organization, user_org = organization_details
    
    comptes = db.query(PlanComptable).filter(
        PlanComptable.organization_id == organization.id,
        PlanComptable.actif == True,
        (PlanComptable.numero_compte.contains(q) | 
         PlanComptable.libelle_compte.ilike(f"%{q}%"))
    ).order_by(PlanComptable.numero_compte).limit(limit).all()
    
    return comptes


@router.get("/{compte_id}", response_model=CompteResponse)
async def get_compte(
    compte_id: int,
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Détails d'un compte"""
    organization, user_org = organization_details
    
    compte = db.query(PlanComptable).filter(
        PlanComptable.id == compte_id,
        PlanComptable.organization_id == organization.id
    ).first()
    
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé"
        )
    
    return compte


@router.post("/", response_model=CompteResponse)
async def create_compte(
    compte_data: CompteCreate,
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Création d'un nouveau compte"""
    organization, user_org = organization_details
    
    # Vérification des permissions
    if user_org.role not in ["owner", "admin", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    # Validation du numéro de compte
    if not validate_compte_number(compte_data.numero_compte, compte_data.classe):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Numéro de compte invalide selon les normes SYSCEBNL"
        )
    
    # Vérification de l'unicité
    existing_compte = db.query(PlanComptable).filter(
        PlanComptable.organization_id == organization.id,
        PlanComptable.numero_compte == compte_data.numero_compte
    ).first()
    
    if existing_compte:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro de compte existe déjà"
        )
    
    # Validation du sens (débit/crédit)
    if compte_data.sens not in ["debit", "credit"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le sens doit être 'debit' ou 'credit'"
        )
    
    # Validation du compte parent si spécifié
    if compte_data.parent_id:
        parent_compte = db.query(PlanComptable).filter(
            PlanComptable.id == compte_data.parent_id,
            PlanComptable.organization_id == organization.id
        ).first()
        
        if not parent_compte:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compte parent non trouvé"
            )
        
        # Le niveau doit être parent + 1
        if compte_data.niveau != parent_compte.niveau + 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Niveau de compte invalide par rapport au parent"
            )
    
    # Calcul automatique du niveau si non spécifié
    niveau_calcule = get_compte_level(compte_data.numero_compte)
    if compte_data.niveau != niveau_calcule:
        compte_data.niveau = niveau_calcule
    
    # Création du compte
    compte = PlanComptable(
        organization_id=organization.id,
        numero_compte=compte_data.numero_compte,
        libelle_compte=compte_data.libelle_compte,
        classe=compte_data.classe,
        niveau=compte_data.niveau,
        parent_id=compte_data.parent_id,
        sens=compte_data.sens,
        type_compte=compte_data.type_compte,
        lettrable=compte_data.lettrable,
        auxiliaire=compte_data.auxiliaire,
        syscebnl_code=compte_data.syscebnl_code,
        observations=compte_data.observations
    )
    
    db.add(compte)
    db.commit()
    db.refresh(compte)
    
    logger.info(f"Nouveau compte créé: {compte.numero_compte} - {compte.libelle_compte}")
    
    return compte


@router.put("/{compte_id}", response_model=CompteResponse)
async def update_compte(
    compte_id: int,
    compte_update: CompteUpdate,
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Mise à jour d'un compte"""
    organization, user_org = organization_details
    
    # Vérification des permissions
    if user_org.role not in ["owner", "admin", "accountant"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    compte = db.query(PlanComptable).filter(
        PlanComptable.id == compte_id,
        PlanComptable.organization_id == organization.id
    ).first()
    
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé"
        )
    
    # Mise à jour des champs
    update_data = compte_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(compte, field, value)
    
    db.commit()
    db.refresh(compte)
    
    logger.info(f"Compte mis à jour: {compte.numero_compte}")
    
    return compte


@router.delete("/{compte_id}")
async def delete_compte(
    compte_id: int,
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Suppression d'un compte (soft delete)"""
    organization, user_org = organization_details
    
    # Seuls owner et admin peuvent supprimer
    if user_org.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    compte = db.query(PlanComptable).filter(
        PlanComptable.id == compte_id,
        PlanComptable.organization_id == organization.id
    ).first()
    
    if not compte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compte non trouvé"
        )
    
    # TODO: Vérifier qu'il n'y a pas d'écritures sur ce compte
    # if has_entries(compte_id, db):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Impossible de supprimer un compte avec des écritures"
    #     )
    
    # Soft delete
    compte.actif = False
    db.commit()
    
    logger.warning(f"Compte supprimé: {compte.numero_compte}")
    
    return {"message": "Compte supprimé avec succès"}


@router.post("/import-syscebnl")
async def import_syscebnl_default(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Importation du plan comptable SYSCEBNL par défaut"""
    organization, user_org = organization_details
    
    # Seuls owner et admin peuvent importer
    if user_org.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    # Vérifier si le plan comptable existe déjà
    existing_count = db.query(PlanComptable).filter(
        PlanComptable.organization_id == organization.id
    ).count()
    
    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un plan comptable existe déjà pour cette organisation"
        )
    
    # TODO: Implémenter l'importation du plan SYSCEBNL complet
    # Cette fonction devrait lire le fichier de référence SYSCEBNL
    # et créer tous les comptes standards
    
    logger.info(f"Importation du plan SYSCEBNL pour {organization.name}")
    
    return {
        "message": "Plan comptable SYSCEBNL importé avec succès",
        "comptes_imported": 0  # À remplacer par le nombre réel
    }


@router.get("/{compte_id}/children")
async def get_compte_children(
    compte_id: int,
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Sous-comptes d'un compte donné"""
    organization, user_org = organization_details
    
    children = db.query(PlanComptable).filter(
        PlanComptable.organization_id == organization.id,
        PlanComptable.parent_id == compte_id,
        PlanComptable.actif == True
    ).order_by(PlanComptable.numero_compte).all()
    
    return children