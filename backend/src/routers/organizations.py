from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import re
import logging

from database import get_db
from models import Organization, User, UserOrganization, OrganizationTypeEnum
from routers.auth import get_current_user
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# SCHEMAS PYDANTIC
# ============================================================================

class OrganizationCreate(BaseModel):
    name: str
    organization_type: str
    country_code: str
    registration_number: Optional[str] = None
    tax_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    currency: str = "XOF"


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    registration_number: Optional[str] = None
    tax_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    organization_type: str
    country_code: str
    registration_number: Optional[str]
    tax_number: Optional[str]
    address_line1: Optional[str]
    city: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    currency: str
    is_active: bool
    
    class Config:
        from_attributes = True


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def generate_slug(name: str) -> str:
    """Génération d'un slug unique pour l'organisation"""
    # Conversion en minuscules et remplacement des caractères spéciaux
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')
    return slug[:50]  # Limiter à 50 caractères


def check_organization_limit(user: User, db: Session) -> bool:
    """Vérification de la limite d'organisations selon le plan d'abonnement"""
    plan = settings.subscription_plans.get(user.subscription_plan.value)
    if not plan:
        return False
    
    max_orgs = plan.get("max_organizations", 1)
    if max_orgs == -1:  # Illimité
        return True
    
    current_count = db.query(UserOrganization).filter(
        UserOrganization.user_id == user.id,
        UserOrganization.is_active == True
    ).count()
    
    return current_count < max_orgs


async def get_user_organization(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> tuple[Organization, UserOrganization]:
    """Récupération d'une organisation avec vérification des droits d'accès"""
    
    user_org = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == organization_id,
        UserOrganization.is_active == True
    ).first()
    
    if not user_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé à cette organisation"
        )
    
    organization = db.query(Organization).filter(
        Organization.id == organization_id,
        Organization.is_active == True
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation non trouvée"
        )
    
    return organization, user_org


# ============================================================================
# ENDPOINTS DES ORGANISATIONS
# ============================================================================

@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Création d'une nouvelle organisation"""
    
    # Vérification de la limite d'organisations
    if not check_organization_limit(current_user, db):
        plan = settings.subscription_plans.get(current_user.subscription_plan.value)
        max_orgs = plan.get("max_organizations", 1) if plan else 1
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Limite d'organisations atteinte ({max_orgs}). Veuillez upgrader votre abonnement."
        )
    
    # Vérification du pays OHADA
    if org_data.country_code not in settings.ohada_countries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pays non supporté. Pays OHADA supportés: {', '.join(settings.ohada_countries)}"
        )
    
    # Vérification du type d'organisation
    try:
        org_type = OrganizationTypeEnum(org_data.organization_type)
    except ValueError:
        valid_types = [e.value for e in OrganizationTypeEnum]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type d'organisation invalide. Types valides: {', '.join(valid_types)}"
        )
    
    # Génération du slug unique
    base_slug = generate_slug(org_data.name)
    slug = base_slug
    counter = 1
    
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Création de l'organisation
    organization = Organization(
        name=org_data.name,
        slug=slug,
        organization_type=org_type,
        country_code=org_data.country_code,
        registration_number=org_data.registration_number,
        tax_number=org_data.tax_number,
        address_line1=org_data.address_line1,
        address_line2=org_data.address_line2,
        city=org_data.city,
        postal_code=org_data.postal_code,
        email=org_data.email,
        phone=org_data.phone,
        website=org_data.website,
        currency=org_data.currency
    )
    
    db.add(organization)
    db.flush()  # Pour obtenir l'ID de l'organisation
    
    # Association de l'utilisateur comme propriétaire
    user_org = UserOrganization(
        user_id=current_user.id,
        organization_id=organization.id,
        role="owner",
        permissions={"all": True}
    )
    
    db.add(user_org)
    db.commit()
    db.refresh(organization)
    
    logger.info(f"Nouvelle organisation créée: {organization.name} par {current_user.email}")
    
    return organization


@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Liste des organisations de l'utilisateur"""
    
    user_orgs = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.is_active == True
    ).all()
    
    organizations = []
    for user_org in user_orgs:
        org = db.query(Organization).filter(
            Organization.id == user_org.organization_id,
            Organization.is_active == True
        ).first()
        if org:
            organizations.append(org)
    
    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_details: tuple = Depends(get_user_organization)
):
    """Détails d'une organisation"""
    organization, user_org = organization_details
    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    org_update: OrganizationUpdate,
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Mise à jour d'une organisation"""
    organization, user_org = organization_details
    
    # Vérification des permissions (seuls owner et admin peuvent modifier)
    if user_org.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour modifier cette organisation"
        )
    
    # Mise à jour des champs
    update_data = org_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    db.commit()
    db.refresh(organization)
    
    logger.info(f"Organisation mise à jour: {organization.name}")
    
    return organization


@router.delete("/{organization_id}")
async def delete_organization(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Suppression d'une organisation (soft delete)"""
    organization, user_org = organization_details
    
    # Seul le propriétaire peut supprimer l'organisation
    if user_org.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le propriétaire peut supprimer cette organisation"
        )
    
    # Soft delete
    organization.is_active = False
    db.commit()
    
    logger.warning(f"Organisation supprimée: {organization.name}")
    
    return {"message": "Organisation supprimée avec succès"}


@router.get("/{organization_id}/users")
async def list_organization_users(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Liste des utilisateurs d'une organisation"""
    organization, user_org = organization_details
    
    # Vérification des permissions
    if user_org.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    
    user_orgs = db.query(UserOrganization).filter(
        UserOrganization.organization_id == organization.id,
        UserOrganization.is_active == True
    ).all()
    
    users = []
    for uo in user_orgs:
        user = db.query(User).filter(User.id == uo.user_id).first()
        if user:
            users.append({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": uo.role,
                "permissions": uo.permissions,
                "created_at": uo.created_at
            })
    
    return {"users": users, "total": len(users)}


@router.get("/{organization_id}/stats")
async def get_organization_stats(
    organization_details: tuple = Depends(get_user_organization),
    db: Session = Depends(get_db)
):
    """Statistiques de l'organisation"""
    organization, user_org = organization_details
    
    # TODO: Implémenter les statistiques réelles
    # Compter les écritures, tiers, projets, etc.
    
    return {
        "organization": {
            "name": organization.name,
            "type": organization.organization_type.value,
            "country": organization.country_code,
            "currency": organization.currency
        },
        "statistics": {
            "total_entries": 0,  # À implémenter
            "total_tiers": 0,    # À implémenter
            "total_projects": 0, # À implémenter
            "current_fiscal_year": 2024  # À calculer
        },
        "subscription": {
            "plan": user_org.user.subscription_plan.value,
            "features": settings.subscription_plans.get(
                user_org.user.subscription_plan.value, {}
            ).get("features", [])
        }
    }