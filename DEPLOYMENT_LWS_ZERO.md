# 🌐 GUIDE DÉPLOIEMENT LWS - RECOMMENCER À ZÉRO

**Date:** Février 2026  
**Objectif:** Configuration nouvelle de LWS pour MySQL + Passenger WSGI  
**Architecture:** LWS cPanel uniquement (Backend + DB locales)

---

## 📋 PRÉREQUIS

1. ✅ Accès cPanel LWS
2. ✅ Domain pointé sur les serveurs LWS
3. ✅ MySQL 5.7+ disponible on LWS
4. ✅ Python 3.9+ supporté par LWS

---

## 🔧 ÉTAPE 1: NETTOYAGE COMPLET LWS

### 1.1 Accéder via SSH

```bash
ssh user@votre-domaine.com
# ou
ssh user@ip-lws
```

### 1.2 Aller au répertoire public_html

```bash
cd /home/YOUR_USERNAME/public_html
```

### 1.3 SUPPRIMER l'ANCIENNE INSTALLATION

```bash
# Supprimer le dossier aime (s'il existe)
rm -rf aime/

# Supprimer les bases de données anciennes
mysql -u root -p
```

Dans MySQL:
```sql
-- Lister les bases de données
SHOW DATABASES;

-- Supprimer l'ancienne base
DROP DATABASE IF EXISTS aime_production;
DROP DATABASE IF EXISTS aime_old;

-- Lister les utilisateurs
SELECT User, Host FROM mysql.user;

-- Supprimer l'ancien utilisateur
DROP USER IF EXISTS 'aime_user'@'localhost';
DROP USER IF EXISTS 'aime_user'@'%';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Quitter
EXIT;
```

✅ **Maintenant tout est vierge!**

---

## 🚀 ÉTAPE 2: NOUVELLE INSTALLATION AIME SUR LWS

### 2.1 Cloner le dépôt

```bash
cd /home/YOUR_USERNAME/public_html

# Cloner le repositoire (branche main)
git clone https://github.com/aimedrcongo/aime-site.git aime

cd aime
```

### 2.2 Créer l'environnement virtuel

```bash
# Dans /home/YOUR_USERNAME/public_html/aime

# Créer le virtualenv (utiliser Python 3.9)
python3.9 -m venv venv

# Activer le virtualenv
source venv/bin/activate

# Vérifier la version
python --version

# Installer les dépendances
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# (Si mysqlclient pose problème, utiliser PyMySQL)
pip install PyMySQL==1.1.0
```

### 2.3 Créer le fichier .env

```bash
nano .env
```

Coller:
```
# Django
DEBUG=False
SECRET_KEY=your-long-random-secret-key-here-min-50-chars
ALLOWED_HOSTS=aime-rdc.org,www.aime-rdc.org

# Database MySQL (LOCAL)
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=aime_production
DATABASE_USER=aime_user
DATABASE_PASSWORD=your-secure-password-here
DATABASE_HOST=localhost
DATABASE_PORT=3306

# Security
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

# Email (optionnel mais recommandé)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.aime-rdc.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@aime-rdc.org
EMAIL_HOST_PASSWORD=your-email-password

# Paths
STATIC_ROOT=/home/YOUR_USERNAME/public_html/aime/staticfiles
MEDIA_ROOT=/home/YOUR_USERNAME/public_html/aime/media
```

**Sauvegarder:** Ctrl+X → Y → Enter

### 2.4 Créer la base de données MySQL

```bash
mysql -u root -p
```

Dans MySQL:
```sql
-- Créer la base de données
CREATE DATABASE aime_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur
CREATE USER 'aime_user'@'localhost' IDENTIFIED BY 'your-secure-password-here';

-- Donner les permissions
GRANT ALL PRIVILEGES ON aime_production.* TO 'aime_user'@'localhost';

-- Appliquer
FLUSH PRIVILEGES;

-- Vérifier
SELECT User, Host FROM mysql.user WHERE User = 'aime_user';

-- Quitter
EXIT;
```

### 2.5 Initialiser la base de données Django

```bash
cd /home/YOUR_USERNAME/public_html/aime

# Activer virtualenv
source venv/bin/activate

# Migrations
python manage.py migrate --settings=aimesite.settings

# Charger les données (optionnel)
python manage.py loaddata initial_data 2>/dev/null || echo "Pas de données initiales"

# Créer un superuser (admin)
python manage.py createsuperuser --settings=aimesite.settings

# Collecter les fichiers statiques
python manage.py collectstatic --noinput --settings=aimesite.settings
```

