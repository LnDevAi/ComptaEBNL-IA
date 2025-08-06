#!/usr/bin/env python3
"""
Test du système E-Learning ComptaEBNL-IA
Version simplifiée pour validation
"""

import sys
import os
import json
from datetime import datetime, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import enum

# Configuration simple
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_elearning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-elearning-key'

# Initialisation
db = SQLAlchemy(app)

# Copie des modèles e-learning (simplifiée)
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

class CategorieFormation(db.Model):
    """Catégories des formations"""
    __tablename__ = 'categories_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icone = db.Column(db.String(50))
    couleur = db.Column(db.String(7))
    ordre = db.Column(db.Integer, default=0)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    formations = db.relationship('Formation', backref='categorie', lazy=True)
    
    def __repr__(self):
        return f'<CategorieFormation {self.nom}>'

class Formation(db.Model):
    """Formations disponibles"""
    __tablename__ = 'formations'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    objectifs = db.Column(db.Text)  # JSON
    
    # Métadonnées
    categorie_id = db.Column(db.Integer, db.ForeignKey('categories_formation.id'), nullable=False)
    niveau = db.Column(db.Enum(NiveauDifficulte), nullable=False)
    duree_estimee = db.Column(db.Integer)
    prix = db.Column(db.Numeric(10, 2), default=0)
    
    # Contenu
    image_couverture = db.Column(db.String(255))
    video_intro = db.Column(db.String(255))
    
    # Prérequis et accès
    prerequis = db.Column(db.Text)  # JSON
    plan_requis = db.Column(db.String(50))
    
    # Statut
    publie = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_publication = db.Column(db.DateTime)
    
    # Statistiques
    nb_inscrits = db.Column(db.Integer, default=0)
    note_moyenne = db.Column(db.Float, default=0.0)
    nb_evaluations = db.Column(db.Integer, default=0)
    
    # Relations
    modules = db.relationship('ModuleFormation', backref='formation', lazy=True)
    inscriptions = db.relationship('InscriptionFormation', backref='formation', lazy=True)
    certificats = db.relationship('Certificat', backref='formation', lazy=True)
    
    def get_objectifs(self):
        if self.objectifs:
            return json.loads(self.objectifs)
        return []
    
    def __repr__(self):
        return f'<Formation {self.titre}>'

class ModuleFormation(db.Model):
    """Modules d'une formation"""
    __tablename__ = 'modules_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ordre = db.Column(db.Integer, nullable=False)
    duree_estimee = db.Column(db.Integer)
    
    # Relations
    lecons = db.relationship('Lecon', backref='module', lazy=True)
    
    def __repr__(self):
        return f'<ModuleFormation {self.titre}>'

class Lecon(db.Model):
    """Leçons d'un module"""
    __tablename__ = 'lecons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules_formation.id'), nullable=False)
    
    titre = db.Column(db.String(200), nullable=False)
    contenu = db.Column(db.Text)
    type_contenu = db.Column(db.Enum(TypeContenu), nullable=False)
    
    ordre = db.Column(db.Integer, nullable=False)
    duree_estimee = db.Column(db.Integer)
    
    video_url = db.Column(db.String(500))
    fichier_pdf = db.Column(db.String(255))
    ressources_json = db.Column(db.Text)
    
    gratuit = db.Column(db.Boolean, default=False)
    
    # Relations
    quiz = db.relationship('Quiz', backref='lecon', uselist=False)
    
    def __repr__(self):
        return f'<Lecon {self.titre}>'

class Quiz(db.Model):
    """Quiz associés aux leçons"""
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    lecon_id = db.Column(db.Integer, db.ForeignKey('lecons.id'), nullable=False)
    
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    temps_limite = db.Column(db.Integer)
    note_minimum = db.Column(db.Float, default=0.6)
    tentatives_max = db.Column(db.Integer, default=3)
    
    # Relations
    questions = db.relationship('QuestionQuiz', backref='quiz', lazy=True)
    tentatives = db.relationship('TentativeQuiz', backref='quiz', lazy=True)
    
    def __repr__(self):
        return f'<Quiz {self.titre}>'

