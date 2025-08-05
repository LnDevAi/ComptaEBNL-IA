# -*- coding: utf-8 -*-
"""
Modèles de données pour ComptaEBNL-IA
Système de gestion comptable pour entités à but non lucratif
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal
import enum

db = SQLAlchemy()

# Énumérations
class StatutEcriture(enum.Enum):
    BROUILLARD = "brouillard"
    VALIDE = "valide"
    ANNULE = "annule"

class TypeJournal(enum.Enum):
    ACHATS = "ACH"
    VENTES = "VTE"
    BANQUE = "BQ"
    CAISSE = "CAI"
    OPERATIONS_DIVERSES = "OD"
    DONS = "DON"
    SUBVENTIONS = "SUB"

# === PLAN COMPTABLE ===
class PlanComptable(db.Model):
    __tablename__ = 'plan_comptable'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_compte = db.Column(db.String(20), unique=True, nullable=False, index=True)
    libelle_compte = db.Column(db.String(255), nullable=False)
    classe = db.Column(db.Integer, nullable=False, index=True)  # 1-9 pour SYCEBNL
    niveau = db.Column(db.Integer, nullable=False, default=0)  # 0=classe, 1=principal, 2=divisionnaire, 3=sous-compte
    parent_id = db.Column(db.Integer, db.ForeignKey('plan_comptable.id'), nullable=True)
    actif = db.Column(db.Boolean, default=True, nullable=False)
    observations = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    parent = db.relationship('PlanComptable', remote_side=[id], backref='enfants')
    lignes_ecriture = db.relationship('LigneEcriture', backref='compte', lazy='dynamic')
    
    def __repr__(self):
        return f'<Compte {self.numero_compte} - {self.libelle_compte}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_compte': self.numero_compte,
            'libelle_compte': self.libelle_compte,
            'classe': self.classe,
            'niveau': self.niveau,
            'parent_id': self.parent_id,
            'actif': self.actif,
            'observations': self.observations,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None
        }

# === JOURNAUX COMPTABLES ===
class JournalComptable(db.Model):
    __tablename__ = 'journaux_comptables'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    libelle = db.Column(db.String(100), nullable=False)
    type_journal = db.Column(db.Enum(TypeJournal), nullable=False)
    actif = db.Column(db.Boolean, default=True, nullable=False)
    description = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    ecritures = db.relationship('EcritureComptable', backref='journal_obj', lazy='dynamic')
    
    def __repr__(self):
        return f'<Journal {self.code} - {self.libelle}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'libelle': self.libelle,
            'type_journal': self.type_journal.value if self.type_journal else None,
            'actif': self.actif,
            'description': self.description,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None
        }

# === ÉCRITURES COMPTABLES ===
class EcritureComptable(db.Model):
    __tablename__ = 'ecritures_comptables'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_ecriture = db.Column(db.String(20), unique=True, nullable=True)  # Auto-généré
    date_ecriture = db.Column(db.Date, nullable=False, index=True)
    libelle = db.Column(db.String(255), nullable=False)
    journal = db.Column(db.String(10), db.ForeignKey('journaux_comptables.code'), nullable=False, index=True)
    piece_justificative = db.Column(db.String(50))
    montant_total = db.Column(db.Numeric(15, 2), nullable=False)
    statut = db.Column(db.Enum(StatutEcriture), default=StatutEcriture.BROUILLARD, nullable=False, index=True)
    
    # Métadonnées de validation et traçabilité
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_validation = db.Column(db.DateTime, nullable=True)
    user_creation = db.Column(db.String(50))  # Pour traçabilité
    user_validation = db.Column(db.String(50))  # Pour traçabilité
    
    # IA et automatisation
    ia_generated = db.Column(db.Boolean, default=False)  # Générée par IA
    ia_confidence = db.Column(db.Float)  # Niveau de confiance IA (0-1)
    document_source = db.Column(db.String(255))  # Chemin du document source
    
    # Relations
    lignes = db.relationship('LigneEcriture', backref='ecriture', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.numero_ecriture:
            self.numero_ecriture = self.generer_numero_ecriture()
    
    def generer_numero_ecriture(self):
        """Génère un numéro d'écriture unique"""
        # Format: JOURNAL-YYYYMMDD-XXX
        if self.journal and self.date_ecriture:
            date_str = self.date_ecriture.strftime('%Y%m%d')
            # Compter les écritures du même journal le même jour
            count = EcritureComptable.query.filter(
                EcritureComptable.journal == self.journal,
                EcritureComptable.date_ecriture == self.date_ecriture
            ).count()
            return f"{self.journal}-{date_str}-{count + 1:03d}"
        return None
    
    def is_equilibree(self):
        """Vérifie si l'écriture est équilibrée (débit = crédit)"""
        total_debit = sum(ligne.debit for ligne in self.lignes)
        total_credit = sum(ligne.credit for ligne in self.lignes)
        return abs(total_debit - total_credit) < Decimal('0.01')  # Tolérance de 1 centime
    
    def valider(self, user=None):
        """Valide l'écriture"""
        if not self.is_equilibree():
            raise ValueError("Impossible de valider une écriture non équilibrée")
        
        self.statut = StatutEcriture.VALIDE
        self.date_validation = datetime.utcnow()
        self.user_validation = user
        db.session.commit()
    
    def __repr__(self):
        return f'<Ecriture {self.numero_ecriture} - {self.libelle}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_ecriture': self.numero_ecriture,
            'date_ecriture': self.date_ecriture.isoformat() if self.date_ecriture else None,
            'libelle': self.libelle,
            'journal': self.journal,
            'piece_justificative': self.piece_justificative,
            'montant_total': float(self.montant_total) if self.montant_total else 0,
            'statut': self.statut.value if self.statut else None,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'date_modification': self.date_modification.isoformat() if self.date_modification else None,
            'date_validation': self.date_validation.isoformat() if self.date_validation else None,
            'user_creation': self.user_creation,
            'user_validation': self.user_validation,
            'ia_generated': self.ia_generated,
            'ia_confidence': self.ia_confidence,
            'document_source': self.document_source,
            'equilibree': self.is_equilibree(),
            'lignes': [ligne.to_dict() for ligne in self.lignes]
        }

