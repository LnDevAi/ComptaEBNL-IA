# ComptaEBNL-IA Backend Dockerfile
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="ComptaEBNL-IA Team"
LABEL description="Backend Flask pour plateforme de gestion EBNL OHADA"
LABEL version="1.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# Créer utilisateur non-root pour la sécurité
RUN groupadd -r comptaebnl && useradd -r -g comptaebnl comptaebnl

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY tests/ ./tests/
COPY *.py ./

# Créer les dossiers nécessaires
RUN mkdir -p instance/uploads instance/certificates instance/logs

# Changer la propriété vers l'utilisateur non-root
RUN chown -R comptaebnl:comptaebnl /app

# Basculer vers l'utilisateur non-root
USER comptaebnl

# Exposer le port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "60", "src.app:app"]