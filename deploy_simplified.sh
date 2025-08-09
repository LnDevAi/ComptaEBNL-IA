#!/bin/bash
# 🚀 Script de déploiement simplifié avec guidance
# Gère toutes les vérifications et guide l'utilisateur

set -e

echo "🚀 ================================================="
echo "   DÉPLOIEMENT SIMPLIFIÉ COMPTAEBNL-IA"
echo "   Guide pas-à-pas avec vérifications"
echo "🚀 ================================================="

# Variables de couleur
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction de pause pour laisser l'utilisateur lire
pause_with_message() {
    local message="$1"
    echo ""
    echo -e "${YELLOW}📋 $message${NC}"
    echo -e "${BLUE}Appuyez sur Entrée pour continuer...${NC}"
    read -r
}

# Étape 1: Vérification des prérequis
check_prerequisites() {
    log_info "Étape 1: Vérification des prérequis techniques"
    echo ""
    
    local all_good=true
    
    # AWS CLI
    if command -v aws &> /dev/null; then
        log_success "AWS CLI installé: $(aws --version | cut -d' ' -f1,2)"
    else
        log_error "AWS CLI non installé"
        all_good=false
    fi
    
    # Node.js
    if command -v node &> /dev/null; then
        log_success "Node.js installé: $(node --version)"
    else
        log_error "Node.js non installé"
        all_good=false
    fi
    
    # Amplify CLI
    if command -v amplify &> /dev/null; then
        log_success "Amplify CLI installé"
    else
        log_error "Amplify CLI non installé"
        all_good=false
    fi
    
    # Docker (optionnel pour Amplify)
    if command -v docker &> /dev/null; then
        log_success "Docker installé: $(docker --version | cut -d' ' -f1,2,3)"
    else
        log_warning "Docker non installé (optionnel pour Amplify)"
    fi
    
    if [ "$all_good" = false ]; then
        echo ""
        log_error "PRÉREQUIS MANQUANTS!"
        echo ""
        echo "🛠️ Pour installer les prérequis:"
        echo "   ./setup_aws_prerequisites.sh"
        echo ""
        exit 1
    fi
    
    log_success "Tous les prérequis sont installés"
    echo ""
}

# Étape 2: Configuration AWS
configure_aws() {
    log_info "Étape 2: Configuration AWS"
    echo ""
    
    # Vérifier si AWS est configuré
    if aws sts get-caller-identity &>/dev/null; then
        log_success "AWS CLI déjà configuré"
        echo ""
        echo "📋 Informations du compte AWS:"
        aws sts get-caller-identity --output table
        echo ""
        
        echo "Voulez-vous utiliser cette configuration ? (o/n)"
        read -r response
        if [[ "$response" != "o" && "$response" != "O" && "$response" != "yes" ]]; then
            configure_aws_fresh
        fi
    else
        log_warning "AWS CLI non configuré"
        echo ""
        configure_aws_fresh
    fi
}

# Configuration AWS fraîche
configure_aws_fresh() {
    echo ""
    log_info "Configuration AWS CLI..."
    echo ""
    echo "🔑 Vous avez besoin de vos clés AWS:"
    echo ""
    echo "📋 Comment obtenir vos clés:"
    echo "   1. Connectez-vous à https://console.aws.amazon.com"
    echo "   2. Allez dans IAM > Users > [Votre utilisateur]"
    echo "   3. Onglet 'Security credentials'"
    echo "   4. Cliquez 'Create access key'"
    echo "   5. Choisissez 'Command Line Interface (CLI)'"
    echo "   6. Copiez les clés générées"
    echo ""
    
    pause_with_message "Avez-vous vos clés AWS prêtes ?"
    
    echo ""
    log_info "Configuration AWS CLI..."
    echo ""
    echo "💡 Conseils:"
    echo "   - Region recommandée: us-east-1"
    echo "   - Output format: json"
    echo ""
    
    aws configure
    
    echo ""
    log_info "Vérification de la configuration..."
    if aws sts get-caller-identity &>/dev/null; then
        log_success "Configuration AWS réussie !"
        echo ""
        aws sts get-caller-identity --output table
    else
        log_error "Configuration AWS échouée"
        echo ""
        echo "🔧 Vérifiez:"
        echo "   - Clés AWS correctes"
        echo "   - Permissions de l'utilisateur"
        echo "   - Connexion internet"
        echo ""
        exit 1
    fi
}

