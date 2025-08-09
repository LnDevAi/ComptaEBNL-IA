#!/bin/bash
# 🚀 Script de déploiement automatisé vers AWS
# Supporte ECS/Fargate, Amplify et EC2

set -e

echo "🚀 ================================================="
echo "   DÉPLOIEMENT AUTOMATISÉ VERS AWS"
echo "   ComptaEBNL-IA Production Deployment"
echo "🚀 ================================================="

# Variables de couleur
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuration
ENVIRONMENT=${1:-production}
DEPLOYMENT_TYPE=${2:-ecs}  # ecs, amplify, ec2
AWS_REGION=${3:-us-east-1}
PROJECT_NAME="comptaebnl-ia"

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

# Fonction de vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI n'est pas installé. Installez-le avec: curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install"
        exit 1
    fi
    
    # Vérifier credentials AWS
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "Credentials AWS non configurés. Exécutez: aws configure"
        exit 1
    fi
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    log_success "Prérequis vérifiés"
}

# Fonction de déploiement ECS/Fargate
deploy_ecs() {
    log_info "Déploiement ECS/Fargate..."
    
    # Variables ECS
    CLUSTER_NAME="${PROJECT_NAME}-cluster"
    ECR_REPO_BACKEND="${PROJECT_NAME}-backend"
    ECR_REPO_FRONTEND="${PROJECT_NAME}-frontend"
    
    # Obtenir l'ID du compte AWS
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    log_info "Configuration ECS:"
    log_info "- Cluster: $CLUSTER_NAME"
    log_info "- Région: $AWS_REGION"
    log_info "- ECR URI: $ECR_URI"
    
    # 1. Créer ECR repositories si ils n'existent pas
    log_info "Création des repositories ECR..."
    aws ecr describe-repositories --repository-names $ECR_REPO_BACKEND --region $AWS_REGION &>/dev/null || \
        aws ecr create-repository --repository-name $ECR_REPO_BACKEND --region $AWS_REGION
    
    aws ecr describe-repositories --repository-names $ECR_REPO_FRONTEND --region $AWS_REGION &>/dev/null || \
        aws ecr create-repository --repository-name $ECR_REPO_FRONTEND --region $AWS_REGION
    
    log_success "Repositories ECR créés/vérifiés"
    
    # 2. Login Docker vers ECR
    log_info "Connexion Docker vers ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI
    log_success "Connexion ECR réussie"
    
    # 3. Build des images Docker
    log_info "Build des images Docker de production..."
    
    # Build backend
    docker build -f backend/Dockerfile.prod -t $ECR_REPO_BACKEND:latest backend/
    docker tag $ECR_REPO_BACKEND:latest $ECR_URI/$ECR_REPO_BACKEND:latest
    docker tag $ECR_REPO_BACKEND:latest $ECR_URI/$ECR_REPO_BACKEND:$ENVIRONMENT
    
    # Build frontend
    docker build -f frontend/Dockerfile.prod -t $ECR_REPO_FRONTEND:latest frontend/
    docker tag $ECR_REPO_FRONTEND:latest $ECR_URI/$ECR_REPO_FRONTEND:latest
    docker tag $ECR_REPO_FRONTEND:latest $ECR_URI/$ECR_REPO_FRONTEND:$ENVIRONMENT
    
    log_success "Images Docker buildées"
    
    # 4. Push des images vers ECR
    log_info "Push des images vers ECR..."
    docker push $ECR_URI/$ECR_REPO_BACKEND:latest
    docker push $ECR_URI/$ECR_REPO_BACKEND:$ENVIRONMENT
    docker push $ECR_URI/$ECR_REPO_FRONTEND:latest
    docker push $ECR_URI/$ECR_REPO_FRONTEND:$ENVIRONMENT
    log_success "Images poussées vers ECR"
    
    # 5. Créer/Mettre à jour le cluster ECS
    log_info "Configuration du cluster ECS..."
    aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION &>/dev/null || \
        aws ecs create-cluster --cluster-name $CLUSTER_NAME --capacity-providers FARGATE --region $AWS_REGION
    log_success "Cluster ECS configuré"
    
    # 6. Déployer les services (si task definitions existent)
    if [ -f "aws/ecs/backend-task-definition.json" ]; then
        log_info "Déploiement backend service..."
        # Remplacer les variables dans la task definition
        sed "s/{{ECR_URI}}/$ECR_URI/g; s/{{AWS_REGION}}/$AWS_REGION/g; s/{{ENVIRONMENT}}/$ENVIRONMENT/g" \
            aws/ecs/backend-task-definition.json > /tmp/backend-task-def.json
        
        aws ecs register-task-definition --cli-input-json file:///tmp/backend-task-def.json --region $AWS_REGION
        log_success "Backend task definition mise à jour"
    fi
    
    log_success "Déploiement ECS terminé avec succès!"
    log_info "URL de vérification: https://console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/$CLUSTER_NAME"
}

