from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, PlanComptable
from config import config
import os


def create_app(config_name='development'):
    app = Flask(__name__)

    # Configuration
    app.config.from_object(config[config_name])

    # Configuration ComptaEBNL-IA
    app.config['APP_NAME'] = 'ComptaEBNL-IA'
    app.config['VERSION'] = '1.0.0'

    # Initialisation des extensions
    db.init_app(app)
    CORS(app, origins="*")

    # Création des tables
    with app.app_context():
        db.create_all()

    # Routes API
    @app.route('/api/info')
    def api_info():
        return jsonify({
            'app': app.config['APP_NAME'],
            'version': app.config['VERSION'],
            'description': 'API de gestion comptable avec IA pour entités à but non lucratif',
            'sycebnl': 'Système Comptable des Entités à But Non Lucratif',
            'status': 'active',
            'database': 'connected'
        })

    @app.route('/api/health')
    def health_check():
        try:
            # Test de connexion à la base
            count = PlanComptable.query.count()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'comptes_count': count
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': 'disconnected',
                'error': str(e)
            }), 500

    @app.route('/api/comptes')
    def get_comptes():
        try:
            comptes = PlanComptable.query.all()
            return jsonify([compte.to_dict() for compte in comptes])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/comptes/classe/<int:classe>')
    def get_comptes_by_classe(classe):
        try:
            comptes = PlanComptable.query.filter_by(classe=classe).all()
            return jsonify([compte.to_dict() for compte in comptes])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/')
    def home():
        return jsonify({
            'message': 'ComptaEBNL-IA API Server',
            'version': app.config['VERSION'],
            'endpoints': ['/api/info', '/api/health', '/api/comptes']
        })

    return app


if __name__ == '__main__':
    app = create_app()
    print("🚀 Démarrage de ComptaEBNL-IA API Server...")
    print("📊 Plateforme de gestion comptable avec IA pour EBNL")
    print("🔗 API disponible sur: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
