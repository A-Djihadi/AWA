#!/bin/bash
# Script de setup complet Supabase pour AWA

set -e

echo "🚀 Configuration Supabase pour AWA"
echo "=================================="

# Vérifier si les dépendances sont installées
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

# Aller dans le dossier frontend
cd services/frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Vérifier si .env.local existe
if [ ! -f ".env.local" ]; then
    echo "⚙️ Création du fichier .env.local..."
    cp .env.example .env.local
    echo "❗ IMPORTANT: Éditez services/frontend/.env.local avec vos vraies clés Supabase"
    echo ""
    echo "Récupérez vos clés dans: https://supabase.com/dashboard"
    echo "Settings > API:"
    echo "- Project URL"
    echo "- anon public key"  
    echo "- service_role key"
    echo ""
    read -p "Appuyez sur Entrée quand vous avez configuré .env.local..."
fi

# Retourner au dossier racine
cd ../..

# Test de connexion
echo "🔍 Test de la connexion Supabase..."
node test-supabase.js

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Aller sur https://supabase.com/dashboard"
echo "2. Ouvrir l'éditeur SQL de votre projet"
echo "3. Exécuter infra/migrations/001_initial_schema.sql"
echo "4. Exécuter infra/migrations/002_rls_and_data.sql"
echo "5. Tester avec: cd services/frontend && npm run dev"
