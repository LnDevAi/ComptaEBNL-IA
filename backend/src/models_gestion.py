"""
Modèles de gestion avancée pour ComptaEBNL-IA
Gestion multi-projets, multi-bailleurs avec dirigeants, budget, activités, patrimoine
"""

from extensions import db
from datetime import datetime, date
import enum
import json
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Numeric, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship

# ============================
# ENUMS POUR LA GESTION
# ============================

class TypeDirigeant(enum.Enum):
    PRESIDENT = 'president'
    VICE_PRESIDENT = 'vice_president'
    SECRETAIRE_GENERAL = 'secretaire_general'
    TRESORIER = 'tresorier'
    COMMISSAIRE_COMPTES = 'commissaire_comptes'
    MEMBRE_BUREAU = 'membre_bureau'
    DIRECTEUR_EXECUTIF = 'directeur_executif'

class StatutDirigeant(enum.Enum):
    ACTIF = 'actif'
    SUSPENDU = 'suspendu'
    DEMISSIONNAIRE = 'demissionnaire'
    REVOQUE = 'revoque'

class TypeBailleur(enum.Enum):
    GOUVERNEMENT = 'gouvernement'
    ONG_INTERNATIONALE = 'ong_internationale'
    FONDATION = 'fondation'
    ENTREPRISE = 'entreprise'
    PARTICULIER = 'particulier'
    ORGANISME_MULTILATERAL = 'organisme_multilateral'
    UNION_EUROPEENNE = 'union_europeenne'

class StatutProjet(enum.Enum):
    PREPARATION = 'preparation'
    EN_COURS = 'en_cours'
    SUSPENDU = 'suspendu'
    TERMINE = 'termine'
    ANNULE = 'annule'

class TypeActivite(enum.Enum):
    FORMATION = 'formation'
    SENSIBILISATION = 'sensibilisation'
    RECHERCHE = 'recherche'
    DEVELOPPEMENT = 'developpement'
    HUMANITAIRE = 'humanitaire'
    ENVIRONNEMENT = 'environnement'
    SANTE = 'sante'
    EDUCATION = 'education'
    CULTURE = 'culture'

class TypeBien(enum.Enum):
    IMMOBILIER = 'immobilier'
    MOBILIER = 'mobilier'
    VEHICULE = 'vehicule'
    EQUIPEMENT_INFORMATIQUE = 'equipement_informatique'
    EQUIPEMENT_TECHNIQUE = 'equipement_technique'
    MATERIEL_BUREAU = 'materiel_bureau'

class StatutBudget(enum.Enum):
    PREVISIONNEL = 'previsionnel'
    VALIDE = 'valide'
    EN_EXECUTION = 'en_execution'
    CLOTURE = 'cloture'
    REVISE = 'revise'

# ============================
# MODÈLES DIRIGEANTS
# ============================

class Dirigeant(db.Model):
    """Dirigeants de l'association"""
    __tablename__ = 'dirigeants'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    
    # Informations personnelles
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(150), nullable=False)
    date_naissance = Column(Date)
    lieu_naissance = Column(String(100))
    nationalite = Column(String(50))
    profession = Column(String(100))
    
    # Contact
    telephone = Column(String(20))
    email = Column(String(100))
    adresse = Column(Text)
    
    # Fonction dans l'association
    type_dirigeant = Column(Enum(TypeDirigeant), nullable=False)
    statut = Column(Enum(StatutDirigeant), default=StatutDirigeant.ACTIF)
    date_nomination = Column(Date, nullable=False)
    date_fin_mandat = Column(Date)
    date_demission = Column(Date)
    
    # Signatures et pouvoirs
    pouvoir_signature = Column(Boolean, default=False)
    pouvoir_engagement = Column(Boolean, default=False)
    seuil_engagement = Column(Numeric(15, 2), default=0)
    
    # Pièces justificatives
    piece_identite_type = Column(String(50))  # CNI, Passeport, etc.
    piece_identite_numero = Column(String(50))
    piece_identite_fichier = Column(String(255))  # Chemin vers le fichier scanné
    cv_fichier = Column(String(255))
    casier_judiciaire_fichier = Column(String(255))
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cree_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations (à configurer après définition du modèle Association)
    # # association = relationship('Association', back_populates='dirigeants')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenoms': self.prenoms,
            'date_naissance': self.date_naissance.isoformat() if self.date_naissance else None,
            'lieu_naissance': self.lieu_naissance,
            'nationalite': self.nationalite,
            'profession': self.profession,
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse,
            'type_dirigeant': self.type_dirigeant.value,
            'statut': self.statut.value,
            'date_nomination': self.date_nomination.isoformat() if self.date_nomination else None,
            'date_fin_mandat': self.date_fin_mandat.isoformat() if self.date_fin_mandat else None,
            'pouvoir_signature': self.pouvoir_signature,
            'pouvoir_engagement': self.pouvoir_engagement,
            'seuil_engagement': float(self.seuil_engagement) if self.seuil_engagement else 0,
            'date_creation': self.date_creation.isoformat()
        }

