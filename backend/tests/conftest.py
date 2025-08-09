"""
Configuration pytest pour ComptaEBNL-IA
Fixtures et configuration des tests
"""

import pytest
import os
import sys

# Ajouter le chemin src au PYTHONPATH pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def test_database_url():
    """URL de base de données pour les tests"""
    return "sqlite:///:memory:"

@pytest.fixture
def test_user_data():
    """Données utilisateur de test"""
    return {
        "email": "test@comptaebnl.com",
        "password": "testpassword123",
        "nom": "Test User",
        "organisation": "Test EBNL"
    }

@pytest.fixture
def test_plan_data():
    """Données de plan d'abonnement de test"""
    return {
        "nom": "Test Plan",
        "prix": 49000,
        "fonctionnalites": ["feature1", "feature2"],
        "quota_utilisateurs": 5
    }