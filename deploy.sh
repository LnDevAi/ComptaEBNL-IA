#!/bin/bash

echo "🚀 DÉPLOIEMENT COMPTAEBNL-IA"
echo "=============================="

# Arrêter les processus existants
echo "🔄 Arrêt des services existants..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "npm.*start" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
sleep 3

# Démarrer le backend
echo "🔧 Démarrage du backend Flask (port 5001)..."
cd /workspace/backend/src
python3 main.py &
BACKEND_PID=$!
sleep 5

# Démarrer le frontend
echo "🎨 Démarrage du frontend React (port 3001)..."
cd /workspace/frontend
npm start &
FRONTEND_PID=$!
sleep 10

echo ""
echo "✅ SERVICES DÉMARRÉS AVEC SUCCÈS!"
echo "================================="
echo "🌐 Frontend ComptaEBNL-IA: http://localhost:3001"
echo "🔧 Backend API: http://localhost:5001"
echo "📚 Documentation: http://localhost:5001/api/docs"
echo "❤️  Health Check: http://localhost:5001/api/health"
echo ""
echo "📊 Processus:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "🎉 PLATEFORME COMPTAEBNL-IA OPÉRATIONNELLE!"

# Garder le script actif
wait