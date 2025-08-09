#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import Final du Plan Comptable SYCEBNL Complet (1162 comptes)
=============================================================

Ce script extrait et importe TOUS les comptes du fichier SQL officiel 
SYCEBNL dans la base de données.
"""

import re
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models import db, PlanComptable

def extract_all_accounts_from_sql():
    """Extrait TOUS les comptes du fichier SQL officiel"""
    sql_file = "/workspace/docs/Plan_Comptable_SYCEBNL_OFFICIEL_COMPLET.sql"
    
    print(f"📄 Lecture du fichier SQL: {sql_file}")
    
    comptes = []
    
    with open(sql_file, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Pattern plus robuste pour extraire les INSERT VALUES
        # Chercher tous les INSERT avec VALUES
        insert_sections = re.findall(
            r"INSERT INTO `plan_comptable`[^;]*VALUES\s*(.*?);", 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        
        print(f"🔍 Trouvé {len(insert_sections)} sections INSERT")
        
        for section_num, section in enumerate(insert_sections):
            print(f"📋 Traitement section {section_num + 1}...")
            
            # Pattern pour extraire chaque ligne de valeurs
            # Format: ('numero', 'code', 'libelle', 'observations', niveau, 'parent', 'classe', 'type')
            values_pattern = r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']*)'\s*,\s*(\d+)\s*,\s*'([^']*)'\s*,\s*'(\d+)'\s*,\s*'([^']*)'\s*\)"
            
            matches = re.findall(values_pattern, section)
            
            for match in matches:
                numero, code, libelle, observations, niveau, parent, classe, type_entite = match
                
                # Nettoyer les échappements SQL
                libelle = libelle.replace("''", "'")
                observations = observations.replace("''", "'")
                
                compte = {
                    'numero': numero.strip(),
                    'code': code.strip(),
                    'libelle': libelle.strip(),
                    'observations': observations.strip(),
                    'niveau': int(niveau),
                    'parent': parent.strip() if parent.strip() else None,
                    'classe': int(classe),
                    'type_entite': type_entite.strip()
                }
                
                # Éviter les doublons
                if not any(c['numero'] == compte['numero'] for c in comptes):
                    comptes.append(compte)
    
    print(f"✅ {len(comptes)} comptes uniques extraits")
    return comptes

def import_all_accounts(comptes):
    """Importe tous les comptes en base de données"""
    print(f"🔄 Import de {len(comptes)} comptes en base de données...")
    
    app = create_app()
    with app.app_context():
        # Supprimer tous les comptes existants
        print("🗑️  Suppression des comptes existants...")
        PlanComptable.query.delete()
        db.session.commit()
        print("✅ Comptes existants supprimés")
        
        # Statistiques par classe
        stats_par_classe = {}
        for i in range(1, 10):
            stats_par_classe[i] = len([c for c in comptes if c['classe'] == i])
        
        print(f"\n📊 Répartition des comptes à importer:")
        for classe, count in stats_par_classe.items():
            if count > 0:
                print(f"   Classe {classe}: {count:>3} comptes")
        
        # Import par batch
        batch_size = 25  # Plus petit pour éviter les erreurs
        imported = 0
        errors = 0
        
        for i in range(0, len(comptes), batch_size):
            batch = comptes[i:i + batch_size]
            
            for compte_data in batch:
                try:
                    # Vérifier si le compte existe déjà
                    existing = PlanComptable.query.filter_by(
                        numero_compte=compte_data['numero']
                    ).first()
                    
                    if existing:
                        # Mettre à jour
                        existing.libelle_compte = compte_data['libelle']
                        existing.classe = compte_data['classe']
                        existing.niveau = compte_data['niveau']
                        existing.observations = compte_data['observations']
                    else:
                        # Créer nouveau
                        compte = PlanComptable(
                            numero_compte=compte_data['numero'],
                            libelle_compte=compte_data['libelle'],
                            classe=compte_data['classe'],
                            niveau=compte_data['niveau'],
                            actif=True,
                            observations=compte_data['observations'] or "Compte SYCEBNL Officiel"
                        )
                        db.session.add(compte)
                        
                except Exception as e:
                    print(f"❌ Erreur compte {compte_data['numero']}: {e}")
                    errors += 1
            
            try:
                db.session.commit()
                imported += len(batch)
                print(f"✅ Batch {i//batch_size + 1:>2}: {len(batch):>2} comptes (total: {imported:>4})")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erreur batch {i//batch_size + 1}: {e}")
                errors += len(batch)
        
        # Vérification finale
        total_final = PlanComptable.query.count()
        
        print(f"\n🎉 RÉSULTAT FINAL:")
        print(f"   📊 Comptes en base: {total_final}")
        print(f"   ✅ Comptes importés: {imported}")
        print(f"   ❌ Erreurs: {errors}")
        print(f"   📈 Taux de succès: {(total_final/len(comptes))*100:.1f}%")
        
        # Statistiques finales par classe
        print(f"\n📋 RÉPARTITION FINALE PAR CLASSE:")
        total_par_classe = {}
        for classe in range(1, 10):
            count = PlanComptable.query.filter_by(classe=classe).count()
            if count > 0:
                total_par_classe[classe] = count
                print(f"   Classe {classe}: {count:>3} comptes")
        
        # Exemples de comptes
        if total_final > 0:
            print(f"\n📋 Exemples de comptes importés:")
            exemples = PlanComptable.query.order_by(PlanComptable.numero_compte).limit(15).all()
            for compte in exemples:
                print(f"   {compte.numero_compte:>6} - {compte.libelle_compte[:60]}")
        
        return total_final

def main():
    """Fonction principale"""
    print("🚀 IMPORT FINAL PLAN COMPTABLE SYCEBNL (1162 COMPTES)")
    print("=" * 60)
    
    try:
        # 1. Extraire tous les comptes du SQL
        comptes = extract_all_accounts_from_sql()
        
        if len(comptes) == 0:
            print("❌ Aucun compte trouvé dans le fichier SQL")
            return
        
        print(f"🎯 {len(comptes)} comptes extraits du fichier SQL officiel")
        
        # 2. Importer en base de données
        total_imported = import_all_accounts(comptes)
        
        if total_imported >= 1000:
            print(f"\n🎉 SUCCÈS ! Plan comptable SYCEBNL complet avec {total_imported} comptes")
            print("✅ Conformité SYCEBNL officielle atteinte")
        else:
            print(f"\n⚠️  Attention: seulement {total_imported} comptes importés")
            print("💡 Vérifiez le fichier SQL source")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()