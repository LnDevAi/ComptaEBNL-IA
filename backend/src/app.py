from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, migrate

from api.auth import auth_bp
from api.comptabilite import comptabilite_bp
from api.documents import documents_bp
from api.entites import entites_bp
from api.ia import ia_bp
from api.subscription import subscription_bp
from middleware.subscription_middleware import init_subscription_middleware

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Initialisation de la base de données
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialisation CORS
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Initialisation du middleware d'abonnement
    init_subscription_middleware(app)
    
    # Enregistrement des blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(comptabilite_bp, url_prefix='/api/v1')
    app.register_blueprint(documents_bp, url_prefix='/api/v1')
    app.register_blueprint(entites_bp, url_prefix='/api/v1')
    app.register_blueprint(ia_bp, url_prefix='/api/v1')
    app.register_blueprint(subscription_bp, url_prefix='/api/v1')
    
    return app