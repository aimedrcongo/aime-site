from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from main.models import *

class Command(BaseCommand):
    help = 'Créer des données d\'exemple pour AIME'

    def handle(self, *args, **options):
        self.stdout.write('Création des données d\'exemple...')
        
        # Créer des catégories
        categories = [
            {'name': 'Éducation', 'description': 'Projets éducatifs'},
            {'name': 'Sport', 'description': 'Activités sportives'},
            {'name': 'Formation', 'description': 'Formations professionnelles'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(**cat_data)
            if created:
                self.stdout.write(f'Catégorie créée: {category.name}')
        
        # Créer des projets
        education_cat = Category.objects.get(name='Éducation')
        sport_cat = Category.objects.get(name='Sport')
        
        projects_data = [
            {
                'name': 'École Numérique AIME',
                'description': 'Formation informatique pour les jeunes de Kinshasa',
                'category': education_cat,
                'goal_amount': 50000,
                'status': 'active',
                'start_date': timezone.now().date(),
                'is_featured': True
            },
            {
                'name': 'Atelier de Mécanique Vélo',
                'description': 'Apprendre la réparation de vélos pour créer des emplois',
                'category': sport_cat,
                'goal_amount': 25000,
                'status': 'active',
                'start_date': timezone.now().date(),
                'is_featured': True
            },
        ]
        
        for proj_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=proj_data['name'], 
                defaults=proj_data
            )
            if created:
                self.stdout.write(f'Projet créé: {project.name}')
        
        # Créer des événements MBC
        mbc_data = [
            {
                'name': 'Mutoto Bike Challenge 2025',
                'description': 'Grand défi cycliste pour sensibiliser à l\'environnement',
                'date': timezone.now().date() + timedelta(days=30),
                'location': 'Parc de la Vallée de la Nsele, Kinshasa',
                'max_participants': 100,
                'registration_fee': 5000,
                'is_active': True
            }
        ]
        
        for mbc in mbc_data:
            event, created = MutotoBikeChallenge.objects.get_or_create(**mbc)
            if created:
                self.stdout.write(f'Événement MBC créé: {event.name}')
        
        # Créer des événements généraux
        events_data = [
            {
                'title': 'Journée Portes Ouvertes AIME',
                'description': 'Découvrez nos programmes et activités',
                'date': timezone.now().date() + timedelta(days=15),
                'location': 'Siège AIME, Kinshasa',
                'max_participants': 200,
                'is_active': True
            },
            {
                'title': 'Formation Entrepreneuriat Jeunes',
                'description': 'Atelier de formation à l\'entrepreneuriat',
                'date': timezone.now().date() + timedelta(days=45),
                'location': 'Centre AIME, Kinshasa',
                'max_participants': 50,
                'is_active': True
            }
        ]
        
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data
            )
            if created:
                self.stdout.write(f'Événement créé: {event.title}')
        
        # Créer du staff
        staff_data = [
            {
                'name': 'Dr. Marie Mulamba',
                'position': 'Directrice Générale',
                'bio': 'Experte en développement communautaire avec plus de 15 ans d\'expérience',
                'email': 'marie.mulamba@aime-rdc.org',
                'is_active': True
            },
            {
                'name': 'Jean-Baptiste Kalonji',
                'position': 'Coordinateur des Programmes',
                'bio': 'Spécialiste en éducation et formation professionnelle',
                'email': 'jb.kalonji@aime-rdc.org',
                'is_active': True
            }
        ]
        
        for staff in staff_data:
            member, created = Staff.objects.get_or_create(
                name=staff['name'],
                defaults=staff
            )
            if created:
                self.stdout.write(f'Membre du staff créé: {member.name}')
        
        self.stdout.write(self.style.SUCCESS('Données d\'exemple créées avec succès!'))
