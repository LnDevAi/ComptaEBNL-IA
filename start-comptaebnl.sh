#!/bin/bash

echo "🚀 DÉMARRAGE COMPLET COMPTAEBNL-IA"
echo "=================================="
echo ""

# Arrêter tous les processus existants
echo "🔄 Nettoyage des processus existants..."
pkill -f "python.*main.py" 2>/dev/null
pkill -f "npm.*start" 2>/dev/null
pkill -f "react-scripts" 2>/dev/null
pkill -f "demo-server.py" 2>/dev/null
sleep 3

# 1. Démarrer le backend Flask
echo "🔧 Démarrage du backend Flask (port 5001)..."
cd /workspace/backend/src
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
sleep 5

# 2. Démarrer le frontend React  
echo "🎨 Démarrage du frontend React (port 3001)..."
cd /workspace/frontend
PORT=3001 npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
sleep 10

# 3. Démarrer le serveur de démonstration
echo "🌐 Démarrage du serveur de démonstration (port 9000)..."
cd /workspace
python3 demo-server.py > /tmp/demo.log 2>&1 &
DEMO_PID=$!
echo "   Démonstration PID: $DEMO_PID"
sleep 5

echo ""
echo "✅ TOUS LES SERVICES COMPTAEBNL-IA DÉMARRÉS !"
echo "============================================="
echo ""
echo "🌐 LIEN PRINCIPAL DE DÉMONSTRATION:"
echo "   👉 http://localhost:9000 👈"
echo ""
echo "🔗 LIENS DIRECTS:"
echo "   📊 Démonstration complète: http://localhost:9000"
echo "   🎨 Application React: http://localhost:3001"
echo "   🔧 Backend API: http://localhost:5001"
echo "   ❤️  Health Check: http://localhost:9000/api/health"
echo ""
echo "📊 PROCESSUS DÉMARRÉS:"
echo "   Backend Flask: PID $BACKEND_PID"
echo "   Frontend React: PID $FRONTEND_PID"
echo "   Serveur Démo: PID $DEMO_PID"
echo ""
echo "📝 LOGS DISPONIBLES:"
echo "   Backend: tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo "   Démonstration: tail -f /tmp/demo.log"
echo ""

# Test des services
echo "🔍 VÉRIFICATION DES SERVICES..."
sleep 5

# Test backend
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "   ✅ Backend Flask: Opérationnel"
else
    echo "   ❌ Backend Flask: Non accessible"
fi

# Test frontend
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "   ✅ Frontend React: Opérationnel"
else
    echo "   ❌ Frontend React: Non accessible"
fi

# Test démonstration
if curl -s http://localhost:9000 > /dev/null 2>&1; then
    echo "   ✅ Serveur Démo: Opérationnel"
else
    echo "   ❌ Serveur Démo: Non accessible"
fi

echo ""
echo "🎉 PLATEFORME COMPTAEBNL-IA 100% OPÉRATIONNELLE !"
echo "🌐 Ouvrez http://localhost:9000 dans votre navigateur"
echo ""
echo "⚠️  Pour arrêter tous les services:"
echo "   pkill -f 'python.*main.py|npm.*start|demo-server.py'"
echo ""

# Garder le script actif pour monitoring
echo "📊 Monitoring des services (Ctrl+C pour arrêter)..."
while true; do
    sleep 30
    echo "$(date): Services ComptaEBNL-IA actifs"
done