# Fonction de déploiement Amplify
deploy_amplify() {
    log_info "Déploiement AWS Amplify..."
    
    # Vérifier Amplify CLI
    if ! command -v amplify &> /dev/null; then
        log_warning "Amplify CLI non installé. Installation..."
        npm install -g @aws-amplify/cli
    fi
    
    # Initialiser Amplify si pas déjà fait
    if [ ! -f "amplify/backend/amplify-meta.json" ]; then
        log_info "Initialisation Amplify..."
        amplify init --yes \
            --name $PROJECT_NAME \
            --environment $ENVIRONMENT \
            --defaultEditor code \
            --appType javascript \
            --framework react \
            --srcDir frontend/src \
            --distDir frontend/build \
            --buildCommand "npm run build" \
            --startCommand "npm start"
    fi
    
    # Ajouter hosting si pas déjà configuré
    if [ ! -f "amplify/backend/hosting/amplifyhosting/amplifyhosting-template.json" ]; then
        log_info "Configuration hosting Amplify..."
        amplify add hosting --yes
    fi
    
    # Déployer
    log_info "Déploiement Amplify en cours..."
    amplify push --yes
    amplify publish --yes
    
    log_success "Déploiement Amplify terminé!"
    
    # Obtenir l'URL de l'application
    APP_URL=$(amplify status | grep "Current Environment" -A 10 | grep "Hosting endpoint" | awk '{print $3}')
    log_success "Application accessible à: $APP_URL"
}

# Fonction de déploiement EC2
deploy_ec2() {
    log_info "Déploiement EC2 avec Docker Compose..."
    
    # Variables EC2
    INSTANCE_NAME="${PROJECT_NAME}-${ENVIRONMENT}"
    KEY_NAME="${PROJECT_NAME}-key"
    
    log_warning "Déploiement EC2 nécessite une instance existante"
    log_info "Configuration manuelle requise:"
    log_info "1. Créer une instance EC2"
    log_info "2. Installer Docker et Docker Compose"
    log_info "3. Transférer le code et les fichiers de configuration"
    log_info "4. Exécuter: docker-compose -f docker-compose.prod.yml up -d"
    
    # Générer un script de déploiement pour EC2
    cat > deployment/ec2-deploy.sh << 'EOF'
#!/bin/bash
# Script à exécuter sur l'instance EC2
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Déployer l'application
docker-compose -f docker-compose.prod.yml up -d
EOF
    
    chmod +x deployment/ec2-deploy.sh
    log_success "Script EC2 généré: deployment/ec2-deploy.sh"
}

# Fonction de vérification post-déploiement
post_deployment_check() {
    log_info "Vérification post-déploiement..."
    
    case $DEPLOYMENT_TYPE in
        "ecs")
            log_info "Vérification des services ECS..."
            aws ecs list-services --cluster $CLUSTER_NAME --region $AWS_REGION
            ;;
        "amplify")
            log_info "Vérification Amplify..."
            amplify status
            ;;
        "ec2")
            log_info "Vérification EC2 - Manuel requis"
            ;;
    esac
    
    log_success "Déploiement terminé avec succès!"
}

# Programme principal
main() {
    echo -e "${BLUE}Configuration:${NC}"
    echo "- Environnement: $ENVIRONMENT"
    echo "- Type de déploiement: $DEPLOYMENT_TYPE"
    echo "- Région AWS: $AWS_REGION"
    echo ""
    
    check_prerequisites
    
    case $DEPLOYMENT_TYPE in
        "ecs"|"fargate")
            deploy_ecs
            ;;
        "amplify")
            deploy_amplify
            ;;
        "ec2")
            deploy_ec2
            ;;
        *)
            log_error "Type de déploiement non supporté: $DEPLOYMENT_TYPE"
            log_info "Types supportés: ecs, amplify, ec2"
            exit 1
            ;;
    esac
    
    post_deployment_check
    
    echo ""
    log_success "🎉 DÉPLOIEMENT AWS TERMINÉ AVEC SUCCÈS!"
    log_info "📋 Prochaines étapes:"
    log_info "   1. Vérifier les services dans la console AWS"
    log_info "   2. Configurer les variables d'environnement"
    log_info "   3. Tester l'application"
    log_info "   4. Configurer le monitoring"
}

# Afficher l'aide si aucun argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 [ENVIRONMENT] [DEPLOYMENT_TYPE] [AWS_REGION]"
    echo ""
    echo "Paramètres:"
    echo "  ENVIRONMENT     - production, staging, dev (défaut: production)"
    echo "  DEPLOYMENT_TYPE - ecs, amplify, ec2 (défaut: ecs)"
    echo "  AWS_REGION      - us-east-1, eu-west-1, etc. (défaut: us-east-1)"
    echo ""
    echo "Exemples:"
    echo "  $0 production ecs us-east-1"
    echo "  $0 staging amplify eu-west-1"
    echo "  $0 production ec2"
    exit 1
fi

# Exécuter le programme principal
main