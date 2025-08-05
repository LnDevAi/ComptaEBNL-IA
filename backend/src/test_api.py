#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour l'API ComptaEBNL-IA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime, date

def test_api():
    """Teste les principales fonctionnalités de l'API"""
    base_url = "http://localhost:5000"
    
    print("🧪 Tests de l'API ComptaEBNL-IA")
    print("=" * 50)
    
    # Test 1: Page d'accueil
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Page d'accueil: {data['application']}")
            print(f"   Version: {data['version']}")
            print(f"   Référentiel: {data['referentiel']}")
        else:
            print(f"❌ Page d'accueil: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Page d'accueil: {e}")
    
    # Test 2: Santé de l'API
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Santé API: {data['status']}")
            print(f"   Base de données: {data['components']['database']}")
        else:
            print(f"❌ Santé API: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Santé API: {e}")
    
    # Test 3: Plan comptable
    try:
        response = requests.get(f"{base_url}/api/v1/plan-comptable?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Plan comptable: {data['total']} comptes")
            if data['data']:
                premier_compte = data['data'][0]
                print(f"   Premier compte: {premier_compte['numero_compte']} - {premier_compte['libelle_compte']}")
        else:
            print(f"❌ Plan comptable: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Plan comptable: {e}")
    
    # Test 4: Classes SYCEBNL
    try:
        response = requests.get(f"{base_url}/api/v1/plan-comptable/classes")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Classes SYCEBNL: {data['total_classes']} classes actives")
            for classe in data['data']:
                if classe['actif']:
                    print(f"   Classe {classe['numero']}: {classe['nombre_comptes']} comptes")
        else:
            print(f"❌ Classes SYCEBNL: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Classes SYCEBNL: {e}")
    
    # Test 5: Recherche de compte
    try:
        response = requests.get(f"{base_url}/api/v1/plan-comptable/search?q=caisse")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recherche 'caisse': {data['total_found']} résultats")
            if data['data']:
                print(f"   Premier résultat: {data['data'][0]['numero_compte']} - {data['data'][0]['libelle_compte']}")
        else:
            print(f"❌ Recherche compte: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Recherche compte: {e}")
    
    # Test 6: Comptes spécifiques EBNL
    comptes_ebnl = ["758", "7581", "412", "1311", "756"]
    print("\n🎯 Vérification des comptes spécifiques EBNL:")
    for numero in comptes_ebnl:
        try:
            response = requests.get(f"{base_url}/api/v1/plan-comptable/compte/{numero}")
            if response.status_code == 200:
                data = response.json()
                compte = data['data']
                print(f"   ✅ {compte['numero_compte']} - {compte['libelle_compte']}")
            else:
                print(f"   ❌ Compte {numero}: Non trouvé")
        except Exception as e:
            print(f"   ❌ Compte {numero}: {e}")
    
    # Test 7: Écritures comptables (liste vide au début)
    try:
        response = requests.get(f"{base_url}/api/v1/ecritures")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Écritures comptables: {data['pagination']['total']} écritures")
        else:
            print(f"❌ Écritures comptables: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Écritures comptables: {e}")
    
    # Test 8: Configuration IA
    try:
        response = requests.get(f"{base_url}/api/v1/config-ia")
        if response.status_code == 200:
            data = response.json()
            config = data['data']
            print(f"✅ Configuration IA: OCR={'✅' if config['ocr_enabled'] else '❌'}, OpenAI={'✅' if config['openai_available'] else '❌'}")
            print(f"   Extensions supportées: {', '.join(config['allowed_extensions'])}")
        else:
            print(f"❌ Configuration IA: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Configuration IA: {e}")
    
    # Test 9: Création d'une écriture de test
    print("\n📝 Test de création d'écriture:")
    ecriture_test = {
        "date_ecriture": date.today().isoformat(),
        "libelle": "Test écriture ComptaEBNL-IA",
        "journal": "OD",
        "piece_justificative": "TEST-001",
        "lignes": [
            {
                "numero_compte": "571",
                "libelle": "Test caisse",
                "debit": 100.00,
                "credit": 0
            },
            {
                "numero_compte": "7561",
                "libelle": "Test don",
                "debit": 0,
                "credit": 100.00
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/ecritures",
            json=ecriture_test,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 201:
            data = response.json()
            ecriture = data['data']
            print(f"   ✅ Écriture créée: {ecriture['numero_ecriture']}")
            print(f"   Montant: {ecriture['montant_total']}€")
            print(f"   Équilibrée: {'✅' if ecriture['equilibree'] else '❌'}")
            print(f"   Statut: {ecriture['statut']}")
            
            # Test de validation de l'écriture
            ecriture_id = ecriture['id']
            response_val = requests.post(f"{base_url}/api/v1/ecritures/{ecriture_id}/valider")
            if response_val.status_code == 200:
                print(f"   ✅ Écriture validée avec succès")
            else:
                print(f"   ⚠️  Validation échouée: {response_val.status_code}")
                
        else:
            print(f"   ❌ Création écriture: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data.get('message', 'Inconnue')}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ Création écriture: {e}")
    
    # Test 10: Balance comptable
    try:
        response = requests.get(f"{base_url}/api/v1/balance")
        if response.status_code == 200:
            data = response.json()
            balance = data['data']
            print(f"✅ Balance comptable: {balance['parametres']['nombre_comptes']} comptes mouvementés")
            print(f"   Total débit: {balance['totaux']['total_debit']}€")
            print(f"   Total crédit: {balance['totaux']['total_credit']}€")
            print(f"   Équilibrée: {'✅' if balance['totaux']['equilibre'] else '❌'}")
        else:
            print(f"❌ Balance comptable: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Balance comptable: {e}")
    
    print("\n🎉 Tests terminés !")

def test_offline():
    """Teste l'application sans serveur web (directement avec Flask)"""
    print("🧪 Tests hors-ligne de ComptaEBNL-IA")
    print("=" * 50)
    
    try:
        from main import create_app
        from models import PlanComptable, EcritureComptable
        
        app = create_app()
        
        with app.app_context():
            # Test du plan comptable
            total_comptes = PlanComptable.query.count()
            print(f"✅ Plan comptable: {total_comptes} comptes en base")
            
            # Test des classes
            for classe in range(1, 10):
                count = PlanComptable.query.filter_by(classe=classe).count()
                if count > 0:
                    print(f"   Classe {classe}: {count} comptes")
            
            # Test des comptes EBNL
            comptes_ebnl = ["758", "7581", "412", "1311", "756"]
            print(f"\n🎯 Comptes EBNL:")
            for numero in comptes_ebnl:
                compte = PlanComptable.query.filter_by(numero_compte=numero).first()
                if compte:
                    print(f"   ✅ {compte.numero_compte} - {compte.libelle_compte}")
                else:
                    print(f"   ❌ {numero} - Non trouvé")
            
            # Test des écritures
            total_ecritures = EcritureComptable.query.count()
            print(f"\n📝 Écritures comptables: {total_ecritures} en base")
            
            print("\n🎉 Tests hors-ligne terminés avec succès !")
            
    except Exception as e:
        print(f"❌ Erreur lors des tests hors-ligne: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'offline':
        test_offline()
    else:
        test_api()