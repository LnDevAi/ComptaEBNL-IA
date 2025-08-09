# 🔧 Résolution des Problèmes - Déploiement AWS

## 🎯 **DIAGNOSTIC DU PROBLÈME ACTUEL**

Le déploiement a échoué car **les prérequis AWS ne sont pas installés**. Voici la solution complète.

## ❌ **PROBLÈMES IDENTIFIÉS**

### **1. AWS CLI non installé**
```
❌ AWS CLI non installé/configuré
```

### **2. Docker non disponible**
```
❌ Docker non installé/disponible
```

### **3. Amplify CLI manquant**
```
❌ Amplify CLI non installé
```

## ✅ **SOLUTIONS IMMÉDIATES**

### **🚀 Solution Automatique (Recommandée)**

```bash
# 1. Rendre le script exécutable
chmod +x setup_aws_prerequisites.sh

# 2. Lancer l'installation automatique
./setup_aws_prerequisites.sh

# 3. Configurer AWS (après installation)
aws configure
```

### **🛠️ Solution Manuelle**

#### **Étape 1: Installer AWS CLI**
```bash
# Pour Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Vérifier
aws --version
```

#### **Étape 2: Installer Docker**
```bash
# Pour Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER

# Vérifier
docker --version
```

#### **Étape 3: Installer Amplify CLI**
```bash
# Via npm (Node.js déjà installé)
sudo npm install -g @aws-amplify/cli

# Vérifier
amplify --version
```

#### **Étape 4: Configurer AWS**
```bash
aws configure
# AWS Access Key ID: [votre clé]
# AWS Secret Access Key: [votre secret]
# Default region name: us-east-1
# Default output format: json
```

## 🔍 **DIAGNOSTICS AVANCÉS**

### **Vérifier l'état actuel**
```bash
# Script de diagnostic
./setup_aws_prerequisites.sh --check
```

### **Erreurs courantes et solutions**

#### **1. Permission denied (Docker)**
```bash
# Problème: permission denied while trying to connect to Docker
# Solution:
sudo usermod -aG docker $USER
newgrp docker
# ou redémarrer la session
```

#### **2. AWS credentials not configured**
```bash
# Problème: Unable to locate credentials
# Solution:
aws configure
# ou
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

#### **3. Amplify init failed**
```bash
# Problème: Amplify CLI not configured
# Solution:
amplify configure
# Suivre les instructions
```

#### **4. Docker daemon not running**
```bash
# Problème: Cannot connect to Docker daemon
# Solution:
sudo systemctl start docker
sudo systemctl enable docker
```

#### **5. Node.js version trop ancienne**
```bash
# Problème: Node.js version < 16
# Solution:
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 🚀 **APRÈS CORRECTION DES PRÉREQUIS**

### **Options de déploiement par ordre de simplicité**

#### **🟢 Option 1: AWS Amplify (Plus simple)**
```bash
# Après avoir configuré AWS CLI
./deployment/scripts/deploy-to-aws.sh production amplify us-east-1
```

#### **🟡 Option 2: Déploiement local puis push**
```bash
# Test local d'abord
docker-compose -f docker-compose.prod.yml build
# Puis déploiement
./deployment/scripts/deploy-to-aws.sh production ecs us-east-1
```

#### **🔵 Option 3: Déploiement manuel Amplify**
```bash
# Initialisation manuelle
amplify init
amplify add hosting
amplify add api
amplify push
amplify publish
```

## 📋 **CHECKLIST PRÉ-DÉPLOIEMENT**

Avant de relancer le déploiement, vérifiez :

- [ ] ✅ AWS CLI installé et configuré
- [ ] ✅ Docker installé et démarré
- [ ] ✅ Node.js v16+ installé
- [ ] ✅ Amplify CLI installé
- [ ] ✅ Credentials AWS valides
- [ ] ✅ Permissions suffisantes

### **Commande de vérification rapide**
```bash
./setup_aws_prerequisites.sh --check
```

## 🎯 **PROBLÈMES SPÉCIFIQUES PAR ENVIRONNEMENT**

### **🐧 Linux (Ubuntu/Debian)**
```bash
# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation prérequis
sudo apt install -y curl unzip wget

# Puis lancer le script
./setup_aws_prerequisites.sh
```

### **🍎 macOS**
```bash
# Installer Homebrew si nécessaire
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Puis lancer le script
./setup_aws_prerequisites.sh
```

### **🪟 Windows (WSL)**
```bash
# Dans WSL Ubuntu
sudo apt update
sudo apt install -y curl unzip

# Puis lancer le script
./setup_aws_prerequisites.sh
```

## 🔧 **SOLUTIONS D'URGENCE**

### **Si le script automatique échoue**

#### **AWS CLI minimal**
```bash
pip3 install awscli --user
export PATH=$PATH:~/.local/bin
aws configure
```

#### **Docker via snap (Ubuntu)**
```bash
sudo snap install docker
sudo snap connect docker:home
```

#### **Amplify via binaire direct**
```bash
# Si npm pose problème
curl -sL https://aws-amplify.github.io/amplify-cli/install | bash
```

## 🎉 **VÉRIFICATION FINALE**

Après correction, ces commandes doivent fonctionner :

```bash
# Test des outils
aws --version
docker --version
node --version
npm --version
amplify --version

# Test configuration AWS
aws sts get-caller-identity

# Test Docker
docker run hello-world

# Prêt pour déploiement !
./deployment/scripts/deploy-to-aws.sh production amplify us-east-1
```

## 📞 **SUPPORT SUPPLÉMENTAIRE**

### **Logs de débogage**
```bash
# Activer les logs détaillés
export AWS_CLI_VERBOSE=true
export DEBUG=1

# Relancer avec logs
./deployment/scripts/deploy-to-aws.sh production amplify us-east-1 2>&1 | tee deployment.log
```

### **Reset complet (si nécessaire)**
```bash
# Supprimer configurations existantes
rm -rf ~/.aws/
rm -rf ~/.amplify/
rm -rf ./amplify/

# Réinstaller depuis zéro
./setup_aws_prerequisites.sh
aws configure
```

## 🎯 **RÉSUMÉ SOLUTION RAPIDE**

```bash
# 1. Installer prérequis
chmod +x setup_aws_prerequisites.sh
./setup_aws_prerequisites.sh

# 2. Configurer AWS
aws configure

# 3. Tester configuration
./setup_aws_prerequisites.sh --check

# 4. Déployer
./deployment/scripts/deploy-to-aws.sh production amplify us-east-1
```

**🎊 Après ces étapes, votre déploiement devrait réussir ! 🎊**