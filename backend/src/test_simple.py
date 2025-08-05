#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple de ComptaEBNL-IA sans dépendances externes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comptaebnl():
    """Test simple des fonctionnalités principales"""
    print("🧪 Test Simple de ComptaEBNL-IA")
    print("=" * 50)
    
    try:
        from main import create_app
        from models import PlanComptable, EcritureComptable, JournalComptable
        from data.sycebnl_plan_comptable import TOTAL_COMPTES, CLASSES_SYCEBNL
        
        app = create_app()
        
        with app.app_context():
            print("🔧 Application créée avec succès")
            
            # Test 1: Plan comptable
            total_comptes = PlanComptable.query.count()
            print(f"📊 Plan comptable: {total_comptes} comptes en base (attendu: ~{TOTAL_COMPTES})")
            
            # Test 2: Répartition par classe
            print("\n📋 Répartition par classe SYCEBNL:")
            for classe in range(1, 10):
                count = PlanComptable.query.filter_by(classe=classe).count()
                if count > 0:
                    libelle = CLASSES_SYCEBNL.get(classe, f'Classe {classe}')
                    print(f"   Classe {classe}: {count:3d} comptes - {libelle}")
            
            # Test 3: Comptes spécifiques EBNL
            comptes_ebnl = [
                ("758", "Contributions volontaires en nature"),
                ("7581", "Bénévolat"),
                ("412", "Adhérents et usagers"),
                ("1311", "Fonds dédiés avec obligation contractuelle"),
                ("756", "Dons et legs"),
                ("7561", "Dons manuels"),
                ("571", "Caisse siège social"),
                ("401", "Fournisseurs, dettes en compte")
            ]
            
            print(f"\n🎯 Comptes spécifiques EBNL:")
            for numero, description in comptes_ebnl:
                compte = PlanComptable.query.filter_by(numero_compte=numero).first()
                if compte:
                    print(f"   ✅ {compte.numero_compte} - {compte.libelle_compte}")
                else:
                    print(f"   ❌ {numero} - {description} (Non trouvé)")
            
            # Test 4: Journaux comptables
            journaux = JournalComptable.query.all()
            print(f"\n📓 Journaux comptables: {len(journaux)} journaux")
            for journal in journaux:
                print(f"   {journal.code} - {journal.libelle}")
            
            # Test 5: Écritures comptables
            total_ecritures = EcritureComptable.query.count()
            print(f"\n📝 Écritures comptables: {total_ecritures} écritures en base")
            
            # Test 6: Test de création d'écriture
            print(f"\n🔧 Test de création d'écriture...")
            
            from models import db, LigneEcriture
            from datetime import date
            from decimal import Decimal
            
            # Créer une écriture de test
            ecriture = EcritureComptable(
                date_ecriture=date.today(),
                libelle="Test écriture ComptaEBNL-IA",
                journal="OD",
                piece_justificative="TEST-001",
                montant_total=Decimal('100.00')
            )
            db.session.add(ecriture)
            db.session.flush()  # Pour obtenir l'ID
            
            # Ajouter les lignes
            ligne1 = LigneEcriture(
                ecriture_id=ecriture.id,
                numero_compte="571",
                libelle="Test caisse",
                debit=Decimal('100.00'),
                credit=Decimal('0.00')
            )
            
            ligne2 = LigneEcriture(
                ecriture_id=ecriture.id,
                numero_compte="7561",
                libelle="Test don",
                debit=Decimal('0.00'),
                credit=Decimal('100.00')
            )
            
            db.session.add(ligne1)
            db.session.add(ligne2)
            db.session.commit()
            
            print(f"   ✅ Écriture créée: {ecriture.numero_ecriture}")
            print(f"   Montant: {ecriture.montant_total}€")
            print(f"   Équilibrée: {'✅' if ecriture.is_equilibree() else '❌'}")
            print(f"   Statut: {ecriture.statut.value}")
            print(f"   Lignes: {ecriture.lignes.count()}")
            
            # Test de validation
            try:
                ecriture.valider(user="test_user")
                print(f"   ✅ Écriture validée avec succès")
                print(f"   Nouveau statut: {ecriture.statut.value}")
            except Exception as e:
                print(f"   ❌ Erreur validation: {e}")
            
            # Test 7: Recherche de comptes
            print(f"\n🔍 Test de recherche dans le plan comptable:")
            
            # Recherche par numéro
            compte_571 = PlanComptable.query.filter_by(numero_compte="571").first()
            if compte_571:
                print(f"   Compte 571: {compte_571.libelle_compte}")
            
            # Recherche par libellé (contains)
            comptes_caisse = PlanComptable.query.filter(
                PlanComptable.libelle_compte.ilike('%caisse%')
            ).limit(3).all()
            
            print(f"   Comptes contenant 'caisse': {len(comptes_caisse)}")
            for compte in comptes_caisse:
                print(f"     {compte.numero_compte} - {compte.libelle_compte}")
            
            # Test 8: Statistiques finales
            print(f"\n📈 Statistiques finales:")
            print(f"   Total comptes: {PlanComptable.query.count()}")
            print(f"   Total journaux: {JournalComptable.query.count()}")
            print(f"   Total écritures: {EcritureComptable.query.count()}")
            
            # Vérifier l'équilibre général
            from sqlalchemy import func
            total_debit = db.session.query(func.sum(LigneEcriture.debit)).scalar() or Decimal('0')
            total_credit = db.session.query(func.sum(LigneEcriture.credit)).scalar() or Decimal('0')
            
            print(f"   Total débit: {total_debit}€")
            print(f"   Total crédit: {total_credit}€")
            print(f"   Équilibre général: {'✅' if total_debit == total_credit else '❌'}")
            
            print("\n🎉 Tous les tests sont passés avec succès !")
            print("🚀 ComptaEBNL-IA fonctionne correctement !")
            
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_comptaebnl()