# Guide d'Installation ComptaOHADA-IA

## 🎯 Vue d'ensemble

ComptaOHADA-IA est une plateforme SaaS de comptabilité pour les entités à but non lucratif de l'espace OHADA avec intelligence artificielle intégrée selon les normes SYSCEBNL.

## 🛠️ Prérequis

### Logiciels requis

- **Docker Desktop** (version 4.0+) - [Télécharger](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (version 2.0+) - Inclus avec Docker Desktop
- **Git** - [Télécharger](https://git-scm.com/)

### Configuration système minimale

- **RAM** : 8 GB minimum, 16 GB recommandé
- **CPU** : 4 cœurs minimum
- **Stockage** : 20 GB d'espace libre
- **OS** : Windows 10/11, macOS 10.15+, Ubuntu 20.04+

## 🚀 Installation Rapide

### 1. Cloner le projet

```bash
git clone https://github.com/LnDevAi/ComptaOHADA-IA.git
cd ComptaOHADA-IA
```

### 2. Configuration des variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
nano .env  # ou votre éditeur préféré
```

### 3. Démarrage avec Docker

```bash
# Windows
.\run_local.bat

# Linux/macOS
chmod +x run_local.sh
./run_local.sh
```

### 4. Accéder à la plateforme

- **Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## ⚙️ Configuration Détaillée

### Variables d'environnement

Modifiez le fichier `.env` avec vos paramètres :

```env
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://comptaohada_user:comptaohada_password@db:5432/comptaohada

# Security
SECRET_KEY=votre-clé-secrète-très-complexe
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview

# Email
MAIL_USERNAME=votre.email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app
MAIL_FROM=noreply@comptaohada.ai

# Stripe (pour les abonnements)
STRIPE_SECRET_KEY=sk_test_votre_clé_stripe
STRIPE_WEBHOOK_SECRET=whsec_votre_webhook_secret
```

### Base de données

La plateforme utilise PostgreSQL par défaut. Pour changer la base de données :

#### SQLite (développement uniquement)

```env
DATABASE_URL=sqlite:///./comptaohada_dev.db
```

#### PostgreSQL (recommandé pour la production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/comptaohada
```

## 🏗️ Installation Manuelle (sans Docker)

### Backend (FastAPI)

```bash
cd backend

# Créer un environnement virtuel Python
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r src/requirements.txt

# Configurer les variables d'environnement
cp ../.env.example .env
# Éditer .env

# Démarrer l'API
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Next.js)

```bash
cd frontend

# Installer Node.js 18+ si nécessaire
# https://nodejs.org/

# Installer les dépendances
npm install

# Configurer les variables d'environnement
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Démarrer le serveur de développement
npm run dev
```

### Base de données

```bash
# Installer PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS avec Homebrew
brew install postgresql

# Créer la base de données
sudo -u postgres psql
CREATE DATABASE comptaohada;
CREATE USER comptaohada_user WITH PASSWORD 'comptaohada_password';
GRANT ALL PRIVILEGES ON DATABASE comptaohada TO comptaohada_user;
\q
```

## 🔧 Configuration Avancée

### IA et OCR

Pour activer les fonctionnalités d'IA :

1. **OpenAI** : Obtenez une clé API sur [platform.openai.com](https://platform.openai.com/)
2. **Tesseract OCR** : Installé automatiquement avec Docker

```bash
# Installation manuelle de Tesseract
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-fra

# macOS
brew install tesseract tesseract-lang

# Windows
# Télécharger depuis: https://github.com/UB-Mannheim/tesseract/wiki
```

### Email

Configuration SMTP pour les notifications :

```env
MAIL_USERNAME=votre.email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-application-gmail
MAIL_FROM=noreply@comptaohada.ai
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

### Stripe (Abonnements)

Pour les fonctionnalités de paiement :

1. Créez un compte [Stripe](https://stripe.com/)
2. Obtenez vos clés API test/production
3. Configurez les webhooks

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 🧪 Tests

### Tests Backend

```bash
cd backend/src
pytest tests/
```

### Tests Frontend

```bash
cd frontend
npm test
```

## 📊 Monitoring

### Logs

```bash
# Voir tous les logs
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Métriques

- **API Health** : http://localhost:8000/health
- **API Info** : http://localhost:8000/info
- **Debug** : http://localhost:8000/debug/config (dev uniquement)

## 🔒 Sécurité

### Recommandations de production

1. **Changer les mots de passe par défaut**
2. **Utiliser HTTPS uniquement**
3. **Configurer un firewall approprié**
4. **Activer les sauvegardes automatiques**
5. **Surveiller les logs de sécurité**

### Variables d'environnement sensibles

```env
# Générer une clé secrète forte
SECRET_KEY=$(openssl rand -base64 32)

# Utiliser des mots de passe complexes
DATABASE_PASSWORD=$(openssl rand -base64 16)
```

## 🔧 Dépannage

### Problèmes courants

#### Erreur de port déjà utilisé

```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
netstat -tulpn | grep :5432

# Arrêter les services
docker-compose down
```

#### Problèmes de permissions Docker

```bash
# Linux : Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
# Puis se déconnecter/reconnecter
```

#### Base de données non accessible

```bash
# Vérifier le statut des conteneurs
docker-compose ps

# Redémarrer la base de données
docker-compose restart db

# Voir les logs de la base
docker-compose logs db
```

#### Frontend ne se connecte pas à l'API

```bash
# Vérifier la configuration CORS
# Dans backend/src/config.py
cors_origins: list = ["http://localhost:3000"]

# Vérifier l'URL de l'API
# Dans frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Commandes utiles

```bash
# Redémarrer complètement
docker-compose down && docker-compose up -d

# Reconstruire les images
docker-compose build --no-cache

# Nettoyer les volumes
docker-compose down -v

# Mise à jour des dépendances
docker-compose pull
```

## 📞 Support

### Documentation

- **API** : http://localhost:8000/docs
- **GitHub** : https://github.com/LnDevAi/ComptaOHADA-IA
- **Issues** : https://github.com/LnDevAi/ComptaOHADA-IA/issues

### Contact

- **Email** : support@comptaohada.ai
- **Discord** : [Rejoindre le serveur](https://discord.gg/comptaohada)

---

*Développé avec ❤️ pour l'écosystème OHADA*