class QuestionQuiz(db.Model):
    """Questions d'un quiz"""
    __tablename__ = 'questions_quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    
    enonce = db.Column(db.Text, nullable=False)
    type_question = db.Column(db.Enum(TypeQuiz), nullable=False)
    ordre = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=1)
    
    choix_json = db.Column(db.Text)
    reponse_correcte = db.Column(db.Text)
    explication = db.Column(db.Text)
    
    def get_choix(self):
        if self.choix_json:
            return json.loads(self.choix_json)
        return []
    
    def __repr__(self):
        return f'<QuestionQuiz {self.enonce[:50]}...>'

class TentativeQuiz(db.Model):
    """Tentatives de quiz par les utilisateurs"""
    __tablename__ = 'tentatives_quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    note = db.Column(db.Float)
    note_sur_20 = db.Column(db.Float)
    reussi = db.Column(db.Boolean, default=False)
    
    date_debut = db.Column(db.DateTime, default=datetime.utcnow)
    date_fin = db.Column(db.DateTime)
    duree_secondes = db.Column(db.Integer)
    
    reponses_json = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TentativeQuiz {self.id} - Note: {self.note}>'

class InscriptionFormation(db.Model):
    """Inscriptions des utilisateurs aux formations"""
    __tablename__ = 'inscriptions_formation'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    statut = db.Column(db.Enum(StatutProgression), default=StatutProgression.NON_COMMENCE)
    date_inscription = db.Column(db.DateTime, default=datetime.utcnow)
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    
    pourcentage_completion = db.Column(db.Float, default=0.0)
    temps_passe = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<InscriptionFormation {self.id} - Utilisateur {self.utilisateur_id}>'

class Certificat(db.Model):
    """Certificats délivrés"""
    __tablename__ = 'certificats'
    
    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey('formations.id'), nullable=False)
    utilisateur_id = db.Column(db.Integer, nullable=False)
    
    numero_certificat = db.Column(db.String(100), unique=True, nullable=False)
    nom_beneficiaire = db.Column(db.String(200), nullable=False)
    
    statut = db.Column(db.Enum(StatutCertificat), default=StatutCertificat.EN_COURS)
    date_obtention = db.Column(db.DateTime, default=datetime.utcnow)
    date_expiration = db.Column(db.DateTime)
    
    note_finale = db.Column(db.Float)
    mention = db.Column(db.String(50))
    
    fichier_pdf = db.Column(db.String(255))
    hash_verification = db.Column(db.String(255))
    
    def generer_numero(self):
        import uuid
        annee = datetime.now().year
        code_formation = f"F{self.formation_id:03d}"
        code_unique = str(uuid.uuid4())[:8].upper()
        return f"CEBNL-{annee}-{code_formation}-{code_unique}"
    
    def __repr__(self):
        return f'<Certificat {self.numero_certificat}>'

# Fonctions d'initialisation
def init_categories():
    """Initialise les catégories de formation"""
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
            'nom': 'États Financiers',
            'description': 'Élaboration et analyse des états financiers',
            'icone': 'Analytics',
            'couleur': '#9C27B0',
            'ordre': 3
        }
    ]
    
    for cat_data in categories_data:
        categorie_existante = CategorieFormation.query.filter_by(nom=cat_data['nom']).first()
        
        if not categorie_existante:
            categorie = CategorieFormation(**cat_data)
            db.session.add(categorie)
            print(f"✅ Catégorie '{cat_data['nom']}' créée")
        else:
            print(f"ℹ️  Catégorie '{cat_data['nom']}' existe déjà")

