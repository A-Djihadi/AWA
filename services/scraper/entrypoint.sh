#!/bin/bash
set -e

# Script d'entrée pour le scraper service

echo "🚀 Starting AWA Scraper Service..."

# Vérification des variables d'environnement requises
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL environment variable is required"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ SUPABASE_SERVICE_ROLE_KEY environment variable is required"
    exit 1
fi

# Configuration Scrapy
export SCRAPY_SETTINGS_MODULE=tjm_scraper.settings

# Création des répertoires nécessaires
mkdir -p /app/logs
mkdir -p /app/data/raw
mkdir -p /app/data/processed

# Démarrage du service de health check en arrière-plan
python -m tjm_scraper.health_server &

echo "✅ Health check server started on port 8000"

# Exécution de la commande demandée
exec "$@"
