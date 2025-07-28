from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Configuration ComptaEBNL-IA
app.config['SECRET_KEY'] = 'ComptaEBNL-IA-Secret-Key-2024-SYCEBNL'
app.config['APP_NAME'] = 'ComptaEBNL-IA'
app.config['VERSION'] = '1.0.0'

# Configuration CORS pour permettre les requêtes frontend
CORS(app, origins="*")

# Route d'information sur l'API
@app.route('/api/info')
def api_info():
    return jsonify({
        'app': app.config['APP_NAME'],
        'version': app.config['VERSION'],
        'description': 'API de gestion comptable avec IA pour entités à but non lucratif',
        'sycebnl': 'Système Comptable des Entités à But Non Lucratif',
        'status': 'active'
    })

# Route de santé pour monitoring
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': 'now()'
    })

# Route des utilisateurs (template)
@app.route('/api/users')
def get_users():
    return jsonify([])

@app.route('/')
def home():
    return jsonify({
        'message': 'ComptaEBNL-IA API Server',
        'version': app.config['VERSION'],
        'endpoints': ['/api/info', '/api/health', '/api/users']
    })

if __name__ == '__main__':
    print("🚀 Démarrage de ComptaEBNL-IA API Server...")
    print("📊 Plateforme de gestion comptable avec IA pour EBNL")
    print("🔗 API disponible sur: http://localhost:5000" )
    app.run(host='0.0.0.0', port=5000, debug=True)
