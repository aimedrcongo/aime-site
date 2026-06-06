# 🚀 Déploiement AIME sur Render.com — Guide DÉFINITIF

> ⚠️ **À LIRE EN PREMIER.** Ce guide remplace tous les anciens.
> Ton site AIME est une application **Django** : Render sert **À LA FOIS**
> les pages (frontend) ET le backend. Tu n'as **PAS** besoin de Cloudflare Pages,
> ni de LWS, ni de MongoDB. Une seule chose : **Render** + une base **PostgreSQL gratuite**.

---

## ✅ Ce qu'on déploie

| Élément | Valeur |
|---|---|
| Repo GitHub | `aimedrcongo/aime-site` (le VRAI site Django) |
| Hébergeur | Render.com (sert frontend + backend) |
| Base de données | PostgreSQL **gratuite** sur Render (PAS MongoDB) |
| Domaine | `https://aime-site.onrender.com` (gratuit, fourni par Render) |

❌ **À NE PLUS UTILISER** : le repo `aime-siteofficiel`, Cloudflare Pages, MongoDB Atlas.
Ces éléments appartenaient à l'app vide qui affichait le badge Emergent.

---

## 🟢 MÉTHODE 1 — Déploiement automatique en 1 clic (RECOMMANDÉ)

Le fichier `render.yaml` est déjà configuré dans le repo : il crée tout automatiquement
(le service web + la base PostgreSQL + la clé secrète).

1. Va sur **https://dashboard.render.com**
2. Clique sur **New +** → **Blueprint**
3. Connecte ton repo GitHub **`aimedrcongo/aime-site`** (branche `main`)
4. Render lit `render.yaml` et affiche : un service `aime-site` + une base `aime-db`
5. Clique sur **Apply**
6. Attends 3 à 5 minutes (build + migrations + remplissage des données)
7. Ton site est en ligne sur : **`https://aime-site.onrender.com`** 🎉

> La base PostgreSQL est connectée automatiquement (variable `DATABASE_URL`).
> Le contenu (projets, événements, stats) est inséré automatiquement au build.

---

## 🟡 MÉTHODE 2 — Configuration manuelle (si tu préfères tout contrôler)

### Étape A — Créer la base PostgreSQL
1. Render Dashboard → **New +** → **PostgreSQL**
2. Name : `aime-db` · Region : `Frankfurt` · Plan : **Free**
3. Clique **Create Database**
4. Copie la valeur **Internal Database URL** (commence par `postgres://...`)

### Étape B — Créer le service web
1. Render Dashboard → **New +** → **Web Service**
2. Connecte le repo **`aimedrcongo/aime-site`** (branche `main`)
3. Remplis :
   - **Runtime** : `Python 3`
   - **Build Command** : `bash build.sh`
   - **Start Command** : `gunicorn aimesite.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Plan** : Free

### Étape C — Variables d'environnement (onglet *Environment*)
Ajoute EXACTEMENT ces variables :

| Clé | Valeur |
|---|---|
| `DATABASE_URL` | *(colle l'Internal Database URL de l'étape A)* |
| `SECRET_KEY` | *(une longue chaîne aléatoire, 50+ caractères)* |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` |
| `PYTHON_VERSION` | `3.11.9` |
| `DJANGO_SETTINGS_MODULE` | `aimesite.settings` |
| `RENDER` | `true` |

4. Clique **Create Web Service** → le déploiement démarre.

---

## 🔑 Accès administrateur

Après déploiement, l'admin est créé automatiquement :
- URL : `https://aime-site.onrender.com/admin/`  (ou `/accounts/login/`)
- Identifiant : **`admin`**
- Mot de passe : **`AimeAdmin2026!`**

> ⚠️ Change ce mot de passe après la première connexion (dans l'admin Django).

---

## 🌐 (Plus tard) Brancher un nom de domaine via Cloudflare

Tu n'as pas encore de domaine. Quand tu en achèteras un (ex: `aime-rdc.org`) :
1. Sur Render : service `aime-site` → **Settings** → **Custom Domains** → ajoute ton domaine.
2. Render te donne un enregistrement **CNAME**.
3. Sur Cloudflare (DNS uniquement) : crée le CNAME vers `aime-site.onrender.com`, nuage **orange** activé.
4. Ajoute ton domaine dans les variables `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` sur Render.

➡️ **Cloudflare = uniquement le DNS.** Render continue de servir tout le site.

---

## ❓ Dépannage rapide

| Problème | Solution |
|---|---|
| Erreur `DisallowedHost` | Vérifie `ALLOWED_HOSTS = .onrender.com` |
| Erreur CSRF lors d'un formulaire | Vérifie `CSRF_TRUSTED_ORIGINS = https://*.onrender.com` |
| Page sans CSS / style | Le build exécute `collectstatic` (WhiteNoise) — relance un *Manual Deploy* |
| Site vide (pas de projets) | Le build exécute `seed_preview.py` — vérifie les logs de build |
| Le site "dort" et met 30s à charger | Normal sur le plan gratuit Render (mise en veille). Passe au plan payant pour l'éviter. |
