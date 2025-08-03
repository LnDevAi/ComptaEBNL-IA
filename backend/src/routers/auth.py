from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from database import get_db
from models import User, Organization, UserOrganization
from config import settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


# ============================================================================
# SCHEMAS PYDANTIC
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    country_code: str
    language: str = "fr"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    country_code: str
    language: str
    subscription_plan: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérification du mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashage du mot de passe"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Création d'un token d'accès JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    """Création d'un token de rafraîchissement"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Récupération de l'utilisateur actuel à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user


# ============================================================================
# ENDPOINTS D'AUTHENTIFICATION
# ============================================================================

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    
    # Vérification si l'utilisateur existe déjà
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ou nom d'utilisateur déjà enregistré"
        )
    
    # Vérification du pays OHADA
    if user_data.country_code not in settings.ohada_countries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pays non supporté. Pays OHADA supportés: {', '.join(settings.ohada_countries)}"
        )
    
    # Création de l'utilisateur
    hashed_password = get_password_hash(user_data.password)
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        country_code=user_data.country_code,
        language=user_data.language
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Nouvel utilisateur enregistré: {user.email}")
    
    return user


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Connexion utilisateur"""
    
    # Recherche de l'utilisateur
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé"
        )
    
    # Création des tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Mise à jour de la dernière connexion
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"Connexion réussie pour: {user.email}")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Rafraîchissement du token d'accès"""
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    
    # Création de nouveaux tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Informations sur l'utilisateur connecté"""
    return current_user


@router.get("/organizations")
async def get_user_organizations(
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
        org = db.query(Organization).filter(Organization.id == user_org.organization_id).first()
        if org:
            organizations.append({
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "organization_type": org.organization_type.value,
                "country_code": org.country_code,
                "role": user_org.role,
                "permissions": user_org.permissions
            })
    
    return {
        "organizations": organizations,
        "total": len(organizations)
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Déconnexion (côté client, suppression du token)"""
    logger.info(f"Déconnexion de: {current_user.email}")
    return {"message": "Déconnexion réussie"}