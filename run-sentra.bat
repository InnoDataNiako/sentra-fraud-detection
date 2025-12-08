@echo off
echo 🚀 Démarrage de SÉNTRA Fraud Detection System...
echo ==============================================

REM Vérifier Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas installé. Veuillez installer Docker Desktop.
    pause
    exit /b 1
)

REM Construire et démarrer
echo 📦 Construction des images Docker...
docker-compose build

echo 🚀 Lancement des services...
docker-compose up -d

echo ⏳ Attente du démarrage des services...
timeout /t 10 /nobreak >nul

echo 🔍 Vérification de l'état des services...
docker-compose ps

echo.
echo 📊 Accès aux services :
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo    PGAdmin:   http://localhost:5050 ^(admin@sentra.com / admin123^)
echo.
echo 📝 Commandes utiles :
echo    Voir les logs: docker-compose logs -f
echo    Arrêter: docker-compose down
echo    Redémarrer: docker-compose restart

pause