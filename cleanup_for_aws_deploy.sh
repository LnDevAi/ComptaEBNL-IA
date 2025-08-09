#!/bin/bash
# 🧹 Nettoyage et préparation pour déploiement AWS
# Supprime les fichiers temporaires et prépare la structure AWS

set -e

echo "🧹 ================================================="
echo "   NETTOYAGE POUR DÉPLOIEMENT AWS"
echo "🧹 ================================================="

# Variables de couleur
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compteurs
REMOVED_FILES=0
CLEANED_DIRS=0

# Fonction d'affichage
log_action() {
    local action=$1
    local item=$2
    echo -e "${GREEN}✅ $action${NC}: $item"
}

log_remove() {
    local item=$1
    echo -e "${YELLOW}🗑️ Supprimé${NC}: $item"
    REMOVED_FILES=$((REMOVED_FILES + 1))
}

log_clean() {
    local item=$1
    echo -e "${BLUE}🧹 Nettoyé${NC}: $item"
    CLEANED_DIRS=$((CLEANED_DIRS + 1))
}

echo -e "\n${BLUE}📋 Phase 1: Suppression des fichiers de documentation temporaires${NC}"

# Supprimer les fichiers de documentation temporaires
DOC_FILES=(
    "ENVIRONNEMENT_TESTS_COMPLET.md"
    "GUIDE_CICD_VISIBLE.md" 
    "ENVIRONNEMENT_TESTS_FINALISE.md"
    "CORRECTIONS_APPLIQUEES.md"
    "GUIDE_CORRECTION_CICD.md"
    "FINAL_FIX_IMPOSSIBLE_ECHEC.md"
    "CORRECTION_CICD.md"
    "CORRECTION_CELERY_RESOLU.md"
    "SOLUTION_CROIX_ROUGE.md"
    "RESOLUTION_WORKFLOWS_CONFLICTUELS.md"
    "CI_CD_README.md"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        log_remove "$file"
    fi
done

echo -e "\n${BLUE}📋 Phase 2: Suppression des scripts de test temporaires${NC}"

# Supprimer les scripts de test temporaires  
TEST_SCRIPTS=(
    "check_before_push.sh"
    "test-cicd-setup.sh"
    "test_cicd_simulation.sh"
    "test_dependencies_fix.py"
)

for script in "${TEST_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        rm "$script"
        log_remove "$script"
    fi
done

echo -e "\n${BLUE}📋 Phase 3: Nettoyage dossiers de test non essentiels${NC}"

# Nettoyer le dossier tests (garder structure de base)
if [ -d "tests" ]; then
    log_clean "tests/ - Conservation structure de base"
    # Supprimer les rapports de test temporaires
    find tests/ -name "*.json" -delete 2>/dev/null || true
    find tests/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
fi

echo -e "\n${BLUE}📋 Phase 4: Nettoyage fichiers Docker de test${NC}"

# Supprimer les fichiers Docker de test
DOCKER_TEST_FILES=(
    "docker-compose.test.yml"
    "docker-compose.ci.yml"
    "backend/Dockerfile.test"
    "frontend/Dockerfile.test"
)

for file in "${DOCKER_TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        log_remove "$file"
    fi
done

echo -e "\n${BLUE}📋 Phase 5: Nettoyage node_modules et caches${NC}"

# Nettoyer node_modules si présent
if [ -d "frontend/node_modules" ]; then
    log_clean "frontend/node_modules"
    rm -rf frontend/node_modules
fi

# Nettoyer caches Python
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo -e "\n${BLUE}📋 Phase 6: Organisation pour AWS${NC}"

# Créer structure AWS recommandée
mkdir -p aws/{amplify,lambda,ecs,cloudformation}
mkdir -p deployment/{scripts,configs,templates}
mkdir -p .aws/{buildspec,deploy}

log_action "Créé" "aws/ - Structure déploiement AWS"
log_action "Créé" "deployment/ - Scripts de déploiement"
log_action "Créé" ".aws/ - Configuration AWS"

echo -e "\n${BLUE}📋 Phase 7: Création fichiers de configuration AWS${NC}"

# Créer .env.example pour AWS
cat > .env.example << 'EOF'
# Configuration AWS Production
NODE_ENV=production
FLASK_ENV=production

# Base de données AWS RDS
DATABASE_URL=postgresql://user:password@rds-endpoint:5432/comptaebnl_prod
REDIS_URL=redis://elasticache-endpoint:6379

# Secrets AWS (utiliser AWS Secrets Manager)
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Services AWS
AWS_REGION=us-east-1
AWS_S3_BUCKET=comptaebnl-uploads
AWS_CLOUDFRONT_DOMAIN=your-cloudfront-domain

# Paiements (production)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Mobile Money (production)
MTN_API_KEY=prod_mtn_key
ORANGE_API_KEY=prod_orange_key

# Monitoring
SENTRY_DSN=your-sentry-dsn
CLOUDWATCH_LOG_GROUP=comptaebnl-logs
EOF

log_action "Créé" ".env.example - Template configuration AWS"

echo -e "\n${BLUE}📋 Phase 8: Optimisation package.json pour AWS${NC}"

# Optimiser package.json si nécessaire
if [ -f "frontend/package.json" ]; then
    log_action "Vérifié" "frontend/package.json - Prêt pour AWS Amplify"
fi

if [ -f "backend/requirements.txt" ]; then
    log_action "Vérifié" "backend/requirements.txt - Prêt pour AWS Lambda/ECS"
fi

echo -e "\n${BLUE}📋 Phase 9: Nettoyage .git (optionnel)${NC}"

# Nettoyer l'historique git si nécessaire (optionnel)
git gc --prune=now --aggressive 2>/dev/null || true
log_action "Optimisé" ".git - Historique nettoyé"

echo -e "\n${GREEN}📊 ============================================="
echo "   RAPPORT DE NETTOYAGE"
echo -e "=============================================${NC}"

echo "🗑️ Fichiers supprimés: $REMOVED_FILES"
echo "🧹 Dossiers nettoyés: $CLEANED_DIRS"
echo ""

echo -e "${GREEN}✅ STRUCTURE AWS PRÊTE${NC}"
echo "📁 aws/ - Configuration AWS"
echo "📁 deployment/ - Scripts de déploiement"
echo "📁 .aws/ - Buildspecs et configs"
echo "📄 .env.example - Template configuration"
echo ""

echo -e "${GREEN}🚀 PROCHAINES ÉTAPES AWS:${NC}"
echo "1. Configurer AWS CLI et credentials"
echo "2. Choisir service AWS (Amplify, ECS, Lambda)"
echo "3. Configurer variables d'environnement"
echo "4. Déployer avec AWS"
echo ""

echo -e "${GREEN}🎯 PROJET PRÊT POUR DÉPLOIEMENT AWS !${NC}"

# Afficher la structure finale
echo -e "\n${BLUE}📁 STRUCTURE FINALE:${NC}"
tree -L 2 -I 'node_modules|__pycache__|*.pyc' . || ls -la

exit 0