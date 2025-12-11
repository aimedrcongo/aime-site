"""
Commande d'optimisation de la base de données PostgreSQL
Usage: python manage.py optimize_db
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Optimise la base de données PostgreSQL (VACUUM, ANALYZE, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Effectue un VACUUM FULL (plus lent mais plus efficace)'
        )

    def handle(self, *args, **options):
        if 'postgresql' not in connection.settings_dict['ENGINE']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Cette commande est optimisée pour PostgreSQL.\n'
                    '   Votre base actuelle : ' + connection.settings_dict['ENGINE']
                )
            )
            return

        self.stdout.write(self.style.WARNING('🔧 Optimisation de la base de données...'))
        
        with connection.cursor() as cursor:
            try:
                # 1. VACUUM - Nettoie les données obsolètes
                if options['full']:
                    self.stdout.write('   → Exécution de VACUUM FULL...')
                    cursor.execute('VACUUM FULL;')
                else:
                    self.stdout.write('   → Exécution de VACUUM...')
                    cursor.execute('VACUUM;')
                
                # 2. ANALYZE - Met à jour les statistiques
                self.stdout.write('   → Exécution de ANALYZE...')
                cursor.execute('ANALYZE;')
                
                # 3. Réindexation
                self.stdout.write('   → Réindexation des tables...')
                cursor.execute('REINDEX DATABASE ' + connection.settings_dict['NAME'] + ';')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '\n✅ Optimisation terminée avec succès !\n'
                        '   La base de données est maintenant optimisée.'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ Erreur lors de l\'optimisation : {str(e)}')
                )
                raise

        # Afficher des statistiques
        self._show_stats()

    def _show_stats(self):
        """Affiche quelques statistiques de la base"""
        with connection.cursor() as cursor:
            # Taille de la base de données
            cursor.execute('''
                SELECT pg_size_pretty(pg_database_size(current_database())) as size;
            ''')
            db_size = cursor.fetchone()[0]
            
            self.stdout.write(
                self.style.SUCCESS(f'\n📊 Statistiques :')
            )
            self.stdout.write(f'   Taille de la base : {db_size}')
