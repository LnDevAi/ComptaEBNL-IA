"""
Modèles pour le système E-Learning ComptaEBNL-IA
Gestion des cours, modules, quiz et certification
"""

from extensions import db
from datetime import datetime, timedelta
import enum
import json

# ============================
# ENUMS
# ============================

class TypeContenu(enum.Enum):
    VIDEO = "video"
    TEXTE = "texte"
    PDF = "pdf"
    QUIZ = "quiz"
    EXERCICE = "exercice"
    ETUDE_CAS = "etude_cas"

class NiveauDifficulte(enum.Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"
    EXPERT = "expert"

class StatutProgression(enum.Enum):
    NON_COMMENCE = "non_commence"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    CERTIFIE = "certifie"

class TypeQuiz(enum.Enum):
    QCM = "qcm"
    VRAI_FAUX = "vrai_faux"
    REPONSE_LIBRE = "reponse_libre"
    CORRESPONDANCE = "correspondance"

class StatutCertificat(enum.Enum):
    EN_COURS = "en_cours"
    VALIDE = "valide"
    EXPIRE = "expire"
    SUSPENDU = "suspendu"

# ============================
# MODÈLES PRINCIPAUX
# ============================

class CategorieFormation(db.Model):
    """Catégories des formations"""
    __tablename__ = 'categories_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icone = db.Column(db.String(50))  # Nom de l'icône Material-UI
    couleur = db.Column(db.String(7))  # Code couleur hex
    ordre = db.Column(db.Integer, default=0)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    formations = db.relationship('Formation', backref='categorie', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'icone': self.icone,
            'couleur': self.couleur,
            'ordre': self.ordre,
            'nb_formations': len(self.formations)
        }

class Formation(db.Model):
    """Formations disponibles"""
    __tablename__ = 'formations'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    objectifs = db.Column(db.Text)  # JSON des objectifs pédagogiques
    
    # Métadonnées
    categorie_id = db.Column(db.Integer, db.ForeignKey('categories_formation.id'), nullable=False)
    niveau = db.Column(db.Enum(NiveauDifficulte), nullable=False)
    duree_estimee = db.Column(db.Integer)  # en minutes
    prix = db.Column(db.Numeric(10, 2), default=0)  # Prix si formation payante
    
    # Contenu
    image_couverture = db.Column(db.String(255))
    video_intro = db.Column(db.String(255))
    
    # Prérequis et accès
    prerequis = db.Column(db.Text)  # JSON des prérequis
    plan_requis = db.Column(db.String(50))  # gratuit, professionnel, enterprise
    
    # Statut
    publie = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_publication = db.Column(db.DateTime)
    
    # Statistiques
    nb_inscrits = db.Column(db.Integer, default=0)
    note_moyenne = db.Column(db.Float, default=0.0)
    nb_evaluations = db.Column(db.Integer, default=0)
    
    # Relations
    modules = db.relationship('ModuleFormation', backref='formation', lazy=True, order_by='ModuleFormation.ordre')
    inscriptions = db.relationship('InscriptionFormation', backref='formation', lazy=True)
    evaluations = db.relationship('EvaluationFormation', backref='formation', lazy=True)
    certificats = db.relationship('Certificat', backref='formation', lazy=True)
    
    def get_objectifs(self):
        """Retourne les objectifs sous forme de liste"""
        if self.objectifs:
            return json.loads(self.objectifs)
        return []
    
    def get_prerequis(self):
        """Retourne les prérequis sous forme de liste"""
        if self.prerequis:
            return json.loads(self.prerequis)
        return []
    
    def to_dict(self, include_modules=False):
        result = {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'objectifs': self.get_objectifs(),
            'categorie': self.categorie.to_dict() if self.categorie else None,
            'niveau': self.niveau.value,
            'duree_estimee': self.duree_estimee,
            'prix': float(self.prix) if self.prix else 0,
            'image_couverture': self.image_couverture,
            'video_intro': self.video_intro,
            'prerequis': self.get_prerequis(),
            'plan_requis': self.plan_requis,
            'publie': self.publie,
            'date_publication': self.date_publication.isoformat() if self.date_publication else None,
            'nb_inscrits': self.nb_inscrits,
            'note_moyenne': self.note_moyenne,
            'nb_evaluations': self.nb_evaluations,
            'nb_modules': len(self.modules)
        }
        
        if include_modules:
            result['modules'] = [module.to_dict() for module in self.modules]
        
        return result

class ModuleFormation(db.Model):
    """Modules d'une formation"""
    __tablename__ = 'modules_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ordre = db.Column(db.Integer, nullable=False)
    
    # Contenu
    duree_estimee = db.Column(db.Integer)  # en minutes
    
    # Relations
    lecons = db.relationship('Lecon', backref='module', lazy=True, order_by='Lecon.ordre')
    
    def to_dict(self, include_lecons=False):
        result = {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'ordre': self.ordre,
            'duree_estimee': self.duree_estimee,
            'nb_lecons': len(self.lecons)
        }
        
        if include_lecons:
            result['lecons'] = [lecon.to_dict() for lecon in self.lecons]
        
        return result

class Lecon(db.Model):
    """Leçons d'un module"""
    __tablename__ = 'lecons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules_formation.id'), nullable=False)
    
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text)  # Contenu principal
    type_contenu = db.Column(db.Enum(TypeContenu), nullable=False)
    
    # Métadonnées
    ordre = db.Column(db.Integer, nullable=False)
    duree_estimee = db.Column(db.Integer)  # en minutes
    
    # Fichiers associés
    video_url = db.Column(db.String(500))
    fichier_pdf = db.Column(db.String(255))
    ressources_json = db.Column(db.Text)  # JSON des ressources supplémentaires
    
    # Statut
    gratuit = db.Column(db.Boolean, default=False)  # Leçon accessible gratuitement
    
    # Relations
    quiz = db.relationship('Quiz', backref='lecon', uselist=False)  # Une leçon peut avoir un quiz
    progressions = db.relationship('ProgressionLecon', backref='lecon', lazy=True)
    
    def get_ressources(self):
        """Retourne les ressources sous forme de liste"""
        if self.ressources_json:
            return json.loads(self.ressources_json)
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'contenu': self.contenu,
            'type_contenu': self.type_contenu.value,
            'ordre': self.ordre,
            'duree_estimee': self.duree_estimee,
            'video_url': self.video_url,
            'fichier_pdf': self.fichier_pdf,
            'ressources': self.get_ressources(),
            'gratuit': self.gratuit,
            'a_quiz': self.quiz is not None
        }

