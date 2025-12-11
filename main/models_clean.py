from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class UserProfile(models.Model):
    """Profil utilisateur étendu"""
    ROLE_CHOICES = [
        ('member', 'Membre'),
        ('volunteer', 'Bénévole'),
        ('staff', 'Personnel'),
        ('partner', 'Partenaire'),
        ('donor', 'Donateur'),
        ('child', 'Enfant'),
        ('parent', 'Parent'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    profile_image = models.ImageField(upload_to='profiles/', blank=True)
    is_active_member = models.BooleanField(default=True)
    joined_date = models.DateTimeField(default=timezone.now)
    
    # Coordonnées pour la carte
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Gamification
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    badges = models.TextField(default='[]')  # JSON des badges obtenus
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    def add_badge(self, badge_name):
        """Ajouter un badge au profil"""
        badges_list = json.loads(self.badges) if self.badges else []
        if badge_name not in badges_list:
            badges_list.append(badge_name)
            self.badges = json.dumps(badges_list)
            self.save()
    
    def get_badges_list(self):
        """Récupérer la liste des badges"""
        return json.loads(self.badges) if self.badges else []

class Category(models.Model):
    """Catégories pour les projets et causes"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Pour les icônes CSS
    color = models.CharField(max_length=7, default='#007bff')  # Code couleur hex
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Project(models.Model):
    """Projets principaux d'AIME"""
    PROJECT_STATUS = [
        ('planning', 'En planification'),
        ('active', 'Actif'),
        ('completed', 'Terminé'),
        ('suspended', 'Suspendu'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/', blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning')
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Métriques d'impact
    beneficiaries_count = models.IntegerField(default=0)
    volunteers_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    @property
    def progress_percentage(self):
        if self.goal_amount and self.goal_amount > 0:
            return min((self.raised_amount / self.goal_amount) * 100, 100)
        return 0

class MutotoBikeChallenge(models.Model):
    """Événement Mutoto Bike Challenge"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=100)
    registration_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='mbc/', blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.date.strftime('%Y-%m-%d')}"
    
    @property
    def participants_count(self):
        return self.mbcparticipant_set.filter(status='confirmed').count()
    
    @property
    def is_full(self):
        return self.participants_count >= self.max_participants

class MBCParticipant(models.Model):
    """Participants au Mutoto Bike Challenge"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
    ]
    
    event = models.ForeignKey(MutotoBikeChallenge, on_delete=models.CASCADE)
    participant_name = models.CharField(max_length=100)
    participant_email = models.EmailField()
    participant_phone = models.CharField(max_length=20)
    age = models.IntegerField()
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    registered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.participant_name} - {self.event.name}"

class MutoScienceAdventure(models.Model):
    """Programme Muto Science Adventure"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    age_group = models.CharField(max_length=50)  # ex: "8-12 ans"
    duration = models.CharField(max_length=50)  # ex: "3 mois"
    start_date = models.DateField()
    end_date = models.DateField()
    max_participants = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    """Événements et activités"""
    EVENT_TYPES = [
        ('workshop', 'Atelier'),
        ('conference', 'Conférence'),
        ('competition', 'Compétition'),
        ('fundraising', 'Collecte de fonds'),
        ('volunteer', 'Bénévolat'),
        ('community', 'Communautaire'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    max_attendees = models.IntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Donation(models.Model):
    """Dons et contributions"""
    DONATION_STATUS = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    
    donor_name = models.CharField(max_length=100)
    donor_email = models.EmailField()
    donor_phone = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='CDF')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=DONATION_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency}"

class ContactMessage(models.Model):
    """Messages de contact"""
    MESSAGE_TYPES = [
        ('general', 'Général'),
        ('volunteer', 'Bénévolat'),
        ('partnership', 'Partenariat'),
        ('donation', 'Don'),
        ('complaint', 'Plainte'),
        ('suggestion', 'Suggestion'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class NewsletterSubscription(models.Model):
    """Abonnements à la newsletter"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class UserActivity(models.Model):
    """Activités des utilisateurs"""
    ACTIVITY_TYPES = [
        ('login', 'Connexion'),
        ('donation', 'Don'),
        ('registration', 'Inscription'),
        ('volunteer', 'Bénévolat'),
        ('badge_earned', 'Badge obtenu'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

class Staff(models.Model):
    """Personnel et équipe AIME"""
    POSITION_CHOICES = [
        ('director', 'Directeur'),
        ('coordinator', 'Coordinateur'),
        ('teacher', 'Enseignant'),
        ('volunteer_coordinator', 'Coordinateur Bénévoles'),
        ('finance', 'Finance'),
        ('communication', 'Communication'),
        ('field_worker', 'Agent de terrain'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    years_experience = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Staff"
        ordering = ['order', 'position']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_position_display()}"
