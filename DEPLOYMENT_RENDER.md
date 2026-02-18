# 🚀 GUIDE DE DÉPLOIEMENT RENDER.com

**Date:** Février 2026  
**Configuration:** Django + MySQL (LWS) + Render.com backend  
**Architecture:** Backend sur Render + Base de données MySQL sur LWS

---

## 📋 PRÉREQUIS

1. **Compte Render.com** - [render.com](https://render.com)
2. **Accès LWS** - Pour la base de données MySQL
3. **Git** - Dépôt GitHub connecté à Render
4. **Variables d'environnement** - À configurer dans le dashboard Render

---

## 🔧 ÉTAPE 1: Configuration LWS (Base de données)

### 1.1 Créer la base de données MySQL sur LWS

Via cPanel MySQL > Nouveau:
```sql
CREATE DATABASE aime_production;
CREATE USER 'aime_user'@'%' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON aime_production.* TO 'aime_user'@'%';
FLUSH PRIVILEGES;
```

Notez:
- 🔑 **Database:** `aime_production`
- 👤 **User:** `aime_user`
- 🔐 **Password:** votre mot de passe sécurisé
- 🌐 **Host:** IP ou domaine externe LWS (ex: `mysql.aime-rdc.org` ou IP_ADDRESS)
- 🔌 **Port:** `3306`

### 1.2 Vérifier la connexion à distance

Depuis Render, vous devez pouvoir vous connecter:
```bash
mysql -h DATABASE_HOST -u aime_user -p aime_production
```

**Si cela ne fonctionne pas:**
- Vérifier que LWS accepte les connexions distantes
- Ajouter l'IP de Render aux pare-feu LWS
- Contacter le support LWS

---

## 🎯 ÉTAPE 2: Déploiement sur Render.com

### 2.1 Connecter le dépôt GitHub

1. Aller à [render.com/dashboard](https://render.com/dashboard)
2. Cliquer **"New"** → **"Web Service"**
3. Sélectionner le dépôt GitHub `aime-site`
4. Cliquer **"Connect"**

### 2.2 Configurer le service Web

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `aime-backend` |
| **Environment** | Python |
| **Region** | Frankfurt (ou votre région) |
| **Branch** | main |
| **Root Directory** | `.` (racine du repo) |
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn aimesite.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --timeout 60` |
| **Plan** | Standard (ou Starter) |

**Note Root Directory:**
- Laisser vide ou `.` si le projet Django est à la racine du repo
- Utile pour les monorepos (ex: `backend/` si Django est dans un sous-dossier)
- Les déploiements automatiques ne se déclenchent que si des fichiers dans ce répertoire changent

### 2.3 Variables d'environnement dans Render Dashboard

1. Aller à **Settings** → **Environment Variables**
2. Ajouter les variables suivantes:

```
SECRET_KEY=your-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=aime-rdc.org,www.aime-rdc.org

# MySQL Database (LWS)
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=aime_production
DATABASE_USER=aime_user
DATABASE_PASSWORD=your-mysql-password
DATABASE_HOST=your-lws-mysql-host-or-ip
DATABASE_PORT=3306

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.aime-rdc.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@aime-rdc.org
EMAIL_HOST_PASSWORD=your-email-password
SERVER_EMAIL=noreply@aime-rdc.org

# Security
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://aime-rdc.org,https://www.aime-rdc.org
```

### 2.4 Options avancées

- ✅ **Auto-Deploy:** Activer pour déployer à chaque push sur `main`
- ✅ **Health Check:** Render le configure automatiquement
- ✅ **Keep Alive:** Cocher si vous utilisez le plan gratuit

---

## 📱 ÉTAPE 3: Connexion du domaine

### 3.1 Configurer le nom de domaine

1. Dans Render dashboard: **Settings** → **Custom Domains**
2. Ajouter: `aime-rdc.org` et `www.aime-rdc.org`
3. Render génère les enregistrements DNS

### 3.2 Mettre à jour DNS chez le registrar

Ajouter les enregistrements CNAME chez votre registrar:
```
aime-rdc.org  CNAME  aime-backend.onrender.com
www.aime-rdc.org CNAME  aime-backend.onrender.com
```

**Note:** SSL est automatiquement configuré avec Let's Encrypt

---

## ✅ ÉTAPE 4: Vérifications après déploiement

### 4.1 Logs de déploiement

Dans Render dashboard:
- ✅ Vérifier que la construction est réussie
- ✅ Vérifier que le service est en ligne
- ✅ Consulter les logs pour erreurs

### 4.2 Test de la base de données

```bash
# SSH dans Render (depuis votre terminal local)
render service logs aime-backend

# Ou directement dans le dashboard > Logs
```

### 4.3 Démontrer le fonctionnement

```bash
curl https://aime-rdc.org/api/health/
```

---

## 🔄 MISE À JOUR ET MAINTENANCE

### Déploie automatiques
- Tout push sur `main` redéploie automatiquement
- Migrations DB sont appliquées lors du déploiement (Procfile)

### Redémarrer le service
```
Render Dashboard → Services → aime-backend → Restart
```

### Accéder à la console Django
```
Render Dashboard → Logs → Shell
cd /opt/render/project/src
python manage.py shell
```

---

## 🐛 DÉPANNAGE COURANT

### Erreur: "Connection refused" à la base de données

1. Vérifier que LWS accepte les connexions distantes
2. Vérifier les variables DATABASE_* dans Render
3. Tester la connexion: `mysql -h HOST -u USER -p DB_NAME`

### Erreur: "Static files not found"

1. Vérifier que `collectstatic` s'exécute en build: revoir build.sh
2. Vérifier le chemin STATIC_ROOT dans settings.py

### Erreur: "SECRET_KEY is empty"

1. Vérifier que SECRET_KEY est défini dans Render Environment Variables
2. Redémarrer le service après ajout

### Slow database queries

1. Optimiser les indices MySQL sur LWS
2. Ajouter du cache Redis (optionnel, configuration supplémentaire)

---

## 📞 SUPPORT

- **Render Docs:** https://render.com/docs
- **Django Docs:** https://docs.djangoproject.com
- **LWS Support:** https://lws.fr

---

**Architecture finale:**
```
┌─────────────────────┐
│  Render.com         │
│  ├─ Backend Django  │
│  └─ Gunicorn        │
└──────────┬──────────┘
           │
           │ (connexion distant)
           │
           ▼
┌─────────────────────┐
│  LWS / cPanel       │
│  └─ MySQL Database  │
└─────────────────────┘
```

**Domaine:** aime-rdc.org → Render.com → MySQL LWS
