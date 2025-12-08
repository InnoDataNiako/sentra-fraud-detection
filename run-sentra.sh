#!/bin/bash

echo "🚀 Démarrage de SÉNTRA Fraud Detection System..."
echo "=============================================="

# Vérifier que Docker et Docker Compose sont installés
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

# Construire et démarrer les conteneurs
echo "📦 Construction des images Docker..."
docker-compose build

echo "🚀 Lancement des services..."
docker-compose up -d

echo "⏳ Attente du démarrage des services..."
sleep 10

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."

if docker-compose ps | grep -q "Up"; then
    echo "✅ Tous les services sont démarrés !"
    echo ""
    echo "📊 Accès aux services :"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   PGAdmin:   http://localhost:5050 (admin@sentra.com / admin123)"
    echo ""
    echo "📝 Commandes utiles :"
    echo "   Voir les logs: docker-compose logs -f"
    echo "   Arrêter: docker-compose down"
    echo "   Redémarrer: docker-compose restart"
else
    echo "⚠️ Certains services n'ont pas démarré correctement."
    echo "Vérifiez les logs avec: docker-compose logs"
fi