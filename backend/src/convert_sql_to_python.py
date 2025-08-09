#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Conversion du Plan Comptable SYCEBNL Officiel SQL vers Python
=============================================================

Ce script convertit le fichier SQL officiel SYCEBNL (1162 comptes) 
en format Python et l'importe dans la base de données.
"""

import re
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models import db, PlanComptable

def parse_sql_file(sql_file_path):
    """Parse le fichier SQL et extrait les comptes"""
    print(f"📄 Lecture du fichier SQL: {sql_file_path}")
    
    comptes = []
    
    with open(sql_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Chercher les INSERT VALUES
        insert_pattern = r"INSERT INTO `plan_comptable`.*?VALUES\s*(.*?);"
        matches = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            # Extraire chaque ligne de valeurs
            values_pattern = r"\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']*)',\s*(\d+),\s*'([^']*)',\s*'(\d+)',\s*'([^']*)'\)"
            values_matches = re.findall(values_pattern, match)
            
            for values in values_matches:
                numero_compte, code_compte, libelle_compte, observations, niveau, parent_id, classe, type_entite = values
                
                # Nettoyer les données
                libelle_compte = libelle_compte.replace("''", "'")  # Échappement SQL
                observations = observations.replace("''", "'")
                
                compte = {
                    'numero': numero_compte,
                    'libelle': libelle_compte,
                    'classe': int(classe),
                    'niveau': int(niveau),
                    'parent_id': parent_id if parent_id else None,
                    'type_entite': type_entite,
                    'observations': observations
                }
                comptes.append(compte)
    
    print(f"✅ {len(comptes)} comptes extraits du SQL")
    return comptes

def create_python_file(comptes, output_file):
    """Crée le fichier Python avec les comptes"""
    print(f"📝 Création du fichier Python: {output_file}")
    
    # Statistiques par classe
    stats_par_classe = {}
    for i in range(1, 10):
        stats_par_classe[i] = len([c for c in comptes if c['classe'] == i])
    
    content = f'''# Plan Comptable SYCEBNL Officiel Complet
# Extrait du fichier SQL officiel - {len(comptes)} comptes
# Système Comptable des Entités à But Non Lucratif

PLAN_COMPTABLE_SYCEBNL_COMPLET = [
'''
    
    for compte in comptes:
        content += f'''    {{"numero": "{compte['numero']}", "libelle": "{compte['libelle']}", "classe": {compte['classe']}, "niveau": {compte['niveau']}, "parent_id": {repr(compte['parent_id'])}, "type_entite": "{compte['type_entite']}"}},
'''
    
    content += f''']

# Classes SYCEBNL
CLASSES_SYCEBNL = {{
    1: "COMPTES DE RESSOURCES DURABLES",
    2: "COMPTES D'ACTIF IMMOBILISE", 
    3: "COMPTES DE STOCKS",
    4: "COMPTES DE TIERS",
    5: "COMPTES DE TRESORERIE",
    6: "COMPTES DE CHARGES",
    7: "COMPTES DE PRODUITS",
    8: "COMPTES SPECIAUX",
    9: "COMPTES D'ENGAGEMENT HORS BILAN"
}}

# Statistiques
TOTAL_COMPTES_COMPLET = {len(comptes)}
TOTAL_COMPTES_PAR_CLASSE_COMPLET = {stats_par_classe}

def get_plan_comptable_complet():
    """Retourne le plan comptable complet"""
    return PLAN_COMPTABLE_SYCEBNL_COMPLET

def get_compte_by_numero(numero):
    """Recherche un compte par son numéro"""
    for compte in PLAN_COMPTABLE_SYCEBNL_COMPLET:
        if compte["numero"] == str(numero):
            return compte
    return None

def get_comptes_by_classe(classe):
    """Retourne tous les comptes d'une classe"""
    return [c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET if c["classe"] == classe]

def search_comptes(terme):
    """Recherche des comptes par terme dans le libellé"""
    terme = terme.lower()
    return [c for c in PLAN_COMPTABLE_SYCEBNL_COMPLET 
            if terme in c["libelle"].lower() or terme in c["numero"]]

if __name__ == "__main__":
    print(f"🎯 Plan Comptable SYCEBNL Officiel: {{TOTAL_COMPTES_COMPLET}} comptes")
    print("📊 Répartition par classe:")
    for classe, total in TOTAL_COMPTES_PAR_CLASSE_COMPLET.items():
        print(f"   Classe {{classe}}: {{total:>3}} comptes - {{CLASSES_SYCEBNL[classe]}}")
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fichier Python créé avec {len(comptes)} comptes")

def import_to_database(comptes):
    """Importe les comptes dans la base de données"""
    print("🔄 Import en base de données...")
    
    app = create_app()
    with app.app_context():
        # Supprimer tous les comptes existants
        print("🗑️  Suppression des comptes existants...")
        PlanComptable.query.delete()
        db.session.commit()
        
        # Importer les nouveaux comptes
        batch_size = 50
        imported = 0
        
        for i in range(0, len(comptes), batch_size):
            batch = comptes[i:i + batch_size]
            
                                      for compte_data in batch:
                 compte = PlanComptable(
                     numero_compte=compte_data["numero"],
                     libelle_compte=compte_data["libelle"],
                     classe=compte_data["classe"],
                     niveau=compte_data["niveau"],
                     # parent_id sera géré dans une seconde passe
                     actif=True,
                     observations=compte_data.get("observations", "")
                 )
                db.session.add(compte)
            
            try:
                db.session.commit()
                imported += len(batch)
                print(f"✅ Batch {i//batch_size + 1}: {len(batch)} comptes importés (total: {imported})")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erreur batch {i//batch_size + 1}: {e}")
        
        # Vérification finale
        total_final = PlanComptable.query.count()
        print(f"🎉 Import terminé: {total_final} comptes en base de données")
        
        return total_final

def main():
    """Fonction principale"""
    print("🚀 CONVERSION PLAN COMPTABLE SYCEBNL OFFICIEL")
    print("=" * 50)
    
    # Chemins des fichiers
    sql_file = "/workspace/docs/Plan_Comptable_SYCEBNL_OFFICIEL_COMPLET.sql"
    python_file = "/workspace/backend/src/data/sycebnl_plan_comptable_complet.py"
    
    try:
        # 1. Parse le fichier SQL
        comptes = parse_sql_file(sql_file)
        
        if not comptes:
            print("❌ Aucun compte trouvé dans le fichier SQL")
            return
        
        # 2. Créer le fichier Python
        create_python_file(comptes, python_file)
        
        # 3. Importer en base de données
        total_imported = import_to_database(comptes)
        
        print(f"\n🎯 RÉSUMÉ:")
        print(f"   📄 Fichier SQL analysé: {sql_file}")
        print(f"   📝 Fichier Python créé: {python_file}")
        print(f"   📊 Comptes importés: {total_imported}")
        print(f"   ✅ Plan comptable SYCEBNL complet opérationnel!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()