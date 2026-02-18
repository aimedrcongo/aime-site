#!/bin/bash
set -e

echo "🔨 AIME Build Script for Render.com"
echo "===================================="

# Créer le répertoire logs
echo "📁 Creating logs directory..."
mkdir -p logs

# Installer les dépendances
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Collecter les fichiers statiques
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || true

# Note: Database migrations will be run after environment variables are set
# Run manually with: python manage.py migrate
echo "⚠️  Database configuration needed - see RENDER_SETUP_GUIDE.md"

# Compiler les messages de traduction si disponibles
echo "🌍 Compiling messages..."
python manage.py compilemessages || true

echo "✅ Build completed successfully!"
