from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from main.models import (
    UserProfile, Donation, Project, Category, Event, 
    MBCParticipant, MutotoBikeChallenge, EventParticipation,
    StaffContribution, ImpactPoint
)

class Command(BaseCommand):
    help = 'Met à jour les données d\'exemple pour les statistiques dynamiques'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Réinitialise toutes les données avant de créer de nouvelles',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Réinitialisation des données...')
            Donation.objects.all().delete()
            EventParticipation.objects.all().delete()
            StaffContribution.objects.all().delete()
            ImpactPoint.objects.all().delete()

        self.stdout.write('Création des données d\'exemple...')

        # 1. Créer des donations pour avoir des FC collectés
        if not Donation.objects.exists():
            for i in range(50):
                Donation.objects.create(
                    donor_name=f'Donateur {i+1}',
                    donor_email=f'donateur{i+1}@exemple.com',
                    amount=random.randint(5000, 50000),  # 5,000 à 50,000 FC
                    currency='CDF',
                    status='completed',
                    created_at=timezone.now() - timedelta(days=random.randint(1, 365))
                )
            self.stdout.write(f'✓ {Donation.objects.count()} donations créées')

        # 2. Créer des profils utilisateurs pour les enfants et familles
        if UserProfile.objects.filter(role='child').count() < 10:
            for i in range(30):
                try:
                    user = User.objects.create_user(
                        username=f'enfant_{i+1}',
                        email=f'enfant{i+1}@exemple.com',
                        first_name=f'Enfant',
                        last_name=f'{i+1}'
                    )
                    UserProfile.objects.create(
                        user=user,
                        role='child',
                        date_of_birth=timezone.now().date() - timedelta(days=random.randint(2555, 5110)),  # 7-14 ans
                        latitude=-4.3317 + random.uniform(-0.1, 0.1),  # Autour de Kinshasa
                        longitude=15.3139 + random.uniform(-0.1, 0.1),
                        points=random.randint(0, 500)
                    )
                except:
                    pass
            self.stdout.write(f'✓ {UserProfile.objects.filter(role="child").count()} profils d\'enfants')

        # 3. Créer des profils pour les parents/familles
        if UserProfile.objects.filter(role='parent').count() < 5:
            for i in range(20):
                try:
                    user = User.objects.create_user(
                        username=f'parent_{i+1}',
                        email=f'parent{i+1}@exemple.com',
                        first_name=f'Parent',
                        last_name=f'{i+1}'
                    )
                    UserProfile.objects.create(
                        user=user,
                        role='parent',
                        latitude=-4.3317 + random.uniform(-0.1, 0.1),
                        longitude=15.3139 + random.uniform(-0.1, 0.1),
                        points=random.randint(0, 200)
                    )
                except:
                    pass
            self.stdout.write(f'✓ {UserProfile.objects.filter(role="parent").count()} profils de parents')

        # 4. Créer des événements de formation
        if Event.objects.filter(event_type='workshop').count() < 5:
            for i in range(15):
                Event.objects.create(
                    title=f'Formation {i+1} - {"Informatique" if i%3==0 else "Mécanique vélo" if i%3==1 else "Entrepreneuriat"}',
                    slug=f'formation-{i+1}',
                    description=f'Description de la formation {i+1}',
                    event_type='workshop',
                    date=timezone.now() + timedelta(days=random.randint(-180, 180)),
                    location=f'Centre {i+1}, Kinshasa',
                    organizer_id=1,  # Supposant qu'il y a un utilisateur avec id=1
                    max_attendees=random.randint(20, 50),
                    is_active=True
                )
            self.stdout.write(f'✓ {Event.objects.filter(event_type="workshop").count()} formations créées')

        # 5. Créer des événements MBC et participants
        if not MutotoBikeChallenge.objects.exists():
            for i in range(5):
                mbc = MutotoBikeChallenge.objects.create(
                    name=f'Mutoto Bike Challenge {2024+i}',
                    slug=f'mbc-{2024+i}',
                    description=f'Édition {2024+i} du Mutoto Bike Challenge',
                    date=timezone.now() + timedelta(days=random.randint(-90, 180)),
                    location=f'Site {i+1}, Kinshasa',
                    max_participants=100,
                    registration_fee=5000,
                    is_active=True
                )
                
                # Ajouter des participants
                for j in range(random.randint(30, 80)):
                    MBCParticipant.objects.create(
                        event=mbc,
                        participant_name=f'Participant {j+1}',
                        participant_email=f'participant{j+1}@exemple.com',
                        participant_phone=f'+243{random.randint(800000000, 999999999)}',
                        age=random.randint(8, 16),
                        emergency_contact=f'Contact {j+1}',
                        emergency_phone=f'+243{random.randint(800000000, 999999999)}',
                        status='confirmed'
                    )
            
            self.stdout.write(f'✓ {MBCParticipant.objects.filter(status="confirmed").count()} participants MBC confirmés')

        # 6. Créer des projets actifs
        if Project.objects.filter(status='active').count() < 3:
            # Créer une catégorie si elle n'existe pas
            if not Category.objects.exists():
                Category.objects.create(
                    name='Éducation',
                    description='Projets éducatifs',
                    color='#007bff'
                )
            
            category = Category.objects.first()
            for i in range(5):
                Project.objects.create(
                    name=f'Projet Impact {i+1}',
                    slug=f'projet-impact-{i+1}',
                    description=f'Description du projet d\'impact {i+1}',
                    category=category,
                    goal_amount=random.randint(100000, 500000),
                    raised_amount=random.randint(10000, 200000),
                    start_date=timezone.now().date() - timedelta(days=random.randint(1, 180)),
                    status='active',
                    beneficiaries_count=random.randint(20, 100),
                    volunteers_count=random.randint(5, 20),
                    is_featured=i < 3
                )
            self.stdout.write(f'✓ {Project.objects.filter(status="active").count()} projets actifs')

        # 7. Créer des points d'impact géographiques
        if ImpactPoint.objects.count() < 10:
            for i in range(25):
                ImpactPoint.objects.create(
                    type=random.choice(['donation', 'event', 'participation', 'project']),
                    related_id=random.randint(1, 10),
                    related_model='Project',
                    latitude=-4.3317 + random.uniform(-0.2, 0.2),
                    longitude=15.3139 + random.uniform(-0.2, 0.2),
                    description=f'Point d\'impact {i+1}',
                    value=random.randint(1000, 50000),
                    status='active'
                )
            self.stdout.write(f'✓ {ImpactPoint.objects.count()} points d\'impact créés')

        # 8. Créer des contributions du staff
        staff_users = User.objects.filter(is_staff=True)
        if staff_users.exists() and StaffContribution.objects.count() < 5:
            for i in range(12):  # 12 mois de contributions
                for staff in staff_users[:3]:  # 3 membres du staff
                    StaffContribution.objects.create(
                        staff=staff,
                        amount=random.randint(10000, 30000),
                        month=f'2024-{i+1:02d}',
                        object=f'Contribution mensuelle {i+1}/2024',
                        is_recorded=True,
                        validated_by=staff_users.first() if staff_users.count() > 1 else None
                    )
            self.stdout.write(f'✓ {StaffContribution.objects.count()} contributions du staff')

        self.stdout.write(
            self.style.SUCCESS('✅ Données d\'exemple créées avec succès!')
        )
        
        # Afficher un résumé des statistiques
        from main.utils import get_site_statistics
        stats = get_site_statistics()
        
        self.stdout.write('\n📊 RÉSUMÉ DES STATISTIQUES:')
        self.stdout.write(f'💰 FC collectés: {stats["total_donations"]:,} FC')
        self.stdout.write(f'👶 Enfants aidés: {stats["total_children_helped"]}')
        self.stdout.write(f'🚀 Projets actifs: {stats["active_projects"]}')
        self.stdout.write(f'📅 Événements totaux: {stats["total_events"]}')
        self.stdout.write(f'🎓 Formations dispensées: {stats["formations_dispensed"]}')
        self.stdout.write(f'👨‍👩‍👧‍👦 Familles soutenues: {stats["families_supported"]}')
        self.stdout.write(f'🚴 Participants MBC: {stats["mbc_participants"]}')
        self.stdout.write(f'🏘️ Quartiers impactés: {stats["quartiers_impacted"]}')
