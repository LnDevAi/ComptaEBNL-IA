# Dockerfile pour Backend ComptaEBNL-IA
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="ComptaEBNL-IA Team"
LABEL description="Backend Flask pour ComptaEBNL-IA - Comptabilité EBNL avec IA"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ .

# Création des répertoires nécessaires
RUN mkdir -p /app/data /app/uploads /app/static

# Permissions
RUN chmod +x main.py

# Port d'exposition
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# Commande de démarrage
CMD ["python3", "main.py"]