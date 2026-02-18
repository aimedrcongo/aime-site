# 🚀 DÉPLOIEMENT RAPIDE RENDER.com (5 minutes)

**Configuration:** Backend Render + MySQL LWS

---

## ✅ 3 ÉTAPES SIMPLES

### ÉTAPE 1: Préparer la base de données LWS (5 min)

**Sur cPanel LWS:**

1. MySQL > Créer base de données: `aime_production`
2. MySQL > Créer utilisateur: `aime_user` avec mot de passe fort
3. Donner tous les droits de `aime_production` à `aime_user`

**Important:** Activer l'accès distant pour `aime_user@%`

Notez:
- 📌 **HOST:** IP ou domaine MySQL LWS
- 📌 **USER:** `aime_user`
- 📌 **PASSWORD:** votre mot de passe
- 📌 **DATABASE:** `aime_production`

---

### ÉTAPE 2: Créer le service Render (2 min)

1. Aller à [render.com/dashboard](https://render.com/dashboard)
2. **New Web Service** → Sélectionner repository `aime-site`
3. Configurer:
   - **Name:** `aime-backend`
   - **Build:** `bash build.sh`
   - **Start:** `gunicorn aimesite.wsgi:application --bind 0.0.0.0:$PORT --workers 4`
   - **Plan:** Standard (recommandé) ou Starter

4. **Create Web Service**

---

### ÉTAPE 3: Ajouter variables d'environnement (3 min)

Une fois le service créé, aller à **Settings** → **Environment**:

```
SECRET_KEY=votre-cle-secrete-super-longue-min-50-caracteres
DEBUG=False
ALLOWED_HOSTS=aime-rdc.org,www.aime-rdc.org,*.onrender.com

DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=aime_production
DATABASE_USER=aime_user
DATABASE_PASSWORD=votre-mot-de-passe-lws
DATABASE_HOST=votre-host-mysql-lws
DATABASE_PORT=3306

EMAIL_HOST=mail.aime-rdc.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@aime-rdc.org
EMAIL_HOST_PASSWORD=votre-mot-de-passe-email
SERVER_EMAIL=noreply@aime-rdc.org
```

**Cliquer "Save"** → Le service redémarre automatiquement

---

## 🎯 Après le déploiement

### Option 1: Utiliser le domaine Render (gratuit, test rapide)
```
https://aime-backend.onrender.com
```

### Option 2: Connecter domaine personnalisé (5 min supplémentaires)
1. Render: **Settings** → **Custom Domains** → Ajouter `aime-rdc.org`
2. Copier les enregistrements CNAME fournis par Render
3. DNS du registrar: Ajouter les CNAME
4. Attendre 5-15 min (propagation DNS)

---

## ✨ Vérifier que ça marche

```bash
# Test rapide (remplacer par votre URL)
curl https://aime-backend.onrender.com/admin/
```

Vous devriez voir la page de connexion Django ✅

---

## 🔄 Déploiements futurs

```bash
# À chaque push sur 'main', Render redéploie automatiquement:
git push origin main
```

Le build, les migrations et collectstatic s'exécutent automatiquement ✅

---

## 🐛 Si ça ne marche pas

**Logs disponibles:**
- Render Dashboard → Logs
- Chercher "migrate" ou "ERROR"

**Erreurs courantes:**
- ❌ Database connection refused → Vérifier DATABASE_HOST et pare-feu LWS
- ❌ Static files not found → Vérifier que collectstatic s'exécute
- ❌ SECRET_KEY empty → Vérifier qu'il est défini dans les variables Render

---

## 📚 Documentation complète

Voir: `DEPLOYMENT_RENDER.md`

---

**Architecture finale:**
```
Client → aime-rdc.org (DNS) → Render.com → MySQL LWS
```

Profitez de votre déploiement Render! 🎉