# ============================
# QUIZ ET ÉVALUATIONS
# ============================

class Quiz(db.Model):
    """Quiz associés aux leçons"""
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    lecon_id = db.Column(db.Integer, db.ForeignKey('lecons.id'), nullable=False)
    
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Paramètres
    temps_limite = db.Column(db.Integer)  # en minutes
    note_minimum = db.Column(db.Float, default=0.6)  # Note minimum pour valider (60%)
    tentatives_max = db.Column(db.Integer, default=3)
    
    # Relations
    questions = db.relationship('QuestionQuiz', backref='quiz', lazy=True, order_by='QuestionQuiz.ordre')
    tentatives = db.relationship('TentativeQuiz', backref='quiz', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'temps_limite': self.temps_limite,
            'note_minimum': self.note_minimum,
            'tentatives_max': self.tentatives_max,
            'nb_questions': len(self.questions)
        }

class QuestionQuiz(db.Model):
    """Questions d'un quiz"""
    __tablename__ = 'questions_quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    
    enonce = db.Column(db.Text, nullable=False)
    type_question = db.Column(db.Enum(TypeQuiz), nullable=False)
    ordre = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=1)
    
    # Réponses (JSON)
    choix_json = db.Column(db.Text)  # Pour QCM : [{"texte": "...", "correct": true/false}]
    reponse_correcte = db.Column(db.Text)  # Pour réponse libre
    explication = db.Column(db.Text)  # Explication de la réponse
    
    # Médias
    image_url = db.Column(db.String(500))
    
    def get_choix(self):
        """Retourne les choix pour QCM"""
        if self.choix_json:
            return json.loads(self.choix_json)
        return []
    
    def to_dict(self, include_answers=False):
        result = {
            'id': self.id,
            'enonce': self.enonce,
            'type_question': self.type_question.value,
            'ordre': self.ordre,
            'points': self.points,
            'image_url': self.image_url,
            'choix': self.get_choix() if self.type_question == TypeQuiz.QCM else []
        }
        
        if include_answers:
            result['reponse_correcte'] = self.reponse_correcte
            result['explication'] = self.explication
        
        return result

