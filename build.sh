#!/bin/bash
# Vercel Build Script

echo "🚀 Starting AWA Frontend Build for Vercel..."

# Change to frontend directory
cd services/frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Type check
echo "🔍 Running type check..."
npm run type-check

# Lint code
echo "✨ Linting code..."
npm run lint

# Build application
echo "🏗️ Building application..."
npm run build

echo "✅ Build completed successfully!"