### 2.6 Configurer Passenger (WSGI)

#### Créer le fichier passenger_wsgi.py

```bash
cat > passenger_wsgi.py << 'EOF'
#!/usr/bin/env python
"""
Passenger WSGI Configuration for LWS cPanel
"""

import sys
import os

# Chemins du projet
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VIRTUALENV_PATH = os.path.join(PROJECT_DIR, 'venv')

# Ajouter Project au path
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Ajouter le virtualenv au path
if os.path.exists(VIRTUALENV_PATH):
    import site
    site.addsitedir(os.path.join(VIRTUALENV_PATH, 'lib/python3.9/site-packages'))
    sys.path.insert(0, os.path.join(VIRTUALENV_PATH, 'lib/python3.9/site-packages'))

# Charger les variables d'environnement depuis .env
from pathlib import Path
from decouple import Config, RepositoryEnv

env_path = Path(PROJECT_DIR) / '.env'
if env_path.exists():
    config = Config(RepositoryEnv(str(env_path)))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'aimesite.settings'
    os.environ['SECRET_KEY'] = config('SECRET_KEY', default='')
    os.environ['DEBUG'] = config('DEBUG', default='False')
    os.environ['ALLOWED_HOSTS'] = config('ALLOWED_HOSTS', default='localhost')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aimesite.settings')

# Configuration MySQL
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# WSGI Application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
EOF
```

Vérifier les permissions:
```bash
chmod 644 passenger_wsgi.py
```

#### Via cPanel (GUI)

1. **Aller dans cPanel** → **Python Apps** (ou Rails/Node.js Apps selon l'interface)
2. **Create Application**:
   - **Python Version:** 3.9
   - **Application Root:** `/home/YOUR_USERNAME/public_html/aime`
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application URL:** `aime-rdc.org/`
   - **Application Environment:** Production

3. **Redémarrer** Passenger

### 2.7 Configurer les domaines dans cPanel

1. Dans cPanel → **Addon Domains** ou **Parked Domains**
2. Ajouter:
   - `aime-rdc.org`
   - `www.aime-rdc.org`
3. Pointer vers `/home/YOUR_USERNAME/public_html/aime/`

### 2.8 Certificat SSL

1. Dans cPanel → **AutoSSL** 
2. Générer un certificat Let's Encrypt
3. Attendre l'activation (5-10 min)

---

## ✅ ÉTAPE 3: VÉRIFICATIONS

### 3.1 Tester la connexion DB

```bash
cd /home/YOUR_USERNAME/public_html/aime
source venv/bin/activate

python manage.py dbshell
```

### 3.2 Vérifier les logs

```bash
# Logs Passenger
tail -f /home/YOUR_USERNAME/logs/aime_errors_log

# Ou dans cPanel → Error Log
```

### 3.3 Accéder au site

```
https://aime-rdc.org/
https://aime-rdc.org/admin/  # Page admin
```

---

## 🔄 MAINTENANCE

### Redémarrer Passenger

Via cPanel ou:
```bash
cd /home/YOUR_USERNAME/public_html/aime
source venv/bin/activate
touch tmp/restart.txt
```

### Backups

```bash
# Backup de la DB
mysqldump -u aime_user -p aime_production > backup_$(date +%Y%m%d).sql

# Backup des fichiers
tar -czf backup_$(date +%Y%m%d).tar.gz .
```

### Mises à jour

```bash
cd /home/YOUR_USERNAME/public_html/aime
source venv/bin/activate

# Pull la dernière version
git pull origin main

# Installer nouvelles dépendances
pip install -r requirements.txt

# Appliquer migrations
python manage.py migrate

# Collecter static files
python manage.py collectstatic --noinput

# Redémarrer Passenger
touch tmp/restart.txt
```

---

## 🐛 DÉPANNAGE

### Erreur: "ModuleNotFoundError: No module named 'django'"
→ Vérifier que le virtualenv est activé
→ Vérifier le chemin dans passenger_wsgi.py

### Erreur: "Connection refused" à MySQL
→ Vérifier que MySQL est en cours d'exécution
→ Vérifier les credentials dans .env

### Site lent
→ Optimiser les requêtes DB
→ Augmenter les workers dans Passenger (cPanel)

---

## 📞 SUPPORT LWS

- **Support:** https://support.lws.fr
- **Documentation:** https://docs.lws.fr
- **Email:** support@lws.fr
