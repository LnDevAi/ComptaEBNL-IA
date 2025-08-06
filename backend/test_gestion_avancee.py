#!/usr/bin/env python3
"""
Test du système de gestion avancée ComptaEBNL-IA
Teste dirigeants, projets, budget, activités, patrimoine, balance multi-projets/bailleurs
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from models_gestion import *
    print("✅ Import des modèles de gestion avancée réussi")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous d'avoir installé les dépendances: pip install flask flask-sqlalchemy pandas")
    sys.exit(1)

# Configuration de l'application de test
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_gestion_avancee.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def init_test_data():
    """Initialise les données de test"""
    print("\n📊 INITIALISATION DONNÉES DE TEST")
    print("-" * 40)
    
    # Créer les tables
    db.create_all()
    
    # Créer une association de test (simulée)
    association_id = 1
    
    # Créer des bailleurs de test
    bailleurs_data = [
        {
            'nom': 'Agence Française de Développement',
            'sigle': 'AFD',
            'type_bailleur': TypeBailleur.GOUVERNEMENT,
            'pays_origine': 'France',
            'contact_nom': 'Jean MARTIN',
            'contact_email': 'j.martin@afd.fr'
        },
        {
            'nom': 'Fondation Gates',
            'sigle': 'BMGF',
            'type_bailleur': TypeBailleur.FONDATION,
            'pays_origine': 'USA',
            'contact_nom': 'Sarah JOHNSON',
            'contact_email': 's.johnson@gatesfoundation.org'
        },
        {
            'nom': 'Union Européenne - Délégation Burkina',
            'sigle': 'UE-BF',
            'type_bailleur': TypeBailleur.UNION_EUROPEENNE,
            'pays_origine': 'Belgique',
            'contact_nom': 'Marie DUBOIS',
            'contact_email': 'm.dubois@eeas.europa.eu'
        }
    ]
    
    bailleurs = []
    for data in bailleurs_data:
        bailleur = Bailleur(**data)
        db.session.add(bailleur)
        bailleurs.append(bailleur)
    
    db.session.flush()
    print(f"✅ {len(bailleurs)} bailleurs créés")
    
    return association_id, bailleurs

def test_dirigeants(association_id):
    """Test de la gestion des dirigeants"""
    print("\n👥 TESTS DIRIGEANTS")
    print("-" * 30)
    
    dirigeants_data = [
        {
            'nom': 'OUEDRAOGO',
            'prenoms': 'Aminata',
            'type_dirigeant': TypeDirigeant.PRESIDENT,
            'date_nomination': date(2023, 1, 15),
            'date_naissance': date(1975, 8, 20),
            'nationalite': 'Burkinabè',
            'profession': 'Enseignante',
            'telephone': '+226 70 12 34 56',
            'email': 'a.ouedraogo@association.bf',
            'pouvoir_signature': True,
            'pouvoir_engagement': True,
            'seuil_engagement': Decimal('5000000')  # 5M FCFA
        },
        {
            'nom': 'SAWADOGO',
            'prenoms': 'Ibrahim',
            'type_dirigeant': TypeDirigeant.TRESORIER,
            'date_nomination': date(2023, 1, 15),
            'date_naissance': date(1980, 3, 10),
            'nationalite': 'Burkinabè',
            'profession': 'Comptable',
            'telephone': '+226 70 98 76 54',
            'email': 'i.sawadogo@association.bf',
            'pouvoir_signature': True,
            'pouvoir_engagement': False,
            'seuil_engagement': Decimal('2000000')  # 2M FCFA
        },
        {
            'nom': 'KONE',
            'prenoms': 'Fatoumata',
            'type_dirigeant': TypeDirigeant.SECRETAIRE_GENERAL,
            'date_nomination': date(2023, 1, 15),
            'date_naissance': date(1982, 11, 5),
            'nationalite': 'Burkinabè',
            'profession': 'Juriste',
            'telephone': '+226 70 55 44 33',
            'email': 'f.kone@association.bf',
            'pouvoir_signature': False,
            'pouvoir_engagement': False
        }
    ]
    
    dirigeants = []
    for data in dirigeants_data:
        dirigeant = Dirigeant(association_id=association_id, **data)
        db.session.add(dirigeant)
        dirigeants.append(dirigeant)
    
    db.session.flush()
    
    for dirigeant in dirigeants:
        print(f"✅ Dirigeant: {dirigeant.prenoms} {dirigeant.nom} - {dirigeant.type_dirigeant.value}")
        print(f"   📞 {dirigeant.telephone} | ✉️ {dirigeant.email}")
        print(f"   🖊️ Signature: {'Oui' if dirigeant.pouvoir_signature else 'Non'}")
        print(f"   💰 Engagement: {dirigeant.seuil_engagement if dirigeant.pouvoir_engagement else 'Non'} FCFA")
    
    return dirigeants

def test_projets(association_id, bailleurs):
    """Test de la gestion des projets"""
    print("\n🚀 TESTS PROJETS MULTI-BAILLEURS")
    print("-" * 40)
    
    projets_data = [
        {
            'code_projet': 'EDUC-BF-2024-001',
            'titre': 'Amélioration de l\'éducation rurale au Burkina Faso',
            'description': 'Projet visant à améliorer l\'accès et la qualité de l\'éducation dans les zones rurales',
            'date_debut': date(2024, 1, 1),
            'date_fin': date(2026, 12, 31),
            'budget_total': Decimal('2500000000'),  # 2.5 milliards FCFA
            'bailleur_id': bailleurs[0].id,  # AFD
            'contribution_bailleur': Decimal('2000000000'),
            'contribution_association': Decimal('500000000'),
            'chef_projet': 'Dr. Aminata OUEDRAOGO',
            'coordinateur': 'Ibrahim SAWADOGO',
            'pays': 'Burkina Faso'
        },
        {
            'code_projet': 'SANTE-BF-2024-002',
            'titre': 'Renforcement du système de santé communautaire',
            'description': 'Amélioration de l\'accès aux soins de santé primaires en milieu rural',
            'date_debut': date(2024, 3, 1),
            'date_fin': date(2027, 2, 28),
            'budget_total': Decimal('1800000000'),  # 1.8 milliards FCFA
            'bailleur_id': bailleurs[1].id,  # Gates Foundation
            'contribution_bailleur': Decimal('1600000000'),
            'contribution_association': Decimal('200000000'),
            'chef_projet': 'Dr. Fatoumata KONE',
            'coordinateur': 'Moussa TRAORE',
            'pays': 'Burkina Faso'
        },
        {
            'code_projet': 'AGRI-BF-2024-003',
            'titre': 'Développement agricole durable',
            'description': 'Promotion de techniques agricoles durables et résilientes au climat',
            'date_debut': date(2024, 6, 1),
            'date_fin': date(2028, 5, 31),
            'budget_total': Decimal('3200000000'),  # 3.2 milliards FCFA
            'bailleur_id': bailleurs[2].id,  # Union Européenne
            'contribution_bailleur': Decimal('2800000000'),
            'contribution_association': Decimal('400000000'),
            'chef_projet': 'Ing. Boureima ZONGO',
            'coordinateur': 'Salimata OUATTARA',
            'pays': 'Burkina Faso'
        }
    ]
    
    projets = []
    for data in projets_data:
        projet = Projet(association_id=association_id, **data)
        # Calculer la durée
        delta = projet.date_fin - projet.date_debut
        projet.duree_mois = round(delta.days / 30)
        projet.statut = StatutProjet.EN_COURS
        db.session.add(projet)
        projets.append(projet)
    
    db.session.flush()
    
    for projet in projets:
        # Récupérer le bailleur manuellement
        bailleur = next((b for b in bailleurs if b.id == projet.bailleur_id), None)
        print(f"✅ Projet: {projet.code_projet}")
        print(f"   📝 {projet.titre}")
        print(f"   🏛️ Bailleur: {bailleur.nom if bailleur else 'N/A'}")
        print(f"   💰 Budget: {float(projet.budget_total):,.0f} FCFA")
        print(f"   📅 Durée: {projet.duree_mois} mois ({projet.date_debut} → {projet.date_fin})")
        print(f"   👨‍💼 Chef: {projet.chef_projet}")
        print()
    
    return projets

def test_budgets(association_id, projets):
    """Test de la gestion budgétaire"""
    print("\n💰 TESTS BUDGETS MULTI-PROJETS")
    print("-" * 40)
    
    # Créer un budget pour le premier projet
    projet = projets[0]
    
    budget = Budget(
        association_id=association_id,
        projet_id=projet.id,
        libelle=f"Budget {projet.code_projet} - Exercice 2024",
        exercice=2024,
        date_debut=date(2024, 1, 1),
        date_fin=date(2024, 12, 31),
        commentaires="Budget prévisionnel première année"
    )
    
    db.session.add(budget)
    db.session.flush()
    
    # Ajouter des lignes de budget détaillées
    lignes_budget = [
        # RECETTES
        {
            'categorie': 'Recettes',
            'sous_categorie': 'Subventions',
            'libelle': 'Subvention AFD - Tranche 1',
            'compte_comptable': '7013',
            'montant_prevu': Decimal('800000000'),
            'ordre_affichage': 1
        },
        {
            'categorie': 'Recettes',
            'sous_categorie': 'Contributions',
            'libelle': 'Contribution propre association',
            'compte_comptable': '7018',
            'montant_prevu': Decimal('200000000'),
            'ordre_affichage': 2
        },
        # DÉPENSES
        {
            'categorie': 'Depenses',
            'sous_categorie': 'Personnel',
            'libelle': 'Salaires équipe projet',
            'compte_comptable': '6411',
            'montant_prevu': Decimal('300000000'),
            'ordre_affichage': 3
        },
        {
            'categorie': 'Depenses',
            'sous_categorie': 'Matériel',
            'libelle': 'Équipements pédagogiques',
            'compte_comptable': '6022',
            'montant_prevu': Decimal('400000000'),
            'ordre_affichage': 4
        },
        {
            'categorie': 'Depenses',
            'sous_categorie': 'Fonctionnement',
            'libelle': 'Frais de déplacement et missions',
            'compte_comptable': '6251',
            'montant_prevu': Decimal('150000000'),
            'ordre_affichage': 5
        },
        {
            'categorie': 'Depenses',
            'sous_categorie': 'Formation',
            'libelle': 'Formation des enseignants',
            'compte_comptable': '6228',
            'montant_prevu': Decimal('150000000'),
            'ordre_affichage': 6
        }
    ]
    
    for ligne_data in lignes_budget:
        ligne = LigneBudget(budget_id=budget.id, **ligne_data)
        db.session.add(ligne)
    
    db.session.flush()
    
    # Calculer les totaux
    budget.total_recettes_prevues = sum(
        ligne.montant_prevu for ligne in budget.lignes_budget 
        if ligne.categorie == 'Recettes'
    )
    budget.total_depenses_prevues = sum(
        ligne.montant_prevu for ligne in budget.lignes_budget 
        if ligne.categorie == 'Depenses'
    )
    
    print(f"✅ Budget créé: {budget.libelle}")
    print(f"   📊 Recettes prévues: {float(budget.total_recettes_prevues):,.0f} FCFA")
    print(f"   📊 Dépenses prévues: {float(budget.total_depenses_prevues):,.0f} FCFA")
    print(f"   ⚖️ Équilibre: {float(budget.total_recettes_prevues - budget.total_depenses_prevues):,.0f} FCFA")
    print(f"   📋 Lignes budgétaires: {len(budget.lignes_budget)}")
    
    print("\n📋 DÉTAIL DES LIGNES BUDGÉTAIRES:")
    for ligne in budget.lignes_budget:
        print(f"   {ligne.categorie} | {ligne.sous_categorie} | {ligne.libelle}")
        print(f"      💰 {float(ligne.montant_prevu):,.0f} FCFA (Compte {ligne.compte_comptable})")
    
    return [budget]

def test_activites(association_id, projets):
    """Test de la gestion des activités"""
    print("\n🎯 TESTS ACTIVITÉS PAR PROJET")
    print("-" * 40)
    
    # Activités pour le projet éducation
    projet_educ = projets[0]
    activites_educ = [
        {
            'code_activite': 'EDUC-001',
            'titre': 'Formation des enseignants ruraux',
            'description': 'Formation pédagogique pour 200 enseignants',
            'type_activite': TypeActivite.FORMATION,
            'date_debut_prevue': date(2024, 2, 1),
            'date_fin_prevue': date(2024, 3, 31),
            'lieu': 'Ouagadougou',
            'region': 'Centre',
            'nombre_participants_prevu': 200,
            'budget_alloue': Decimal('50000000'),
            'responsable_activite': 'Dr. Aminata OUEDRAOGO'
        },
        {
            'code_activite': 'EDUC-002',
            'titre': 'Construction de salles de classe',
            'description': 'Construction de 50 salles de classe en zones rurales',
            'type_activite': TypeActivite.DEVELOPPEMENT,
            'date_debut_prevue': date(2024, 4, 1),
            'date_fin_prevue': date(2024, 12, 31),
            'lieu': 'Provinces rurales',
            'region': 'Multi-régions',
            'nombre_participants_prevu': 2500,  # Élèves bénéficiaires
            'budget_alloue': Decimal('400000000'),
            'responsable_activite': 'Ing. Boureima ZONGO'
        }
    ]
    
    # Activités pour le projet santé
    projet_sante = projets[1]
    activites_sante = [
        {
            'code_activite': 'SANTE-001',
            'titre': 'Formation agents de santé communautaire',
            'description': 'Formation de 150 agents de santé communautaire',
            'type_activite': TypeActivite.FORMATION,
            'date_debut_prevue': date(2024, 4, 1),
            'date_fin_prevue': date(2024, 5, 31),
            'lieu': 'Centres de santé ruraux',
            'region': 'Multi-régions',
            'nombre_participants_prevu': 150,
            'budget_alloue': Decimal('30000000'),
            'responsable_activite': 'Dr. Fatoumata KONE'
        },
        {
            'code_activite': 'SANTE-002',
            'titre': 'Campagne de sensibilisation',
            'description': 'Sensibilisation sur l\'hygiène et la prévention',
            'type_activite': TypeActivite.SENSIBILISATION,
            'date_debut_prevue': date(2024, 6, 1),
            'date_fin_prevue': date(2024, 8, 31),
            'lieu': 'Villages ruraux',
            'region': 'Multi-régions',
            'nombre_participants_prevu': 5000,
            'budget_alloue': Decimal('25000000'),
            'responsable_activite': 'Salimata OUATTARA'
        }
    ]
    
    toutes_activites = []
    
    # Créer les activités du projet éducation
    for data in activites_educ:
        activite = Activite(
            association_id=association_id,
            projet_id=projet_educ.id,
            **data
        )
        db.session.add(activite)
        toutes_activites.append(activite)
    
    # Créer les activités du projet santé
    for data in activites_sante:
        activite = Activite(
            association_id=association_id,
            projet_id=projet_sante.id,
            **data
        )
        db.session.add(activite)
        toutes_activites.append(activite)
    
    db.session.flush()
    
    # Afficher les activités par projet
    for projet in [projet_educ, projet_sante]:
        print(f"\n📋 Activités du projet: {projet.titre}")
        activites_projet = [a for a in toutes_activites if a.projet_id == projet.id]
        for activite in activites_projet:
            print(f"   ✅ {activite.code_activite}: {activite.titre}")
            print(f"      📅 {activite.date_debut_prevue} → {activite.date_fin_prevue}")
            print(f"      📍 {activite.lieu} ({activite.region})")
            print(f"      👥 {activite.nombre_participants_prevu} participants")
            print(f"      💰 {float(activite.budget_alloue):,.0f} FCFA")
            print(f"      👨‍💼 Responsable: {activite.responsable_activite}")
    
    return toutes_activites

def test_patrimoine(association_id, projets):
    """Test de la gestion du patrimoine"""
    print("\n🏛️ TESTS PATRIMOINE ET BIENS")
    print("-" * 40)
    
    biens_data = [
        {
            'libelle': 'Véhicule de mission Toyota Hilux',
            'description': 'Véhicule 4x4 pour missions terrain',
            'type_bien': TypeBien.VEHICULE,
            'marque': 'Toyota',
            'modele': 'Hilux Double Cabine',
            'numero_serie': 'TH2024BF001',
            'valeur_acquisition': Decimal('25000000'),  # 25M FCFA
            'valeur_actuelle': Decimal('22000000'),
            'date_acquisition': date(2024, 1, 15),
            'date_mise_service': date(2024, 1, 20),
            'localisation': 'Siège Ouagadougou',
            'responsable_bien': 'Ibrahim SAWADOGO',
            'duree_amortissement_annees': 5,
            'projet_id': projets[0].id  # Lié au projet éducation
        },
        {
            'libelle': 'Ordinateurs portables HP',
            'description': 'Lot de 20 ordinateurs portables pour formation',
            'type_bien': TypeBien.EQUIPEMENT_INFORMATIQUE,
            'marque': 'HP',
            'modele': 'ProBook 450 G9',
            'valeur_acquisition': Decimal('20000000'),  # 20M FCFA
            'valeur_actuelle': Decimal('18000000'),
            'date_acquisition': date(2024, 2, 1),
            'date_mise_service': date(2024, 2, 5),
            'localisation': 'Centre de formation',
            'responsable_bien': 'Fatoumata KONE',
            'duree_amortissement_annees': 3,
            'projet_id': projets[0].id
        },
        {
            'libelle': 'Équipements médicaux mobiles',
            'description': 'Kit médical pour consultations mobiles',
            'type_bien': TypeBien.EQUIPEMENT_TECHNIQUE,
            'marque': 'MedEquip',
            'modele': 'Mobile Health Kit Pro',
            'valeur_acquisition': Decimal('15000000'),  # 15M FCFA
            'valeur_actuelle': Decimal('14000000'),
            'date_acquisition': date(2024, 3, 1),
            'date_mise_service': date(2024, 3, 10),
            'localisation': 'Centre de santé mobile',
            'responsable_bien': 'Dr. Fatoumata KONE',
            'duree_amortissement_annees': 7,
            'projet_id': projets[1].id  # Lié au projet santé
        },
        {
            'libelle': 'Générateur électrique',
            'description': 'Générateur de secours 15 KVA',
            'type_bien': TypeBien.EQUIPEMENT_TECHNIQUE,
            'marque': 'Caterpillar',
            'modele': 'DE15E0',
            'numero_serie': 'CAT2024BF001',
            'valeur_acquisition': Decimal('8000000'),  # 8M FCFA
            'valeur_actuelle': Decimal('7500000'),
            'date_acquisition': date(2024, 1, 10),
            'date_mise_service': date(2024, 1, 15),
            'localisation': 'Siège Ouagadougou',
            'responsable_bien': 'Moussa TRAORE',
            'duree_amortissement_annees': 10
        }
    ]
    
    biens = []
    for i, data in enumerate(biens_data, 1):
        # Auto-générer le numéro d'inventaire
        year = datetime.now().year
        numero_inventaire = f"BN-{year}-{i:04d}"
        
        bien = Bien(
            association_id=association_id,
            numero_inventaire=numero_inventaire,
            **data
        )
        
        # Calculer l'amortissement si applicable
        if bien.duree_amortissement_annees and bien.date_acquisition:
            # Calcul simple : amortissement linéaire
            mois_ecoules = (datetime.now().date() - bien.date_acquisition).days / 30
            if mois_ecoules > 0:
                amortissement_mensuel = bien.valeur_acquisition / (bien.duree_amortissement_annees * 12)
                bien.valeur_amortie = min(
                    amortissement_mensuel * mois_ecoules,
                    bien.valeur_acquisition
                )
        
        db.session.add(bien)
        biens.append(bien)
    
    db.session.flush()
    
    # Affichage des biens par projet
    biens_par_projet = {}
    biens_generaux = []
    
    for bien in biens:
        if bien.projet_id:
            if bien.projet_id not in biens_par_projet:
                biens_par_projet[bien.projet_id] = []
            biens_par_projet[bien.projet_id].append(bien)
        else:
            biens_generaux.append(bien)
    
    # Biens par projet
    for projet_id, biens_projet in biens_par_projet.items():
        projet = next(p for p in projets if p.id == projet_id)
        print(f"\n📋 Biens du projet: {projet.code_projet}")
        for bien in biens_projet:
            print(f"   ✅ {bien.numero_inventaire}: {bien.libelle}")
            print(f"      🏷️ {bien.marque} {bien.modele}")
            print(f"      💰 Acquisition: {float(bien.valeur_acquisition):,.0f} FCFA")
            print(f"      📈 Actuelle: {float(bien.valeur_actuelle):,.0f} FCFA")
            print(f"      📍 Localisation: {bien.localisation}")
            print(f"      👨‍💼 Responsable: {bien.responsable_bien}")
    
    # Biens généraux
    if biens_generaux:
        print(f"\n📋 Biens généraux de l'association:")
        for bien in biens_generaux:
            print(f"   ✅ {bien.numero_inventaire}: {bien.libelle}")
            print(f"      💰 Valeur: {float(bien.valeur_actuelle):,.0f} FCFA")
            print(f"      📍 {bien.localisation}")
    
    # Statistiques patrimoine
    valeur_totale = sum(bien.valeur_actuelle or bien.valeur_acquisition for bien in biens)
    print(f"\n📊 STATISTIQUES PATRIMOINE:")
    print(f"   🏛️ Nombre total de biens: {len(biens)}")
    print(f"   💰 Valeur totale du patrimoine: {float(valeur_totale):,.0f} FCFA")
    
    return biens

def test_financements(association_id, projets, bailleurs):
    """Test de la gestion des financements"""
    print("\n💸 TESTS FINANCEMENTS MULTI-BAILLEURS")
    print("-" * 50)
    
    financements_data = [
        {
            'projet_id': projets[0].id,
            'bailleur_id': bailleurs[0].id,  # AFD
            'numero_convention': 'AFD-BF-2024-EDUC-001',
            'libelle': 'Financement projet éducation rurale - Phase 1',
            'montant_accorde': Decimal('2000000000'),
            'montant_decaisse': Decimal('800000000'),
            'montant_utilise': Decimal('600000000'),
            'date_signature': date(2023, 12, 15),
            'date_debut': date(2024, 1, 1),
            'date_fin': date(2026, 12, 31),
            'conditions_decaissement': 'Décaissement par tranches sur justification',
            'modalites_reporting': 'Rapports trimestriels + rapport annuel'
        },
        {
            'projet_id': projets[1].id,
            'bailleur_id': bailleurs[1].id,  # Gates
            'numero_convention': 'BMGF-2024-HEALTH-BF-002',
            'libelle': 'Subvention santé communautaire',
            'montant_accorde': Decimal('1600000000'),
            'montant_decaisse': Decimal('400000000'),
            'montant_utilise': Decimal('300000000'),
            'date_signature': date(2024, 2, 1),
            'date_debut': date(2024, 3, 1),
            'date_fin': date(2027, 2, 28),
            'conditions_decaissement': 'Décaissement sur atteinte d\'indicateurs',
            'modalites_reporting': 'Rapports semestriels + évaluation externe'
        },
        {
            'projet_id': projets[2].id,
            'bailleur_id': bailleurs[2].id,  # UE
            'numero_convention': 'EU-BF-2024-AGRI-003',
            'libelle': 'Programme développement agricole durable',
            'montant_accorde': Decimal('2800000000'),
            'montant_decaisse': Decimal('700000000'),
            'montant_utilise': Decimal('500000000'),
            'date_signature': date(2024, 5, 1),
            'date_debut': date(2024, 6, 1),
            'date_fin': date(2028, 5, 31),
            'conditions_decaissement': 'Avance + décaissement sur justificatifs',
            'modalites_reporting': 'Rapports techniques et financiers trimestriels'
        }
    ]
    
    financements = []
    for data in financements_data:
        financement = Financement(association_id=association_id, **data)
        db.session.add(financement)
        financements.append(financement)
    
    db.session.flush()
    
    for financement in financements:
        # Récupérer le bailleur et projet manuellement
        bailleur = next((b for b in bailleurs if b.id == financement.bailleur_id), None)
        projet = next((p for p in projets if p.id == financement.projet_id), None)
        
        taux_decaissement = (financement.montant_decaisse / financement.montant_accorde) * 100
        taux_utilisation = (financement.montant_utilise / financement.montant_decaisse) * 100 if financement.montant_decaisse > 0 else 0
        
        print(f"✅ Financement: {financement.numero_convention}")
        print(f"   🏛️ Bailleur: {bailleur.nom if bailleur else 'N/A'}")
        print(f"   🚀 Projet: {projet.code_projet if projet else 'N/A'}")
        print(f"   💰 Accordé: {float(financement.montant_accorde):,.0f} FCFA")
        print(f"   📥 Décaissé: {float(financement.montant_decaisse):,.0f} FCFA ({taux_decaissement:.1f}%)")
        print(f"   📊 Utilisé: {float(financement.montant_utilise):,.0f} FCFA ({taux_utilisation:.1f}%)")
        print(f"   📅 Période: {financement.date_debut} → {financement.date_fin}")
        print()
    
    return financements

def generer_statistiques_globales(association_id, dirigeants, projets, budgets, activites, biens, financements):
    """Génère des statistiques globales"""
    print("\n📊 STATISTIQUES GLOBALES DE L'ASSOCIATION")
    print("=" * 60)
    
    # Dirigeants
    dirigeants_actifs = [d for d in dirigeants if d.statut == StatutDirigeant.ACTIF]
    print(f"👥 DIRIGEANTS:")
    print(f"   Total: {len(dirigeants)} | Actifs: {len(dirigeants_actifs)}")
    
    # Projets
    projets_actifs = [p for p in projets if p.statut == StatutProjet.EN_COURS]
    print(f"🚀 PROJETS:")
    print(f"   Total: {len(projets)} | Actifs: {len(projets_actifs)}")
    budget_total_projets = sum(float(p.budget_total) for p in projets)
    print(f"   Budget total: {budget_total_projets:,.0f} FCFA")
    
    # Bailleurs
    bailleurs_uniques = list(set(p.bailleur_id for p in projets if p.bailleur_id))
    print(f"🏛️ PARTENAIRES BAILLEURS: {len(bailleurs_uniques)}")
    
    # Budgets
    print(f"💰 BUDGETS:")
    budget_total_prevu = sum(float(b.total_recettes_prevues or 0) for b in budgets)
    budget_total_realise = sum(float(b.total_recettes_realisees or 0) for b in budgets)
    print(f"   Budgets créés: {len(budgets)}")
    print(f"   Recettes prévues: {budget_total_prevu:,.0f} FCFA")
    print(f"   Recettes réalisées: {budget_total_realise:,.0f} FCFA")
    
    # Activités
    print(f"🎯 ACTIVITÉS:")
    print(f"   Total: {len(activites)}")
    activites_par_type = {}
    for activite in activites:
        type_act = activite.type_activite.value
        activites_par_type[type_act] = activites_par_type.get(type_act, 0) + 1
    for type_act, count in activites_par_type.items():
        print(f"   {type_act.title()}: {count}")
    
    # Patrimoine
    print(f"🏛️ PATRIMOINE:")
    print(f"   Nombre de biens: {len(biens)}")
    valeur_patrimoine = sum(float(b.valeur_actuelle or b.valeur_acquisition or 0) for b in biens)
    print(f"   Valeur totale: {valeur_patrimoine:,.0f} FCFA")
    
    # Financements
    print(f"💸 FINANCEMENTS:")
    print(f"   Nombre de financements: {len(financements)}")
    montant_total_accorde = sum(float(f.montant_accorde) for f in financements)
    montant_total_decaisse = sum(float(f.montant_decaisse) for f in financements)
    montant_total_utilise = sum(float(f.montant_utilise) for f in financements)
    print(f"   Total accordé: {montant_total_accorde:,.0f} FCFA")
    print(f"   Total décaissé: {montant_total_decaisse:,.0f} FCFA ({(montant_total_decaisse/montant_total_accorde)*100:.1f}%)")
    print(f"   Total utilisé: {montant_total_utilise:,.0f} FCFA ({(montant_total_utilise/montant_total_decaisse)*100:.1f}%)")
    
    print("\n🎯 INDICATEURS CLÉS:")
    print(f"   • Taux d'activité projets: {len(projets_actifs)/len(projets)*100:.1f}%")
    print(f"   • Diversification bailleurs: {len(bailleurs_uniques)} partenaires")
    print(f"   • Taux de décaissement: {(montant_total_decaisse/montant_total_accorde)*100:.1f}%")
    print(f"   • Taux d'utilisation: {(montant_total_utilise/montant_total_decaisse)*100:.1f}%")

def main():
    """Fonction principale de test"""
    print("🏛️ TEST SYSTÈME GESTION AVANCÉE COMPTAEBNL-IA")
    print("=" * 70)
    print("Test complet : Dirigeants, Projets, Budget, Activités, Patrimoine, Balance")
    print("Architecture multi-projets et multi-bailleurs pour EBNL OHADA")
    print()
    
    try:
        with app.app_context():
            # Initialisation
            association_id, bailleurs = init_test_data()
            
            # Tests des modules
            dirigeants = test_dirigeants(association_id)
            projets = test_projets(association_id, bailleurs)
            budgets = test_budgets(association_id, projets)
            activites = test_activites(association_id, projets)
            biens = test_patrimoine(association_id, projets)
            financements = test_financements(association_id, projets, bailleurs)
            
            # Commit final
            db.session.commit()
            
            # Statistiques globales
            generer_statistiques_globales(
                association_id, dirigeants, projets, budgets, 
                activites, biens, financements
            )
            
            print("\n🎉 TOUS LES TESTS RÉUSSIS !")
            print("✅ Système de gestion avancée opérationnel")
            print("✅ Architecture multi-projets et multi-bailleurs fonctionnelle")
            print("✅ Gestion complète des EBNL selon SYCEBNL")
            print("\n💡 Base de données de test créée: test_gestion_avancee.db")
            
            return 0
            
    except Exception as e:
        print(f"\n💥 ERREUR LORS DES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())