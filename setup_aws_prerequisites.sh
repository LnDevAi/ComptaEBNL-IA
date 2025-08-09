#!/bin/bash
# 🛠️ Installation automatique des prérequis AWS pour ComptaEBNL-IA
# Ce script installe AWS CLI, Docker, et Amplify CLI

set -e

echo "🛠️ ================================================="
echo "   INSTALLATION PRÉREQUIS AWS"
echo "   ComptaEBNL-IA - Configuration automatique"
echo "🛠️ ================================================="

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

# Fonction de vérification système
check_system() {
    log_info "Vérification du système..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_success "Système détecté: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_success "Système détecté: macOS"
    else
        log_error "Système non supporté: $OSTYPE"
        exit 1
    fi
    
    # Vérifier les permissions sudo
    if sudo -n true 2>/dev/null; then
        log_success "Permissions sudo disponibles"
    else
        log_warning "Certaines installations nécessiteront sudo"
    fi
}

# Fonction d'installation AWS CLI
install_aws_cli() {
    log_info "Installation AWS CLI..."
    
    if command -v aws &> /dev/null; then
        log_success "AWS CLI déjà installé: $(aws --version)"
        return 0
    fi
    
    if [[ "$OS" == "linux" ]]; then
        # Installation pour Linux
        log_info "Téléchargement AWS CLI pour Linux..."
        curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
        
        if command -v unzip &> /dev/null; then
            cd /tmp
            unzip -q awscliv2.zip
            sudo ./aws/install --update 2>/dev/null || sudo ./aws/install
            rm -rf /tmp/aws /tmp/awscliv2.zip
        else
            log_error "unzip non disponible. Installez-le avec: sudo apt install unzip"
            exit 1
        fi
        
    elif [[ "$OS" == "macos" ]]; then
        # Installation pour macOS
        if command -v brew &> /dev/null; then
            log_info "Installation via Homebrew..."
            brew install awscli
        else
            log_info "Téléchargement AWS CLI pour macOS..."
            curl -s "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "/tmp/AWSCLIV2.pkg"
            sudo installer -pkg /tmp/AWSCLIV2.pkg -target /
            rm /tmp/AWSCLIV2.pkg
        fi
    fi
    
    # Vérification installation
    if command -v aws &> /dev/null; then
        log_success "AWS CLI installé avec succès: $(aws --version)"
    else
        log_error "Échec installation AWS CLI"
        exit 1
    fi
}

# Fonction d'installation Docker
install_docker() {
    log_info "Installation Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker déjà installé: $(docker --version)"
        return 0
    fi
    
    if [[ "$OS" == "linux" ]]; then
        # Installation Docker pour Linux
        log_info "Installation Docker pour Linux..."
        
        # Mettre à jour les paquets
        sudo apt-get update -qq
        
        # Installer les prérequis
        sudo apt-get install -y -qq \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Ajouter la clé GPG Docker
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # Ajouter le repository Docker
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Installer Docker
        sudo apt-get update -qq
        sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io
        
        # Ajouter l'utilisateur au groupe docker
        sudo usermod -aG docker $USER
        
        # Démarrer Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
    elif [[ "$OS" == "macos" ]]; then
        # Installation Docker pour macOS
        if command -v brew &> /dev/null; then
            log_info "Installation Docker Desktop via Homebrew..."
            brew install --cask docker
        else
            log_warning "Installez Docker Desktop manuellement depuis https://docker.com/products/docker-desktop"
            return 1
        fi
    fi
    
    # Vérification installation
    if command -v docker &> /dev/null; then
        log_success "Docker installé avec succès"
        log_warning "Vous devrez peut-être vous reconnecter pour utiliser Docker sans sudo"
    else
        log_error "Échec installation Docker"
        exit 1
    fi
}

# Fonction d'installation Node.js (si nécessaire)
install_nodejs() {
    log_info "Vérification Node.js..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_success "Node.js déjà installé: $NODE_VERSION"
        
        # Vérifier la version (minimum v16)
        if [[ "${NODE_VERSION#v}" =~ ^([0-9]+) ]]; then
            if [[ ${BASH_REMATCH[1]} -ge 16 ]]; then
                return 0
            else
                log_warning "Version Node.js trop ancienne ($NODE_VERSION). Mise à jour recommandée."
            fi
        fi
    fi
    
    log_info "Installation Node.js LTS..."
    
    if [[ "$OS" == "linux" ]]; then
        # Installation Node.js pour Linux
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
        
    elif [[ "$OS" == "macos" ]]; then
        # Installation Node.js pour macOS
        if command -v brew &> /dev/null; then
            brew install node
        else
            log_warning "Installez Node.js manuellement depuis https://nodejs.org"
            return 1
        fi
    fi
    
    if command -v node &> /dev/null; then
        log_success "Node.js installé: $(node --version)"
    else
        log_error "Échec installation Node.js"
        exit 1
    fi
}

