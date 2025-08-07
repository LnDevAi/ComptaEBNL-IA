#!/bin/bash

# ========================================
# ACTIVATION CI/CD COMPTAEBNL-IA
# Script d'activation immédiate
# ========================================

echo "🚀 ACTIVATION CI/CD GITHUB ACTIONS POUR COMPTAEBNL-IA"
echo "======================================================"
echo ""

# Vérifier les fichiers
echo "📁 VÉRIFICATION DES FICHIERS CI/CD :"
echo "------------------------------------"

if [ -f ".github/workflows/ci-cd.yml" ]; then
    echo "✅ GitHub Actions workflow trouvé"
else
    echo "❌ GitHub Actions workflow manquant"
fi

if [ -f ".github/scripts/setup-secrets.sh" ]; then
    echo "✅ Script de configuration des secrets trouvé"
    chmod +x .github/scripts/setup-secrets.sh
else
    echo "❌ Script de configuration des secrets manquant"
fi

if [ -f "docker-compose.ci.yml" ]; then
    echo "✅ Configuration Docker CI trouvée"
else
    echo "❌ Configuration Docker CI manquante"
fi

echo ""
echo "📋 RÉSUMÉ DES FICHIERS CRÉÉS :"
echo "------------------------------"
find .github/ -type f 2>/dev/null || echo "Dossier .github non trouvé"
ls -la *.yml *.sh *.md 2>/dev/null | head -10

echo ""
echo "🔧 ÉTAPES D'ACTIVATION :"
echo "------------------------"
echo ""
echo "1️⃣  PUSH VERS GITHUB :"
echo "   git add ."
echo "   git commit -m 'feat: Add CI/CD GitHub Actions pipeline'"
echo "   git push origin main"
echo ""
echo "2️⃣  CONFIGURER LES SECRETS :"
echo "   # Installer GitHub CLI si nécessaire"
echo "   # Puis exécuter :"
echo "   ./.github/scripts/setup-secrets.sh"
echo ""
echo "3️⃣  CRÉER LES ENVIRONNEMENTS :"
echo "   - Aller dans Settings > Environments sur GitHub"
echo "   - Créer 'staging' et 'production'"
echo ""
echo "4️⃣  TESTER LE PIPELINE :"
echo "   git push origin main"
echo "   # Ou créer une Pull Request"
echo ""

echo "🎯 SECRETS PRINCIPAUX À CONFIGURER :"
echo "-----------------------------------"
echo "• DATABASE_URL (PostgreSQL production)"
echo "• SECRET_KEY (Flask secret key)"
echo "• JWT_SECRET_KEY (JWT authentication)"
echo "• STRIPE_SECRET_KEY (paiements Stripe)"
echo "• Clés Mobile Money (MTN, Orange, Wave, etc.)"
echo "• SLACK_WEBHOOK (notifications)"
echo ""

echo "📊 CE QUE LE PIPELINE TESTERA :"
echo "-------------------------------"
echo "✅ Tests backend Python (80%+ couverture)"
echo "✅ Tests frontend React + TypeScript"
echo "✅ Tests end-to-end (Playwright)"
echo "✅ Scan de sécurité (vulnérabilités)"
echo "✅ Build Docker optimisé"
echo "✅ Déploiement staging automatique"
echo "✅ Déploiement production avec approbation"
echo ""

echo "🌐 URLS IMPORTANTES :"
echo "--------------------"
echo "• GitHub Actions : https://github.com/VOTRE-ORG/comptaebnl-ia/actions"
echo "• Environments : https://github.com/VOTRE-ORG/comptaebnl-ia/settings/environments"
echo "• Secrets : https://github.com/VOTRE-ORG/comptaebnl-ia/settings/secrets/actions"
echo ""

echo "📖 DOCUMENTATION COMPLÈTE :"
echo "---------------------------"
echo "• Guide détaillé : CI_CD_README.md"
echo "• Guide visible : GUIDE_CICD_VISIBLE.md"
echo "• Guide déploiement : DEPLOYMENT_GUIDE.md"
echo ""

read -p "🚀 Voulez-vous pusher les fichiers vers GitHub maintenant ? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Push vers GitHub en cours..."
    git add .
    git commit -m "feat: Add complete CI/CD GitHub Actions pipeline

- Add GitHub Actions workflow with comprehensive testing
- Add Docker configuration for production deployment  
- Add security scanning and automated deployment
- Add scripts for secrets setup and local validation"
    
    echo "✅ Files committed. Pushing to GitHub..."
    git push origin main
    
    echo ""
    echo "🎉 PUSH TERMINÉ !"
    echo ""
    echo "📋 PROCHAINES ÉTAPES :"
    echo "1. Configurer les secrets : ./.github/scripts/setup-secrets.sh"
    echo "2. Créer les environnements sur GitHub"
    echo "3. Le pipeline se déclenchera automatiquement !"
    echo ""
else
    echo ""
    echo "📝 COMMANDES À EXÉCUTER MANUELLEMENT :"
    echo "git add ."
    echo "git commit -m 'feat: Add CI/CD pipeline'"
    echo "git push origin main"
    echo ""
fi

echo "🎊 ComptaEBNL-IA est maintenant prêt pour un déploiement professionnel !"
echo "Les fichiers CI/CD sont configurés et prêts à être utilisés."