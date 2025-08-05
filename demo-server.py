#!/usr/bin/env python3
"""
Serveur de démonstration ComptaEBNL-IA
Sert le frontend et expose l'API backend sur un seul port
"""

import os
import time
import subprocess
import threading
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Template HTML pour la page de démonstration
DEMO_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ComptaEBNL-IA - Plateforme de Démonstration</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
            color: #333;
            line-height: 1.6;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header {
            text-align: center;
            color: white;
            padding: 40px 0;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .status-ok { color: #4caf50; font-weight: bold; }
        .status-error { color: #f44336; font-weight: bold; }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #1976d2;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 10px 10px 0 0;
            transition: background 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        .btn:hover { background: #1565c0; }
        .btn-success { background: #4caf50; }
        .btn-success:hover { background: #45a049; }
        .feature {
            display: flex;
            align-items: center;
            margin: 15px 0;
        }
        .icon {
            width: 30px;
            height: 30px;
            background: #1976d2;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            margin-right: 15px;
            font-weight: bold;
        }
        .api-endpoint {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
            border-left: 4px solid #1976d2;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 40px 0;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 ComptaEBNL-IA</h1>
            <p>Plateforme de Comptabilité EBNL avec Intelligence Artificielle</p>
            <p><em>Système Comptable des Entités à But Non Lucratif</em></p>
        </div>

        <div class="card">
            <h2>🚀 État des Services</h2>
            <div class="grid">
                <div>
                    <h3>🔧 Backend Flask API</h3>
                    <p>Port: <strong>5001</strong></p>
                    <p>Status: <span id="backend-status">Vérification...</span></p>
                    <a href="/api/health" class="btn" target="_blank">Health Check</a>
                    <a href="/api/docs" class="btn" target="_blank">Documentation</a>
                </div>
                <div>
                    <h3>🎨 Frontend React</h3>
                    <p>Port: <strong>3001</strong></p>
                    <p>Status: <span id="frontend-status">Vérification...</span></p>
                    <a href="http://localhost:3001" class="btn btn-success" target="_blank">Ouvrir l'Application</a>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>✨ Fonctionnalités Développées</h2>
            <div class="grid">
                <div>
                    <div class="feature">
                        <div class="icon">📊</div>
                        <div>
                            <strong>Plan Comptable SYCEBNL</strong><br>
                            975+ comptes officiels intégrés
                        </div>
                    </div>
                    <div class="feature">
                        <div class="icon">🤖</div>
                        <div>
                            <strong>Intelligence Artificielle</strong><br>
                            OCR et génération automatique
                        </div>
                    </div>
                    <div class="feature">
                        <div class="icon">🔐</div>
                        <div>
                            <strong>Authentification JWT</strong><br>
                            Sécurité et gestion des rôles
                        </div>
                    </div>
                </div>
                <div>
                    <div class="feature">
                        <div class="icon">📈</div>
                        <div>
                            <strong>États Financiers</strong><br>
                            Bilan, compte de résultat, flux
                        </div>
                    </div>
                    <div class="feature">
                        <div class="icon">🏦</div>
                        <div>
                            <strong>Rapprochement Bancaire</strong><br>
                            Réconciliation automatique
                        </div>
                    </div>
                    <div class="feature">
                        <div class="icon">📱</div>
                        <div>
                            <strong>Interface Moderne</strong><br>
                            React + TypeScript + Material-UI
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔗 Liens d'Accès Direct</h2>
            <div class="api-endpoint">
                <strong>Application Principale:</strong><br>
                <a href="http://localhost:3001" target="_blank">http://localhost:3001</a>
            </div>
            <div class="api-endpoint">
                <strong>API Health Check:</strong><br>
                <a href="/api/health" target="_blank">http://localhost:8080/api/health</a>
            </div>
            <div class="api-endpoint">
                <strong>Plan Comptable SYCEBNL:</strong><br>
                <a href="/api/v1/plan-comptable/stats" target="_blank">http://localhost:8080/api/v1/plan-comptable/stats</a>
            </div>
        </div>

        <div class="card">
            <h2>📊 Statistiques Système</h2>
            <div id="stats-container">
                <p>Chargement des statistiques...</p>
            </div>
        </div>

        <div class="footer">
            <p>🎉 Plateforme ComptaEBNL-IA - Développée avec succès!</p>
            <p>Stack: Flask + React + TypeScript + Material-UI + SQLite</p>
        </div>
    </div>

    <script>
        // Vérification du statut des services
        async function checkServices() {
            try {
                const response = await fetch('/api/health');
                if (response.ok) {
                    document.getElementById('backend-status').innerHTML = '<span class="status-ok">✅ Opérationnel</span>';
                } else {
                    document.getElementById('backend-status').innerHTML = '<span class="status-error">❌ Erreur</span>';
                }
            } catch (error) {
                document.getElementById('backend-status').innerHTML = '<span class="status-error">❌ Non accessible</span>';
            }

            try {
                const response = await fetch('http://localhost:3001');
                if (response.ok) {
                    document.getElementById('frontend-status').innerHTML = '<span class="status-ok">✅ Opérationnel</span>';
                } else {
                    document.getElementById('frontend-status').innerHTML = '<span class="status-error">❌ Erreur</span>';
                }
            } catch (error) {
                document.getElementById('frontend-status').innerHTML = '<span class="status-error">❌ Non accessible</span>';
            }
        }

        // Charger les statistiques
        async function loadStats() {
            try {
                const response = await fetch('/api/v1/plan-comptable/stats');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        const stats = data.data;
                        document.getElementById('stats-container').innerHTML = `
                            <div class="grid">
                                <div>
                                    <h4>📊 Plan Comptable</h4>
                                    <p><strong>${stats.total_comptes}</strong> comptes SYCEBNL</p>
                                    <p><strong>${stats.comptes_utilises}</strong> comptes utilisés</p>
                                </div>
                                <div>
                                    <h4>🏗️ Architecture</h4>
                                    <p><strong>12</strong> modules backend</p>
                                    <p><strong>50+</strong> endpoints API</p>
                                </div>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                document.getElementById('stats-container').innerHTML = '<p class="status-error">❌ Erreur de chargement des statistiques</p>';
            }
        }

        // Lancer les vérifications
        checkServices();
        loadStats();
        
        // Actualiser toutes les 30 secondes
        setInterval(checkServices, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def demo_page():
    """Page de démonstration principale"""
    return render_template_string(DEMO_TEMPLATE)

@app.route('/api/<path:path>')
def proxy_api(path):
    """Proxy vers l'API backend"""
    try:
        backend_url = f"http://localhost:5001/api/{path}"
        response = requests.get(backend_url)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": f"Backend non accessible: {str(e)}"}, 503

@app.route('/status')
def status():
    """Status général de la plateforme"""
    try:
        # Test backend
        backend_response = requests.get("http://localhost:5001/api/health", timeout=5)
        backend_ok = backend_response.status_code == 200
    except:
        backend_ok = False
    
    try:
        # Test frontend
        frontend_response = requests.get("http://localhost:3001", timeout=5)
        frontend_ok = frontend_response.status_code == 200
    except:
        frontend_ok = False
    
    return jsonify({
        "platform": "ComptaEBNL-IA",
        "backend": "✅ Opérationnel" if backend_ok else "❌ Non accessible",
        "frontend": "✅ Opérationnel" if frontend_ok else "❌ Non accessible",
        "demo_url": "http://localhost:8080",
        "app_url": "http://localhost:3001" if frontend_ok else "Non disponible"
    })

if __name__ == '__main__':
    print("🌐 SERVEUR DE DÉMONSTRATION COMPTAEBNL-IA")
    print("=" * 50)
    print("🎯 Page de démonstration: http://localhost:8080")
    print("🔧 Proxy API: http://localhost:8080/api/...")
    print("📊 Status: http://localhost:8080/status")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )