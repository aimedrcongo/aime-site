# 📋 FICHE DE DÉPLOIEMENT COMPLET - AIME sur LWS cPanel

**Date:** 11 décembre 2025  
**Version:** 1.0  
**Plateforme:** LWS cPanel avec Passenger WSGI  
**Environnement:** Production

---

## 1. 📦 PAQUETS & DÉPENDANCES

### Python (3.9+)
```bash
pip install -r requirements.txt
```

**Packages critiques:**
- Django==4.2.14
- mysqlclient==2.2.0 OU pymysql==1.1.0
- Pillow==10.0.0
- python-dotenv==1.0.0
- gunicorn==21.0.0

### Serveur Web
- **Passenger WSGI** (fourni par LWS cPanel)
- **MySQL 5.7+** (via cPanel)
- **Node.js** (optionnel, pour static files optimization)

### Système (macOS/Linux - pour tests locaux)
```bash
brew install mysql@5.7  # macOS
apt-get install mysql-server  # Ubuntu/Debian
```

---

## 2. 🔧 CONFIGURATION PRE-DEPLOIEMENT

### 2.1 Variables d'environnement (.env)

Créer `/home/aime/.env`:
```
DEBUG=False
ALLOWED_HOSTS=aime-rdc.org,www.aime-rdc.org
SECRET_KEY=your-long-random-secret-key-here
DB_ENGINE=django.db.backends.mysql
DB_NAME=aime_production
DB_USER=aime_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.aime-rdc.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@aime-rdc.org
EMAIL_HOST_PASSWORD=email-password
SERVER_EMAIL=noreply@aime-rdc.org
STATIC_ROOT=/home/aime/public_html/staticfiles
MEDIA_ROOT=/home/aime/public_html/media
```

### 2.2 Settings Django (production_settings.py)

✅ **Vérifier dans `/aimesite/production_settings.py`:**

```python
# ✓ DEBUG = False
# ✓ ALLOWED_HOSTS = ['aime-rdc.org', 'www.aime-rdc.org']
# ✓ DATABASES utilisent MySQL
# ✓ STATIC_ROOT = '/home/aime/public_html/staticfiles'
# ✓ MEDIA_ROOT = '/home/aime/public_html/media'
# ✓ SESSION_COOKIE_SECURE = True
# ✓ CSRF_COOKIE_SECURE = True
# ✓ SECURE_BROWSER_XSS_FILTER = True
# ✓ SECURE_CONTENT_SECURITY_POLICY configuré
```

### 2.3 Base de données

**Sur cPanel MySQL:**
```sql
CREATE DATABASE aime_production;
CREATE USER 'aime_user'@'localhost' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON aime_production.* TO 'aime_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 3. 📤 ÉTAPES DE DÉPLOIEMENT

### Étape 1: Préparation du serveur
```bash
cd /home/aime/public_html
python3.9 manage.py migrate --settings=aimesite.production_settings
python3.9 manage.py collectstatic --noinput --settings=aimesite.production_settings
python3.9 manage.py compilemessages --settings=aimesite.production_settings
```

### Étape 2: Vérifications de sécurité
```bash
python3.9 manage.py check --deploy --settings=aimesite.production_settings
```

### Étape 3: Permissions fichiers
```bash
chmod 755 /home/aime/public_html
chmod 755 /home/aime/public_html/staticfiles
chmod 755 /home/aime/public_html/media
chmod 600 /home/aime/.env
```

### Étape 4: Configuration Passenger (passenger_wsgi.py)

Fichier: `/home/aime/public_html/passenger_wsgi.py`
```python
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'aimesite.production_settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Étape 5: Redémarrage Passenger
```bash
touch /home/aime/public_html/tmp/restart.txt
```

---

## 4. ✅ CHECKLIST DE VALIDATION

### Tests locaux (avant déploiement)
- [ ] `python manage.py check --deploy` = 0 errors
- [ ] Dashboard affiche avec theme bleu + texte blanc
- [ ] Navbar affiche correctement (blanc + texte bleu)
- [ ] Footer affiche avec gradient bleu
- [ ] Logout redirige vers home (pas vers admin)
- [ ] Modal visiteur n'apparaît pas en boucle
- [ ] Dropdown menus visibles avec bordures
- [ ] Images logo chargent correctement
- [ ] CSS pas affiché comme texte sur page

### Tests post-déploiement (sur LWS)
- [ ] Site accessible via https://aime-rdc.org
- [ ] Certificat SSL valide
- [ ] Page d'accueil charge en <2s
- [ ] Dashboard responsive sur mobile
- [ ] Formules de contact fonctionnent
- [ ] Emails de notification envoient
- [ ] Admin accessible via /admin/
- [ ] Logs sans erreurs 500

### Performances
```bash
curl -I https://aime-rdc.org
# Vérifier: 200 OK, Content-Type: text/html
# Vérifier: Cache-Control présent
```

---

## 5. 📊 STRUCTURE FICHIERS ESSENTIELS

