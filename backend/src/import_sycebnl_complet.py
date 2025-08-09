#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'importation du Plan Comptable SYCEBNL Complet
=======================================================

Ce script importe le plan comptable SYCEBNL complet extrait de la documentation 
officielle PDF dans la base de données SQLite.

Fonctionnalités :
- Import de tous les comptes SYCEBNL extraits de la documentation officielle
- Gestion des doublons avec mise à jour des comptes existants
- Statistiques d'import détaillées
- Recherche et affichage des comptes

Usage:
    python3 import_sycebnl_complet.py
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models import db, PlanComptable
from data.sycebnl_plan_comptable import (
    PLAN_COMPTABLE_SYCEBNL_COMPLET,
    TOTAL_COMPTES_COMPLET,
    TOTAL_COMPTES_PAR_CLASSE_COMPLET,
    CLASSES_SYCEBNL,
    get_comptes_by_classe,
    search_comptes
)

def import_plan_comptable_complet():
    """Import le plan comptable SYCEBNL complet dans la base de données"""
    
    print("🚀 Début de l'import du Plan Comptable SYCEBNL Complet")
    print("=" * 60)
    print(f"📊 Nombre total de comptes à importer: {TOTAL_COMPTES_COMPLET}")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Statistiques avant import
            comptes_existants = PlanComptable.query.count()
            print(f"📋 Comptes existants dans la base: {comptes_existants}")
            
            # Import par batch pour éviter les erreurs de mémoire
            batch_size = 50
            comptes_ajoutes = 0
            comptes_modifies = 0
            erreurs = 0
            
            print(f"\n🔄 Import en cours par batch de {batch_size} comptes...")
            
            for i in range(0, len(PLAN_COMPTABLE_SYCEBNL_COMPLET), batch_size):
                batch = PLAN_COMPTABLE_SYCEBNL_COMPLET[i:i + batch_size]
                
                for compte_data in batch:
                    try:
                        # Vérifier si le compte existe déjà
                        existing = PlanComptable.query.filter_by(
                            numero_compte=compte_data["numero"]
                        ).first()
                        
                        if existing:
                            # Mettre à jour le compte existant
                            existing.libelle_compte = compte_data["libelle"]
                            existing.classe_compte = compte_data["classe"]
                            existing.niveau_compte = compte_data["niveau"]
                            existing.parent_id = compte_data.get("parent_id")
                            comptes_modifies += 1
                        else:
                            # Créer un nouveau compte
                            nouveau_compte = PlanComptable(
                                numero_compte=compte_data["numero"],
                                libelle_compte=compte_data["libelle"],
                                classe_compte=compte_data["classe"],
                                niveau_compte=compte_data["niveau"],
                                parent_id=compte_data.get("parent_id")
                            )
                            db.session.add(nouveau_compte)
                            comptes_ajoutes += 1
                            
                    except Exception as e:
                        print(f"⚠️  Erreur avec le compte {compte_data['numero']}: {e}")
                        erreurs += 1
                        continue
                
                # Commit du batch
                try:
                    db.session.commit()
                    progress = min(100, ((i + batch_size) / len(PLAN_COMPTABLE_SYCEBNL_COMPLET)) * 100)
                    print(f"   ✅ Batch {i//batch_size + 1} traité ({progress:.1f}%)")
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"   ❌ Erreur lors du commit du batch {i//batch_size + 1}: {e}")
                    erreurs += len(batch)
            
            # Statistiques finales
            print("\n" + "=" * 60)
            print("🎉 IMPORT TERMINÉ AVEC SUCCÈS!")
            print("=" * 60)
            print(f"📈 Comptes ajoutés:     {comptes_ajoutes}")
            print(f"📝 Comptes modifiés:    {comptes_modifies}")
            print(f"❌ Erreurs:             {erreurs}")
            print(f"📊 Total dans la base:  {PlanComptable.query.count()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur générale lors de l'import: {e}")
            db.session.rollback()
            return False

