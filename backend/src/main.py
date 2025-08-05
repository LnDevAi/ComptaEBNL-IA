#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComptaEBNL-IA - Application Flask Principale
Système de gestion comptable avec IA pour entités à but non lucratif
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime
import logging

# Import des modèles et configurations
from models import db, init_default_data
from config import Config

def create_app(config_class=Config):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configuration du logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Initialisation des extensions
    db.init_app(app)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Création du dossier uploads
    upload_folder = os.path.join(app.root_path, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Enregistrement des blueprints API
    from api import create_api_blueprints
    create_api_blueprints(app)
    
    # Routes principales
    @app.route('/')
    def index():
        """Page d'accueil avec informations système"""
        return jsonify({
            'application': 'ComptaEBNL-IA',
            'version': '1.0.0-beta',
            'description': 'Système de gestion comptable avec IA pour entités à but non lucratif',
            'referentiel': 'SYCEBNL - Système Comptable des Entités à But Non Lucratif',
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'api_base': '/api/v1',
                'plan_comptable': '/api/v1/plan-comptable',
                'ecritures': '/api/v1/ecritures',
                'balance': '/api/v1/balance',
                'ia': '/api/v1/upload-document',
                'tableau_bord': '/api/v1/tableau-bord'
            },
            'features': [
                'Plan comptable SYCEBNL complet (1162+ comptes)',
                'Saisie et validation d\'écritures comptables',
                'Balance comptable et grand livre',
                'Agent IA pour génération automatique d\'écritures',
                'OCR et traitement de documents',
                'Gestion spécialisée EBNL (dons, subventions, bénévolat)',
                'API REST complète'
            ]
        })
    
    @app.route('/api/info')
    def api_info():
        """Informations sur l'API"""
        return jsonify({
            'api_name': 'ComptaEBNL-IA API',
            'version': '1.0.0',
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'documentation': '/api/docs',
            'health': 'ok'
        })
    
    @app.route('/api/health')
    def health_check():
        """Vérification de santé de l'application"""
        try:
            # Test de connexion à la base de données
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        # Vérification des dossiers nécessaires
        uploads_exists = os.path.exists(upload_folder)
        
        health_data = {
            'status': 'healthy' if db_status == 'connected' and uploads_exists else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {
                'database': db_status,
                'uploads_folder': 'ok' if uploads_exists else 'missing',
                'config': 'loaded'
            }
        }
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return jsonify(health_data), status_code
    
    @app.route('/api/docs')
    def api_documentation():
        """Documentation de l'API"""
        return jsonify({
            'title': 'ComptaEBNL-IA API Documentation',
            'version': '1.0.0',
            'description': 'API REST pour la gestion comptable des entités à but non lucratif',
            'base_url': request.url_root + 'api/v1',
            'endpoints': {
                'Plan Comptable': {
                    'GET /plan-comptable': 'Liste des comptes avec filtres',
                    'GET /plan-comptable/classes': 'Liste des classes SYCEBNL',
                    'GET /plan-comptable/classe/{classe}': 'Comptes d\'une classe',
                    'GET /plan-comptable/compte/{numero}': 'Détail d\'un compte',
                    'GET /plan-comptable/search': 'Recherche de comptes',
                    'GET /plan-comptable/stats': 'Statistiques du plan comptable',
                    'GET /plan-comptable/validate': 'Validation du plan comptable'
                },
                'Écritures Comptables': {
                    'GET /ecritures': 'Liste des écritures avec pagination',
                    'POST /ecritures': 'Création d\'une nouvelle écriture',
                    'GET /ecritures/{id}': 'Détail d\'une écriture',
                    'POST /ecritures/{id}/valider': 'Validation d\'une écriture',
                    'GET /balance': 'Balance comptable',
                    'GET /grand-livre/{compte}': 'Grand livre d\'un compte',
                    'GET /journaux': 'Liste des journaux comptables',
                    'GET /tableau-bord': 'Tableau de bord comptable'
                },
                'Intelligence Artificielle': {
                    'POST /upload-document': 'Upload et traitement de document',
                    'POST /ocr-document/{id}': 'Traitement OCR d\'un document',
                    'POST /generer-ecriture': 'Génération automatique d\'écriture',
                    'POST /suggestions-compte': 'Suggestions de comptes comptables',
                    'GET /config-ia': 'Configuration de l\'IA'
                }
            },
            'authentication': 'Bearer token (à implémenter)',
            'rate_limiting': 'À implémenter',
            'examples': {
                'create_ecriture': {
                    'url': 'POST /api/v1/ecritures',
                    'body': {
                        'date_ecriture': '2024-01-15',
                        'libelle': 'Achat fournitures bureau',
                        'journal': 'ACH',
                        'piece_justificative': 'FAC-2024-001',
                        'lignes': [
                            {
                                'numero_compte': '6064',
                                'libelle': 'Fournitures de bureau',
                                'debit': 120.50,
                                'credit': 0
                            },
                            {
                                'numero_compte': '401',
                                'libelle': 'Fournisseur ABC',
                                'debit': 0,
                                'credit': 120.50
                            }
                        ]
                    }
                },
                'ia_generation': {
                    'url': 'POST /api/v1/generer-ecriture',
                    'body': {
                        'type_operation': 'don',
                        'donateur': 'Jean Dupont',
                        'date': '2024-01-15',
                        'montant': 50.00,
                        'description': 'Don pour projet éducatif'
                    }
                }
            }
        })
    
    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint non trouvé',
            'message': 'L\'URL demandée n\'existe pas',
            'code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Erreur interne du serveur',
            'message': 'Une erreur inattendue s\'est produite',
            'code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 'Requête invalide',
            'message': 'Les données envoyées sont incorrectes',
            'code': 400
        }), 400
    
    # Middleware pour logging des requêtes API
    @app.before_request
    def log_request_info():
        if request.path.startswith('/api/'):
            app.logger.info(f'{request.method} {request.path} - {request.remote_addr}')
    
    # Initialisation de la base de données et données par défaut
    with app.app_context():
        try:
            # Créer toutes les tables
            db.create_all()
            
            # Initialiser les données par défaut
            init_default_data()
            
            app.logger.info("Base de données initialisée avec succès")
            
        except Exception as e:
            app.logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
    
    return app

# Application instance pour le développement
app = create_app()

if __name__ == '__main__':
    print("🚀 Démarrage de ComptaEBNL-IA")
    print("=" * 50)
    print("📊 Système comptable avec IA pour EBNL")
    print("📋 Référentiel: SYCEBNL")
    print("🌐 Interface API: http://localhost:5000")
    print("📖 Documentation: http://localhost:5000/api/docs")
    print("💚 Santé: http://localhost:5000/api/health")
    print("=" * 50)
    
    # Lancement en mode développement
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