```
/home/aime/public_html/
├── passenger_wsgi.py          ← Point d'entrée WSGI
├── manage.py
├── requirements.txt
├── .env                        ← Secrets (non en git!)
│
├── aimesite/
│   ├── production_settings.py  ← Configuration production
│   ├── urls.py
│   └── wsgi.py
│
├── main/
│   ├── static/main/            ← Fichiers CSS/JS
│   │   ├── dashboard_ocean.css
│   │   ├── dashboard-fix.css
│   │   ├── navbar-fix.css
│   │   ├── footer-fix.css
│   │   ├── global-fix.css
│   │   └── base-cleanup.css
│   │
│   ├── templates/main/
│   │   └── base.html           ← Template maître (NETTOYÉ!)
│   │
│   └── auth_views.py           ← Views auth (logout_view OK)
│
├── staticfiles/                ← Generated by collectstatic
├── media/                      ← User uploads
├── tmp/restart.txt             ← For Passenger restarts
└── db.sqlite3                  ← Local only (pas en prod)
```

---

## 6. 🔐 SÉCURITÉ

### Secrets à protéger
- [ ] `.env` non commité
- [ ] `SECRET_KEY` changé
- [ ] `DB_PASSWORD` sécurisé (>16 chars)
- [ ] `EMAIL_HOST_PASSWORD` sécurisé

### Firewall/Ports
- [ ] Port 443 (HTTPS) ouvert
- [ ] Port 80 (HTTP) redirige vers HTTPS
- [ ] SSH accès limité à votre IP
- [ ] FTP désactivé (utiliser SFTP)

### Django Security
```python
# ✓ SECURE_SSL_REDIRECT = True
# ✓ SESSION_COOKIE_SECURE = True
# ✓ CSRF_COOKIE_SECURE = True
# ✓ SECURE_BROWSER_XSS_FILTER = True
# ✓ X_FRAME_OPTIONS = 'DENY'
```

---

## 7. 🆘 TROUBLESHOOTING

### Erreur 500 Internal Server Error
```bash
# Vérifier logs
tail -50 /home/aime/public_html/tmp/error.log
tail -50 /home/aime/public_html/tmp/access.log

# Vérifier variables d'environnement
grep -i debug .env
```

### CSS/Images ne chargent pas
```bash
# Regénérer static files
python3.9 manage.py collectstatic --clear --noinput

# Vérifier permissions
ls -la staticfiles/
# Doit être readable (755)
```

### Erreur "ALLOWED_HOSTS"
```bash
# Éditer .env
ALLOWED_HOSTS=aime-rdc.org,www.aime-rdc.org

# Redémarrer
touch tmp/restart.txt
```

### Erreur MySQL "Access Denied"
```bash
# Vérifier credentials dans .env
mysql -h localhost -u aime_user -p
# Entrer password depuis .env
```

---

## 8. 📈 POST-DÉPLOIEMENT

### Monitoring
- [ ] Mettre en place Google Analytics
- [ ] Configurer monitoring CPU/RAM via cPanel
- [ ] Activer notifications d'erreur Django

### Backups
```bash
# Quotidien - Base de données
mysqldump -u aime_user -p aime_production > backup_$(date +%Y%m%d).sql

# Mensuel - Fichiers complets
tar czf aime_backup_$(date +%Y%m%d).tar.gz /home/aime/public_html/
```

### Updates
- [ ] Django patches: `pip install --upgrade Django`
- [ ] Dependencies: `pip install -r requirements.txt --upgrade`
- [ ] System: cPanel automatic updates enabled

---

## 9. 🔄 ROLLBACK (si problème)

### Restore depuis backup
```bash
# Restaurer BD
mysql -u aime_user -p aime_production < backup_20251210.sql

# Restaurer fichiers
tar xzf aime_backup_20251210.tar.gz -C /home/

# Redémarrer
touch /home/aime/public_html/tmp/restart.txt
```

---

## 10. 📞 CONTACTS SUPPORT

| Service | Contact |
|---------|---------|
| LWS Support | support@lws.fr |
| Hébergement | Ticket dans cPanel |
| Email | Vérifier SPF/DKIM/DMARC |
| DNS | Votre registraire domaine |

---

## ✨ CHANGEMENTS APPLIQUÉS AVANT DÉPLOIEMENT

✅ **HTML Cleanup**
- Suppression CSS débordant dans base.html
- Structure HTML propre et valide
- Block extra_css unique

✅ **Styled System**
- Dashboard: Blue gradient + white text
- Navbar: White background + blue text  
- Footer: Blue gradient + proper spacing
- Logo: White background box

✅ **Functionalité**
- Logout redirige vers home
- Modal visiteur: Cookie-based suppression
- Dropdowns: Visible avec borders

✅ **Static Files**
- 7 CSS files externe (zero inline styles)
- collectstatic prêt
- Images optimisées

---

## 🚀 PRÊT À DÉPLOYER?

```bash
# Dernier check avant livraison:
python manage.py check --deploy --settings=aimesite.production_settings

# Résultat attendu:
# System check identified no issues (0 silenced).
```

**Date déploiement proposée:** [À remplir]  
**Responsable déploiement:** [À remplir]  
**Validation:** ☐ APPROUVÉ

---

*Document généré le 11 décembre 2025*  
*AIME - Agissons Ici et Maintenant pour les Enfants*
