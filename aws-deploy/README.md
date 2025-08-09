# 🚀 Déploiement ComptaEBNL-IA sur AWS

Ce guide vous permet de déployer la plateforme ComptaEBNL-IA sur Amazon Web Services (AWS) avec une infrastructure complète et scalable.

## 📋 Prérequis

### 1. Compte AWS
- Compte AWS actif avec accès administrateur
- Accès à la console AWS et AWS CLI

### 2. Outils locaux
```bash
# Installation AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configuration AWS CLI
aws configure
```

### 3. Paire de clés EC2
- Créer une paire de clés EC2 dans la région choisie
- Télécharger le fichier .pem et le sécuriser

## 🎯 Architecture AWS déployée

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet Gateway                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                Application Load Balancer                    │
│              (Auto-scaling, Health Checks)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                   EC2 Instance                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Docker Containers                      │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │    │
│  │  │   Backend   │ │  Frontend   │ │    Demo     │   │    │
│  │  │   Flask     │ │   React     │ │   Server    │   │    │
│  │  │  Port 5001  │ │  Port 3001  │ │  Port 9000  │   │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Déploiement automatique

### Méthode 1: Script automatisé (Recommandé)

```bash
cd /workspace/aws-deploy
chmod +x deploy-aws.sh
./deploy-aws.sh
```

Le script vous guidera pour :
1. ✅ Vérifier les prérequis AWS
2. 🔑 Sélectionner votre paire de clés EC2
3. 🌍 Choisir la région AWS
4. 💻 Configurer le type d'instance
5. 🚀 Déployer l'infrastructure complète

### Méthode 2: Déploiement manuel CloudFormation

```bash
# Déploiement via AWS CLI
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name ComptaEBNL-IA-Stack \
    --parameter-overrides \
        KeyPairName=ma-cle-ec2 \
        InstanceType=t3.medium \
    --capabilities CAPABILITY_IAM \
    --region eu-west-1
```

## 📊 Services déployés

### ✅ Infrastructure AWS
- **VPC** avec subnets publics multi-AZ
- **Internet Gateway** et tables de routage
- **Security Groups** configurés pour les ports nécessaires
- **Application Load Balancer** avec health checks
- **EC2 Instance** avec auto-scaling
- **IAM Roles** et politiques de sécurité

### ✅ Applications ComptaEBNL-IA
- **Backend Flask** (Port 5001)
  - API RESTful complète
  - Plan comptable SYCEBNL (975+ comptes)
  - Intelligence artificielle intégrée
  - Authentification JWT
- **Frontend React** (Port 3001)
  - Interface Material-UI responsive
  - Tableaux de bord interactifs
  - Gestion comptable complète
- **Serveur de démonstration** (Port 9000)
  - Page d'accueil unifiée
  - Liens vers tous les services
  - Monitoring en temps réel

## 🌐 Accès à l'application

Après le déploiement (5-10 minutes), vous recevrez :

```
🌐 ACCÈS À L'APPLICATION:
   URL Principale: http://comptaebnl-alb-1234567890.eu-west-1.elb.amazonaws.com
   URL Directe: http://54.123.45.67:9000

🔧 ACCÈS TECHNIQUE:
   SSH: ssh -i ma-cle.pem ec2-user@54.123.45.67
   Backend API: http://54.123.45.67:5001
   Frontend React: http://54.123.45.67:3001
```

## 🔧 Configuration avancée

### Variables d'environnement
Modifiez `docker-compose.yml` pour personnaliser :
```yaml
environment:
  - FLASK_ENV=production
  - JWT_SECRET_KEY=votre-cle-secrete
  - DATABASE_URL=sqlite:///comptaebnl.db
```

### Domaine personnalisé
1. Configurez Route 53 ou votre DNS
2. Pointez vers le Load Balancer DNS
3. Configurez SSL/TLS avec Certificate Manager

### Scaling et haute disponibilité
- Auto Scaling Group configuré
- Multi-AZ deployment
- Health checks automatiques
- Load balancing distribué

## 📋 Gestion post-déploiement

### Monitoring des services
```bash
# Connexion SSH
ssh -i ma-cle.pem ec2-user@IP-INSTANCE

# Vérification des containers
docker ps

# Logs des services
cd ComptaEBNL-IA/aws-deploy
docker-compose logs -f
```

### Mise à jour de l'application
```bash
# Sur l'instance EC2
cd ComptaEBNL-IA
git pull origin main
cd aws-deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Sauvegarde des données
```bash
# Sauvegarde de la base de données
docker exec comptaebnl-backend cp /app/comptaebnl.db /app/data/
```

## 💰 Coûts estimés AWS

### Configuration minimale (t3.micro)
- **EC2 t3.micro** : ~$8/mois
- **Load Balancer** : ~$18/mois
- **Data Transfer** : Variable
- **Total estimé** : ~$30/mois

### Configuration recommandée (t3.medium)
- **EC2 t3.medium** : ~$30/mois
- **Load Balancer** : ~$18/mois
- **Data Transfer** : Variable
- **Total estimé** : ~$55/mois

## 🛡️ Sécurité

### Security Groups configurés
- Port 80/443 : Accès web public
- Port 22 : SSH (restreindre à votre IP)
- Ports 3001, 5001, 9000 : Services applicatifs

### Bonnes pratiques
- ✅ IAM roles avec permissions minimales
- ✅ Security Groups restrictifs
- ✅ Instances dans subnets privés (optionnel)
- ✅ Chiffrement des données en transit
- ✅ Monitoring CloudWatch

## 🔄 Suppression de l'infrastructure

```bash
# Suppression complète via CloudFormation
aws cloudformation delete-stack \
    --stack-name ComptaEBNL-IA-Stack \
    --region eu-west-1
```

## 📞 Support et dépannage

### Problèmes courants

1. **Déploiement échoue**
   - Vérifiez les quotas AWS de votre région
   - Vérifiez que la paire de clés existe
   - Vérifiez les permissions IAM

2. **Services non accessibles**
   - Attendez 5-10 minutes après déploiement
   - Vérifiez les Security Groups
   - Consultez les logs Docker

3. **Performance lente**
   - Augmentez le type d'instance
   - Activez l'auto-scaling
   - Optimisez la base de données

### Logs utiles
```bash
# Logs CloudFormation
aws logs describe-log-groups --region eu-west-1

# Logs EC2 User Data
sudo cat /var/log/cloud-init-output.log

# Logs applications
docker-compose logs -f
```

---

## 🎉 Félicitations !

Votre plateforme ComptaEBNL-IA est maintenant déployée sur AWS avec :
- ✅ Infrastructure scalable et sécurisée
- ✅ Haute disponibilité multi-AZ
- ✅ Monitoring et health checks automatiques
- ✅ Accès public via Load Balancer
- ✅ Toutes les fonctionnalités comptables EBNL

**🌐 Accédez à votre application via l'URL fournie après déploiement !**