# ============================
# MODÈLES BAILLEURS ET PROJETS
# ============================

class Bailleur(db.Model):
    """Bailleurs de fonds"""
    __tablename__ = 'bailleurs'
    
    id = Column(Integer, primary_key=True)
    
    # Informations de base
    nom = Column(String(200), nullable=False)
    sigle = Column(String(20))
    type_bailleur = Column(Enum(TypeBailleur), nullable=False)
    pays_origine = Column(String(50))
    
    # Contact
    adresse = Column(Text)
    telephone = Column(String(20))
    email = Column(String(100))
    site_web = Column(String(200))
    
    # Contact principal
    contact_nom = Column(String(100))
    contact_fonction = Column(String(100))
    contact_telephone = Column(String(20))
    contact_email = Column(String(100))
    
    # Informations complémentaires
    domaines_intervention = Column(Text)  # JSON des domaines
    zones_intervention = Column(Text)  # JSON des zones géographiques
    
    # Statut
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    projets = relationship('Projet', back_populates='bailleur')
    financements = relationship('Financement', back_populates='bailleur')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'sigle': self.sigle,
            'type_bailleur': self.type_bailleur.value,
            'pays_origine': self.pays_origine,
            'adresse': self.adresse,
            'telephone': self.telephone,
            'email': self.email,
            'contact_nom': self.contact_nom,
            'contact_email': self.contact_email,
            'actif': self.actif
        }

class Projet(db.Model):
    """Projets de l'association"""
    __tablename__ = 'projets'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    bailleur_id = Column(Integer, ForeignKey('bailleurs.id'))
    
    # Informations de base
    code_projet = Column(String(50), unique=True, nullable=False)
    titre = Column(String(300), nullable=False)
    description = Column(Text)
    objectifs = Column(Text)  # JSON des objectifs
    
    # Période
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    duree_mois = Column(Integer)
    
    # Localisation
    pays = Column(String(50))
    regions = Column(Text)  # JSON des régions
    zones_intervention = Column(Text)  # JSON des zones
    
    # Financier
    budget_total = Column(Numeric(15, 2), nullable=False)
    contribution_bailleur = Column(Numeric(15, 2))
    contribution_association = Column(Numeric(15, 2))
    autres_contributions = Column(Numeric(15, 2))
    
    # Statut et suivi
    statut = Column(Enum(StatutProjet), default=StatutProjet.PREPARATION)
    taux_execution_physique = Column(Numeric(5, 2), default=0)
    taux_execution_financiere = Column(Numeric(5, 2), default=0)
    
    # Responsables
    chef_projet = Column(String(100))
    coordinateur = Column(String(100))
    
    # Documents
    document_projet_fichier = Column(String(255))
    convention_fichier = Column(String(255))
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cree_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    # association = relationship('Association', back_populates='projets')
    # bailleur = relationship('Bailleur', back_populates='projets')
    activites = relationship('Activite', back_populates='projet')
    budgets = relationship('Budget', back_populates='projet')
    financements = relationship('Financement', back_populates='projet')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code_projet': self.code_projet,
            'titre': self.titre,
            'description': self.description,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'budget_total': float(self.budget_total) if self.budget_total else 0,
            'contribution_bailleur': float(self.contribution_bailleur) if self.contribution_bailleur else 0,
            'statut': self.statut.value,
            'taux_execution_physique': float(self.taux_execution_physique) if self.taux_execution_physique else 0,
            'taux_execution_financiere': float(self.taux_execution_financiere) if self.taux_execution_financiere else 0,
            'chef_projet': self.chef_projet,
            'bailleur': self.bailleur.to_dict() if self.bailleur else None
        }

