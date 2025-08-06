"""
Configuration Flask pour ComptaEBNL-IA
"""

import os
from datetime import timedelta

class Config:
    """Configuration de base"""
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///comptaebnl.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Paiements
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_...'
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') or 'whsec_...'
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID') or 'paypal_client_id'
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET') or 'paypal_client_secret'
    
    # Mobile Money
    MTN_MOMO_API_KEY = os.environ.get('MTN_MOMO_API_KEY') or 'mtn_api_key'
    ORANGE_MONEY_API_KEY = os.environ.get('ORANGE_MONEY_API_KEY') or 'orange_api_key'
    WAVE_API_KEY = os.environ.get('WAVE_API_KEY') or 'wave_api_key'

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    """Configuration de test"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration par défaut
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
