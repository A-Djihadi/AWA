#!/bin/bash
# AWA Vercel Deployment Script

set -e

echo "🚀 Deploying AWA Frontend to Vercel..."

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Change to project root
cd "$(dirname "$0")"

# Login to Vercel (if not already logged in)
echo "🔐 Checking Vercel authentication..."
vercel whoami || vercel login

# Link project (if not already linked)
echo "🔗 Linking project to Vercel..."
vercel link --yes

# Set environment variables (interactive)
echo "🔧 Setting up environment variables..."
echo "Please set the following environment variables in your Vercel dashboard:"
echo "- NEXT_PUBLIC_SUPABASE_URL"
echo "- NEXT_PUBLIC_SUPABASE_ANON_KEY" 
echo "- SUPABASE_SERVICE_ROLE_KEY"

read -p "Have you set the environment variables? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please set the environment variables first"
    echo "Visit: https://vercel.com/dashboard -> Your Project -> Settings -> Environment Variables"
    exit 1
fi

# Deploy to production
echo "🚀 Deploying to production..."
vercel --prod

echo "✅ Deployment completed!"
echo "🌐 Your app is now live on Vercel"
