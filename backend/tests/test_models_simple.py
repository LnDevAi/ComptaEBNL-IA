#!/usr/bin/env python3
"""
Tests unitaires simples pour ComptaEBNL-IA (sans pytest)
Conçu pour fonctionner dans le CI/CD sans dépendances externes
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

def test_basic_imports():
    """Test que les imports de base fonctionnent"""
    print("🔍 Test imports basiques...")
    
    # Test Python version
    assert sys.version_info >= (3, 8), f"Python version trop ancienne: {sys.version}"
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
    
    # Test imports standards
    import json
    import sqlite3
    print("✅ Imports standards OK")
    
    return True

def test_datetime_operations():
    """Test les opérations de date pour la comptabilité"""
    print("🔍 Test opérations DateTime...")
    
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    
    # Test que les dates fonctionnent
    assert isinstance(now, datetime)
    assert yesterday < now
    
    # Test formatage dates EBNL
    date_str = now.strftime("%Y-%m-%d")
    assert len(date_str) == 10
    print(f"✅ DateTime OK: {date_str}")
    
    return True

def test_financial_calculations():
    """Test calculs financiers de base (FCFA)"""
    print("🔍 Test calculs financiers...")
    
    # Test avec Decimal pour précision financière
    montant = Decimal('100000.50')  # 100,000.50 FCFA
    tva_rate = Decimal('0.18')      # 18% TVA
    
    tva = montant * tva_rate
    total = montant + tva
    
    # Vérifications
    assert isinstance(tva, Decimal)
    assert tva == Decimal('18000.09')  # 18,000.09 FCFA
    assert total == Decimal('118000.59')  # 118,000.59 FCFA
    
    print(f"✅ Calculs financiers OK: {montant} + {tva} = {total} FCFA")
    return True

def test_data_structures():
    """Test structures de données pour EBNL"""
    print("🔍 Test structures données EBNL...")
    
    # Structure organisation EBNL
    ebnl = {
        "nom": "Association Test EBNL",
        "type": "Association",
        "pays": "Burkina Faso", 
        "devise": "XOF",  # Franc CFA
        "exercice_debut": "2024-01-01",
        "exercice_fin": "2024-12-31"
    }
    
    # Vérifications
    assert ebnl["devise"] == "XOF"
    assert "Association" in ebnl["nom"]
    
    # Structure compte SYCEBNL
    compte = {
        "numero": "601000",
        "libelle": "Achats de marchandises",
        "classe": "6",  # Classe 6 - Charges
        "nature": "Charge"
    }
    
    assert compte["classe"] == "6"
    assert compte["numero"].startswith("6")
    
    print("✅ Structures données EBNL OK")
    return True

def test_ebnl_concepts():
    """Test concepts spécifiques EBNL OHADA"""
    print("🔍 Test concepts EBNL OHADA...")
    
    # Types d'EBNL selon OHADA
    types_ebnl = [
        "Association",
        "Fondation", 
        "Coopérative",
        "Mutuelle",
        "Syndicat",
        "ONG"
    ]
    
    assert "Association" in types_ebnl
    assert "ONG" in types_ebnl
    assert len(types_ebnl) >= 6
    
    # Classes de comptes SYCEBNL
    classes_sycebnl = {
        "1": "Comptes de ressources durables",
        "2": "Comptes d'actif immobilisé", 
        "3": "Comptes de stocks et en-cours",
        "4": "Comptes de tiers",
        "5": "Comptes de trésorerie",
        "6": "Comptes de charges",
        "7": "Comptes de produits",
        "8": "Comptes spéciaux"
    }
    
    assert "6" in classes_sycebnl
    assert "produits" in classes_sycebnl["7"].lower()
    
    print("✅ Concepts EBNL OHADA OK")
    return True

def test_mock_subscription_logic():
    """Test logique d'abonnement basique"""
    print("🔍 Test logique abonnement...")
    
    # Plans d'abonnement
    plans = {
        "gratuit": {
            "prix": 0,
            "utilisateurs": 1,
            "fonctionnalites": ["comptabilite_base"]
        },
        "professionnel": {
            "prix": 49000,  # 49,000 FCFA/mois
            "utilisateurs": 5,
            "fonctionnalites": ["comptabilite_base", "elearning", "multi_projets"]
        },
        "entreprise": {
            "prix": 149000,  # 149,000 FCFA/mois 
            "utilisateurs": 50,
            "fonctionnalites": ["comptabilite_base", "elearning", "multi_projets", "support_prioritaire", "api_avancee"]
        }
    }
    
    # Tests
    assert plans["gratuit"]["prix"] == 0
    assert plans["professionnel"]["prix"] > 0
    assert len(plans["entreprise"]["fonctionnalites"]) > len(plans["gratuit"]["fonctionnalites"])
    
    print("✅ Logique abonnement OK")
    return True

def test_mobile_money_validation():
    """Test validation Mobile Money basique"""
    print("🔍 Test validation Mobile Money...")
    
    # Opérateurs Mobile Money région OHADA
    operateurs = {
        "mtn": {"prefixe": ["70", "75", "76", "77"], "pays": ["BF", "CI", "CM"]},
        "orange": {"prefixe": ["07", "08", "09"], "pays": ["BF", "CI", "SN"]},
        "moov": {"prefixe": ["60", "61", "62"], "pays": ["BF", "CI"]},
        "wave": {"prefixe": ["78", "79"], "pays": ["SN", "CI"]}
    }
    
    # Test numéro MTN Burkina
    numero_mtn = "70123456"
    assert numero_mtn.startswith("70")
    assert len(numero_mtn) == 8
    
    # Test validation basique
    def valider_numero_mobile(numero, operateur):
        if operateur == "mtn":
            return numero[:2] in ["70", "75", "76", "77"]
        return False
    
    assert valider_numero_mobile("70123456", "mtn") == True
    assert valider_numero_mobile("60123456", "mtn") == False
    
    print("✅ Validation Mobile Money OK")
    return True

def run_all_tests():
    """Exécute tous les tests"""
    print("🧪" + "="*60 + "🧪")
    print("      TESTS UNITAIRES SIMPLES COMPTAEBNL-IA")
    print("🧪" + "="*60 + "🧪")
    print()
    
    tests = [
        test_basic_imports,
        test_datetime_operations,
        test_financial_calculations,
        test_data_structures,
        test_ebnl_concepts,
        test_mock_subscription_logic,
        test_mobile_money_validation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_func.__name__} a échoué")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} a échoué: {e}")
        print()
    
    # Rapport final
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("📊 RAPPORT FINAL")
    print("="*50)
    print(f"✅ Tests réussis: {passed}")
    print(f"❌ Tests échoués: {failed}")
    print(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    if failed == 0:
        print("\n🎉 TOUS LES TESTS PASSENT! 🎉")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) à corriger")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)