# ============================
# MODÈLES BUDGET
# ============================

class Budget(db.Model):
    """Budgets par projet"""
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    projet_id = Column(Integer, ForeignKey('projets.id'))
    
    # Informations de base
    libelle = Column(String(200), nullable=False)
    exercice = Column(Integer, nullable=False)  # Année budgétaire
    version = Column(Integer, default=1)  # Version du budget
    
    # Période
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    
    # Montants globaux
    total_recettes_prevues = Column(Numeric(15, 2), default=0)
    total_depenses_prevues = Column(Numeric(15, 2), default=0)
    total_recettes_realisees = Column(Numeric(15, 2), default=0)
    total_depenses_realisees = Column(Numeric(15, 2), default=0)
    
    # Statut
    statut = Column(Enum(StatutBudget), default=StatutBudget.PREVISIONNEL)
    date_validation = Column(DateTime)
    valide_par = Column(Integer, ForeignKey('users.id'))
    
    # Commentaires
    commentaires = Column(Text)
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cree_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    # association = relationship('Association', back_populates='budgets')
    # projet = relationship('Projet', back_populates='budgets')
    lignes_budget = relationship('LigneBudget', back_populates='budget', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'libelle': self.libelle,
            'exercice': self.exercice,
            'version': self.version,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'total_recettes_prevues': float(self.total_recettes_prevues) if self.total_recettes_prevues else 0,
            'total_depenses_prevues': float(self.total_depenses_prevues) if self.total_depenses_prevues else 0,
            'total_recettes_realisees': float(self.total_recettes_realisees) if self.total_recettes_realisees else 0,
            'total_depenses_realisees': float(self.total_depenses_realisees) if self.total_depenses_realisees else 0,
            'statut': self.statut.value,
            'projet': self.projet.to_dict() if self.projet else None
        }

class LigneBudget(db.Model):
    """Lignes détaillées du budget"""
    __tablename__ = 'lignes_budget'
    
    id = Column(Integer, primary_key=True)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    
    # Classification
    compte_comptable = Column(String(20))  # Référence SYCEBNL
    categorie = Column(String(100))  # Recettes/Dépenses
    sous_categorie = Column(String(100))
    
    # Description
    libelle = Column(String(300), nullable=False)
    description = Column(Text)
    
    # Montants
    montant_prevu = Column(Numeric(15, 2), nullable=False)
    montant_realise = Column(Numeric(15, 2), default=0)
    montant_engage = Column(Numeric(15, 2), default=0)
    
    # Suivi
    taux_execution = Column(Numeric(5, 2), default=0)
    
    # Métadonnées
    ordre_affichage = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    budget = relationship('Budget', back_populates='lignes_budget')
    
    def to_dict(self):
        return {
            'id': self.id,
            'compte_comptable': self.compte_comptable,
            'categorie': self.categorie,
            'sous_categorie': self.sous_categorie,
            'libelle': self.libelle,
            'description': self.description,
            'montant_prevu': float(self.montant_prevu) if self.montant_prevu else 0,
            'montant_realise': float(self.montant_realise) if self.montant_realise else 0,
            'montant_engage': float(self.montant_engage) if self.montant_engage else 0,
            'taux_execution': float(self.taux_execution) if self.taux_execution else 0
        }

# ============================
# MODÈLES ACTIVITÉS
# ============================

