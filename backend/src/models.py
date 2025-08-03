from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    Numeric, ForeignKey, Date, JSON, Enum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum


Base = declarative_base()


class SubscriptionPlanEnum(enum.Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class OrganizationTypeEnum(enum.Enum):
    ASSOCIATION = "association"
    FONDATION = "fondation"
    ONG = "ong"
    COOPERATIVE = "cooperative"
    AUTRE = "autre"


class JournalTypeEnum(enum.Enum):
    VENTES = "ventes"
    ACHATS = "achats"
    TRESORERIE = "tresorerie"
    OPERATIONS_DIVERSES = "operations_diverses"


class EcritureTypeEnum(enum.Enum):
    STANDARD = "standard"
    OUVERTURE = "ouverture"
    CLOTURE = "cloture"
    A_NOUVEAU = "a_nouveau"
    REGULARISATION = "regularisation"


class FileTypeEnum(enum.Enum):
    FACTURE = "facture"
    RECU = "recu"
    JUSTIFICATIF = "justificatif"
    RELEVE_BANCAIRE = "releve_bancaire"
    AUTRE = "autre"


# ============================================================================
# GESTION DES UTILISATEURS ET ORGANISATIONS
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    phone = Column(String(20))
    country_code = Column(String(2))  # Code pays OHADA
    language = Column(String(5), default="fr")
    timezone = Column(String(50), default="UTC")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Subscription
    subscription_plan = Column(Enum(SubscriptionPlanEnum), default=SubscriptionPlanEnum.STARTER)
    subscription_end_date = Column(DateTime)
    stripe_customer_id = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    organizations = relationship("UserOrganization", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    
    # Organization details
    organization_type = Column(Enum(OrganizationTypeEnum), nullable=False)
    registration_number = Column(String(100))
    tax_number = Column(String(100))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20))
    country_code = Column(String(2), nullable=False)  # Pays OHADA
    
    # Contact
    email = Column(String(255))
    phone = Column(String(20))
    website = Column(String(255))
    
    # Fiscal year
    fiscal_year_start = Column(Integer, default=1)  # 1 = Janvier
    fiscal_year_end = Column(Integer, default=12)   # 12 = Décembre
    
    # Currency and locale
    currency = Column(String(3), default="XOF")  # FCFA par défaut
    locale = Column(String(5), default="fr_FR")
    
    # Configuration
    settings = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("UserOrganization", back_populates="organization")
    plan_comptable = relationship("PlanComptable", back_populates="organization")
    journaux = relationship("Journal", back_populates="organization")
    exercices = relationship("ExerciceComptable", back_populates="organization")


class UserOrganization(Base):
    __tablename__ = "user_organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Role dans l'organisation
    role = Column(String(50), default="user")  # owner, admin, accountant, user
    
    # Permissions
    permissions = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="organizations")
    organization = relationship("Organization", back_populates="users")
    
    # Unique constraint
    __table_args__ = (Index("idx_user_org", "user_id", "organization_id", unique=True),)


# ============================================================================
# PLAN COMPTABLE SYSCEBNL/OHADA
# ============================================================================

class PlanComptable(Base):
    __tablename__ = "plan_comptable"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Identifiant du compte
    numero_compte = Column(String(10), nullable=False, index=True)
    libelle_compte = Column(String(255), nullable=False)
    
    # Hiérarchie
    classe = Column(Integer, nullable=False, index=True)
    niveau = Column(Integer, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("plan_comptable.id"))
    
    # Caractéristiques du compte
    sens = Column(String(10), nullable=False)  # debit, credit
    type_compte = Column(String(50))  # bilan, resultat, hors_bilan
    
    # Configuration
    lettrable = Column(Boolean, default=False)
    auxiliaire = Column(Boolean, default=False)
    pointable = Column(Boolean, default=True)
    
    # SYSCEBNL specific
    syscebnl_code = Column(String(10))
    observations = Column(Text)
    
    # Status
    actif = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="plan_comptable")
    parent = relationship("PlanComptable", remote_side=[id])
    enfants = relationship("PlanComptable")
    ecritures_debit = relationship("LigneEcriture", foreign_keys="LigneEcriture.compte_debit_id", back_populates="compte_debit")
    ecritures_credit = relationship("LigneEcriture", foreign_keys="LigneEcriture.compte_credit_id", back_populates="compte_credit")
    
    # Unique constraint per organization
    __table_args__ = (Index("idx_org_compte", "organization_id", "numero_compte", unique=True),)


# ============================================================================
# JOURNAUX COMPTABLES
# ============================================================================