# === LIGNES D'ÉCRITURE ===
class LigneEcriture(db.Model):
    __tablename__ = 'lignes_ecriture'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ecriture_id = db.Column(db.Integer, db.ForeignKey('ecritures_comptables.id'), nullable=False, index=True)
    numero_compte = db.Column(db.String(20), db.ForeignKey('plan_comptable.numero_compte'), nullable=False, index=True)
    libelle = db.Column(db.String(255), nullable=False)
    debit = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    credit = db.Column(db.Numeric(15, 2), default=0, nullable=False)
    quantite = db.Column(db.Numeric(12, 3))  # Pour la gestion analytique
    prix_unitaire = db.Column(db.Numeric(12, 2))  # Pour la gestion analytique
    
    # Métadonnées supplémentaires
    date_echeance = db.Column(db.Date)  # Pour les comptes de tiers
    reference_externe = db.Column(db.String(50))  # Référence externe (facture, etc.)
    
    def __repr__(self):
        return f'<LigneEcriture {self.numero_compte} - D:{self.debit} C:{self.credit}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ecriture_id': self.ecriture_id,
            'numero_compte': self.numero_compte,
            'libelle': self.libelle,
            'debit': float(self.debit) if self.debit else 0,
            'credit': float(self.credit) if self.credit else 0,
            'quantite': float(self.quantite) if self.quantite else None,
            'prix_unitaire': float(self.prix_unitaire) if self.prix_unitaire else None,
            'date_echeance': self.date_echeance.isoformat() if self.date_echeance else None,
            'reference_externe': self.reference_externe,
            'compte': self.compte.to_dict() if self.compte else None
        }

# === DOCUMENTS ===
class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_fichier = db.Column(db.String(255), nullable=False)
    chemin_fichier = db.Column(db.String(500), nullable=False)
    taille_fichier = db.Column(db.Integer)  # En octets
    type_mime = db.Column(db.String(100))
    type_document = db.Column(db.String(50))  # facture, recu, releve_bancaire, etc.
    
    # Traitement IA/OCR
    ocr_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    ocr_text = db.Column(db.Text)  # Texte extrait par OCR
    ocr_confidence = db.Column(db.Float)  # Niveau de confiance OCR
    extracted_data = db.Column(db.JSON)  # Données extraites structurées
    
    # Métadonnées
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
    date_traitement = db.Column(db.DateTime)
    user_upload = db.Column(db.String(50))
    
    # Relations
    ecriture_id = db.Column(db.Integer, db.ForeignKey('ecritures_comptables.id'), nullable=True)
    
    def __repr__(self):
        return f'<Document {self.nom_fichier}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_fichier': self.nom_fichier,
            'chemin_fichier': self.chemin_fichier,
            'taille_fichier': self.taille_fichier,
            'type_mime': self.type_mime,
            'type_document': self.type_document,
            'ocr_status': self.ocr_status,
            'ocr_confidence': self.ocr_confidence,
            'extracted_data': self.extracted_data,
            'date_upload': self.date_upload.isoformat() if self.date_upload else None,
            'date_traitement': self.date_traitement.isoformat() if self.date_traitement else None,
            'user_upload': self.user_upload,
            'ecriture_id': self.ecriture_id
        }

# === EXERCICES COMPTABLES ===
class ExerciceComptable(db.Model):
    __tablename__ = 'exercices_comptables'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_exercice = db.Column(db.String(50), nullable=False)  # Ex: "2024"
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(20), default='ouvert')  # ouvert, cloture, archive
    cloture_par = db.Column(db.String(50))
    date_cloture = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Exercice {self.nom_exercice}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_exercice': self.nom_exercice,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'statut': self.statut,
            'cloture_par': self.cloture_par,
            'date_cloture': self.date_cloture.isoformat() if self.date_cloture else None
        }

