# 🚀 GUIDE CONFIGURATION RENDER + LWS MySQL

**Date:** Février 2026  
**Objectif:** Configurer Render pour utiliser MySQL distant sur LWS

---

## ✅ INFOS LWS

```
IP Serveur:           91.234.194.126
Username cPanel:      cp2639565p41
Domaine Primaire:     aime-rdc.org
Home Directory:       /home/cp2639565p41
```

---

## 📋 ÉTAPE 1: CONFIGURATION RENDER DASHBOARD

### 1.1 Générer SECRET_KEY (une seule fois)

Localement, générez une clé sécurisée:

```bash
cd /workspaces/aime-site
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copier la clé affichée.

### 1.2 Aller sur Render Dashboard

1. Allez sur: https://dashboard.render.com
2. Cliquez sur service **aime-backend**
3. Allez dans **Settings** → **Environment Variables**

### 1.3 Ajouter les variables d'environnement

Cliquez **Add Environment Variable** et remplissez:

```
KEY                    VALUE
─────────────────────────────────────────────────────────
SECRET_KEY             [Votre clé générée ci-dessus]
DEBUG                  False
ALLOWED_HOSTS          aime-rdc.org,www.aime-rdc.org

DATABASE_ENGINE        django.db.backends.mysql
DATABASE_NAME          cp2639565p41_aimer2639565
DATABASE_USER          cp2639565p41_aimer2639565
DATABASE_PASSWORD      Waze@Dataaime2026
DATABASE_HOST          91.234.194.126
DATABASE_PORT          3306
```

**⚠️ IMPORTANT:** Le `DATABASE_HOST` DOIT être accessible depuis Internet. Vérifiez que:
- Port 3306 est ouvert sur LWS pour connexions externes
- L'utilisateur MySQL a les permissions `@'%'` pas juste `@'localhost'`

### 1.4 Sauvegarder et Redémarrer

1. Cliquez **Save**
2. Allez dans **Deploy** → **Restart** pour redémarrer

---

## 🔧 ÉTAPE 2: VÉRIFIER LA CONNEXION

Une fois le redémarrage terminé, vérifiez les logs:

1. Dashboard → **aime-backend** → **Logs**
2. Cherchez les messages:

```
✅ "Successfully installed all packages"
✅ "Applying migrations"
✅ "Operations to perform"
✅ "Service live at: https://aime-backend.onrender.com"
```

❌ Si vous voyez une erreur de connexion MySQL:
```
django.db.utils.OperationalError: (2002, "Can't connect to MySQL")
```

Cela signifie:
- `DATABASE_HOST` incorrect
- Port 3306 fermé sur LWS
- Utilisateur MySQL n'a pas les droits `@'%'`

---

## 🏠 ÉTAPE 3: VÉRIFIER QUE LE SITE FONCTIONNE

### 3.1 Accédez à votre app Render

1. Allez sur: https://aime-backend.onrender.com/
2. Vérifiez que la page d'accueil affiche

### 3.2 Testez l'admin Django

1. Allez sur: https://aime-backend.onrender.com/admin/
2. Vous devriez voir le login Django

---

## 📊 PROCHAINES ÉTAPES

Une fois que Render fonctionne:

1. ✅ **Configurer le DNS** pour pointer vers Render
   - DNS → A record → IP de Render
   
2. ✅ **Ajouter le certificat SSL** (Render le fait automatiquement avec Let's Encrypt)

3. ✅ **Tester en production**
   - Allez sur https://aime-rdc.org

---

## 🐛 DÉPANNAGE COURANT

### Erreur: "Access denied for user"
**Solution:** Vérifiez que l'utilisateur MySQL a les droits `@'%'` sur LWS

```sql
GRANT ALL PRIVILEGES ON cp2639565p41_aimer2639565.* TO 'cp2639565p41_aimer2639565'@'%';
FLUSH PRIVILEGES;
```

### Erreur: "Can't connect to MySQL"
**Solution:** Vérifiez que le port 3306 est ouvert sur le firewall LWS

Testez depuis votre machine locale:
```bash
mysql -h 91.234.194.126 -u cp2639565p41_aimer2639565 -p
```

### Pages statiques ne se chargent pas
**Solution:** Render a peut-être oublié de collecter les fichiers statiques. Relancez les migrations:

Dashboard → **aime-backend** → **Restart**

---

## ♻️ DÉPLOIEMENT CONTINU

À partir de maintenant, chaque fois que vous poussez du code :

```bash
git push origin main
```

Render redéploie **automatiquement** en 2-5 minutes ✨

---

## 📞 SUPPORT

Si vous avez besoin d'aide:
- Vérifiez les logs Render: Dashboard → Logs
- Vérifiez la connectivité MySQL: `mysql -h 91.234.194.126 -u...`
- Consultez: https://render.com/docs
