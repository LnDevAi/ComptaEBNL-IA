# API Module for ComptaEBNL-IA
from flask import Blueprint

def create_api_blueprints(app):
    """Enregistre tous les blueprints API"""
    from .comptabilite import comptabilite_bp
    from .plan_comptable import plan_comptable_bp
    from .ia import ia_bp
    
    # Préfixe API v1
    app.register_blueprint(plan_comptable_bp, url_prefix='/api/v1')
    app.register_blueprint(comptabilite_bp, url_prefix='/api/v1')
    app.register_blueprint(ia_bp, url_prefix='/api/v1')