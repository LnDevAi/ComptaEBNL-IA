"""
Extensions Flask pour ComptaEBNL-IA
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()