class Journal(Base):
    __tablename__ = "journaux"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Identifiant du journal
    code = Column(String(10), nullable=False)
    libelle = Column(String(255), nullable=False)
    type_journal = Column(Enum(JournalTypeEnum), nullable=False)
    
    # Configuration
    compte_contrepartie_id = Column(Integer, ForeignKey("plan_comptable.id"))
    numerotation_auto = Column(Boolean, default=True)
    prefixe = Column(String(10))
    
    # Status
    actif = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="journaux")
    compte_contrepartie = relationship("PlanComptable")
    ecritures = relationship("EcritureComptable", back_populates="journal")
    
    # Unique constraint per organization
    __table_args__ = (Index("idx_org_journal", "organization_id", "code", unique=True),)


# ============================================================================
# EXERCICES COMPTABLES
# ============================================================================

class ExerciceComptable(Base):
    __tablename__ = "exercices_comptables"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Période
    annee = Column(Integer, nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    
    # Status
    ouvert = Column(Boolean, default=True)
    cloture = Column(Boolean, default=False)
    date_cloture = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="exercices")
    ecritures = relationship("EcritureComptable", back_populates="exercice")
    
    # Unique constraint per organization
    __table_args__ = (Index("idx_org_exercice", "organization_id", "annee", unique=True),)


# ============================================================================
# ÉCRITURES COMPTABLES
# ============================================================================

class EcritureComptable(Base):
    __tablename__ = "ecritures_comptables"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    exercice_id = Column(Integer, ForeignKey("exercices_comptables.id"), nullable=False)
    journal_id = Column(Integer, ForeignKey("journaux.id"), nullable=False)
    
    # Identifiant
    numero = Column(String(50), nullable=False)
    numero_piece = Column(String(50))
    
    # Date et période
    date_ecriture = Column(Date, nullable=False)
    date_piece = Column(Date)
    
    # Description
    libelle = Column(Text, nullable=False)
    reference = Column(String(100))
    
    # Type d'écriture
    type_ecriture = Column(Enum(EcritureTypeEnum), default=EcritureTypeEnum.STANDARD)
    
    # Contrôle
    equilibree = Column(Boolean, default=False)
    validee = Column(Boolean, default=False)
    
    # Montants
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    
    # IA Integration
    ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Numeric(3, 2))  # Score de confiance 0-1
    
    # Documents attachés
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    validated_at = Column(DateTime(timezone=True))
    
    # Relationships
    organization = relationship("Organization")
    exercice = relationship("ExerciceComptable", back_populates="ecritures")
    journal = relationship("Journal", back_populates="ecritures")
    lignes = relationship("LigneEcriture", back_populates="ecriture", cascade="all, delete-orphan")
    document = relationship("Document", back_populates="ecritures")
    
    # Unique constraint per organization
    __table_args__ = (Index("idx_org_ecriture", "organization_id", "numero", unique=True),)


