@echo off
echo 🚀 Démarrage de ComptaOHADA-IA...
echo 🏛️ Plateforme de comptabilité OHADA avec IA intégrée
echo.

REM Vérifier si Docker est installé
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker n'est pas installé ou non accessible
    echo Veuillez installer Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Vérifier si docker-compose est installé
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose n'est pas installé
    echo Veuillez installer Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker est installé
echo.

REM Créer le fichier .env s'il n'existe pas
if not exist .env (
    echo 📝 Création du fichier .env...
    copy .env.example .env
    echo ⚠️  Veuillez configurer les variables d'environnement dans le fichier .env
    echo.
)

echo 🐳 Démarrage des conteneurs Docker...
echo.

REM Démarrer les services avec Docker Compose
docker-compose up -d

if errorlevel 1 (
    echo ❌ Erreur lors du démarrage des conteneurs
    pause
    exit /b 1
)

echo.
echo ✅ ComptaOHADA-IA démarré avec succès !
echo.
echo 🔗 API Backend: http://localhost:8000
echo 📚 Documentation API: http://localhost:8000/docs
echo 🌐 Frontend: http://localhost:3000
echo 🗄️ Base de données: PostgreSQL sur le port 5432
echo 📦 Redis: Cache sur le port 6379
echo.
echo 📊 Fonctionnalités disponibles:
echo   - Authentification JWT
echo   - Gestion multi-tenant
echo   - Plan comptable SYSCEBNL
echo   - Conformité OHADA
echo   - Assistant IA intégré
echo.
echo Pour arrêter les services: docker-compose down
echo Pour voir les logs: docker-compose logs -f
echo.
pause
