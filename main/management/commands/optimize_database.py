"""
Commande Django pour optimiser la base de données
Usage: python manage.py optimize_database
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
import time


class Command(BaseCommand):
    help = 'Optimise la base de données et nettoie le cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--vacuum',
            action='store_true',
            help='Exécute VACUUM sur SQLite (réorganise et compacte)',
        )
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyse les statistiques de la base de données',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Vide complètement le cache Redis',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔧 Optimisation de la base de données...'))
        
        start_time = time.time()
        
        # Nettoyer le cache si demandé
        if options['clear_cache']:
            self.stdout.write('🧹 Nettoyage du cache...')
            try:
                cache.clear()
                self.stdout.write(self.style.SUCCESS('  ✅ Cache vidé'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠️  Erreur cache: {e}'))
        
        # Optimisations spécifiques à SQLite
        if 'sqlite' in connection.settings_dict['ENGINE']:
            with connection.cursor() as cursor:
                # VACUUM - Réorganise la base de données
                if options['vacuum']:
                    self.stdout.write('🗜️  Exécution de VACUUM (compactage)...')
                    try:
                        cursor.execute('VACUUM;')
                        self.stdout.write(self.style.SUCCESS('  ✅ VACUUM terminé'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur VACUUM: {e}'))
                
                # ANALYZE - Met à jour les statistiques
                if options['analyze']:
                    self.stdout.write('📊 Analyse des statistiques...')
                    try:
                        cursor.execute('ANALYZE;')
                        self.stdout.write(self.style.SUCCESS('  ✅ ANALYZE terminé'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur ANALYZE: {e}'))
                
                # Vérifier l'intégrité
                self.stdout.write('🔍 Vérification de l\'intégrité...')
                try:
                    cursor.execute('PRAGMA integrity_check;')
                    result = cursor.fetchone()
                    if result[0] == 'ok':
                        self.stdout.write(self.style.SUCCESS('  ✅ Intégrité OK'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  ❌ Problème: {result[0]}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ❌ Erreur vérification: {e}'))
        
        # Optimisations PostgreSQL
        elif 'postgresql' in connection.settings_dict['ENGINE']:
            with connection.cursor() as cursor:
                if options['vacuum']:
                    self.stdout.write('🗜️  Exécution de VACUUM...')
                    try:
                        cursor.execute('VACUUM ANALYZE;')
                        self.stdout.write(self.style.SUCCESS('  ✅ VACUUM ANALYZE terminé'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur: {e}'))
                
                if options['analyze']:
                    self.stdout.write('📊 Analyse des statistiques...')
                    try:
                        cursor.execute('ANALYZE;')
                        self.stdout.write(self.style.SUCCESS('  ✅ ANALYZE terminé'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Erreur: {e}'))
        
        # Nettoyer les sessions expirées
        self.stdout.write('🧹 Nettoyage des sessions expirées...')
        from django.core.management import call_command
        try:
            call_command('clearsessions')
            self.stdout.write(self.style.SUCCESS('  ✅ Sessions nettoyées'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Erreur: {e}'))
        
        # Temps écoulé
        elapsed = time.time() - start_time
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Optimisation terminée en {elapsed:.2f} secondes!'
            )
        )