class LigneEcriture(Base):
    __tablename__ = "lignes_ecritures"
    
    id = Column(Integer, primary_key=True, index=True)
    ecriture_id = Column(Integer, ForeignKey("ecritures_comptables.id"), nullable=False)
    
    # Comptes
    compte_debit_id = Column(Integer, ForeignKey("plan_comptable.id"))
    compte_credit_id = Column(Integer, ForeignKey("plan_comptable.id"))
    
    # Montant
    montant = Column(Numeric(15, 2), nullable=False)
    
    # Description
    libelle = Column(String(255))
    
    # Lettrage
    lettrage = Column(String(10))
    lettre = Column(Boolean, default=False)
    date_lettrage = Column(DateTime(timezone=True))
    
    # Pointage
    pointe = Column(Boolean, default=False)
    date_pointage = Column(DateTime(timezone=True))
    
    # Tiers
    tiers_id = Column(Integer, ForeignKey("tiers.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ecriture = relationship("EcritureComptable", back_populates="lignes")
    compte_debit = relationship("PlanComptable", foreign_keys=[compte_debit_id], back_populates="ecritures_debit")
    compte_credit = relationship("PlanComptable", foreign_keys=[compte_credit_id], back_populates="ecritures_credit")
    tiers = relationship("Tiers", back_populates="lignes_ecritures")


# ============================================================================
# GESTION DES TIERS (SPÉCIFIQUE EBNL)
# ============================================================================

class Tiers(Base):
    __tablename__ = "tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Identification
    code = Column(String(20), nullable=False)
    nom = Column(String(255), nullable=False)
    type_tiers = Column(String(50), nullable=False)  # adherent, donateur, fournisseur, partenaire
    
    # Contact
    email = Column(String(255))
    telephone = Column(String(20))
    adresse = Column(Text)
    
    # Spécifique EBNL
    numero_adherent = Column(String(50))
    date_adhesion = Column(Date)
    cotisation_annuelle = Column(Numeric(15, 2))
    statut_cotisation = Column(String(20))  # a_jour, en_retard, exonere
    
    # Donateur
    donateur_regulier = Column(Boolean, default=False)
    total_dons = Column(Numeric(15, 2), default=0)
    
    # Status
    actif = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    lignes_ecritures = relationship("LigneEcriture", back_populates="tiers")
    cotisations = relationship("Cotisation", back_populates="adherent")
    dons = relationship("Don", back_populates="donateur")
    
    # Unique constraint per organization
    __table_args__ = (Index("idx_org_tiers", "organization_id", "code", unique=True),)


# ============================================================================
# GESTION SPÉCIALISÉE EBNL
# ============================================================================

class Projet(Base):
    __tablename__ = "projets"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Identification
    code = Column(String(20), nullable=False)
    nom = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Période
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    
    # Budget
    budget_prevu = Column(Numeric(15, 2))
    budget_consomme = Column(Numeric(15, 2), default=0)
    
    # Financement
    bailleur = Column(String(255))
    numero_convention = Column(String(100))
    
    # Status
    statut = Column(String(20), default="actif")  # actif, termine, suspendu
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    fonds_affectes = relationship("FondsAffecte", back_populates="projet")
    
    # Unique constraint per organization
    __table_args__ = (Index("idx_org_projet", "organization_id", "code", unique=True),)


class FondsAffecte(Base):
    __tablename__ = "fonds_affectes"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    projet_id = Column(Integer, ForeignKey("projets.id"), nullable=False)
    
    # Identification
    nom = Column(String(255), nullable=False)
    type_fonds = Column(String(50))  # subvention, don_affecte, legs
    
    # Montants
    montant_initial = Column(Numeric(15, 2), nullable=False)
    montant_utilise = Column(Numeric(15, 2), default=0)
    montant_disponible = Column(Numeric(15, 2))
    
    # Contraintes
    restrictions = Column(Text)
    date_limite_utilisation = Column(Date)
    
    # Status
    actif = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    projet = relationship("Projet", back_populates="fonds_affectes")


class Cotisation(Base):
    __tablename__ = "cotisations"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    adherent_id = Column(Integer, ForeignKey("tiers.id"), nullable=False)
    
    # Période
    annee = Column(Integer, nullable=False)
    
    # Montants
    montant_du = Column(Numeric(15, 2), nullable=False)
    montant_paye = Column(Numeric(15, 2), default=0)
    
    # Dates
    date_echeance = Column(Date, nullable=False)
    date_paiement = Column(Date)
    
    # Status
    statut = Column(String(20), default="due")  # due, payee, en_retard, exoneree
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    adherent = relationship("Tiers", back_populates="cotisations")


class Don(Base):
    __tablename__ = "dons"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    donateur_id = Column(Integer, ForeignKey("tiers.id"))
    
    # Don
    montant = Column(Numeric(15, 2), nullable=False)
    date_don = Column(Date, nullable=False)
    type_don = Column(String(50))  # especes, cheque, virement, nature
    
    # Affectation
    affecte = Column(Boolean, default=False)
    projet_id = Column(Integer, ForeignKey("projets.id"))
    
    # Reçu fiscal
    recu_fiscal = Column(Boolean, default=False)
    numero_recu = Column(String(50))
    
    # Description
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    donateur = relationship("Tiers", back_populates="dons")
    projet = relationship("Projet")


# ============================================================================
# GESTION DOCUMENTAIRE ET IA
# ============================================================================

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Fichier
    nom_fichier = Column(String(255), nullable=False)
    nom_original = Column(String(255), nullable=False)
    chemin_fichier = Column(String(500), nullable=False)
    taille_fichier = Column(Integer)
    type_mime = Column(String(100))
    
    # Type de document
    type_document = Column(Enum(FileTypeEnum), nullable=False)
    
    # OCR et IA
    ocr_effectue = Column(Boolean, default=False)
    texte_ocr = Column(Text)
    donnees_extraites = Column(JSON)  # Données extraites par l'IA
    
    # Processing status
    traite = Column(Boolean, default=False)
    erreur_traitement = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    ecritures = relationship("EcritureComptable", back_populates="document")


# ============================================================================
# AUDIT ET LOGGING
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Action
    action = Column(String(100), nullable=False)
    table_name = Column(String(100))
    record_id = Column(Integer)
    
    # Données
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User", back_populates="audit_logs")


# Index pour les performances
Index("idx_audit_org_date", AuditLog.organization_id, AuditLog.created_at)
Index("idx_audit_user_date", AuditLog.user_id, AuditLog.created_at)
Index("idx_ecriture_date", EcritureComptable.date_ecriture)
Index("idx_ecriture_journal", EcritureComptable.journal_id)
Index("idx_ligne_compte_debit", LigneEcriture.compte_debit_id)
Index("idx_ligne_compte_credit", LigneEcriture.compte_credit_id)
