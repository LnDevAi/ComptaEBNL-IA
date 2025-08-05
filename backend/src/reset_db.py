#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de réinitialisation de la base de données ComptaEBNL-IA
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import create_app
from models import db

def reset_database():
    """Supprime et recrée toute la base de données"""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Suppression de toutes les tables...")
        
        # Supprimer toutes les tables
        db.drop_all()
        
        print("✅ Tables supprimées")
        
        print("🔨 Création des nouvelles tables...")
        
        # Recréer toutes les tables
        db.create_all()
        
        print("✅ Tables créées")
        
        # Initialiser les données par défaut
        from models import init_default_data
        init_default_data()
        
        print("✅ Données par défaut initialisées")
        
        print("🎉 Base de données réinitialisée avec succès !")

if __name__ == '__main__':
    confirm = input("⚠️  Voulez-vous vraiment supprimer toute la base de données ? (oui/non): ")
    if confirm.lower() in ['oui', 'o', 'yes', 'y']:
        reset_database()
    else:
        print("❌ Opération annulée")