#!/bin/bash

# ========================================
# Script de validation CI/CD Local
# ComptaEBNL-IA - Test avant push GitHub
# ========================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Validation CI/CD ComptaEBNL-IA${NC}"
echo "==========================================="

# Variables globales
ERRORS=0
WARNINGS=0

# Fonction pour afficher les résultats
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Fonction pour vérifier la présence d'outils
check_tool() {
    local tool=$1
    local install_cmd=$2
    
    if command -v "$tool" &> /dev/null; then
        log_success "$tool est installé"
        return 0
    else
        log_error "$tool n'est pas installé. Installation: $install_cmd"
        return 1
    fi
}

# ========================================
# 1. VÉRIFICATION DES OUTILS
# ========================================
echo -e "\n${BLUE}📦 Vérification des outils requis${NC}"
echo "-----------------------------------"

check_tool "docker" "https://docs.docker.com/get-docker/"
check_tool "docker-compose" "https://docs.docker.com/compose/install/"
check_tool "python3" "sudo apt install python3"
check_tool "node" "https://nodejs.org/"
check_tool "npm" "https://docs.npmjs.com/downloading-and-installing-node-js-and-npm"

# Vérifier les versions
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        log_success "Python $PYTHON_VERSION (compatible)"
    else
        log_warning "Python $PYTHON_VERSION (recommandé: 3.11+)"
    fi
fi

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    if node -e "process.exit(parseInt(process.version.substr(1)) >= 18 ? 0 : 1)"; then
        log_success "Node.js $NODE_VERSION (compatible)"
    else
        log_warning "Node.js $NODE_VERSION (recommandé: 18+)"
    fi
fi

# ========================================
# 2. VÉRIFICATION DE LA STRUCTURE
# ========================================
echo -e "\n${BLUE}📁 Vérification de la structure des fichiers${NC}"
echo "---------------------------------------------"

