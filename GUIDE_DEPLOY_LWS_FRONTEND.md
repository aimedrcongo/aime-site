# Guide : Déployer le Frontend sur LWS

## Architecture finale
```
Backend (API Django) → RENDER
Frontend (HTML/CSS/JS) → LWS
Base de données → SUPABASE
```

---

## Étape 1 : Préparer les fichiers sur Render

### Via la console Render Shell

1. Aller dans Render dashboard → service `aime-backend` → **Shell**
2. Exécuter :

```bash
# Créer une archive du frontend
cd /opt/render/project
tar -czf frontend.tar.gz main/templates/ main/static/ staticfiles/

# Vérifier que l'archive est créée
ls -lh frontend.tar.gz
```

3. Télécharger le fichier `frontend.tar.gz` depuis Render Files → **Download**

---

## Étape 2 : Structure à uploader sur LWS

Extraire localement `frontend.tar.gz` et voici la structure attendue :

```
frontend/
├── main/
│   ├── templates/
│   │   └── main/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── about.html
│   │       └── ... (autres pages)
│   └── static/
│       └── main/
│           ├── *.css
│           ├── images/
│           └── ... (autres statiques)
└── staticfiles/
    └── main/
        ├── *.css (compilés)
        └── images/
```

---

## Étape 3 : Connexion FTP à LWS

### Obtenir les identifiants FTP

1. Aller dans **cPanel LWS** → **FTP Accounts**
2. Créer ou récupérer un compte FTP (ex: `ftpuser@votre-domaine.com`)
   - Host : `ftp.votre-domaine.com` ou `votre-domaine.com`
   - Port : `21`
   - Username : `ftpuser` ou `votre_identifiant`
   - Password : *(votre mot de passe FTP)*

---

### Connexion avec FileZilla (gratuit)

1. **Télécharger FileZilla** : filezilla-project.org
2. Ouvrir FileZilla → **File** → **Site Manager** → **New Site**
3. Remplir :
   - Protocol : `FTP`
   - Host : `ftp.votre-domaine.com`
   - Port : `21`
   - Encryption : `Use explicit FTP over TLS if available`
   - Logon Type : `Normal`
   - User : `ftpuser@votre-domaine.com`
   - Password : *(votre mot de passe)*
4. Cliquer **Connect**

---

## Étape 4 : Uploader les fichiers

### Structure à créer sur LWS

```
public_html/
├── static/              ← fichiers statiques (CSS/JS/images)
├── templates/           ← fichiers HTML
├── index.html           ← page d'accueil (optionnel si Django gère)
└── assets/              ← fichiers compilés
```

### Via FileZilla

1. **Naviguer** dans FileZilla :
   - Gauche (Local) : aller dans le dossier extrait `frontend/main/`
   - Droite (Remote) : aller dans `/public_html/`

2. **Uploader les statiques** :
   - Drag & drop `static/main/` → `/public_html/static/`
   - Drag & drop `staticfiles/main/` → `/public_html/assets/`

3. **Uploader les templates** :
   - Drag & drop `templates/main/` → `/public_html/templates/`

**Résultat final** :
```
public_html/
├── static/main/*.css
├── templates/main/*.html
└── assets/main/*.css (compilés)
```

---

## Étape 5 : Créer un index.html sur LWS

Si vous voulez une **page d'accueil statique** sur LWS (pas Django), créer `/public_html/index.html` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIME - Plateforme</title>
    <link rel="stylesheet" href="/static/main/base-cleanup.css">
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: #333; color: white; padding: 20px; text-align: center; }
        h1 { margin: 0; }
        .buttons { margin-top: 20px; text-align: center; }
        a { display: inline-block; margin: 10px; padding: 10px 20px; 
            background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        a:hover { background: #0056b3; }
    </style>
</head>
<body>
    <header>
        <h1>AIME - Plateforme de Développement</h1>
    </header>
    <div class="container">
        <p>Bienvenue sur @IMe - Association pour l'Innovation et le Monitoring Entrepreneurial</p>
        <div class="buttons">
            <a href="https://aime-backend.onrender.com">Accédez à la plateforme complète</a>
            <a href="/templates/main/about.html">À propos</a>
        </div>
    </div>
</body>
</html>
```

---

## Étape 6 : Mise à jour des URLs Django

### Sur Render

Ajouter dans **Environment Variables** du service `aime-backend` :

| NAME | VALUE |
|---|---|
| `STATIC_URL` | `https://votre-domaine.com/static/` |
| `MEDIA_URL` | `https://votre-domaine.com/media/` |

Puis redéployer le service.

---

## Étape 7 : Tester

### Tests à faire

1. **Vérifier que les fichiers sont uploadés** :
   - Ouvrir `https://votre-domaine.com/static/main/base-cleanup.css`
   - Doit afficher du CSS, pas une erreur 404

2. **Vérifier que Django sur Render relie les statiques** :
   - Ouvrir `https://aime-backend.onrender.com`
   - Les CSS/images doivent charger depuis `votre-domaine.com/static/`

3. **Vérifier la page d'accueil LWS** :
   - Ouvrir `https://votre-domaine.com`
   - Doit afficher l'index.html

---

## Dépannage

### Erreur 404 sur les CSS
- Vérifier que les fichiers sont bien uploadés : `https://votre-domaine.com/static/main/`
- Vérifier les chemins dans les URLs Django

### Les chemins CSS cassés sur LWS
- S'assurer que `STATIC_URL` sur Render pointe vers LWS
- Mettre à jour les URLs en dur dans les templates HTML

### L'index.html ne s'affiche pas
- Dans cPanel → **File Manager** → vérifier le contenu de `/public_html/`
- Vérifier que `index.html` est bien lisible (permissions 644)

---

## Résumé des URLs finales

| Élément | URL |
|---|---|
| **API/Backend Django** | https://aime-backend.onrender.com |
| **Page d'accueil** | https://votre-domaine.com/ |
| **Fichiers statiques** | https://votre-domaine.com/static/main/ |
| **Admin Django** | https://aime-backend.onrender.com/admin |

---

## Prochaines étapes

- [ ] Extraire `frontend.tar.gz` depuis Render
- [ ] Uploader les dossiers via FTP/FileZilla sur LWS
- [ ] Créer l'index.html d'accueil sur LWS
- [ ] Mettre à jour `STATIC_URL` dans Render
- [ ] Tester les URLs
- [ ] Configurer domain custom sur Render (si vous le souhaitez)
