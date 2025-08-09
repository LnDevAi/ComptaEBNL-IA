# 🚀 Guide de Déploiement AWS - ComptaEBNL-IA

## 🎯 **Projet Prêt pour AWS !**

Le projet ComptaEBNL-IA est maintenant **nettoyé et optimisé** pour un déploiement AWS professionnel.

## 📋 **Options de Déploiement AWS**

### **🟢 Option 1: AWS Amplify (Recommandé - Simple)**
**Idéal pour**: Déploiement rapide, scaling automatique, développeurs
- ✅ Frontend React déployé automatiquement
- ✅ Backend API avec AWS Lambda
- ✅ Base de données managée (RDS)
- ✅ CDN CloudFront inclus
- ✅ SSL/HTTPS automatique
- ✅ CI/CD intégré

### **🟡 Option 2: AWS ECS/Fargate (Recommandé - Production)**
**Idéal pour**: Applications containerisées, contrôle avancé
- ✅ Containers Docker optimisés prêts
- ✅ Scaling horizontal automatique
- ✅ Load Balancer Application (ALB)
- ✅ Monitoring CloudWatch intégré
- ✅ Zero-downtime deployments

### **🔵 Option 3: AWS EC2 + Docker (Contrôle Total)**
**Idéal pour**: Contrôle infrastructure, coûts optimisés
- ✅ Instances EC2 configurables
- ✅ Docker Compose production prêt
- ✅ Contrôle complet de l'infrastructure

## 🚀 **Déploiement AWS Amplify (Recommandé)**

### **📋 Prérequis**
```bash
# 1. Installer AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 2. Installer Amplify CLI
npm install -g @aws-amplify/cli

# 3. Configurer AWS credentials
aws configure
```

### **🎯 Étapes de Déploiement**

#### **1. Initialiser Amplify**
```bash
# Dans le dossier du projet
amplify init

# Configuration recommandée:
# Project name: comptaebnl-ia
# Environment: production
# Default editor: Visual Studio Code
# App type: javascript
# Framework: react
# Source directory: frontend/src
# Build directory: frontend/build
# Build command: npm run build
# Start command: npm start
```

#### **2. Ajouter Hosting**
```bash
# Hosting pour le frontend
amplify add hosting

# Choisir:
# - Amazon CloudFront and S3
# - DEV (S3 only with HTTP) ou PROD (S3 with CloudFront over HTTPS)
```

#### **3. Ajouter API Backend**
```bash
# API REST pour le backend Flask
amplify add api

# Configuration:
# - REST API
# - API name: comptaebnl-api
# - Path: /api
# - Lambda function: comptaebnl-backend
# - Runtime: Python 3.11
```

#### **4. Ajouter Base de Données**
```bash
# Base de données PostgreSQL
amplify add storage

# Configuration:
# - SQL Database (Amazon RDS)
# - PostgreSQL
# - Database name: comptaebnl_prod
```

#### **5. Déployer**
```bash
# Déploiement complet
amplify push

# Publier le site
amplify publish
```

## 🐳 **Déploiement AWS ECS/Fargate**

### **📋 Prérequis**
```bash
# 1. AWS CLI configuré
# 2. Docker installé
# 3. ECR (Elastic Container Registry) configuré
```

### **🎯 Étapes de Déploiement**

#### **1. Créer ECR Repository**
```bash
# Créer repositories pour les images
aws ecr create-repository --repository-name comptaebnl-backend
aws ecr create-repository --repository-name comptaebnl-frontend

# Obtenir l'URL de connexion
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

#### **2. Build et Push Images**
```bash
# Build images de production
docker build -f backend/Dockerfile.prod -t comptaebnl-backend:latest backend/
docker build -f frontend/Dockerfile.prod -t comptaebnl-frontend:latest frontend/

# Tag pour ECR
docker tag comptaebnl-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/comptaebnl-backend:latest
docker tag comptaebnl-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/comptaebnl-frontend:latest

# Push vers ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/comptaebnl-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/comptaebnl-frontend:latest
```

#### **3. Créer ECS Cluster**
```bash
# Créer cluster Fargate
aws ecs create-cluster --cluster-name comptaebnl-cluster --capacity-providers FARGATE
```

#### **4. Déployer avec Task Definition**
```bash
# Utiliser les task definitions dans aws/ecs/
aws ecs register-task-definition --cli-input-json file://aws/ecs/backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://aws/ecs/frontend-task-definition.json

# Créer services
aws ecs create-service --cluster comptaebnl-cluster --service-name comptaebnl-backend --task-definition comptaebnl-backend
aws ecs create-service --cluster comptaebnl-cluster --service-name comptaebnl-frontend --task-definition comptaebnl-frontend
```

## 🏗️ **Infrastructure AWS Recommandée**

### **🌐 Architecture Production**
```
Internet
    ↓
CloudFront (CDN)
    ↓
Application Load Balancer (ALB)
    ↓
┌─────────────────┬─────────────────┐
│  Frontend       │  Backend        │
│  (React/Nginx)  │  (Flask/Python) │
│  ECS Fargate    │  ECS Fargate    │
└─────────────────┴─────────────────┘
    ↓                      ↓
