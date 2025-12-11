"""
Django settings for aimesite project - OPTIMISÉ & SÉCURISÉ
Version: 2.0 - Octobre 2025

Configuration production-ready avec:
- Variables d'environnement sécurisées
- Cache Redis
- Compression static files
- Security headers
- Performance optimizations
"""

from pathlib import Path
import os
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY SETTINGS - PRODUCTION READY
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-temporary-key-CHANGE-IN-PRODUCTION')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# CSRF settings
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS',
    default='https://aime-rdc.org,https://www.aime-rdc.org',
    cast=Csv()
)

# Security settings (Production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
else:
    # Development settings
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = False

# ==============================================================================
# Application definition
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Compression statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aimesite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aimesite.wsgi.application'

# ==============================================================================
# DATABASE - MySQL Configuration (Compatible avec cPanel) / SQLite (Dev)
# ==============================================================================

DATABASE_ENGINE = config('DATABASE_ENGINE', default='django.db.backends.sqlite3')

if DATABASE_ENGINE == 'django.db.backends.mysql':
    # Configuration MySQL (Compatible cPanel - Production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DATABASE_NAME', default='aime_db'),
            'USER': config('DATABASE_USER', default='aime_user'),
            'PASSWORD': config('DATABASE_PASSWORD', default=''),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='3306'),
            'CONN_MAX_AGE': 600,  # Connexions persistantes (10 min)
            'OPTIONS': {
                'connect_timeout': 10,
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # SQLite (Développement local uniquement - inclus dans le repo)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# CACHE - Configuration compatible cPanel (utilise la DB ou fichiers)
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_table',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Sessions basées sur la base de données
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Kinshasa'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration - Compression et cache
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================================================
# MEDIA FILES (Uploads)
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@aime-rdc.org')

# ==============================================================================
# AUTHENTICATION
# ==============================================================================

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ==============================================================================
# LOGGING - Production uniquement
# ==============================================================================

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': BASE_DIR / 'logs/django.log',
                'maxBytes': 1024 * 1024 * 15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'main': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
