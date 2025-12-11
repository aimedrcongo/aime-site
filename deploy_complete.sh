#!/bin/bash

# ========================================================================
# SCRIPT DE DÉPLOIEMENT AIME - LWS cPanel
# ========================================================================
# Utilisation: bash deploy_complete.sh
# Prérequis: SSH accès, Python 3.9+, Git
# ========================================================================

set -e  # Exit on any error

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Config
DEPLOY_PATH="/home/aime/public_html"
PYTHON_CMD="python3.9"
BACKUP_DIR="/home/aime/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ========================================================================
# Fonctions
# ========================================================================

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ========================================================================
# 1. PRE-DEPLOYMENT CHECKS
# ========================================================================

print_header "ETAPE 1: Vérifications pré-déploiement"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "$DEPLOY_PATH/manage.py" ]; then
    print_error "manage.py non trouvé à $DEPLOY_PATH"
    exit 1
fi
print_success "Répertoire de déploiement OK"

# Vérifier Python
if ! command -v $PYTHON_CMD &> /dev/null; then
    print_error "Python 3.9+ non trouvé"
    exit 1
fi
PYTHON_VERSION=$($PYTHON_CMD --version)
print_success "Python trouvé: $PYTHON_VERSION"

# Vérifier .env
if [ ! -f "$DEPLOY_PATH/.env" ]; then
    print_error ".env non trouvé - créer depuis .env.example"
    exit 1
fi
print_success ".env fichier présent"

# Vérifier répertoires critiques
mkdir -p "$DEPLOY_PATH/staticfiles"
mkdir -p "$DEPLOY_PATH/media"
mkdir -p "$DEPLOY_PATH/tmp"
mkdir -p "$BACKUP_DIR"
print_success "Répertoires créés/vérifiés"

# ========================================================================
# 2. BACKUP BASE DE DONNÉES
# ========================================================================

print_header "ETAPE 2: Backup de la base de données"

if command -v mysql &> /dev/null; then
    DB_USER=$(grep "^DB_USER=" "$DEPLOY_PATH/.env" | cut -d= -f2)
    DB_NAME=$(grep "^DB_NAME=" "$DEPLOY_PATH/.env" | cut -d= -f2)
    
    print_info "Backup: $DB_NAME..."
    mysqldump -u "$DB_USER" -p --single-transaction "$DB_NAME" \
        > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    print_success "Backup base de données créé"
else
    print_warning "MySQL non disponible sur ce serveur"
fi

# ========================================================================
# 3. DEPENDENCIES
# ========================================================================

print_header "ETAPE 3: Installation des dépendances"

cd "$DEPLOY_PATH"

# Créer/activer virtual env si nécessaire
if [ ! -d "venv" ]; then
    print_info "Création virtualenv..."
    $PYTHON_CMD -m venv venv
fi

# Installer/upgrader pip
print_info "Upgrade pip..."
venv/bin/pip install --upgrade pip setuptools wheel > /dev/null

# Installer requirements
print_info "Installation requirements.txt..."
venv/bin/pip install -r requirements.txt > /dev/null
print_success "Dépendances installées"

# ========================================================================
# 4. DATABASE MIGRATIONS
# ========================================================================

print_header "ETAPE 4: Migrations base de données"

$PYTHON_CMD manage.py migrate --settings=aimesite.production_settings --noinput
print_success "Migrations appliquées"

# ========================================================================
# 5. STATIC FILES
# ========================================================================

print_header "ETAPE 5: Collecte des static files"

$PYTHON_CMD manage.py collectstatic --clear --noinput \
    --settings=aimesite.production_settings
print_success "Static files collectés"

# ========================================================================
# 6. SECURITY CHECKS
# ========================================================================

print_header "ETAPE 6: Vérifications de sécurité Django"

if $PYTHON_CMD manage.py check --deploy \
    --settings=aimesite.production_settings 2>&1 | grep -q "System check identified no issues"; then
    print_success "Vérifications de sécurité OK"
else
    print_warning "Des avertissements de sécurité détectés - vérifier ci-dessus"
    $PYTHON_CMD manage.py check --deploy --settings=aimesite.production_settings
fi

# ========================================================================
# 7. PERMISSIONS
# ========================================================================

print_header "ETAPE 7: Configuration des permissions"

chmod 755 "$DEPLOY_PATH"
chmod 755 "$DEPLOY_PATH/staticfiles"
chmod 755 "$DEPLOY_PATH/media"
chmod 600 "$DEPLOY_PATH/.env"
chmod 755 "$DEPLOY_PATH/tmp"
print_success "Permissions configurées"

# ========================================================================
# 8. PASSENGER RESTART
# ========================================================================

print_header "ETAPE 8: Redémarrage Passenger"

touch "$DEPLOY_PATH/tmp/restart.txt"
print_success "Fichier de redémarrage créé"
print_info "Le serveur Passenger se redémarrera automatiquement..."
sleep 2

# ========================================================================
# 9. VALIDATION POST-DEPLOY
# ========================================================================

print_header "ETAPE 9: Validation post-déploiement"

# Vérifier que le site est accessible
DOMAIN=$(grep "^ALLOWED_HOSTS=" "$DEPLOY_PATH/.env" | cut -d= -f2 | awk -F, '{print $1}')
print_info "Vérification du site: https://$DOMAIN"

sleep 3  # Attendre le redémarrage

if curl -Is "https://$DOMAIN" 2>/dev/null | grep -q "200\|301\|302"; then
    print_success "Site accessible!"
else
    print_warning "Impossible de vérifier le site (peut être normal avec SSH)"
    print_info "Vérifier manuellement: https://$DOMAIN"
fi

# ========================================================================
# 10. RAPPORT FINAL
# ========================================================================

print_header "DÉPLOIEMENT TERMINÉ!"

echo "
${GREEN}═════════════════════════════════════════${NC}
${GREEN}  ✓ DÉPLOIEMENT RÉUSSI${NC}
${GREEN}═════════════════════════════════════════${NC}

${BLUE}Informations${NC}:
  • Timestamp: $TIMESTAMP
  • Répertoire: $DEPLOY_PATH
  • Backup BD: $BACKUP_DIR/db_backup_$TIMESTAMP.sql
  • Static files: $DEPLOY_PATH/staticfiles

${BLUE}Prochaines étapes${NC}:
  1. Vérifier https://aime-rdc.org
  2. Tester les principales fonctionnalités
  3. Vérifier les logs pour les erreurs
  4. Configurer monitoring et backups automatiques

${BLUE}Support${NC}:
  • Logs Passenger: /home/aime/logs/error.log
  • Logs Django: grep 'ERROR' dans Passenger logs
  • Tickets support: support@lws.fr

${YELLOW}Rappel sécurité${NC}:
  • Jamais commiter .env sur Git
  • Changer SECRET_KEY régulièrement
  • Faire des backups quotidiens
"

print_success "$(date '+%Y-%m-%d %H:%M:%S') - Déploiement achevé"