# Étape 3: Choix de l'option de déploiement
choose_deployment_option() {
    log_info "Étape 3: Choix de l'option de déploiement"
    echo ""
    
    echo "🚀 Options de déploiement disponibles:"
    echo ""
    echo "1. 🟢 AWS Amplify (RECOMMANDÉ)"
    echo "   ✅ Simple et rapide"
    echo "   ✅ SSL/HTTPS automatique"
    echo "   ✅ Scaling automatique"
    echo "   ✅ Free tier disponible"
    echo "   💰 Coût: ~$15-40/mois après free tier"
    echo ""
    echo "2. 🟡 Déploiement manuel Amplify"
    echo "   ✅ Contrôle étape par étape"
    echo "   ✅ Idéal pour débogage"
    echo ""
    echo "3. 🔵 AWS ECS/Fargate (AVANCÉ)"
    echo "   ✅ Containers Docker"
    echo "   ✅ Production enterprise"
    echo "   💰 Coût: ~$100-150/mois"
    echo ""
    
    echo "Choisissez une option (1-3): "
    read -r choice
    
    case $choice in
        1)
            DEPLOYMENT_TYPE="amplify-auto"
            log_success "Option choisie: AWS Amplify automatique"
            ;;
        2)
            DEPLOYMENT_TYPE="amplify-manual"
            log_success "Option choisie: AWS Amplify manuel"
            ;;
        3)
            DEPLOYMENT_TYPE="ecs"
            log_success "Option choisie: AWS ECS/Fargate"
            ;;
        *)
            log_warning "Option invalide, utilisation d'Amplify automatique par défaut"
            DEPLOYMENT_TYPE="amplify-auto"
            ;;
    esac
    
    echo ""
}

# Déploiement Amplify automatique
deploy_amplify_auto() {
    log_info "Déploiement AWS Amplify automatique"
    echo ""
    
    log_info "Utilisation du script de déploiement automatisé..."
    
    if [ -f "deployment/scripts/deploy-to-aws.sh" ]; then
        chmod +x deployment/scripts/deploy-to-aws.sh
        echo ""
        log_info "Lancement du déploiement..."
        echo ""
        
        ./deployment/scripts/deploy-to-aws.sh production amplify us-east-1
        
    else
        log_error "Script de déploiement non trouvé"
        echo ""
        log_info "Tentative de déploiement manuel..."
        deploy_amplify_manual
    fi
}

# Déploiement Amplify manuel
deploy_amplify_manual() {
    log_info "Déploiement AWS Amplify manuel"
    echo ""
    
    # Vérifier si Amplify est déjà initialisé
    if [ -d "amplify" ]; then
        log_warning "Projet Amplify déjà initialisé"
        echo ""
        echo "Voulez-vous réinitialiser ? (o/n)"
        read -r response
        if [[ "$response" == "o" || "$response" == "O" || "$response" == "yes" ]]; then
            rm -rf amplify
            log_info "Projet Amplify supprimé"
        fi
    fi
    
    echo ""
    log_info "Étape 1: Initialisation Amplify"
    echo ""
    echo "💡 Configuration recommandée:"
    echo "   - Project name: comptaebnl-ia"
    echo "   - Environment: production"
    echo "   - Editor: Visual Studio Code"
    echo "   - Type: javascript"
    echo "   - Framework: react"
    echo "   - Source directory: frontend/src"
    echo "   - Build directory: frontend/build"
    echo "   - Build command: npm run build"
    echo "   - Start command: npm start"
    echo ""
    
    pause_with_message "Prêt pour l'initialisation Amplify ?"
    
    echo ""
    amplify init
    
    echo ""
    log_info "Étape 2: Ajout du hosting"
    pause_with_message "Configuration du hosting..."
    
    amplify add hosting
    
    echo ""
    log_info "Étape 3: Déploiement"
    pause_with_message "Lancement du déploiement..."
    
    amplify push
    
    echo ""
    log_info "Étape 4: Publication"
    amplify publish
    
    echo ""
    log_success "Déploiement Amplify manuel terminé !"
}