class TentativeQuiz(db.Model):
    """Tentatives de quiz par les utilisateurs"""
    __tablename__ = 'tentatives_quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    # Résultats
    note = db.Column(db.Float)  # Note sur 1.0
    note_sur_20 = db.Column(db.Float)  # Note sur 20
    reussi = db.Column(db.Boolean, default=False)
    
    # Timing
    date_debut = db.Column(db.DateTime, default=datetime.utcnow)
    date_fin = db.Column(db.DateTime)
    duree_secondes = db.Column(db.Integer)
    
    # Données
    reponses_json = db.Column(db.Text)  # JSON des réponses données
    
    def get_reponses(self):
        """Retourne les réponses sous forme de dictionnaire"""
        if self.reponses_json:
            return json.loads(self.reponses_json)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'note': self.note,
            'note_sur_20': self.note_sur_20,
            'reussi': self.reussi,
            'date_debut': self.date_debut.isoformat(),
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'duree_secondes': self.duree_secondes
        }

# ============================
# PROGRESSION ET INSCRIPTIONS
# ============================

class InscriptionFormation(db.Model):
    """Inscriptions des utilisateurs aux formations"""
    __tablename__ = 'inscriptions_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    # Statut
    statut = db.Column(db.Enum(StatutProgression), default=StatutProgression.NON_COMMENCE)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    
    # Progression
    pourcentage_completion = db.Column(db.Float, default=0.0)
    temps_passe = db.Column(db.Integer, default=0)  # en minutes
    
    # Relations
    progressions_lecons = db.relationship('ProgressionLecon', backref='inscription', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'formation': self.formation.to_dict(),
            'statut': self.statut.value,
            'date_inscription': self.date_inscription.isoformat(),
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'pourcentage_completion': self.pourcentage_completion,
            'temps_passe': self.temps_passe
        }

