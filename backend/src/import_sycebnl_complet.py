#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import du Plan Comptable SYCEBNL Complet
Système Comptable des Entités à But Non Lucratif
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models import db, PlanComptable
from data.sycebnl_plan_comptable import (
    PLAN_COMPTABLE_SYCEBNL, 
    TOTAL_COMPTES, 
    TOTAL_COMPTES_PAR_CLASSE,
    CLASSES_SYCEBNL
)

def import_plan_comptable_complet():
    """Import le plan comptable SYCEBNL complet dans la base de données"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Démarrage de l'import du Plan Comptable SYCEBNL...")
        print(f"📊 {TOTAL_COMPTES} comptes à importer")
        
        # Vider la table existante
        print("🗑️  Suppression des données existantes...")
        db.session.query(PlanComptable).delete()
        db.session.commit()
        
        # Import par lots pour optimiser les performances
        print("📥 Import des comptes SYCEBNL...")
        batch_size = 50  # Réduire la taille des lots
        imported_count = 0
        skipped_count = 0
        
        for i in range(0, len(PLAN_COMPTABLE_SYCEBNL), batch_size):
            batch = PLAN_COMPTABLE_SYCEBNL[i:i + batch_size]
            
            for compte_data in batch:
                # Vérifier si le compte existe déjà
                existing = PlanComptable.query.filter_by(numero_compte=compte_data["numero"]).first()
                if existing:
                    print(f"   ⚠️  Compte {compte_data['numero']} existe déjà, mis à jour")
                    # Mettre à jour le compte existant
                    existing.libelle_compte = compte_data["libelle"]
                    existing.classe = compte_data["classe"]
                    existing.niveau = compte_data["niveau"]
                    existing.parent_id = compte_data.get("parent_id")
                    existing.observations = f"Compte SYCEBNL - Classe {compte_data['classe']} (mis à jour)"
                    skipped_count += 1
                else:
                    # Créer un nouveau compte
                    compte = PlanComptable(
                        numero_compte=compte_data["numero"],
                        libelle_compte=compte_data["libelle"],
                        classe=compte_data["classe"],
                        niveau=compte_data["niveau"],
                        parent_id=compte_data.get("parent_id"),
                        observations=f"Compte SYCEBNL - Classe {compte_data['classe']}"
                    )
                    db.session.add(compte)
                    imported_count += 1
            
            # Commit par batch avec gestion d'erreur
            try:
                db.session.commit()
                print(f"   ✅ {min(i + batch_size, len(PLAN_COMPTABLE_SYCEBNL))} / {len(PLAN_COMPTABLE_SYCEBNL)} comptes traités")
            except Exception as e:
                print(f"   ❌ Erreur batch {i}: {e}")
                db.session.rollback()
                continue
        
        print(f"\n🎉 Import terminé avec succès !")
        print(f"✅ {imported_count} nouveaux comptes SYCEBNL importés")
        print(f"🔄 {skipped_count} comptes existants mis à jour")
        
        # Vérification de l'import
        print("\n📊 Vérification de l'import:")
        for classe in range(1, 10):
            count_db = PlanComptable.query.filter_by(classe=classe).count()
            count_expected = TOTAL_COMPTES_PAR_CLASSE.get(classe, 0)
            status = "✅" if count_db >= count_expected else "❌"
            print(f"   {status} Classe {classe}: {count_db} comptes en base - {CLASSES_SYCEBNL.get(classe, 'Inconnue')}")
        
        total_db = PlanComptable.query.count()
        print(f"\n📈 Total: {total_db} comptes en base de données")
        
        if total_db >= TOTAL_COMPTES:
            print("🎯 Import PARFAIT ! Le plan comptable SYCEBNL est complet.")
        else:
            print(f"⚠️  Base incomplète: {TOTAL_COMPTES} attendus, {total_db} en base")

def afficher_stats_plan_comptable():
    """Affiche les statistiques du plan comptable"""
    app = create_app()
    
    with app.app_context():
        print("\n📊 STATISTIQUES DU PLAN COMPTABLE SYCEBNL")
        print("=" * 60)
        
        total = PlanComptable.query.count()
        print(f"📈 Total des comptes: {total}")
        
        print(f"\n📋 Répartition par classe:")
        for classe in range(1, 10):
            count = PlanComptable.query.filter_by(classe=classe).count()
            if count > 0:
                print(f"   Classe {classe}: {count:3d} comptes - {CLASSES_SYCEBNL.get(classe, 'Inconnue')}")
        
        print(f"\n🔍 Répartition par niveau:")
        for niveau in range(0, 4):
            count = PlanComptable.query.filter_by(niveau=niveau).count()
            if count > 0:
                niveau_desc = {
                    0: "Classes principales",
                    1: "Comptes principaux", 
                    2: "Comptes divisionnaires",
                    3: "Sous-comptes"
                }
                print(f"   Niveau {niveau}: {count:3d} comptes - {niveau_desc.get(niveau, 'Autre')}")
        
        # Quelques exemples de comptes spécifiques EBNL
        print(f"\n🎯 Comptes spécifiques EBNL:")
        comptes_ebnl = [
            "758",   # Contributions volontaires en nature
            "7581",  # Bénévolat
            "412",   # Adhérents et usagers
            "1311",  # Fonds dédiés avec obligation contractuelle
            "756",   # Dons et legs
        ]
        
        for numero in comptes_ebnl:
            compte = PlanComptable.query.filter_by(numero_compte=numero).first()
            if compte:
                print(f"   ✅ {compte.numero_compte} - {compte.libelle_compte}")
            else:
                print(f"   ❌ {numero} - Non trouvé")

def rechercher_compte(terme):
    """Recherche un compte par numéro ou libellé"""
    app = create_app()
    
    with app.app_context():
        print(f"\n🔍 Recherche: '{terme}'")
        print("=" * 50)
        
        # Recherche par numéro
        if terme.isdigit():
            comptes = PlanComptable.query.filter(
                PlanComptable.numero_compte.like(f"{terme}%")
            ).order_by(PlanComptable.numero_compte).limit(10).all()
        else:
            # Recherche par libellé
            comptes = PlanComptable.query.filter(
                PlanComptable.libelle_compte.ilike(f"%{terme}%")
            ).order_by(PlanComptable.numero_compte).limit(10).all()
        
        if comptes:
            print(f"📋 {len(comptes)} compte(s) trouvé(s):")
            for compte in comptes:
                print(f"   {compte.numero_compte:8s} - {compte.libelle_compte}")
        else:
            print("❌ Aucun compte trouvé")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "import":
            import_plan_comptable_complet()
        elif command == "stats":
            afficher_stats_plan_comptable()
        elif command == "search" and len(sys.argv) > 2:
            rechercher_compte(sys.argv[2])
        else:
            print("Usage:")
            print("  python import_sycebnl_complet.py import   # Import le plan comptable")
            print("  python import_sycebnl_complet.py stats    # Affiche les statistiques")
            print("  python import_sycebnl_complet.py search TERME  # Recherche un compte")
    else:
        # Import par défaut
        import_plan_comptable_complet()
        afficher_stats_plan_comptable()