# Déploiement ECS
deploy_ecs() {
    log_info "Déploiement AWS ECS/Fargate"
    echo ""
    
    log_warning "Déploiement ECS nécessite Docker configuré"
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker non installé - requis pour ECS"
        echo ""
        echo "Installez Docker avec:"
        echo "   ./setup_aws_prerequisites.sh"
        exit 1
    fi
    
    # Vérifier si Docker fonctionne
    if ! docker info &>/dev/null; then
        log_error "Docker daemon non démarré"
        echo ""
        echo "Démarrez Docker avec:"
        echo "   sudo systemctl start docker"
        echo "   sudo usermod -aG docker $USER"
        echo "   newgrp docker"
        exit 1
    fi
    
    log_info "Lancement du déploiement ECS..."
    echo ""
    
    if [ -f "deployment/scripts/deploy-to-aws.sh" ]; then
        chmod +x deployment/scripts/deploy-to-aws.sh
        ./deployment/scripts/deploy-to-aws.sh production ecs us-east-1
    else
        log_error "Script ECS non trouvé"
        exit 1
    fi
}

# Vérification post-déploiement
post_deployment_check() {
    log_info "Vérification post-déploiement"
    echo ""
    
    case $DEPLOYMENT_TYPE in
        "amplify-auto"|"amplify-manual")
            if command -v amplify &> /dev/null; then
                echo ""
                log_info "Statut Amplify:"
                amplify status || echo "Impossible d'obtenir le statut"
                
                echo ""
                log_info "Pour obtenir l'URL de votre application:"
                echo "   amplify hosting list"
                echo ""
            fi
            ;;
        "ecs")
            echo ""
            log_info "Pour vérifier ECS:"
            echo "   aws ecs list-clusters"
            echo "   aws ecs list-services --cluster comptaebnl-ia-cluster"
            echo ""
            ;;
    esac
    
    echo ""
    log_success "🎉 DÉPLOIEMENT TERMINÉ !"
    echo ""
    echo "📋 Prochaines étapes:"
    echo "   1. Testez votre application"
    echo "   2. Configurez un domaine personnalisé (optionnel)"
    echo "   3. Configurez le monitoring"
    echo ""
}

# Programme principal
main() {
    echo ""
    echo "🎯 Ce script va vous guider étape par étape pour déployer ComptaEBNL-IA"
    echo ""
    
    pause_with_message "Prêt à commencer ?"
    
    check_prerequisites
    configure_aws
    choose_deployment_option
    
    echo ""
    log_info "Début du déploiement avec l'option: $DEPLOYMENT_TYPE"
    echo ""
    
    case $DEPLOYMENT_TYPE in
        "amplify-auto")
            deploy_amplify_auto
            ;;
        "amplify-manual")
            deploy_amplify_manual
            ;;
        "ecs")
            deploy_ecs
            ;;
    esac
    
    post_deployment_check
}

# Gestion des erreurs
trap 'echo ""; log_error "Déploiement interrompu"; exit 1' INT

# Aide
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "🚀 Script de déploiement simplifié ComptaEBNL-IA"
    echo ""
    echo "Usage: $0"
    echo ""
    echo "Ce script guide pas-à-pas pour:"
    echo "   1. Vérifier les prérequis"
    echo "   2. Configurer AWS CLI"
    echo "   3. Choisir l'option de déploiement"
    echo "   4. Déployer l'application"
    echo ""
    echo "Options de déploiement:"
    echo "   - AWS Amplify (automatique)"
    echo "   - AWS Amplify (manuel)"
    echo "   - AWS ECS/Fargate"
    echo ""
    exit 0
fi

# Exécuter le programme principal
main