class Activite(db.Model):
    """Activités des projets"""
    __tablename__ = 'activites'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    projet_id = Column(Integer, ForeignKey('projets.id'))
    
    # Informations de base
    code_activite = Column(String(50))
    titre = Column(String(300), nullable=False)
    description = Column(Text)
    type_activite = Column(Enum(TypeActivite), nullable=False)
    
    # Période
    date_debut_prevue = Column(Date)
    date_fin_prevue = Column(Date)
    date_debut_reelle = Column(Date)
    date_fin_reelle = Column(Date)
    
    # Localisation
    lieu = Column(String(200))
    region = Column(String(100))
    
    # Participants
    nombre_participants_prevu = Column(Integer, default=0)
    nombre_participants_reel = Column(Integer, default=0)
    
    # Budget
    budget_alloue = Column(Numeric(15, 2), default=0)
    budget_consomme = Column(Numeric(15, 2), default=0)
    
    # Responsable
    responsable_activite = Column(String(100))
    
    # Statut
    statut = Column(String(50), default='planifie')  # planifie, en_cours, termine, annule
    taux_execution = Column(Numeric(5, 2), default=0)
    
    # Résultats
    resultats_obtenus = Column(Text)
    indicateurs = Column(Text)  # JSON des indicateurs
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cree_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    # association = relationship('Association', back_populates='activites')
    # projet = relationship('Projet', back_populates='activites')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code_activite': self.code_activite,
            'titre': self.titre,
            'description': self.description,
            'type_activite': self.type_activite.value,
            'date_debut_prevue': self.date_debut_prevue.isoformat() if self.date_debut_prevue else None,
            'date_fin_prevue': self.date_fin_prevue.isoformat() if self.date_fin_prevue else None,
            'lieu': self.lieu,
            'nombre_participants_prevu': self.nombre_participants_prevu,
            'nombre_participants_reel': self.nombre_participants_reel,
            'budget_alloue': float(self.budget_alloue) if self.budget_alloue else 0,
            'budget_consomme': float(self.budget_consomme) if self.budget_consomme else 0,
            'responsable_activite': self.responsable_activite,
            'statut': self.statut,
            'taux_execution': float(self.taux_execution) if self.taux_execution else 0,
            'projet': self.projet.to_dict() if self.projet else None
        }

# ============================
# MODÈLES PATRIMOINE
# ============================

class Bien(db.Model):
    """Biens patrimoniaux de l'association"""
    __tablename__ = 'biens'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    projet_id = Column(Integer, ForeignKey('projets.id'))  # Optionnel si lié à un projet
    
    # Identification
    numero_inventaire = Column(String(50), unique=True)
    libelle = Column(String(300), nullable=False)
    description = Column(Text)
    type_bien = Column(Enum(TypeBien), nullable=False)
    
    # Caractéristiques
    marque = Column(String(100))
    modele = Column(String(100))
    numero_serie = Column(String(100))
    
    # Valeurs
    valeur_acquisition = Column(Numeric(15, 2))
    valeur_actuelle = Column(Numeric(15, 2))
    valeur_assurance = Column(Numeric(15, 2))
    
    # Dates
    date_acquisition = Column(Date)
    date_mise_service = Column(Date)
    
    # Localisation
    localisation = Column(String(200))
    responsable_bien = Column(String(100))
    
    # Statut
    statut = Column(String(50), default='en_service')  # en_service, en_panne, reforme, vendu
    
    # Amortissement
    duree_amortissement_annees = Column(Integer)
    taux_amortissement = Column(Numeric(5, 2))
    valeur_amortie = Column(Numeric(15, 2), default=0)
    
    # Maintenance
    date_derniere_maintenance = Column(Date)
    date_prochaine_maintenance = Column(Date)
    cout_maintenance_annuel = Column(Numeric(15, 2))
    
    # Documents
    facture_fichier = Column(String(255))
    certificat_propriete_fichier = Column(String(255))
    assurance_fichier = Column(String(255))
    photo_fichier = Column(String(255))
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_modification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cree_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    # association = relationship('Association', back_populates='biens')
    # projet = relationship('Projet')
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_inventaire': self.numero_inventaire,
            'libelle': self.libelle,
            'description': self.description,
            'type_bien': self.type_bien.value,
            'marque': self.marque,
            'modele': self.modele,
            'valeur_acquisition': float(self.valeur_acquisition) if self.valeur_acquisition else 0,
            'valeur_actuelle': float(self.valeur_actuelle) if self.valeur_actuelle else 0,
            'date_acquisition': self.date_acquisition.isoformat() if self.date_acquisition else None,
            'localisation': self.localisation,
            'responsable_bien': self.responsable_bien,
            'statut': self.statut,
            'duree_amortissement_annees': self.duree_amortissement_annees,
            'valeur_amortie': float(self.valeur_amortie) if self.valeur_amortie else 0
        }

# ============================
# MODÈLES BALANCE ET REPORTS
# ============================

