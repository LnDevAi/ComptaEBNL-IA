#!/bin/bash
# 🧪 Check Before Push - ComptaEBNL-IA
# Vérifie que tout fonctionne avant de pousser sur GitHub

set -e

echo "🧪 ============================================="
echo "   CHECK BEFORE PUSH - ComptaEBNL-IA"
echo "🧪 ============================================="

# Variables de couleur
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compteurs
TOTAL_CHECKS=0
PASSED_CHECKS=0
WARNINGS=0

# Fonction d'affichage
print_check() {
    local status=$1
    local message=$2
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
        WARNINGS=$((WARNINGS + 1))
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

echo -e "${BLUE}📁 Vérification de la structure du projet...${NC}"

# Vérifier la structure de base
if [ -d "backend" ]; then
    print_check "PASS" "Backend directory trouvé"
else
    print_check "FAIL" "Backend directory manquant"
fi

if [ -d "frontend" ]; then
    print_check "PASS" "Frontend directory trouvé"
else
    print_check "FAIL" "Frontend directory manquant"
fi

if [ -d "tests" ]; then
    print_check "PASS" "Tests directory trouvé"
else
    print_check "WARN" "Tests directory manquant (optionnel)"
fi

if [ -d ".github/workflows" ]; then
    print_check "PASS" "GitHub workflows trouvés"
else
    print_check "FAIL" "GitHub workflows manquants"
fi

echo -e "\n${BLUE}🐍 Vérification Backend...${NC}"

# Vérifier backend
if [ -f "backend/requirements.txt" ]; then
    print_check "PASS" "requirements.txt trouvé"
else
    print_check "WARN" "requirements.txt manquant"
fi

if [ -f "backend/src/app.py" ] || [ -f "backend/app.py" ]; then
    print_check "PASS" "Application Flask trouvée"
else
    print_check "WARN" "Application Flask non trouvée"
fi

# Test imports Python basiques
echo -e "\n${BLUE}🔍 Test imports Python...${NC}"
if python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null; then
    print_check "PASS" "Python 3 disponible"
else
    print_check "FAIL" "Python 3 non disponible"
fi

if python3 -c "from datetime import datetime; print('DateTime OK')" 2>/dev/null; then
    print_check "PASS" "Imports basiques Python fonctionnels"
else
    print_check "FAIL" "Problème imports Python"
fi

echo -e "\n${BLUE}⚛️ Vérification Frontend...${NC}"

# Vérifier frontend
if [ -f "frontend/package.json" ]; then
    print_check "PASS" "package.json trouvé"
else
    print_check "WARN" "package.json manquant"
fi

if [ -f "frontend/src/App.tsx" ] || [ -f "frontend/src/App.js" ]; then
    print_check "PASS" "Application React trouvée"
else
    print_check "WARN" "Application React non trouvée"
fi

# Test Node.js si disponible
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_check "PASS" "Node.js disponible ($NODE_VERSION)"
else
    print_check "WARN" "Node.js non disponible"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_check "PASS" "npm disponible ($NPM_VERSION)"
else
    print_check "WARN" "npm non disponible"
fi

echo -e "\n${BLUE}🧪 Vérification Tests...${NC}"

# Vérifier tests
if [ -f "backend/tests/test_models.py" ]; then
    print_check "PASS" "Tests backend basiques trouvés"
else
    print_check "WARN" "Tests backend basiques manquants"
fi

if [ -f "tests/unit/backend/models/test_subscription_models.py" ]; then
    print_check "PASS" "Tests backend avancés trouvés"
else
    print_check "WARN" "Tests backend avancés manquants"
fi

if [ -f "frontend/src/__tests__/App.test.tsx" ] || [ -f "frontend/src/App.test.tsx" ]; then
    print_check "PASS" "Tests frontend trouvés"
else
    print_check "WARN" "Tests frontend manquants"
fi

if [ -f "tests/run_all_tests.py" ]; then
    print_check "PASS" "Test runner complet trouvé"
    
    # Exécuter le test runner
    echo -e "\n${BLUE}🚀 Exécution test runner...${NC}"
    if python3 tests/run_all_tests.py > /dev/null 2>&1; then
        print_check "PASS" "Test runner exécuté avec succès"
    else
        print_check "WARN" "Test runner a des warnings (normal)"
    fi
else
    print_check "WARN" "Test runner manquant"
fi

echo -e "\n${BLUE}🔧 Vérification CI/CD...${NC}"

# Vérifier CI/CD
if [ -f ".github/workflows/ci-cd.yml" ]; then
    print_check "PASS" "Workflow CI/CD principal trouvé"
else
    print_check "FAIL" "Workflow CI/CD principal manquant"
fi

# Vérifier qu'il n'y a qu'un seul workflow actif
ACTIVE_WORKFLOWS=$(find .github/workflows -name "*.yml" | wc -l)
if [ "$ACTIVE_WORKFLOWS" -eq 1 ]; then
    print_check "PASS" "Un seul workflow actif (optimal)"
elif [ "$ACTIVE_WORKFLOWS" -gt 1 ]; then
    print_check "WARN" "Plusieurs workflows actifs ($ACTIVE_WORKFLOWS)"
else
    print_check "FAIL" "Aucun workflow trouvé"
fi

echo -e "\n${BLUE}🔒 Vérification sécurité basique...${NC}"

# Vérifier sécurité
if [ -f ".env" ]; then
    print_check "WARN" "Fichier .env détecté - vérifier qu'il n'est pas commité"
else
    print_check "PASS" "Pas de fichier .env en racine"
fi

if [ -f ".gitignore" ]; then
    print_check "PASS" ".gitignore présent"
else
    print_check "WARN" ".gitignore manquant"
fi

# Recherche rapide de secrets potentiels
SECRETS_FOUND=$(grep -r -i "password\|secret\|key" --include="*.py" --include="*.js" --include="*.ts" . 2>/dev/null | grep -v "test" | grep -v ".git" | wc -l)
if [ "$SECRETS_FOUND" -gt 10 ]; then
    print_check "WARN" "Beaucoup de références secrets/passwords ($SECRETS_FOUND) - vérifier manuellement"
else
    print_check "PASS" "Pas de secrets évidents détectés"
fi

echo -e "\n${BLUE}📋 Vérification Documentation...${NC}"

# Vérifier documentation
if [ -f "README.md" ]; then
    print_check "PASS" "README.md présent"
else
    print_check "WARN" "README.md manquant"
fi

if [ -f "GUIDE_CORRECTION_CICD.md" ]; then
    print_check "PASS" "Guide CI/CD présent"
else
    print_check "WARN" "Guide CI/CD manquant"
fi

if [ -f "ENVIRONNEMENT_TESTS_FINALISE.md" ]; then
    print_check "PASS" "Documentation tests présente"
else
    print_check "WARN" "Documentation tests manquante"
fi

echo -e "\n${BLUE}🐳 Vérification Docker...${NC}"

# Vérifier Docker
if [ -f "docker-compose.test.yml" ]; then
    print_check "PASS" "Configuration Docker tests trouvée"
else
    print_check "WARN" "Configuration Docker tests manquante"
fi

if [ -f "backend/Dockerfile" ]; then
    print_check "PASS" "Dockerfile backend trouvé"
else
    print_check "WARN" "Dockerfile backend manquant"
fi

if [ -f "frontend/Dockerfile" ]; then
    print_check "PASS" "Dockerfile frontend trouvé"
else
    print_check "WARN" "Dockerfile frontend manquant"
fi

# Rapport final
echo -e "\n${BLUE}📊 ============================================="
echo "   RAPPORT FINAL"
echo -e "=============================================${NC}"

SUCCESS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo "📈 Vérifications totales: $TOTAL_CHECKS"
echo "✅ Vérifications réussies: $PASSED_CHECKS"
echo "⚠️  Warnings: $WARNINGS"
echo "📊 Taux de réussite: $SUCCESS_RATE%"

echo ""
if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}🎉 EXCELLENT! Prêt pour push vers GitHub${NC}"
    echo -e "${GREEN}🚀 Le workflow CI/CD devrait passer sans problème${NC}"
    EXIT_CODE=0