class ProgressionLecon(db.Model):
    """Progression des utilisateurs dans les leçons"""
    __tablename__ = 'progression_lecons'
    
    id = db.Column(db.Integer, primary_key=True)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscriptions_formation.id'), nullable=False)
    lecon_id = db.Column(db.Integer, db.ForeignKey('lecons.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    # Progression
    commence = db.Column(db.Boolean, default=False)
    termine = db.Column(db.Boolean, default=False)
    temps_passe = db.Column(db.Integer, default=0)  # en secondes
    
    # Timing
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    derniere_position = db.Column(db.Integer, default=0)  # Pour les vidéos
    
    # Contrainte unique
    __table_args__ = (db.UniqueConstraint('inscription_id', 'lecon_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lecon': self.lecon.to_dict(),
            'commence': self.commence,
            'termine': self.termine,
            'temps_passe': self.temps_passe,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'derniere_position': self.derniere_position
        }

# ============================
# ÉVALUATIONS ET CERTIFICATS
# ============================

class EvaluationFormation(db.Model):
    """Évaluations des formations par les utilisateurs"""
    __tablename__ = 'evaluations_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    # Évaluation
    note = db.Column(db.Integer, nullable=False)  # 1 à 5 étoiles
    commentaire = db.Column(db.Text)
    
    # Critères détaillés
    note_contenu = db.Column(db.Integer)  # 1 à 5
    note_pedagogie = db.Column(db.Integer)  # 1 à 5
    note_pratique = db.Column(db.Integer)  # 1 à 5
    
    date_evaluation = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Contrainte unique
    __table_args__ = (db.UniqueConstraint('formation_id', 'utilisateur_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'note': self.note,
            'commentaire': self.commentaire,
            'note_contenu': self.note_contenu,
            'note_pedagogie': self.note_pedagogie,
            'note_pratique': self.note_pratique,
            'date_evaluation': self.date_evaluation.isoformat()
        }

class Certificat(db.Model):
    """Certificats délivrés"""
    __tablename__ = 'certificats'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    # Informations du certificat
    numero_certificat = db.Column(db.String(100), unique=True, nullable=False)
    nom_beneficiaire = db.Column(db.String(200), nullable=False)
    
    # Statut
    statut = db.Column(db.Enum(StatutCertificat), default=StatutCertificat.EN_COURS)
    date_obtention = db.Column(db.DateTime, default=datetime.utcnow)
    date_expiration = db.Column(db.DateTime)  # Si applicable
    
    # Résultats
    note_finale = db.Column(db.Float)  # Note finale de la formation
    mention = db.Column(db.String(50))  # Passable, Bien, Très bien, Excellent
    
    # Fichiers
    fichier_pdf = db.Column(db.String(255))  # Chemin vers le PDF généré
    hash_verification = db.Column(db.String(255))  # Hash pour vérification
    
    # Contrainte unique
    __table_args__ = (db.UniqueConstraint('formation_id', 'utilisateur_id'),)
    
    def generer_numero(self):
        """Génère un numéro de certificat unique"""
        from datetime import datetime
        import uuid
        
        annee = datetime.now().year
        code_formation = f"F{self.formation_id:03d}"
        code_unique = str(uuid.uuid4())[:8].upper()
        
        return f"CEBNL-{annee}-{code_formation}-{code_unique}"
    
    def calculer_mention(self, note):
        """Calcule la mention selon la note"""
        if note >= 0.9:
            return "Excellent"
        elif note >= 0.8:
            return "Très bien"
        elif note >= 0.7:
            return "Bien"
        elif note >= 0.6:
            return "Passable"
        else:
            return "Insuffisant"
    
    def to_dict(self):
        return {
            'id': self.id,
            'formation': self.formation.to_dict() if self.formation else None,
            'numero_certificat': self.numero_certificat,
            'nom_beneficiaire': self.nom_beneficiaire,
            'statut': self.statut.value,
            'date_obtention': self.date_obtention.isoformat(),
            'date_expiration': self.date_expiration.isoformat() if self.date_expiration else None,
            'note_finale': self.note_finale,
            'mention': self.mention,
            'fichier_pdf': self.fichier_pdf,
            'est_valide': self.statut == StatutCertificat.VALIDE and (
                not self.date_expiration or self.date_expiration > datetime.utcnow()
            )
        }

# ============================
# FONCTIONS UTILITAIRES
# ============================

def init_categories_formation():
    """Initialise les catégories de formation par défaut"""
    categories_data = [
        {
            'nom': 'Fondamentaux EBNL',
            'description': 'Bases de la comptabilité des EBNL selon SYCEBNL',
            'icone': 'School',
            'couleur': '#2196F3',
            'ordre': 1
        },
        {
            'nom': 'Plan Comptable',
            'description': 'Maîtrise du plan comptable SYCEBNL',
            'icone': 'AccountBalance',
            'couleur': '#4CAF50',
            'ordre': 2
        },
        {
            'nom': 'Écritures Comptables',
            'description': 'Passation et contrôle des écritures',
            'icone': 'Receipt',
            'couleur': '#FF9800',
            'ordre': 3
        },
        {
            'nom': 'États Financiers',
            'description': 'Élaboration et analyse des états financiers',
            'icone': 'Analytics',
            'couleur': '#9C27B0',
            'ordre': 4
        },
        {
            'nom': 'Contrôle de Gestion',
            'description': 'Budgets, tableaux de bord et indicateurs',
            'icone': 'Dashboard',
            'couleur': '#F44336',
            'ordre': 5
        },
        {
            'nom': 'Audit et Conformité',
            'description': 'Audit interne et conformité réglementaire',
            'icone': 'Verified',
            'couleur': '#607D8B',
            'ordre': 6
        }
    ]
    
    for cat_data in categories_data:
        categorie_existante = CategorieFormation.query.filter_by(nom=cat_data['nom']).first()
        
        if not categorie_existante:
            categorie = CategorieFormation(**cat_data)
            db.session.add(categorie)
    
    try:
        db.session.commit()
        print("✅ Catégories de formation initialisées")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors de l'initialisation des catégories: {e}")

if __name__ == '__main__':
    print("📚 Modèles E-Learning ComptaEBNL-IA définis !")
    print("Modèles disponibles:")
    print("  • CategorieFormation, Formation, ModuleFormation, Lecon")
    print("  • Quiz, QuestionQuiz, TentativeQuiz")
    print("  • InscriptionFormation, ProgressionLecon")
    print("  • EvaluationFormation, Certificat")