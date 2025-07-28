@echo off
echo 🚀 Démarrage de ComptaEBNL-IA...
echo 📊 Plateforme de gestion comptable avec IA pour EBNL

cd backend\src
echo 📦 Installation des dépendances Python...
pip install -r requirements.txt

echo 🔧 Démarrage du serveur API...
python main.py

pause