class Balance(db.Model):
    """Balance comptable N-1 et reports à nouveau"""
    __tablename__ = 'balances'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    
    # Période
    exercice = Column(Integer, nullable=False)
    date_cloture = Column(Date, nullable=False)
    
    # Type
    type_balance = Column(String(50), nullable=False)  # 'balance_n1', 'report_nouveau'
    
    # Statut
    statut = Column(String(50), default='brouillon')  # brouillon, valide, integre
    
    # Fichier importé
    fichier_balance = Column(String(255))  # Chemin vers fichier Excel/CSV
    
    # Métadonnées
    date_import = Column(DateTime, default=datetime.utcnow)
    importe_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    # association = relationship('Association', back_populates='balances')
    lignes_balance = relationship('LigneBalance', back_populates='balance', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'exercice': self.exercice,
            'date_cloture': self.date_cloture.isoformat() if self.date_cloture else None,
            'type_balance': self.type_balance,
            'statut': self.statut,
            'date_import': self.date_import.isoformat(),
            'nombre_lignes': len(self.lignes_balance) if self.lignes_balance else 0
        }

class LigneBalance(db.Model):
    """Lignes de la balance comptable"""
    __tablename__ = 'lignes_balance'
    
    id = Column(Integer, primary_key=True)
    balance_id = Column(Integer, ForeignKey('balances.id'), nullable=False)
    
    # Compte
    numero_compte = Column(String(20), nullable=False)
    libelle_compte = Column(String(300), nullable=False)
    
    # Soldes
    solde_debiteur = Column(Numeric(15, 2), default=0)
    solde_crediteur = Column(Numeric(15, 2), default=0)
    
    # Mouvements (si disponibles)
    mouvement_debit = Column(Numeric(15, 2), default=0)
    mouvement_credit = Column(Numeric(15, 2), default=0)
    
    # Métadonnées
    ligne_fichier = Column(Integer)  # Numéro de ligne dans le fichier importé
    
    # Relations
    balance = relationship('Balance', back_populates='lignes_balance')
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_compte': self.numero_compte,
            'libelle_compte': self.libelle_compte,
            'solde_debiteur': float(self.solde_debiteur) if self.solde_debiteur else 0,
            'solde_crediteur': float(self.solde_crediteur) if self.solde_crediteur else 0,
            'mouvement_debit': float(self.mouvement_debit) if self.mouvement_debit else 0,
            'mouvement_credit': float(self.mouvement_credit) if self.mouvement_credit else 0
        }

# ============================
# MODÈLES FINANCEMENT
# ============================

class Financement(db.Model):
    """Financements reçus des bailleurs"""
    __tablename__ = 'financements'
    
    id = Column(Integer, primary_key=True)
    association_id = Column(Integer, ForeignKey('associations.id'), nullable=False)
    projet_id = Column(Integer, ForeignKey('projets.id'))
    bailleur_id = Column(Integer, ForeignKey('bailleurs.id'), nullable=False)
    
    # Informations de base
    numero_convention = Column(String(100))
    libelle = Column(String(300), nullable=False)
    
    # Montants
    montant_accorde = Column(Numeric(15, 2), nullable=False)
    montant_decaisse = Column(Numeric(15, 2), default=0)
    montant_utilise = Column(Numeric(15, 2), default=0)
    
    # Période
    date_signature = Column(Date)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    
    # Conditions
    conditions_decaissement = Column(Text)
    modalites_reporting = Column(Text)
    
    # Statut
    statut = Column(String(50), default='signe')  # signe, en_cours, termine, suspendu
    
    # Documents
    convention_fichier = Column(String(255))
    
    # Métadonnées
    date_creation = Column(DateTime, default=datetime.utcnow)
    cree_par = Column(Integer, ForeignKey('users.id'))
    
    # Relations
    # association = relationship('Association', back_populates='financements')
    # projet = relationship('Projet', back_populates='financements')
    # bailleur = relationship('Bailleur', back_populates='financements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_convention': self.numero_convention,
            'libelle': self.libelle,
            'montant_accorde': float(self.montant_accorde) if self.montant_accorde else 0,
            'montant_decaisse': float(self.montant_decaisse) if self.montant_decaisse else 0,
            'montant_utilise': float(self.montant_utilise) if self.montant_utilise else 0,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'statut': self.statut,
            'bailleur': self.bailleur.to_dict() if self.bailleur else None,
            'projet': self.projet.to_dict() if self.projet else None
        }

# ============================
# EXTENSION MODÈLE ASSOCIATION
# ============================

def extend_association_model():
    """Étend le modèle Association avec les nouvelles relations"""
    # Cette fonction sera appelée après l'import du modèle Association
    # pour ajouter les nouvelles relations
    pass