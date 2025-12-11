"""
Commande Django pour restaurer une base de données depuis un backup
Usage: python manage.py restore_database <backup_file>
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import gzip
import os


class Command(BaseCommand):
    help = 'Restaure la base de données depuis un fichier backup'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Nom du fichier de backup (dans le répertoire backups/)'
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Vider la base de données avant la restauration (ATTENTION: supprime toutes les données)',
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        
        # Chercher le fichier dans le répertoire backups
        backup_dir = settings.BASE_DIR / 'backups'
        filepath = backup_dir / backup_file
        
        if not filepath.exists():
            raise CommandError(f'❌ Fichier de backup introuvable: {filepath}')
        
        self.stdout.write(
            self.style.WARNING(
                f'⚠️  ATTENTION: Vous allez restaurer la base de données depuis:\n'
                f'   {filepath}\n'
            )
        )
        
        if options['flush']:
            self.stdout.write(
                self.style.ERROR(
                    '🚨 DANGER: Cette opération va SUPPRIMER toutes les données actuelles!\n'
                )
            )
            confirm = input('Taper "OUI" pour confirmer: ')
            if confirm != 'OUI':
                self.stdout.write(self.style.WARNING('❌ Restauration annulée'))
                return
            
            # Flush de la base de données
            self.stdout.write('🗑️  Vidage de la base de données...')
            call_command('flush', '--no-input')
        
        try:
            # Décompresser si nécessaire
            if filepath.suffix == '.gz':
                self.stdout.write('📦 Décompression du backup...')
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    data = f.read()
                    
                # Créer un fichier temporaire
                temp_file = backup_dir / 'temp_restore.json'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                restore_file = temp_file
            else:
                restore_file = filepath
            
            # Restaurer les données
            self.stdout.write('🔄 Restauration des données...')
            call_command('loaddata', str(restore_file))
            
            # Nettoyer le fichier temporaire
            if restore_file != filepath:
                os.remove(restore_file)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Base de données restaurée avec succès depuis {backup_file}!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la restauration: {str(e)}')
            )
            raise