# Fonction d'installation Amplify CLI
install_amplify_cli() {
    log_info "Installation Amplify CLI..."
    
    if command -v amplify &> /dev/null; then
        log_success "Amplify CLI déjà installé: $(amplify --version)"
        return 0
    fi
    
    # Installer via npm
    if command -v npm &> /dev/null; then
        log_info "Installation Amplify CLI via npm..."
        sudo npm install -g @aws-amplify/cli
        
        # Vérification installation
        if command -v amplify &> /dev/null; then
            log_success "Amplify CLI installé avec succès"
        else
            log_error "Échec installation Amplify CLI"
            exit 1
        fi
    else
        log_error "npm non disponible. Installez Node.js d'abord."
        exit 1
    fi
}

# Fonction de configuration AWS
configure_aws() {
    log_info "Configuration AWS..."
    
    if aws sts get-caller-identity &>/dev/null; then
        log_success "AWS CLI déjà configuré"
        aws sts get-caller-identity --output table
        return 0
    fi
    
    log_warning "AWS CLI non configuré. Configuration manuelle requise."
    echo ""
    echo "🔑 Pour configurer AWS CLI, exécutez:"
    echo "   aws configure"
    echo ""
    echo "Vous aurez besoin de:"
    echo "   - AWS Access Key ID"
    echo "   - AWS Secret Access Key"
    echo "   - Default region (ex: us-east-1)"
    echo "   - Default output format (json)"
    echo ""
}

# Fonction de vérification finale
final_check() {
    log_info "Vérification finale des prérequis..."
    
    echo ""
    echo "📋 ÉTAT DES PRÉREQUIS:"
    echo "====================="
    
    # AWS CLI
    if command -v aws &> /dev/null; then
        echo "✅ AWS CLI: $(aws --version)"
    else
        echo "❌ AWS CLI: Non installé"
    fi
    
    # Docker
    if command -v docker &> /dev/null; then
        echo "✅ Docker: $(docker --version 2>/dev/null || echo 'Installé mais service arrêté')"
    else
        echo "❌ Docker: Non installé"
    fi
    
    # Node.js
    if command -v node &> /dev/null; then
        echo "✅ Node.js: $(node --version)"
    else
        echo "❌ Node.js: Non installé"
    fi
    
    # npm
    if command -v npm &> /dev/null; then
        echo "✅ npm: $(npm --version)"
    else
        echo "❌ npm: Non installé"
    fi
    
    # Amplify CLI
    if command -v amplify &> /dev/null; then
        echo "✅ Amplify CLI: Installé"
    else
        echo "❌ Amplify CLI: Non installé"
    fi
    
    # Configuration AWS
    if aws sts get-caller-identity &>/dev/null; then
        echo "✅ AWS Configuration: Configuré"
    else
        echo "⚠️ AWS Configuration: À configurer"
    fi
    
    echo ""
}

# Programme principal
main() {
    echo -e "${BLUE}Début de l'installation des prérequis AWS...${NC}"
    echo ""
    
    check_system
    echo ""
    
    install_aws_cli
    echo ""
    
    install_docker
    echo ""
    
    install_nodejs
    echo ""
    
    install_amplify_cli
    echo ""
    
    configure_aws
    echo ""
    
    final_check
    
    echo ""
    log_success "🎉 INSTALLATION DES PRÉREQUIS TERMINÉE !"
    echo ""
    echo "📋 PROCHAINES ÉTAPES:"
    echo "1. Si AWS CLI n'est pas configuré: aws configure"
    echo "2. Si vous avez installé Docker: vous reconnecter ou faire 'newgrp docker'"
    echo "3. Tester le déploiement: ./deployment/scripts/deploy-to-aws.sh production amplify"
    echo ""
}

# Afficher l'aide si demandé
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "🛠️ Script d'installation des prérequis AWS pour ComptaEBNL-IA"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h    Afficher cette aide"
    echo "  --check       Vérifier seulement l'état actuel"
    echo ""
    echo "Ce script installe:"
    echo "  - AWS CLI v2"
    echo "  - Docker CE"
    echo "  - Node.js LTS"
    echo "  - Amplify CLI"
    echo ""
    exit 0
fi

# Option de vérification seulement
if [[ "$1" == "--check" ]]; then
    final_check
    exit 0
fi

# Exécuter le programme principal
main