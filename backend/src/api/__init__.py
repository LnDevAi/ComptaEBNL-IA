# API Module for ComptaEBNL-IA
from flask import Blueprint

def create_api_blueprints(app):
    """Enregistre tous les blueprints API"""
    from .comptabilite import comptabilite_bp
    from .plan_comptable import plan_comptable_bp
    from .ia import ia_bp
    from .etats_financiers import etats_financiers_bp
    from .exercices import exercices_bp
    from .import_export import import_export_bp
    from .utilisateurs import utilisateurs_bp

    # Préfixe API v1
    app.register_blueprint(plan_comptable_bp, url_prefix='/api/v1')
    app.register_blueprint(comptabilite_bp, url_prefix='/api/v1')
    app.register_blueprint(ia_bp, url_prefix='/api/v1')
    app.register_blueprint(etats_financiers_bp, url_prefix='/api/v1')
    app.register_blueprint(exercices_bp, url_prefix='/api/v1')
    app.register_blueprint(import_export_bp, url_prefix='/api/v1')
    app.register_blueprint(utilisateurs_bp, url_prefix='/api/v1')