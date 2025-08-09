#!/bin/bash

echo "🌐 DÉPLOIEMENT COMPTAEBNL-IA EN LIGNE"
echo "====================================="
echo ""

# Configuration ngrok
echo "🔧 Configuration des tunnels publics..."
echo ""

# Démarrer ngrok pour le frontend (port 3001)
echo "🎨 Exposition du frontend React..."
./ngrok http 3001 --log=stdout > frontend_tunnel.log 2>&1 &
NGROK_FRONTEND_PID=$!
sleep 5

# Démarrer ngrok pour le backend (port 5001)  
echo "🔧 Exposition du backend API..."
./ngrok http 5001 --log=stdout > backend_tunnel.log 2>&1 &
NGROK_BACKEND_PID=$!
sleep 5

echo ""
echo "⏳ Attente de l'initialisation des tunnels..."
sleep 10

echo ""
echo "🌐 LIENS PUBLICS COMPTAEBNL-IA:"
echo "================================"

# Extraire les URLs publiques
FRONTEND_URL=$(curl -s localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | head -1 | cut -d'"' -f4)
BACKEND_URL=$(curl -s localhost:4041/api/tunnels | grep -o '"public_url":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -n "$FRONTEND_URL" ]; then
    echo "🎨 Frontend ComptaEBNL-IA: $FRONTEND_URL"
else
    echo "❌ Frontend tunnel non disponible"
fi

if [ -n "$BACKEND_URL" ]; then
    echo "🔧 Backend API: $BACKEND_URL"
    echo "📚 Documentation: $BACKEND_URL/api/docs"
    echo "❤️  Health Check: $BACKEND_URL/api/health"
else
    echo "❌ Backend tunnel non disponible"
fi

echo ""
echo "📊 Tunnels ngrok:"
echo "   Frontend PID: $NGROK_FRONTEND_PID" 
echo "   Backend PID: $NGROK_BACKEND_PID"
echo ""
echo "🎉 PLATEFORME COMPTAEBNL-IA ACCESSIBLE PUBLIQUEMENT!"
echo ""
echo "⚠️  Note: Les tunnels gratuits ngrok sont temporaires"
echo "   et se ferment après quelques heures."

# Garder le script actif
wait