def afficher_statistiques():
    """Affiche les statistiques du plan comptable"""
    
    print("\n📊 STATISTIQUES DU PLAN COMPTABLE SYCEBNL")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        total_comptes = PlanComptable.query.count()
        print(f"📋 Total des comptes en base: {total_comptes}")
        
        print("\n📈 Répartition par classe:")
        for classe_num in range(1, 10):
            comptes_classe = PlanComptable.query.filter_by(classe_compte=classe_num).count()
            classe_nom = CLASSES_SYCEBNL.get(classe_num, f"Classe {classe_num}")
            print(f"   Classe {classe_num}: {comptes_classe:>3} comptes - {classe_nom}")

def rechercher_comptes(terme_recherche):
    """Recherche des comptes par terme"""
    
    print(f"\n🔍 RECHERCHE: '{terme_recherche}'")
    print("=" * 40)
    
    app = create_app()
    with app.app_context():
        # Recherche en base
        comptes = PlanComptable.query.filter(
            db.or_(
                PlanComptable.numero_compte.like(f"%{terme_recherche}%"),
                PlanComptable.libelle_compte.like(f"%{terme_recherche}%")
            )
        ).order_by(PlanComptable.numero_compte).limit(20).all()
        
        if comptes:
            print(f"📋 {len(comptes)} compte(s) trouvé(s):")
            for compte in comptes:
                print(f"   {compte.numero_compte:>6} - {compte.libelle_compte}")
        else:
            print("❌ Aucun compte trouvé")

def menu_principal():
    """Menu interactif principal"""
    
    while True:
        print("\n" + "=" * 60)
        print("📋 PLAN COMPTABLE SYCEBNL - MENU PRINCIPAL")
        print("=" * 60)
        print("1. 📥 Importer le plan comptable complet")
        print("2. 📊 Afficher les statistiques")
        print("3. 🔍 Rechercher des comptes")
        print("4. 📋 Afficher les comptes par classe")
        print("5. ❌ Quitter")
        print("=" * 60)
        
        choix = input("Votre choix (1-5): ").strip()
        
        if choix == "1":
            if import_plan_comptable_complet():
                print("\n✅ Import réussi!")
            else:
                print("\n❌ Échec de l'import")
                
        elif choix == "2":
            afficher_statistiques()
            
        elif choix == "3":
            terme = input("\n🔍 Terme à rechercher: ").strip()
            if terme:
                rechercher_comptes(terme)
            else:
                print("❌ Terme de recherche vide")
                
        elif choix == "4":
            try:
                classe = int(input("\n📋 Numéro de classe (1-9): ").strip())
                if 1 <= classe <= 9:
                    app = create_app()
                    with app.app_context():
                        comptes = PlanComptable.query.filter_by(classe_compte=classe).order_by(PlanComptable.numero_compte).all()
                        if comptes:
                            print(f"\n📋 Classe {classe} - {CLASSES_SYCEBNL.get(classe, 'Classe inconnue')}")
                            print(f"Total: {len(comptes)} comptes")
                            print("-" * 50)
                            for compte in comptes[:30]:  # Limiter l'affichage
                                print(f"   {compte.numero_compte:>6} - {compte.libelle_compte}")
                            if len(comptes) > 30:
                                print(f"   ... et {len(comptes) - 30} autres comptes")
                        else:
                            print(f"❌ Aucun compte trouvé pour la classe {classe}")
                else:
                    print("❌ Numéro de classe invalide (1-9)")
            except ValueError:
                print("❌ Veuillez saisir un numéro valide")
                
        elif choix == "5":
            print("\n👋 Au revoir!")
            break
            
        else:
            print("\n❌ Choix invalide, veuillez recommencer")

if __name__ == '__main__':
    print("🌟 PLAN COMPTABLE SYCEBNL - SYSTÈME DE GESTION")
    print("Système Comptable des Entités à But Non Lucratif")
    print(f"Version extraite de la documentation officielle PDF")
    print(f"Total de {TOTAL_COMPTES_COMPLET} comptes disponibles")
    
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⛔ Interruption utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")