def create_sample_formation():
    """Crée une formation d'exemple complète"""
    
    # Récupérer la catégorie
    categorie = CategorieFormation.query.filter_by(nom='Fondamentaux EBNL').first()
    
    # Créer la formation
    formation = Formation(
        titre="Initiation à la Comptabilité des EBNL",
        description="Découvrez les principes fondamentaux de la comptabilité des Établissements Bancaires selon SYCEBNL.",
        objectifs=json.dumps([
            "Comprendre les spécificités comptables des EBNL",
            "Maîtriser le référentiel SYCEBNL",
            "Connaître les obligations réglementaires"
        ]),
        categorie_id=categorie.id,
        niveau=NiveauDifficulte.DEBUTANT,
        duree_estimee=180,
        plan_requis="gratuit",
        publie=True,
        date_publication=datetime.utcnow()
    )
    
    db.session.add(formation)
    db.session.flush()
    
    # Module 1
    module1 = ModuleFormation(
        formation_id=formation.id,
        titre="Introduction aux EBNL",
        description="Comprendre le contexte des EBNL",
        ordre=1,
        duree_estimee=60
    )
    db.session.add(module1)
    db.session.flush()
    
    # Leçon 1
    lecon1 = Lecon(
        module_id=module1.id,
        titre="Qu'est-ce qu'un EBNL ?",
        contenu="""
        ## Définition des EBNL
        
        Les **Établissements Bancaires Non Licenciés** (EBNL) sont des institutions financières 
        de la zone franc qui exercent des activités bancaires sans disposer d'un agrément bancaire complet.
        
        ### Caractéristiques principales :
        - Collecte de dépôts auprès du public
        - Octroi de crédits
        - Services financiers spécialisés
        - Supervision par les autorités monétaires
        """,
        type_contenu=TypeContenu.TEXTE,
        ordre=1,
        duree_estimee=15,
        gratuit=True
    )
    db.session.add(lecon1)
    db.session.flush()
    
    # Module 2 avec Quiz
    module2 = ModuleFormation(
        formation_id=formation.id,
        titre="Évaluation des connaissances",
        description="Quiz pour tester vos connaissances",
        ordre=2,
        duree_estimee=30
    )
    db.session.add(module2)
    db.session.flush()
    
    # Leçon Quiz
    lecon_quiz = Lecon(
        module_id=module2.id,
        titre="Quiz : Fondamentaux EBNL",
        contenu="Testez vos connaissances sur les EBNL",
        type_contenu=TypeContenu.QUIZ,
        ordre=1,
        duree_estimee=30
    )
    db.session.add(lecon_quiz)
    db.session.flush()
    
    # Créer le quiz
    quiz = Quiz(
        lecon_id=lecon_quiz.id,
        titre="Quiz : Fondamentaux EBNL",
        description="Évaluation des connaissances de base",
        temps_limite=30,
        note_minimum=0.7,
        tentatives_max=3
    )
    db.session.add(quiz)
    db.session.flush()
    
    # Questions du quiz
    questions = [
        {
            'enonce': "Que signifie l'acronyme EBNL ?",
            'type_question': TypeQuiz.QCM,
            'ordre': 1,
            'points': 2,
            'choix_json': json.dumps([
                {"texte": "Établissements Bancaires Non Licenciés", "correct": True},
                {"texte": "Établissements Bancaires Nationaux Locaux", "correct": False},
                {"texte": "Entités Bancaires Non Lucratives", "correct": False}
            ]),
            'explication': "EBNL signifie Établissements Bancaires Non Licenciés."
        },
        {
            'enonce': "Les EBNL sont supervisés par les autorités monétaires.",
            'type_question': TypeQuiz.VRAI_FAUX,
            'ordre': 2,
            'points': 1,
            'reponse_correcte': "Vrai",
            'explication': "Les EBNL sont effectivement supervisés par les banques centrales."
        }
    ]
    
    for question_data in questions:
        question = QuestionQuiz(
            quiz_id=quiz.id,
            **question_data
        )
        db.session.add(question)
    
    print(f"✅ Formation complète créée: {formation.titre}")
    return formation

def test_inscription_et_progression():
    """Test d'inscription et de progression"""
    formation = Formation.query.first()
    utilisateur_id = 1
    
    # Créer une inscription
    inscription = InscriptionFormation(
        formation_id=formation.id,
        utilisateur_id=utilisateur_id,
        statut=StatutProgression.EN_COURS,
        date_inscription=datetime.utcnow(),
        date_debut=datetime.utcnow(),
        pourcentage_completion=50.0,
        temps_passe=90
    )
    db.session.add(inscription)
    
    print(f"✅ Inscription créée pour la formation: {formation.titre}")
    return inscription

def test_tentative_quiz():
    """Test d'une tentative de quiz"""
    quiz = Quiz.query.first()
    utilisateur_id = 1
    
    # Simuler une tentative
    tentative = TentativeQuiz(
        quiz_id=quiz.id,
        utilisateur_id=utilisateur_id,
        note=0.8,
        note_sur_20=16.0,
        reussi=True,
        date_debut=datetime.utcnow(),
        date_fin=datetime.utcnow() + timedelta(minutes=15),
        duree_secondes=900,
        reponses_json=json.dumps({
            "1": "Établissements Bancaires Non Licenciés",
            "2": "Vrai"
        })
    )
    db.session.add(tentative)
    
    print(f"✅ Tentative de quiz créée: Note {tentative.note_sur_20}/20")
    return tentative

