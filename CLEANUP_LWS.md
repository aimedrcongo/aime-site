# 🗑️ GUIDE SUPPRESSION COMPLÈTE LWS

**Date:** Février 2026  
**Objectif:** Nettoyer complètement LWS (après migration vers Render)

---

## ⚠️ ATTENTION: CETTE OPÉRATION EST IRRÉVERSIBLE

Assurez-vous que:
- ✅ L'application est déployée sur **Render.com** et **fonctionne correctement**
- ✅ Les données sont **sauvegardées**
- ✅ Vous avez la **permission** de supprimer

---

## 🔧 ÉTAPE 1: SAUVEGARDE FINALE (AVANT SUPPRESSION)

### 1.1 Accéder via SSH

```bash
ssh user@votre-domaine.com
```

### 1.2 Créer les backups

```bash
cd /tmp

# Backup base de données complète
mysqldump -u aime_user -p aime_production > aime_final_backup.sql

# Backup des fichiers du projet
cd /home/YOUR_USERNAME/public_html
tar -czf /tmp/aime_final_files.tar.gz aime/

# Télécharger les fichiers de backup (depuis votre local)
scp user@votre-domaine.com:/tmp/aime_final_backup.sql ./backups/
scp user@votre-domaine.com:/tmp/aime_final_files.tar.gz ./backups/

echo "✅ Backups créés:"
ls -lh /tmp/aime_final_*
```

---

## 🚀 ÉTAPE 2: SUPPRESSION DES FICHIERS

### 2.1 Supprimer le dossier du projet

```bash
cd /home/YOUR_USERNAME/public_html

# Supprimer complètement
rm -rf aime/

# Vérifier la suppression
ls -la | grep aime

echo "✅ Dossier aime supprimé"
```

### 2.2 Supprimer les fichiers temporaires

```bash
rm -rf /tmp/aime_*
rm -rf /home/YOUR_USERNAME/tmp/restart.txt
```

---

## 🗄️ ÉTAPE 3: SUPPRESSION DE LA BASE DE DONNÉES

### 3.1 Accéder à MySQL

```bash
mysql -u root -p
```

### 3.2 Supprimer la BD et l'utilisateur

```sql
-- Lister les bases (vérifier avant de supprimer)
SHOW DATABASES;

-- Supprimer la base de données
DROP DATABASE IF EXISTS aime_production;

-- Lister les utilisateurs
SELECT User, Host FROM mysql.user WHERE User = 'aime_user';

-- Supprimer l'utilisateur
DROP USER IF EXISTS 'aime_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Vérifier que c'est supprimé
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'aime_user';

-- Quitter
EXIT;
```

Résultat attendu:
```
mysql> SELECT User, Host FROM mysql.user WHERE User = 'aime_user';
Empty set (0.00 sec)
```

---

## 🌐 ÉTAPE 4: SUPPRIMER LES DOMAINES DANS cPANEL

### Via cPanel:

1. **Addon Domains** → Sélectionner `aime-rdc.org` → **Remove**
2. **Parked Domains** → Sélectionner `www.aime-rdc.org` → **Remove**
3. **Subdomains** → Supprimer si nécessaire

### Ou via SSH:

```bash
# Lister les domaines
cd /home/YOUR_USERNAME/public_html
ls -la

# Vérifier la configuration Apache
grep -r "aime" /home/YOUR_USERNAME/

# Supprimer les config de domaine
cPanel API ou contact support LWS pour supprimer du nameserver
```

---

## 🔐 ÉTAPE 5: SÉCURITÉ - NETTOYER LES LOGS

```bash
# Vider les logs de l'application
rm -rf /home/YOUR_USERNAME/logs/aime_*
rm -rf /home/YOUR_USERNAME/logs/error_log

# Vérifier
ls -la /home/YOUR_USERNAME/logs/ | grep aime
```

---

## ✅ VÉRIFICATION FINALE

```bash
# Rien ne doit rester d'AIME sur LWS

# 1. Vérifier répertoire
ls -la /home/YOUR_USERNAME/public_html/ | grep aime
# Résultat: RIEN ne doit apparaître

# 2. Vérifier bases de données
mysql -u root -p -e "SHOW DATABASES LIKE 'aime%';"
# Résultat: 0 bases

# 3. Vérifier utilisateurs MySQL
mysql -u root -p -e "SELECT User FROM mysql.user WHERE User LIKE 'aime%';"
# Résultat: 0 utilisateurs

# 4. Vérifier DNS
nslookup aime-rdc.org
# Doit pointer sur Render ou domaine nouveau

echo "✅ LWS COMPLÈTEMENT NETTOYÉ!"
```

---

## 📊 RÉSUMÉ DE L'ARCHITECTURE FINALE

### AVANT (LWS)
```
LWS cPanel
├─ Backend Django
├─ MySQL Database
└─ Fichiers statiques
```

### APRÈS (Render + LWS)
```
Render.com
├─ Backend Django
└─ Gunicorn Server

LWS
└─ [VIDE - Plus rien]
(Ou nouveau domaine/projet)
```

---

## 🚨 RÉCUPÉRATION D'URGENCE

Si vous avez besoin de restaurer:

```bash
# Depuis vos backups locaux
scp ./backups/aime_final_backup.sql user@votre-domaine:/tmp/
scp ./backups/aime_final_files.tar.gz user@votre-domaine:/tmp/

# Connexion SSH
ssh user@votre-domaine

# Restaurer les fichiers
cd /home/YOUR_USERNAME/public_html
tar -xzf /tmp/aime_final_files.tar.gz

# Restaurer la BD
mysql -u root -p aime_production < /tmp/aime_final_backup.sql

# Réactiver les domaines
# Via cPanel ou contact support
```

---

## ✨ C'EST FAIT!

Votre projet **AIME** est maintenant:
- ✅ **Déployé sur Render.com** - Automatiquement à chaque push
- ✅ **Utilise MySQL sur LWS** - Base de données externe
- ✅ **Dynamique et scalable** - Render gère la performance
- ✅ **LWS est vierge** - Prêt pour autre chose

**Maintenance maintenant = GitHub push → Render déploie automatiquement!** 🚀

---

## 📞 EN CAS DE PROBLÈME

**Besoin de récupérer AIME sur LWS?** → Utiliser les backups et DEPLOYMENT_LWS_ZERO.md
**Erreurs sur Render?** → Consulter DEPLOYMENT_RENDER.md
**Questions?** → Render support ou GitHub issues
