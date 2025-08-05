#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import direct du Plan Comptable SYCEBNL Complet
===============================================

Ce script importe directement les comptes du fichier Python créé 
par convert_sql_to_python.py dans la base de données.
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models import db, PlanComptable

def import_plan_comptable_complet():
    """Importe le plan comptable complet depuis le fichier Python"""
    try:
        # Importer le plan comptable complet
        from data.sycebnl_plan_comptable_complet import (
            PLAN_COMPTABLE_SYCEBNL_COMPLET, 
            TOTAL_COMPTES_COMPLET,
            TOTAL_COMPTES_PAR_CLASSE_COMPLET
        )
        
        print(f"🎯 IMPORT PLAN COMPTABLE SYCEBNL COMPLET")
        print("=" * 50)
        print(f"📊 Total comptes à importer: {TOTAL_COMPTES_COMPLET}")
        print(f"📋 Répartition par classe:")
        for classe, count in TOTAL_COMPTES_PAR_CLASSE_COMPLET.items():
            print(f"   Classe {classe}: {count:>3} comptes")
        
        app = create_app()
        with app.app_context():
            # Supprimer tous les comptes existants
            print("\n🗑️  Suppression des comptes existants...")
            PlanComptable.query.delete()
            db.session.commit()
            print("✅ Comptes existants supprimés")
            
            # Importer les nouveaux comptes
            print("\n🔄 Import des nouveaux comptes...")
            batch_size = 50
            imported = 0
            errors = 0
            
            for i in range(0, len(PLAN_COMPTABLE_SYCEBNL_COMPLET), batch_size):
                batch = PLAN_COMPTABLE_SYCEBNL_COMPLET[i:i + batch_size]
                
                for compte_data in batch:
                    try:
                        compte = PlanComptable(
                            numero_compte=compte_data["numero"],
                            libelle_compte=compte_data["libelle"],
                            classe=compte_data["classe"],
                            niveau=compte_data["niveau"],
                            actif=True,
                            observations=compte_data.get("observations", "Compte SYCEBNL Officiel")
                        )
                        db.session.add(compte)
                    except Exception as e:
                        print(f"❌ Erreur compte {compte_data['numero']}: {e}")
                        errors += 1
                
                try:
                    db.session.commit()
                    imported += len(batch)
                    print(f"✅ Batch {i//batch_size + 1:>2}: {len(batch):>2} comptes importés (total: {imported:>4})")
                except Exception as e:
                    db.session.rollback()
                    print(f"❌ Erreur batch {i//batch_size + 1}: {e}")
                    errors += batch_size
            
            # Vérification finale
            total_final = PlanComptable.query.count()
            print(f"\n🎉 RÉSULTAT FINAL:")
            print(f"   📊 Comptes importés avec succès: {total_final}")
            print(f"   ❌ Erreurs rencontrées: {errors}")
            print(f"   ✅ Taux de succès: {(total_final/TOTAL_COMPTES_COMPLET)*100:.1f}%")
            
            if total_final > 0:
                print(f"\n📋 Exemples de comptes importés:")
                comptes_exemples = PlanComptable.query.order_by(PlanComptable.numero_compte).limit(10).all()
                for compte in comptes_exemples:
                    print(f"   {compte.numero_compte:>6} - {compte.libelle_compte}")
            
            return total_final
            
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Suggestion: Exécutez d'abord convert_sql_to_python.py")
        return 0
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 0

def afficher_statistiques():
    """Affiche les statistiques de la base de données"""
    app = create_app()
    with app.app_context():
        total = PlanComptable.query.count()
        print(f"\n📊 STATISTIQUES BASE DE DONNÉES:")
        print(f"   Total comptes: {total}")
        
        if total > 0:
            print(f"   Répartition par classe:")
            for classe in range(1, 10):
                count = PlanComptable.query.filter_by(classe=classe).count()
                if count > 0:
                    print(f"     Classe {classe}: {count:>3} comptes")

def main():
    """Fonction principale"""
    total_imported = import_plan_comptable_complet()
    
    if total_imported > 0:
        afficher_statistiques()
        print(f"\n✅ Plan comptable SYCEBNL complet opérationnel!")
        print(f"🚀 Vous pouvez maintenant utiliser l'API avec {total_imported} comptes")
    else:
        print(f"\n❌ Échec de l'import du plan comptable")

if __name__ == "__main__":
    main()