S3 Bucket              RDS PostgreSQL
(Uploads)              ElastiCache Redis
```

### **📋 Services AWS Requis**

#### **🔧 Compute & Hosting**
- **ECS Fargate** ou **Amplify** (containers/serverless)
- **ALB** (Application Load Balancer)
- **CloudFront** (CDN global)

#### **💾 Stockage & Base de Données**
- **RDS PostgreSQL** (base de données principale)
- **ElastiCache Redis** (cache et sessions)
- **S3** (uploads, certificates, static files)

#### **🔐 Sécurité & Monitoring**
- **Secrets Manager** (clés API, passwords)
- **CloudWatch** (logs et monitoring)
- **Certificate Manager** (SSL certificates)
- **IAM** (permissions et rôles)

#### **🌍 Réseau**
- **VPC** (réseau privé)
- **Security Groups** (firewall)
- **NAT Gateway** (accès internet sortant)

## 🔧 **Configuration des Variables**

### **📄 .env Production**
```bash
# Copier le template
cp .env.example .env.production

# Configurer les variables AWS
NODE_ENV=production
FLASK_ENV=production

# Base de données AWS RDS
DATABASE_URL=postgresql://comptaebnl:password@comptaebnl-db.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/comptaebnl_prod

# Cache AWS ElastiCache
REDIS_URL=redis://comptaebnl-cache.xxxxx.cache.amazonaws.com:6379

# Secrets (AWS Secrets Manager)
SECRET_KEY={{resolve:secretsmanager:comptaebnl/secret-key}}
JWT_SECRET_KEY={{resolve:secretsmanager:comptaebnl/jwt-secret}}

# AWS Services
AWS_REGION=us-east-1
AWS_S3_BUCKET=comptaebnl-uploads-prod
AWS_CLOUDFRONT_DOMAIN=d123456789.cloudfront.net

# Paiements Production
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY={{resolve:secretsmanager:comptaebnl/stripe-secret}}

# Mobile Money Production
MTN_API_KEY={{resolve:secretsmanager:comptaebnl/mtn-api-key}}
ORANGE_API_KEY={{resolve:secretsmanager:comptaebnl/orange-api-key}}

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
CLOUDWATCH_LOG_GROUP=/aws/ecs/comptaebnl
```

## 💰 **Estimation des Coûts AWS**

### **💡 Configuration Optimisée (50-100 utilisateurs)**
```
🏗️ Infrastructure:
├── ECS Fargate (2 vCPU, 4GB)    ~$50/mois
├── RDS PostgreSQL (db.t3.micro)  ~$20/mois
├── ElastiCache Redis (t3.micro)  ~$15/mois
├── ALB                          ~$20/mois
├── CloudFront                   ~$5/mois
├── S3 Storage (10GB)            ~$1/mois
└── Secrets Manager              ~$2/mois

💰 Total estimé: ~$113/mois
```

### **🚀 Configuration Production (500+ utilisateurs)**
```
🏗️ Infrastructure:
├── ECS Fargate (4 vCPU, 8GB)    ~$150/mois
├── RDS PostgreSQL (db.t3.small)  ~$40/mois
├── ElastiCache Redis (t3.small)  ~$30/mois
├── ALB + Auto Scaling           ~$30/mois
├── CloudFront                   ~$15/mois
├── S3 Storage (50GB)            ~$3/mois
└── Monitoring & Logs            ~$10/mois

💰 Total estimé: ~$278/mois
```

## 🎯 **Commandes de Déploiement Rapide**

### **🚀 Déploiement Complet (ECS)**
```bash
# 1. Préparer l'environnement
./deployment/scripts/setup-aws-environment.sh

# 2. Build et déployer
./deployment/scripts/deploy-to-aws.sh production

# 3. Vérifier le déploiement
./deployment/scripts/health-check.sh
```

### **⚡ Déploiement Amplify**
```bash
# 1. Initialiser
amplify init --yes

# 2. Configurer et déployer
amplify add hosting
amplify add api
amplify add storage
amplify push --yes

# 3. Publier
amplify publish --yes
```

## 📊 **Monitoring et Maintenance**

### **🔍 Monitoring Essentiel**
- **CloudWatch Dashboards** (métriques temps réel)
- **CloudWatch Alarms** (alertes automatiques)
- **X-Ray Tracing** (performance API)
- **AWS Config** (conformité sécurité)

### **🔄 Maintenance Régulière**
- **Backup automatique RDS** (daily)
- **Log rotation CloudWatch** (30 jours)
- **Security patches** (automatique)
- **Scaling monitoring** (métriques CPU/RAM)

## 🎉 **Résultat Final**

Après déploiement, vous aurez :

✅ **Application accessible** via URL AWS
✅ **HTTPS/SSL automatique** avec CloudFront
✅ **Scaling automatique** selon la charge
✅ **Monitoring complet** avec CloudWatch
✅ **Backups automatiques** de la base
✅ **CI/CD intégré** pour les mises à jour
✅ **Sécurité AWS** avec IAM et Security Groups

## 🚀 **Prochaines Étapes**

1. **Choisir option déploiement** (Amplify recommandé pour simplicité)
2. **Configurer AWS CLI** et credentials
3. **Ajuster variables d'environnement** selon besoins
4. **Lancer déploiement** avec commandes ci-dessus
5. **Configurer monitoring** et alertes

**🎯 ComptaEBNL-IA est prêt pour un déploiement AWS professionnel ! 🎯**