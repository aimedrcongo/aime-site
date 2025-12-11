"""
Commande de backup automatique de la base de données
Usage: python manage.py backup_database
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Crée un backup complet de la base de données au format JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Répertoire de sortie pour les backups (défaut: backups/)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        
        # Créer le répertoire de backup s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer le nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(output_dir, f'backup_{timestamp}.json')
        
        self.stdout.write(self.style.WARNING(f'🔄 Création du backup...'))
        
        try:
            # Exporter les données
            with open(filename, 'w', encoding='utf-8') as f:
                call_command(
                    'dumpdata',
                    '--natural-foreign',
                    '--natural-primary',
                    '-e', 'contenttypes',
                    '-e', 'auth.Permission',
                    '--indent', '4',
                    stdout=f
                )
            
            # Vérifier la taille du fichier
            file_size = os.path.getsize(filename)
            size_mb = file_size / (1024 * 1024)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Backup créé avec succès !\n'
                    f'   Fichier : {filename}\n'
                    f'   Taille  : {size_mb:.2f} MB'
                )
            )
            
            # Nettoyer les vieux backups (garder les 10 derniers)
            self._cleanup_old_backups(output_dir, keep=10)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors du backup : {str(e)}')
            )
            raise

    def _cleanup_old_backups(self, directory, keep=10):
        """Supprime les vieux backups, garde seulement les N derniers"""
        backup_files = sorted(
            [f for f in os.listdir(directory) if f.startswith('backup_') and f.endswith('.json')],
            reverse=True
        )
        
        if len(backup_files) > keep:
            for old_backup in backup_files[keep:]:
                old_path = os.path.join(directory, old_backup)
                os.remove(old_path)
                self.stdout.write(
                    self.style.WARNING(f'🗑️  Ancien backup supprimé : {old_backup}')
                )
