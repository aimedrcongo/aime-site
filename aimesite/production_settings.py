# Configuration de production pour AIME RDC - Python 3.9
# Basée sur debug_settings.py qui fonctionne, adaptée pour la production

from .settings import *
import os
import pymysql

# Configure PyMySQL to work with Django MySQL backend
pymysql.install_as_MySQLdb()

# SÉCURITÉ - Production mode
DEBUG = False  # Production
ALLOWED_HOSTS = [
    'aime-rdc.org',
    'www.aime-rdc.org',
    '127.0.0.1',
    'localhost',
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    'https://aime-rdc.org',
    'https://www.aime-rdc.org',
    'http://aime-rdc.org',
    'http://www.aime-rdc.org',
]

# Configuration timezone pour éviter les erreurs de timestamp
USE_TZ = True
TIME_ZONE = 'Africa/Kinshasa'  # Timezone RDC

# Base de données MySQL avec PyMySQL (copiée du debug_settings qui fonctionne)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cp2639565p41_aimer2639565',
        'USER': 'cp2639565p41_aimer2639565',
        'PASSWORD': 'Wazenga007@bd',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,
    }
}

# Fichiers statiques et médias pour cPanel
STATIC_URL = '/static/'
STATIC_ROOT = '/home/cp2639565p41/public_html/staticfiles/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/cp2639565p41/public_html/media/'

# Configuration WhiteNoise pour les fichiers statiques en production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Pour servir les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# HTTPS/SSL Configuration
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Base de données MySQL pour la production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cp2639565p41_aimer2639565',
        'USER': 'cp2639565p41_aimer2639565',
        'PASSWORD': 'Wazenga007@bd',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,
    }
}

# Configuration email pour la production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.aime-rdc.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'web@aime-rdc.org'
EMAIL_HOST_PASSWORD = 'Wazenga007@Fab'
DEFAULT_FROM_EMAIL = 'AIME RDC <web@aime-rdc.org>'
SERVER_EMAIL = 'web@aime-rdc.org'

# Les chemins statiques sont déjà définis plus haut - pas de duplication

# Configuration WhiteNoise pour servir les fichiers statiques
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Ajout pour les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Configuration de cache (optionnel)
# CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'location': 'cache_table',
    }
}

# Logging pour la production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(BASE_DIR / 'django.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Clé secrète pour la production (généré automatiquement)
SECRET_KEY = 'django-prod-k9m#2p$8n@v7x4z&w6q3r!s5u8y*a1c+e9g^h2j@k5l&n8p#q2r$t7v*x3z'

# Configuration du fuseau horaire
TIME_ZONE = 'Africa/Kinshasa'
USE_TZ = True

# Paramètres pour l'administration
ADMIN_URL = 'admin/'