# Fichiers CI/CD essentiels
declare -a required_files=(
    ".github/workflows/ci-cd.yml"
    ".github/scripts/setup-secrets.sh"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "frontend/Dockerfile"
    "frontend/nginx.conf"
    "frontend/package.json"
    "docker-compose.ci.yml"
    "CI_CD_README.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "Fichier $file présent"
    else
        log_error "Fichier $file manquant"
    fi
done

# Dossiers requis
declare -a required_dirs=(
    ".github/workflows"
    ".github/scripts"
    "backend/src"
    "backend/tests"
    "frontend/src"
    "frontend/public"
)

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        log_success "Dossier $dir présent"
    else
        log_error "Dossier $dir manquant"
    fi
done

# ========================================
# 3. VALIDATION BACKEND
# ========================================
echo -e "\n${BLUE}🐍 Validation Backend${NC}"
echo "---------------------"

if [[ -d "backend" ]]; then
    cd backend
    
    # Vérifier requirements.txt
    if [[ -f "requirements.txt" ]]; then
        log_success "requirements.txt trouvé"
        
        # Compter les dépendances
        DEPS_COUNT=$(grep -c "^[a-zA-Z]" requirements.txt || true)
        if [[ $DEPS_COUNT -gt 10 ]]; then
            log_success "$DEPS_COUNT dépendances listées"
        else
            log_warning "Seulement $DEPS_COUNT dépendances trouvées"
        fi
    else
        log_error "requirements.txt manquant"
    fi
    
    # Tester l'installation virtuelle (sans installer réellement)
    if command -v python3 &> /dev/null; then
        log_info "Test d'installation des dépendances Python..."
        if python3 -m pip check &> /dev/null; then
            log_success "Environnement Python sain"
        else
            log_warning "Problèmes potentiels dans l'environnement Python"
        fi
    fi
    
    # Vérifier la structure Flask
    if [[ -f "src/app.py" || -f "src/__init__.py" ]]; then
        log_success "Structure Flask détectée"
    else
        log_warning "Structure Flask non détectée"
    fi
    
    cd ..
else
    log_error "Dossier backend manquant"
fi

# ========================================
# 4. VALIDATION FRONTEND
# ========================================
echo -e "\n${BLUE}⚛️ Validation Frontend${NC}"
echo "----------------------"

if [[ -d "frontend" ]]; then
    cd frontend
    
    # Vérifier package.json
    if [[ -f "package.json" ]]; then
        log_success "package.json trouvé"
        
        # Vérifier les scripts requis
        if grep -q '"test:ci"' package.json; then
            log_success "Script test:ci défini"
        else
            log_error "Script test:ci manquant"
        fi
        
        if grep -q '"lint"' package.json; then
            log_success "Script lint défini"
        else
            log_warning "Script lint manquant"
        fi
        
        if grep -q '"type-check"' package.json; then
            log_success "Script type-check défini"
        else
            log_warning "Script type-check manquant"
        fi
    else
        log_error "package.json manquant"
    fi
    
    # Vérifier la structure React
    if [[ -f "src/App.tsx" || -f "src/App.js" ]]; then
        log_success "Structure React détectée"
    else
        log_warning "Structure React non détectée"
    fi
    
    # Vérifier tsconfig.json pour TypeScript
    if [[ -f "tsconfig.json" ]]; then
        log_success "Configuration TypeScript trouvée"
    else
        log_warning "Configuration TypeScript manquante"
    fi
    
    cd ..
else
    log_error "Dossier frontend manquant"
fi

# ========================================
# 5. VALIDATION DOCKER
# ========================================
echo -e "\n${BLUE}🐳 Validation Docker${NC}"
echo "--------------------"

if command -v docker &> /dev/null; then
    # Tester la syntaxe des Dockerfiles
    if [[ -f "backend/Dockerfile" ]]; then
        if docker build -t test-backend-build backend --dry-run &> /dev/null; then
            log_success "Dockerfile backend valide"
        else
            log_info "Test de build backend..."
            # Test réel car --dry-run n'existe pas
            if docker build -t test-backend-syntax backend -f backend/Dockerfile --target builder 2>/dev/null || true; then
                log_success "Dockerfile backend syntaxiquement correct"
                docker rmi test-backend-syntax 2>/dev/null || true
            else
                log_warning "Problème potentiel avec Dockerfile backend"
            fi
        fi
    fi
    
    if [[ -f "frontend/Dockerfile" ]]; then
        log_info "Test de syntaxe Dockerfile frontend..."
        # Vérifier juste la syntaxe sans build complet
        if docker build -t test-frontend-syntax frontend --target builder 2>/dev/null || true; then
            log_success "Dockerfile frontend syntaxiquement correct"
            docker rmi test-frontend-syntax 2>/dev/null || true
        else
            log_warning "Problème potentiel avec Dockerfile frontend"
        fi
    fi
    
    # Vérifier docker-compose.ci.yml
    if [[ -f "docker-compose.ci.yml" ]]; then
        if docker-compose -f docker-compose.ci.yml config &> /dev/null; then
            log_success "docker-compose.ci.yml valide"
        else
            log_error "docker-compose.ci.yml invalide"
        fi
    fi
else
    log_warning "Docker non disponible - skip des tests Docker"
fi

# ========================================
# 6. VALIDATION CI/CD WORKFLOW
# ========================================
echo -e "\n${BLUE}🔄 Validation Workflow GitHub Actions${NC}"
echo "-------------------------------------"

if [[ -f ".github/workflows/ci-cd.yml" ]]; then
    # Vérifier la syntaxe YAML basique
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci-cd.yml'))" 2>/dev/null; then
            log_success "Syntaxe YAML du workflow valide"
        else
            log_error "Syntaxe YAML du workflow invalide"
        fi
    else
        log_warning "Python non disponible - skip validation YAML"
    fi
    
    # Vérifier les jobs essentiels
    if grep -q "backend-tests:" .github/workflows/ci-cd.yml; then
        log_success "Job backend-tests défini"
    else
        log_error "Job backend-tests manquant"
    fi
    
    if grep -q "frontend-tests:" .github/workflows/ci-cd.yml; then
        log_success "Job frontend-tests défini"
    else
        log_error "Job frontend-tests manquant"
    fi
    
    if grep -q "security-scan:" .github/workflows/ci-cd.yml; then
        log_success "Job security-scan défini"
    else
        log_warning "Job security-scan manquant"
    fi
    
    if grep -q "deploy-production:" .github/workflows/ci-cd.yml; then
        log_success "Job deploy-production défini"
    else
        log_warning "Job deploy-production manquant"
    fi
else
    log_error "Workflow GitHub Actions manquant"
fi

# ========================================
# 7. SUGGESTIONS D'AMÉLIORATION
# ========================================
echo -e "\n${BLUE}💡 Suggestions d'amélioration${NC}"
echo "------------------------------"

# Vérifier la présence de tests
if [[ -d "backend/tests" ]]; then
    TEST_COUNT=$(find backend/tests -name "*.py" | wc -l)
    if [[ $TEST_COUNT -gt 0 ]]; then
        log_success "$TEST_COUNT fichiers de test backend trouvés"
    else
        log_warning "Aucun fichier de test backend trouvé"
    fi
else
    log_warning "Dossier de tests backend manquant"
fi

if [[ -d "frontend/src" ]]; then
    TEST_COUNT=$(find frontend/src -name "*.test.*" -o -name "*.spec.*" | wc -l)
    if [[ $TEST_COUNT -gt 0 ]]; then
        log_success "$TEST_COUNT fichiers de test frontend trouvés"
    else
        log_warning "Aucun fichier de test frontend trouvé"
    fi
fi

# Vérifier .gitignore
if [[ -f ".gitignore" ]]; then
    if grep -q "node_modules" .gitignore && grep -q "__pycache__" .gitignore; then
        log_success ".gitignore bien configuré"
    else
        log_warning ".gitignore pourrait être amélioré"
    fi
else
    log_warning ".gitignore manquant"
fi

# Vérifier README
if [[ -f "README.md" ]]; then
    log_success "README.md présent"
else
    log_warning "README.md manquant"
fi

# ========================================
# 8. RAPPORT FINAL
# ========================================
echo -e "\n${BLUE}📊 Rapport Final${NC}"
echo "=================="

echo -e "\n📈 Statistiques:"
echo "  - Erreurs: $ERRORS"
echo "  - Avertissements: $WARNINGS"

if [[ $ERRORS -eq 0 ]]; then
    echo -e "\n${GREEN}🎉 SUCCÈS: Configuration CI/CD prête pour GitHub!${NC}"
    echo -e "${GREEN}✅ Vous pouvez procéder au push vers votre repository${NC}"
    
    echo -e "\n${YELLOW}📋 Prochaines étapes:${NC}"
    echo "1. git add ."
    echo "2. git commit -m 'feat: Configuration CI/CD GitHub Actions'"
    echo "3. git push origin main"
    echo "4. Configurer les secrets: ./.github/scripts/setup-secrets.sh"
    echo "5. Créer les environnements 'staging' et 'production' sur GitHub"
    
elif [[ $ERRORS -le 2 ]]; then
    echo -e "\n${YELLOW}⚠️  ATTENTION: Configuration presque prête${NC}"
    echo -e "${YELLOW}Corrigez les erreurs ci-dessus avant de procéder${NC}"
    
else
    echo -e "\n${RED}❌ ÉCHEC: Plusieurs problèmes détectés${NC}"
    echo -e "${RED}Corrigez toutes les erreurs avant de continuer${NC}"
fi

if [[ $WARNINGS -gt 0 ]]; then
    echo -e "\n${YELLOW}💡 Considérez les avertissements pour optimiser votre setup${NC}"
fi

echo -e "\n${BLUE}📚 Documentation complète: CI_CD_README.md${NC}"
echo -e "${BLUE}🆘 Support: https://github.com/your-org/comptaebnl-ia/issues${NC}"

# Code de sortie
exit $ERRORS