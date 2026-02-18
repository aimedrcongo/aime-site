# ⚡ CHECKLIST DÉPLOIEMENT COMPLET

**Objectif:** Passer de LWS seul → Render.com (Backend) + LWS (MySQL)

---

## ✅ ÉTAPE 1: PUSH GITHUB POUR RENDER (À FAIRE MAINTENANT)

Dans votre terminal local:

```bash
cd /workspaces/aime-site

# 1. Ajouter tous les fichiers
git add -A

# 2. Commit
git commit -m "chore: Configure Render.com deployment with MySQL (LWS)

- Updated requirements.txt with MySQL support
- Added Procfile for Render
- Created render.yaml configuration
- Added build.sh script
- Created deployment guides
- Updated settings.py for remote MySQL
- Added runtime.txt with Python 3.11"

# 3. Pousser sur main
git push origin main
```

**Après le push:**
- ⏳ Render commence automatiquement le déploiement
- 📊 Surveillance: https://dashboard.render.com
- ⏱️ Temps d'attente: 5-10 minutes

### Vérifier que Render démarre:
```bash
# Voir le log de build
# Dashboard → Services → aime-backend → Logs
# Chercher:
# ✅ "Cloning..." 
# ✅ "Installing dependencies..."
# ✅ "Running migrations..."
# ✅ "Build completed successfully"
# ✅ "Service live at:"
```

---

## 📝 ÉTAPE 2: AVANT DE DÉPLOYER SUR LWS

Avant de commencer avec LWS, remplir ces informations:

### Variables Render (pour MySQL distant)

Dans **Render Dashboard** → **aime-backend** → **Settings** → **Environment Variables**:

```
SECRET_KEY=GÉNÉRER_UNE_CLÉ_SÉCURISÉE
DEBUG=False
ALLOWED_HOSTS=aime-rdc.org,www.aime-rdc.org

# À remplir APRÈS avoir créé la DB sur LWS:
DATABASE_USER=aime_user
DATABASE_PASSWORD=votre_mot_de_passe
DATABASE_HOST=votre_ip_ou_domaine_lws
DATABASE_PORT=3306

# Email (optionnel)
EMAIL_HOST=mail.aime-rdc.org
EMAIL_HOST_USER=noreply@aime-rdc.org
EMAIL_HOST_PASSWORD=votre_email_password
```

**Note:** Si vous ne remplissez pas DATABASE_HOST maintenant, Render continuera avec SQLite en prod (non-optimal)

---

## 🏠 ÉTAPE 3: DÉPLOYER SUR LWS (RECOMMENCER À ZÉRO)

### Préparation (5 min)

```bash
# Savoir les informations LWS:
- Username cPanel: _______________
- Password cPanel: _______________
- Domain: _______________
- SSH Host: _______________
```

### Exécution

Suivre **ÉTAPE PAR ÉTAPE** le guide: [DEPLOYMENT_LWS_ZERO.md](DEPLOYMENT_LWS_ZERO.md)

Sections clés:
1. ✅ **Nettoyage complet** (section 1)
2. ✅ **Installation nouvelle** (section 2)
3. ✅ **Configuration Passenger** (section 2.6)
4. ✅ **Configuration domaines** (section 2.7)
5. ✅ **Certificat SSL** (section 2.8)

**Durée totale:** 30-45 minutes

---

## 🗑️ ÉTAPE 4: EFFACER COMPLÈTEMENT LWS (OPTIONNEL)

⚠️ **Une fois que Render fonctionne parfaitement**, vous pouvez nettoyer LWS:

Suivre le guide: [CLEANUP_LWS.md](CLEANUP_LWS.md)

**Points critiques:**
1. ✅ Créer les BACKUPS FINALES
2. ✅ Supprimer les fichiers (`rm -rf aime/`)
3. ✅ Supprimer la base de données
4. ✅ Supprimer le compte MySQL
5. ✅ Supprimer les domaines cPanel

---

## 🎯 ARCHITECTURE FINALE

```
Internet
    ↓
aime-rdc.org
    ↓
┌─────────────────────┐
│   Render.com        │
│  ├─ Django App      │
│  └─ Gunicorn        │
└──────────┬──────────┘
           │
      [TCP Connection]
           │
           ↓
┌─────────────────────┐
│   LWS / cPanel      │
│  └─ MySQL Database  │
└─────────────────────┘
```

---

## 📊 RÉSUMÉ DES GUIDES

| Document | Objectif | Durée |
|----------|----------|--------|
| **DEPLOYMENT_RENDER.md** | Configurer Render.com | 10 min |
| **DEPLOYMENT_LWS_ZERO.md** | Installer LWS from scratch | 45 min |
| **CLEANUP_LWS.md** | Supprimer tout de LWS | 15 min |

---

## 🔑 FICHIERS IMPORTANTS CRÉÉS

```
aime-site/
├── Procfile                    # Configuration Render
├── render.yaml                 # Config détaillée Render
├── runtime.txt                 # Python version pour Render
├── build.sh                    # Script de build
├── requirements.txt            # Dependencies (MySQL)
├── .env.render                 # Template variables
├── DEPLOYMENT_RENDER.md        # Guide Render
├── DEPLOYMENT_LWS_ZERO.md      # Guide LWS from scratch
├── CLEANUP_LWS.md              # Guide nettoyage LWS
└── aimesite/settings.py        # Configuré pour MySQL distant
```

---

## 🚀 COMMANDES RAPIDES

### Voir le statut Render
```bash
# Dashboard: https://dashboard.render.com
# Ou via CLI:
render logs -f @aime-backend
```

### Redémarrer Render
```
Dashboard → Services → aime-backend → Restart
```

### Redémarrer LWS
```bash
ssh user@domaine.com
cd /home/user/public_html/aime
source venv/bin/activate
touch tmp/restart.txt
```

### Se connecter à MySQL depuis Render
```bash
# Dans Render shell:
mysql -h DATABASE_HOST -u aime_user -p aime_production
```

---

## ✅ CHECKLIST DE VÉRIFICATION

### Après Render déploie:
- [ ] Service est "Live"
- [ ] Pas d'erreurs dans les logs
- [ ] Page d'accueil répond
- [ ] Admin panel `/admin/` fonctionne

### Après LWS configuré:
- [ ] Domaine pointe sur LWS
- [ ] SSL certificat active
- [ ] Base de données MySQL accessible
- [ ] Pages se chargent correctement
- [ ] Database sur LWS ↔ Backend sur Render communiquent

### Avant suppression LWS:
- [ ] Render fonctionne PARFAITEMENT
- [ ] Backups complets effectuées
- [ ] Données transférées/vérifiées
- [ ] Permission de nettoyer

---

## 🔧 SECRET_KEY GENERATOR

```bash
# Pour générer une clé sécurisée:
python -c "import secrets; print(secrets.token_urlsafe(60))"

# Ou avec Django:
cd /workspaces/aime-site
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copier la clé générée → Coller dans Render Dashboard

---

## 🎊 RÉSULTAT FINAL

✅ **Backend dynamique:** Render.com (auto-scaling, auto-deploy)  
✅ **Base de données:** MySQL sur LWS (stable, performante)  
✅ **Mises à jour:** `git push` → auto-déploi sur Render  
✅ **Downtime:** Zéro (Render gère la haute disponibilité)  
✅ **Coûts:** Render gratuit ou $7/mois, LWS 3-5€/mois

---

**Prêt à commencer? Lancez l'ÉTAPE 1: Push vers GitHub!** 🚀
