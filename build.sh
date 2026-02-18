#!/bin/bash
set -e

echo "🔨 AIME Build Script for Render.com"
echo "===================================="

# Installer les dépendances
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Préparer les migrations
echo "🗄️  Running migrations..."
python manage.py migrate

# Collecter les fichiers statiques
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Compiler les messages de traduction si disponibles
echo "🌍 Compiling messages..."
python manage.py compilemessages || true

echo "✅ Build completed successfully!"
