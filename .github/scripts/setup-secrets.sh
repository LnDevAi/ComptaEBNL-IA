#!/bin/bash

# ========================================
# Script de configuration des secrets GitHub Actions
# ComptaEBNL-IA CI/CD Pipeline
# ========================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Configuration des secrets GitHub Actions pour ComptaEBNL-IA${NC}"
echo "=================================================================="

# Vérifier si GitHub CLI est installé
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) n'est pas installé.${NC}"
    echo "Installez-le depuis: https://cli.github.com/"
    exit 1
fi

# Vérifier l'authentification GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}🔑 Authentification GitHub requise...${NC}"
    gh auth login
fi

# Fonction pour définir un secret
set_secret() {
    local secret_name=$1
    local secret_description=$2
    local secret_value=""
    
    echo -e "\n${YELLOW}🔐 Configuration: ${secret_name}${NC}"
    echo "Description: ${secret_description}"
    
    # Vérifier si le secret existe déjà
    if gh secret list | grep -q "^${secret_name}"; then
        echo -e "${YELLOW}⚠️  Le secret ${secret_name} existe déjà.${NC}"
        read -p "Voulez-vous le remplacer? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 0
        fi
    fi
    
    # Demander la valeur du secret
    echo -n "Entrez la valeur pour ${secret_name}: "
    read -s secret_value
    echo
    
    # Définir le secret
    if echo "$secret_value" | gh secret set "$secret_name"; then
        echo -e "${GREEN}✅ Secret ${secret_name} configuré avec succès${NC}"
    else
        echo -e "${RED}❌ Erreur lors de la configuration du secret ${secret_name}${NC}"
    fi
}

# Fonction pour définir des variables d'environnement
set_env_var() {
    local var_name=$1
    local var_description=$2
    local var_value=""
    
    echo -e "\n${YELLOW}🔧 Configuration: ${var_name}${NC}"
    echo "Description: ${var_description}"
    
    echo -n "Entrez la valeur pour ${var_name}: "
    read var_value
    
    # GitHub CLI ne supporte pas encore les variables d'environnement
    # Nous les configurons comme des secrets pour l'instant
    if echo "$var_value" | gh secret set "$var_name"; then
        echo -e "${GREEN}✅ Variable ${var_name} configurée avec succès${NC}"
    else
        echo -e "${RED}❌ Erreur lors de la configuration de la variable ${var_name}${NC}"
    fi
}

echo -e "\n${GREEN}📋 Liste des secrets à configurer:${NC}"
echo "=================================="

# Configuration des secrets pour le déploiement
echo -e "\n${BLUE}🚀 SECRETS DE DÉPLOIEMENT${NC}"

set_secret "DATABASE_URL" "URL de la base de données PostgreSQL de production"
set_secret "SECRET_KEY" "Clé secrète Flask pour la production (générez une clé aléatoire de 32+ caractères)"
set_secret "JWT_SECRET_KEY" "Clé secrète JWT pour l'authentification"

# Configuration des secrets de paiement
echo -e "\n${BLUE}💳 SECRETS DE PAIEMENT${NC}"

set_secret "STRIPE_SECRET_KEY" "Clé secrète Stripe pour le traitement des paiements"
set_secret "STRIPE_WEBHOOK_SECRET" "Secret webhook Stripe pour vérifier les signatures"
set_secret "PAYPAL_CLIENT_ID" "ID client PayPal pour les paiements"
set_secret "PAYPAL_CLIENT_SECRET" "Secret client PayPal"

# Configuration des secrets Mobile Money
echo -e "\n${BLUE}📱 SECRETS MOBILE MONEY${NC}"

set_secret "MTN_MOMO_API_KEY" "Clé API MTN Mobile Money"
set_secret "ORANGE_MONEY_API_KEY" "Clé API Orange Money"
set_secret "WAVE_API_KEY" "Clé API Wave"
set_secret "MOOV_MONEY_API_KEY" "Clé API Moov Money"
set_secret "AIRTEL_MONEY_API_KEY" "Clé API Airtel Money"

# Configuration des secrets de notification
echo -e "\n${BLUE}📢 SECRETS DE NOTIFICATION${NC}"

set_secret "SLACK_WEBHOOK" "URL webhook Slack pour les notifications de déploiement"
set_secret "EMAIL_USERNAME" "Nom d'utilisateur email pour les notifications"
set_secret "EMAIL_PASSWORD" "Mot de passe email pour les notifications"

# Configuration des secrets de monitoring
echo -e "\n${BLUE}📊 SECRETS DE MONITORING${NC}"

set_secret "SENTRY_DSN" "DSN Sentry pour le monitoring des erreurs"
set_secret "CODECOV_TOKEN" "Token Codecov pour les rapports de couverture"

# Configuration des secrets Docker
echo -e "\n${BLUE}🐳 SECRETS DOCKER${NC}"

echo -e "${YELLOW}Note: Le token GitHub est automatiquement disponible via GITHUB_TOKEN${NC}"
echo -e "${YELLOW}Aucune configuration supplémentaire nécessaire pour Docker Registry${NC}"

# Affichage du résumé
echo -e "\n${GREEN}📋 RÉSUMÉ DE LA CONFIGURATION${NC}"
echo "=================================="

# Lister tous les secrets configurés
echo -e "\n${BLUE}Secrets configurés:${NC}"
gh secret list

echo -e "\n${GREEN}✅ Configuration terminée!${NC}"
echo -e "\n${YELLOW}📝 PROCHAINES ÉTAPES:${NC}"
echo "1. Vérifiez que tous les secrets sont correctement configurés"
echo "2. Testez le pipeline CI/CD en créant une Pull Request"
echo "3. Configurez les environnements 'staging' et 'production' dans GitHub"
echo "4. Activez les protections de branche pour la branche 'main'"

echo -e "\n${BLUE}🔗 Liens utiles:${NC}"
echo "- Secrets GitHub: https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/settings/secrets/actions"
echo "- Environnements: https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/settings/environments"
echo "- Actions: https://github.com/$(gh repo view --json owner,name -q '.owner.login + \"/\" + .name')/actions"

echo -e "\n${GREEN}🎉 Votre pipeline CI/CD ComptaEBNL-IA est prêt!${NC}"