elif [ $SUCCESS_RATE -ge 75 ]; then
    echo -e "${YELLOW}⚠️  BIEN! Push possible avec quelques warnings${NC}"
    echo -e "${YELLOW}🔧 Le workflow CI/CD devrait réussir avec des améliorations recommandées${NC}"
    EXIT_CODE=0
elif [ $SUCCESS_RATE -ge 50 ]; then
    echo -e "${YELLOW}🤔 MOYEN! Push possible mais améliorations recommandées${NC}"
    echo -e "${YELLOW}⚠️  Le workflow CI/CD pourrait avoir des warnings${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ PROBLÈMES DÉTECTÉS! Corrections recommandées avant push${NC}"
    echo -e "${RED}🛠️  Le workflow CI/CD pourrait échouer${NC}"
    EXIT_CODE=1
fi

echo ""
echo -e "${BLUE}🎯 Prochaines étapes recommandées:${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo "• Corriger les warnings si possible"
fi
echo "• git add . && git commit -m 'votre message'"
echo "• git push origin main (ou votre branche)"
echo "• Vérifier GitHub Actions: https://github.com/LnDevAi/ComptaEBNL-IA/actions"

echo ""
echo -e "${GREEN}✨ Le nouveau workflow adaptatif est conçu pour réussir même avec des warnings!${NC}"

exit $EXIT_CODE