# === UTILISATEURS ET AUTHENTIFICATION ===
class Utilisateur(db.Model):
    __tablename__ = 'utilisateurs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_utilisateur = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe_hash = db.Column(db.String(255), nullable=False)
    nom_complet = db.Column(db.String(100))
    role = db.Column(db.String(20), default='comptable')  # admin, comptable, consultant
    actif = db.Column(db.Boolean, default=True)
    
    # Permissions spécifiques
    peut_valider = db.Column(db.Boolean, default=False)
    peut_cloturer = db.Column(db.Boolean, default=False)
    peut_gerer_plan_comptable = db.Column(db.Boolean, default=False)
    
    # Métadonnées
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Utilisateur {self.nom_utilisateur}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_utilisateur': self.nom_utilisateur,
            'email': self.email,
            'nom_complet': self.nom_complet,
            'role': self.role,
            'actif': self.actif,
            'peut_valider': self.peut_valider,
            'peut_cloturer': self.peut_cloturer,
            'peut_gerer_plan_comptable': self.peut_gerer_plan_comptable,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'derniere_connexion': self.derniere_connexion.isoformat() if self.derniere_connexion else None
        }

# === PARAMÈTRES DE L'ENTITÉ ===
class EntiteEBNL(db.Model):
    __tablename__ = 'entite_ebnl'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_entite = db.Column(db.String(200), nullable=False)
    sigle = db.Column(db.String(20))
    numero_identification = db.Column(db.String(50))  # SIREN, RNA, etc.
    type_entite = db.Column(db.String(50))  # association, fondation, etc.
    
    # Adresse
    adresse = db.Column(db.String(255))
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(100))
    pays = db.Column(db.String(50), default='France')
    
    # Contact
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    site_web = db.Column(db.String(255))
    
    # Paramètres comptables
    devise_principale = db.Column(db.String(3), default='EUR')
    exercice_debut_mois = db.Column(db.Integer, default=1)  # Mois de début d'exercice
    tva_applicable = db.Column(db.Boolean, default=True)
    
    # Spécificités EBNL
    objet_social = db.Column(db.Text)
    date_creation_entite = db.Column(db.Date)
    prefecture_declaration = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<EntiteEBNL {self.nom_entite}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom_entite': self.nom_entite,
            'sigle': self.sigle,
            'numero_identification': self.numero_identification,
            'type_entite': self.type_entite,
            'adresse': self.adresse,
            'code_postal': self.code_postal,
            'ville': self.ville,
            'pays': self.pays,
            'telephone': self.telephone,
            'email': self.email,
            'site_web': self.site_web,
            'devise_principale': self.devise_principale,
            'exercice_debut_mois': self.exercice_debut_mois,
            'tva_applicable': self.tva_applicable,
            'objet_social': self.objet_social,
            'date_creation_entite': self.date_creation_entite.isoformat() if self.date_creation_entite else None,
            'prefecture_declaration': self.prefecture_declaration
        }

# Fonction d'initialisation des données de base
def init_default_data():
    """Initialise les données par défaut (journaux, exercice, etc.)"""
    
    # Journaux comptables par défaut
    journaux_defaut = [
        ('ACH', 'Journal des Achats', TypeJournal.ACHATS),
        ('VTE', 'Journal des Ventes', TypeJournal.VENTES), 
        ('BQ', 'Journal de Banque', TypeJournal.BANQUE),
        ('CAI', 'Journal de Caisse', TypeJournal.CAISSE),
        ('OD', 'Opérations Diverses', TypeJournal.OPERATIONS_DIVERSES),
        ('DON', 'Journal des Dons', TypeJournal.DONS),
        ('SUB', 'Journal des Subventions', TypeJournal.SUBVENTIONS),
    ]
    
    for code, libelle, type_journal in journaux_defaut:
        if not JournalComptable.query.filter_by(code=code).first():
            journal = JournalComptable(
                code=code,
                libelle=libelle,
                type_journal=type_journal
            )
            db.session.add(journal)
    
    # Exercice comptable par défaut (année courante)
    annee_courante = datetime.now().year
    if not ExerciceComptable.query.filter_by(nom_exercice=str(annee_courante)).first():
        exercice = ExerciceComptable(
            nom_exercice=str(annee_courante),
            date_debut=date(annee_courante, 1, 1),
            date_fin=date(annee_courante, 12, 31),
            statut='ouvert'
        )
        db.session.add(exercice)
    
    db.session.commit()

if __name__ == '__main__':
    # Test des modèles
    print("Modèles ComptaEBNL-IA définis avec succès !")
    print("Tables disponibles:")
    print("- plan_comptable")
    print("- journaux_comptables") 
    print("- ecritures_comptables")
    print("- lignes_ecriture")
    print("- documents")
    print("- exercices_comptables")
    print("- utilisateurs")
    print("- entite_ebnl")