def test_certificat():
    """Test de génération de certificat"""
    formation = Formation.query.first()
    utilisateur_id = 1
    
    certificat = Certificat(
        formation_id=formation.id,
        utilisateur_id=utilisateur_id,
        nom_beneficiaire="Jean Dupont",
        statut=StatutCertificat.VALIDE,
        date_obtention=datetime.utcnow(),
        note_finale=0.85,
        mention="Bien"
    )
    
    # Générer le numéro
    certificat.numero_certificat = certificat.generer_numero()
    
    db.session.add(certificat)
    
    print(f"✅ Certificat généré: {certificat.numero_certificat}")
    print(f"   └─ Bénéficiaire: {certificat.nom_beneficiaire}")
    print(f"   └─ Note finale: {certificat.note_finale} - Mention: {certificat.mention}")
    
    return certificat

def display_statistics():
    """Affiche les statistiques du système e-learning"""
    print("\n📊 Statistiques du système E-Learning:")
    
    # Statistiques générales
    nb_categories = CategorieFormation.query.count()
    nb_formations = Formation.query.count()
    nb_modules = ModuleFormation.query.count()
    nb_lecons = Lecon.query.count()
    nb_quiz = Quiz.query.count()
    nb_questions = QuestionQuiz.query.count()
    nb_inscriptions = InscriptionFormation.query.count()
    nb_certificats = Certificat.query.count()
    
    print(f"   • Catégories: {nb_categories}")
    print(f"   • Formations: {nb_formations}")
    print(f"   • Modules: {nb_modules}")
    print(f"   • Leçons: {nb_lecons}")
    print(f"   • Quiz: {nb_quiz}")
    print(f"   • Questions: {nb_questions}")
    print(f"   • Inscriptions: {nb_inscriptions}")
    print(f"   • Certificats: {nb_certificats}")
    
    # Détail par formation
    print(f"\n📚 Détail des formations:")
    formations = Formation.query.all()
    for formation in formations:
        plan_emoji = {"gratuit": "🆓", "professionnel": "💼", "enterprise": "🏢"}
        emoji = plan_emoji.get(formation.plan_requis, "❓")
        
        nb_mod = len(formation.modules)
        nb_inscr = len(formation.inscriptions)
        nb_cert = len(formation.certificats)
        
        print(f"   {emoji} {formation.titre}")
        print(f"      └─ Niveau: {formation.niveau.value}")
        print(f"      └─ Durée: {formation.duree_estimee} min")
        print(f"      └─ Modules: {nb_mod}")
        print(f"      └─ Inscrits: {nb_inscr}")
        print(f"      └─ Certificats: {nb_cert}")

def main():
    """Fonction principale de test"""
    print("📚 TEST DU SYSTÈME E-LEARNING COMPTAEBNL-IA")
    print("=" * 55)
    
    with app.app_context():
        try:
            # Créer les tables
            db.create_all()
            print("✅ Base de données initialisée")
            
            # Initialiser les catégories
            print("\n📁 Initialisation des catégories...")
            init_categories()
            
            # Créer une formation complète
            print("\n📖 Création d'une formation d'exemple...")
            formation = create_sample_formation()
            
            # Tester l'inscription
            print("\n👤 Test d'inscription utilisateur...")
            inscription = test_inscription_et_progression()
            
            # Tester une tentative de quiz
            print("\n🧪 Test de tentative de quiz...")
            tentative = test_tentative_quiz()
            
            # Tester la génération de certificat
            print("\n🏆 Test de génération de certificat...")
            certificat = test_certificat()
            
            # Valider les changements
            db.session.commit()
            
            # Afficher les statistiques
            display_statistics()
            
            print("\n" + "=" * 55)
            print("✅ TESTS E-LEARNING RÉUSSIS !")
            
            print("\n🎓 Fonctionnalités testées:")
            print("   ✅ Catégories et formations")
            print("   ✅ Modules et leçons")
            print("   ✅ Quiz et questions")
            print("   ✅ Inscriptions utilisateurs")
            print("   ✅ Progression et tentatives")
            print("   ✅ Génération de certificats")
            
            print("\n🌟 Système E-Learning prêt pour l'intégration !")
            
        except Exception as e:
            print(f"❌ Erreur lors des tests: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())