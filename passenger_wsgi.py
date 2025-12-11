#!/usr/bin/env python
"""
Passenger WSGI Configuration for cPanel - MySQL Compatible
Version: 2.0 - Décembre 2025

Configuration optimisée pour déploiement cPanel avec MySQL
"""

import sys
import os

# ===============================================================================
# CONFIGURATION CPANEL - À PERSONNALISER
# ===============================================================================

# Obtenez votre username cPanel
# Vous pouvez le trouver : cPanel > Account Information > Primary Domain Owner
CPANEL_USER = 'votre_username_cpanel'  # À REMPLACER

# Chemins principaux (à adapter selon votre structure)
PROJECT_DIR = f'/home/{CPANEL_USER}/public_html/aime'  # Dossier racine du projet
VIRTUALENV_PATH = f'/home/{CPANEL_USER}/public_html/aime/venv'  # Venv local (recommandé)

# Alternative si venv est au niveau du home:
# VIRTUALENV_PATH = f'/home/{CPANEL_USER}/aime_venv'

# ===============================================================================
# SETUP PYTHON PATH
# ===============================================================================

# Ajouter le chemin du projet
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Ajouter le virtualenv au path
if os.path.exists(VIRTUALENV_PATH):
    import site
    site.addsitedir(f'{VIRTUALENV_PATH}/lib/python3.9/site-packages')
    sys.path.insert(0, f'{VIRTUALENV_PATH}/lib/python3.9/site-packages')

# ===============================================================================
# CONFIGURATION DJANGO
# ===============================================================================

# Utiliser settings.py avec variables .env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aimesite.settings')

# Charger les variables d'environnement depuis .env
from pathlib import Path
from decouple import Config, RepositoryEnv

env_path = Path(PROJECT_DIR) / '.env'
if env_path.exists():
    config = Config(RepositoryEnv(str(env_path)))
    # Charger les variables critiques
    os.environ['SECRET_KEY'] = config('SECRET_KEY', default='')
    os.environ['DEBUG'] = config('DEBUG', default='False')
    os.environ['ALLOWED_HOSTS'] = config('ALLOWED_HOSTS', default='localhost')
    os.environ['DATABASE_ENGINE'] = config('DATABASE_ENGINE', default='django.db.backends.mysql')
    os.environ['DATABASE_NAME'] = config('DATABASE_NAME', default='')
    os.environ['DATABASE_USER'] = config('DATABASE_USER', default='')
    os.environ['DATABASE_PASSWORD'] = config('DATABASE_PASSWORD', default='')
    os.environ['DATABASE_HOST'] = config('DATABASE_HOST', default='localhost')
    os.environ['DATABASE_PORT'] = config('DATABASE_PORT', default='3306')

# ===============================================================================
# CONFIGURATION MYSQL / PYMYSQL (SI MYSQL EST UTILISÉ)
# ===============================================================================

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # MySQLdb ou mysqlclient sont utilisés

# ===============================================================================
# IMPORT WSGI APPLICATION
# ===============================================================================

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Créer l'application WSGI
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    # Log l'erreur dans un fichier accessible
    with open(f'{PROJECT_DIR}/wsgi_error.log', 'w') as f:
        import traceback
        f.write(f"WSGI Error: {e}\n")
        f.write(traceback.format_exc())
    raise
