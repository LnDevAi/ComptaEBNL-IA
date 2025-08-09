#!/usr/bin/env python3
"""
Initialisation du contenu E-Learning ComptaEBNL-IA
Crée les formations, modules, leçons et quiz pour la comptabilité EBNL
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Ajouter le répertoire src au PYTHONPATH  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models_elearning import *

# Configuration simple
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elearning_content.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'elearning-secret-key'

# Initialisation
db = SQLAlchemy(app)

def init_formations_fondamentaux():
    """Initialise la formation sur les fondamentaux EBNL"""
    
    # Récupérer la catégorie
    categorie = CategorieFormation.query.filter_by(nom='Fondamentaux EBNL').first()
    if not categorie:
        print("❌ Catégorie 'Fondamentaux EBNL' introuvable")
        return
    
    formation = Formation(
        titre="Initiation à la Comptabilité des EBNL",
        description="Découvrez les principes fondamentaux de la comptabilité des Établissements Bancaires de la zone franc selon le référentiel SYCEBNL.",
        objectifs=json.dumps([
            "Comprendre les spécificités comptables des EBNL",
            "Maîtriser le référentiel SYCEBNL", 
            "Connaître les obligations réglementaires",
            "Appliquer les principes comptables de base"
        ]),
        categorie_id=categorie.id,
        niveau=NiveauDifficulte.DEBUTANT,
        duree_estimee=180,  # 3 heures
        plan_requis="gratuit",
        publie=True,
        date_publication=datetime.utcnow()
    )
    
    db.session.add(formation)
    db.session.flush()
    
    # Module 1: Introduction aux EBNL
    module1 = ModuleFormation(
        formation_id=formation.id,
        titre="Introduction aux EBNL",
        description="Comprendre le contexte et les spécificités des Établissements Bancaires de la zone franc",
        ordre=1,
        duree_estimee=60
    )
    db.session.add(module1)
    db.session.flush()
    
    # Leçons du module 1
    lecons_module1 = [
        {
            'titre': "Qu'est-ce qu'un EBNL ?",
            'contenu': """
            ## Définition des EBNL

            Les **Établissements Bancaires Non Licenciés** (EBNL) sont des institutions financières de la zone franc qui exercent des activités bancaires sans disposer d'un agrément bancaire complet.

            ### Caractéristiques principales :
            - Collecte de dépôts auprès du public
            - Octroi de crédits
            - Services financiers spécialisés
            - Supervision par les autorités monétaires

            ### Types d'EBNL :
            1. **Institutions de microfinance**
            2. **Coopératives d'épargne et de crédit**
            3. **Établissements de paiement**
            4. **Bureaux de change**

            ### Importance économique :
            Les EBNL jouent un rôle crucial dans l'inclusion financière et le développement économique de la zone franc.
            """,
            'type_contenu': TypeContenu.TEXTE,
            'ordre': 1,
            'duree_estimee': 15,
            'gratuit': True
        },
        {
            'titre': "Le système financier de la zone franc",
            'contenu': """
            ## Organisation du système financier

            ### Les institutions centrales :
            - **BCEAO** : Banque Centrale des États de l'Afrique de l'Ouest
            - **BEAC** : Banque des États de l'Afrique Centrale
            - **COBAC** : Commission Bancaire de l'Afrique Centrale
            - **CBS** : Commission Bancaire de l'UMOA

            ### Supervision et régulation :
            Les EBNL sont soumis à une réglementation spécifique adaptée à leurs activités et leur taille.

            ### Cadre légal :
            - Loi bancaire CEMAC/UEMOA
            - Instructions de supervision
            - Normes prudentielles adaptées
            """,
            'type_contenu': TypeContenu.TEXTE,
            'ordre': 2,
            'duree_estimee': 20
        },
        {
            'titre': "Obligations comptables des EBNL",
            'contenu': """
            ## Obligations réglementaires

            ### Tenue de la comptabilité :
            - Respect du plan comptable SYCEBNL
            - Enregistrement chronologique des opérations
            - Conservation des pièces justificatives
            - Établissement des états financiers

            ### Reporting réglementaire :
            - États périodiques à la Banque Centrale
            - Déclarations de supervision
            - Rapport d'activité annuel
            - Audit externe obligatoire

            ### Sanctions en cas de non-respect :
            - Amendes administratives
            - Restrictions d'activité
            - Retrait d'agrément
            """,
            'type_contenu': TypeContenu.TEXTE,
            'ordre': 3,
            'duree_estimee': 25
        }
    ]
    
    for lecon_data in lecons_module1:
        lecon = Lecon(
            module_id=module1.id,
            **lecon_data
        )
        db.session.add(lecon)
    
    # Module 2: Le référentiel SYCEBNL
    module2 = ModuleFormation(
        formation_id=formation.id,
        titre="Le référentiel comptable SYCEBNL",
        description="Maîtrise du Système Comptable des EBNL",
        ordre=2,
        duree_estimee=90
    )
    db.session.add(module2)
    db.session.flush()
    
    # Leçons du module 2
    lecons_module2 = [
        {
            'titre': "Présentation du SYCEBNL",
            'contenu': """
            ## Le Système Comptable des EBNL

            ### Objectifs du SYCEBNL :
            - Harmoniser les pratiques comptables
            - Améliorer la transparence financière
            - Faciliter la supervision
            - Permettre les comparaisons inter-établissements

            ### Principes fondamentaux :
            1. **Image fidèle** : Les comptes doivent donner une image fidèle de la situation
            2. **Régularité** : Respect des règles et procédures
            3. **Sincérité** : Bonne foi dans l'évaluation
            4. **Prudence** : Prise en compte des risques

            ### Structure du référentiel :
            - Plan de comptes standardisé
            - Règles d'évaluation
            - Modèles d'états financiers
            - Instructions d'application
            """,
            'type_contenu': TypeContenu.TEXTE,
            'ordre': 1,
            'duree_estimee': 30
        },
        {
            'titre': "Architecture du plan de comptes",
            'contenu': """
            ## Organisation du plan comptable

            ### Classes de comptes :
            - **Classe 1** : Comptes de bilan - Passif
            - **Classe 2** : Comptes de bilan - Actif immobilisé
            - **Classe 3** : Comptes de bilan - Actif circulant
            - **Classe 4** : Comptes de tiers
            - **Classe 5** : Comptes de trésorerie
            - **Classe 6** : Comptes de charges
            - **Classe 7** : Comptes de produits
            - **Classe 8** : Comptes spéciaux EBNL

            ### Codification :
            - 3 chiffres minimum
            - Subdivision par spécialité
            - Codes réservés par activité

            ### Spécificités EBNL :
            - Comptes dédiés aux opérations bancaires
            - Suivi des engagements hors bilan
            - Provisions spécifiques aux risques
            """,
            'type_contenu': TypeContenu.TEXTE,
            'ordre': 2,
            'duree_estimee': 35
        },
        {
            'titre': "Règles d'évaluation",
            'contenu': """
            ## Principes d'évaluation SYCEBNL

            ### Coût historique :
            - Valorisation à la date d'acquisition
            - Amortissements et provisions
            - Réévaluations exceptionnelles

            ### Évaluation des créances :
            - Valeur nominale
            - Provisions pour risques
            - Classification par qualité

            ### Instruments financiers :
            - Titres de placement
            - Titres d'investissement
            - Dérivés et couverture

            ### Change :
            - Conversion des devises
            - Couverture du risque de change
            - Positions nettes
            """,
            'type_contenu': TypeContenu.TEXTE,
            'ordre': 3,
            'duree_estimee': 25
        }
    ]
    
    for lecon_data in lecons_module2:
        lecon = Lecon(
            module_id=module2.id,
            **lecon_data
        )
        db.session.add(lecon)
    
    # Module 3: Quiz d'évaluation
    module3 = ModuleFormation(
        formation_id=formation.id,
        titre="Évaluation des connaissances",
        description="Quiz pour valider votre compréhension des fondamentaux",
        ordre=3,
        duree_estimee=30
    )
    db.session.add(module3)
    db.session.flush()
    
    # Leçon quiz
    lecon_quiz = Lecon(
        module_id=module3.id,
        titre="Quiz : Fondamentaux EBNL",
        contenu="Testez vos connaissances sur les fondamentaux de la comptabilité EBNL",
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
        description="Évaluation des connaissances de base sur les EBNL et SYCEBNL",
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
                {"texte": "Entités Bancaires Non Lucratives", "correct": False},
                {"texte": "Établissements Bancaires Nouveaux Labels", "correct": False}
            ]),
            'explication': "EBNL signifie Établissements Bancaires Non Licenciés, qui sont des institutions financières sans agrément bancaire complet."
        },
        {
            'enonce': "Quelles sont les deux banques centrales de la zone franc ?",
            'type_question': TypeQuiz.QCM,
            'ordre': 2,
            'points': 2,
            'choix_json': json.dumps([
                {"texte": "BCEAO et BEAC", "correct": True},
                {"texte": "BCC et BCEAO", "correct": False},
                {"texte": "BEAC et BDF", "correct": False},
                {"texte": "COBAC et CBS", "correct": False}
            ]),
            'explication': "La BCEAO supervise l'UMOA (Afrique de l'Ouest) et la BEAC supervise la CEMAC (Afrique Centrale)."
        },
        {
            'enonce': "SYCEBNL est le référentiel comptable des EBNL.",
            'type_question': TypeQuiz.VRAI_FAUX,
            'ordre': 3,
            'points': 1,
            'reponse_correcte': "Vrai",
            'explication': "SYCEBNL (Système Comptable des EBNL) est effectivement le référentiel comptable spécialement conçu pour les EBNL."
        },
        {
            'enonce': "Combien y a-t-il de classes de comptes dans le plan comptable SYCEBNL ?",
            'type_question': TypeQuiz.REPONSE_LIBRE,
            'ordre': 4,
            'points': 2,
            'reponse_correcte': "8",
            'explication': "Le plan comptable SYCEBNL comporte 8 classes de comptes (Classes 1 à 8)."
        },
        {
            'enonce': "Quel principe impose de prendre en compte les risques potentiels dans l'évaluation ?",
            'type_question': TypeQuiz.QCM,
            'ordre': 5,
            'points': 2,
            'choix_json': json.dumps([
                {"texte": "Principe de prudence", "correct": True},
                {"texte": "Principe de sincérité", "correct": False},
                {"texte": "Principe de régularité", "correct": False},
                {"texte": "Principe d'image fidèle", "correct": False}
            ]),
            'explication': "Le principe de prudence impose de prendre en compte tous les risques et pertes probables."
        }
    ]
    
    for question_data in questions:
        question = QuestionQuiz(
            quiz_id=quiz.id,
            **question_data
        )
        db.session.add(question)
    
    print(f"✅ Formation '{formation.titre}' créée avec {len(formation.modules)} modules")
    return formation

def init_formation_plan_comptable():
    """Initialise la formation sur le plan comptable"""
    
    categorie = CategorieFormation.query.filter_by(nom='Plan Comptable').first()
    if not categorie:
        print("❌ Catégorie 'Plan Comptable' introuvable")
        return
    
    formation = Formation(
        titre="Maîtrise du Plan Comptable SYCEBNL",
        description="Formation approfondie sur l'utilisation du plan comptable spécifique aux EBNL",
        objectifs=json.dumps([
            "Naviguer efficacement dans le plan comptable SYCEBNL",
            "Maîtriser la codification et la structure des comptes",
            "Comprendre les spécificités de chaque classe de comptes",
            "Savoir choisir les comptes appropriés pour chaque opération"
        ]),
        categorie_id=categorie.id,
        niveau=NiveauDifficulte.INTERMEDIAIRE,
        duree_estimee=240,  # 4 heures
        plan_requis="professionnel",
        publie=True,
        date_publication=datetime.utcnow()
    )
    
    db.session.add(formation)
    db.session.flush()
    
    # Module 1: Classes de comptes de bilan
    module1 = ModuleFormation(
        formation_id=formation.id,
        titre="Comptes de Bilan (Classes 1, 2, 3)",
        description="Étude détaillée des comptes de bilan selon SYCEBNL",
        ordre=1,
        duree_estimee=90
    )
    db.session.add(module1)
    db.session.flush()
    
    # Module 2: Comptes de gestion  
    module2 = ModuleFormation(
        formation_id=formation.id,
        titre="Comptes de Gestion (Classes 6, 7)",
        description="Maîtrise des comptes de charges et produits",
        ordre=2,
        duree_estimee=80
    )
    db.session.add(module2)
    db.session.flush()
    
    # Module 3: Comptes spécialisés EBNL
    module3 = ModuleFormation(
        formation_id=formation.id,
        titre="Comptes Spécialisés EBNL (Classes 4, 5, 8)",
        description="Comptes spécifiques aux activités bancaires des EBNL",
        ordre=3,
        duree_estimee=70
    )
    db.session.add(module3)
    db.session.flush()
    
    print(f"✅ Formation '{formation.titre}' créée avec {len(formation.modules)} modules")
    return formation

def init_formation_etats_financiers():
    """Initialise la formation sur les états financiers"""
    
    categorie = CategorieFormation.query.filter_by(nom='États Financiers').first()
    if not categorie:
        print("❌ Catégorie 'États Financiers' introuvable")
        return
    
    formation = Formation(
        titre="Élaboration et Analyse des États Financiers EBNL",
        description="Formation complète sur la production et l'analyse des états financiers selon SYCEBNL",
        objectifs=json.dumps([
            "Élaborer les états financiers obligatoires",
            "Maîtriser les techniques d'analyse financière",
            "Calculer et interpréter les ratios financiers",
            "Détecter les anomalies et risques"
        ]),
        categorie_id=categorie.id,
        niveau=NiveauDifficulte.AVANCE,
        duree_estimee=360,  # 6 heures
        plan_requis="enterprise",
        publie=True,
        date_publication=datetime.utcnow()
    )
    
    db.session.add(formation)
    db.session.flush()
    
    # Modules de la formation
    modules_data = [
        {
            'titre': "Bilan et Annexes",
            'description': "Construction et analyse du bilan EBNL",
            'duree_estimee': 120
        },
        {
            'titre': "Compte de Résultat",
            'description': "Élaboration et analyse du compte de résultat",
            'duree_estimee': 90
        },
        {
            'titre': "États de Synthèse",
            'description': "Tableau de flux et autres états obligatoires",
            'duree_estimee': 80
        },
        {
            'titre': "Analyse Financière",
            'description': "Ratios, tendances et diagnostic financier",
            'duree_estimee': 70
        }
    ]
    
    for i, module_data in enumerate(modules_data, 1):
        module = ModuleFormation(
            formation_id=formation.id,
            ordre=i,
            **module_data
        )
        db.session.add(module)
    
    print(f"✅ Formation '{formation.titre}' créée avec {len(modules_data)} modules")
    return formation

def main():
    """Fonction principale d'initialisation du contenu"""
    print("📚 INITIALISATION DU CONTENU E-LEARNING COMPTAEBNL-IA")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Créer les tables
            db.create_all()
            print("✅ Base de données initialisée")
            
            # Initialiser les catégories
            print("\n📁 Initialisation des catégories...")
            init_categories_formation()
            
            # Initialiser les formations
            print("\n📖 Initialisation des formations...")
            
            # Formation fondamentaux (accessible à tous)
            formation1 = init_formations_fondamentaux()
            
            # Formation plan comptable (plan professionnel)
            formation2 = init_formation_plan_comptable()
            
            # Formation états financiers (plan enterprise)
            formation3 = init_formation_etats_financiers()
            
            # Valider les changements
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ CONTENU E-LEARNING INITIALISÉ AVEC SUCCÈS !")
            
            # Statistiques
            nb_categories = CategorieFormation.query.count()
            nb_formations = Formation.query.count()
            nb_modules = ModuleFormation.query.count()
            nb_lecons = Lecon.query.count()
            nb_quiz = Quiz.query.count()
            
            print(f"\n📊 Statistiques du contenu :")
            print(f"   • Catégories : {nb_categories}")
            print(f"   • Formations : {nb_formations}")
            print(f"   • Modules : {nb_modules}")
            print(f"   • Leçons : {nb_lecons}")
            print(f"   • Quiz : {nb_quiz}")
            
            print(f"\n🎓 Formations par niveau d'abonnement :")
            formations = Formation.query.all()
            for formation in formations:
                plan_emoji = {"gratuit": "🆓", "professionnel": "💼", "enterprise": "🏢"}
                emoji = plan_emoji.get(formation.plan_requis, "❓")
                print(f"   {emoji} {formation.titre} ({formation.plan_requis})")
                print(f"      └─ {formation.duree_estimee} min, {len(formation.modules)} modules")
            
            print(f"\n🌟 Prêt pour l'apprentissage de la comptabilité EBNL !")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())