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

class Location(models.Model):
    """Localisation géographique pour les projets et événements"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='République Démocratique du Congo')
    
    def __str__(self):
        return f"{self.name} - {self.city}"

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
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
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

class ImpactMetric(models.Model):
    """Métriques d'impact en temps réel"""
    METRIC_TYPES = [
        ('beneficiaries', 'Bénéficiaires'),
        ('volunteers', 'Bénévoles'),
        ('donations', 'Dons reçus'),
        ('events', 'Événements organisés'),
        ('participants', 'Participants'),
        ('meals', 'Repas distribués'),
        ('formations', 'Formations dispensées'),
        ('equipments', 'Équipements fournis'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.IntegerField()
    date_recorded = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.get_metric_type_display()}: {self.value}"

class SocialImpactPin(models.Model):
    """Points d'impact sur la carte interactive"""
    PIN_TYPES = [
        ('project', 'Projet'),
        ('event', 'Événement'),
        ('beneficiary', 'Bénéficiaire'),
        ('volunteer', 'Bénévole'),
        ('donation', 'Don'),
        ('achievement', 'Réalisation'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    pin_type = models.CharField(max_length=20, choices=PIN_TYPES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='impact_pins/', blank=True)
    impact_value = models.IntegerField(default=0)  # Valeur d'impact (nombre de bénéficiaires, montant, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Données pour l'animation temps réel
    is_new = models.BooleanField(default=True)  # Pour les animations de nouveaux points
    
    def __str__(self):
        return f"{self.title} - {self.location.name}"

class Testimonial(models.Model):
    """Témoignages des bénéficiaires"""
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=100)  # Parent, enfant, bénévole, etc.
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"

class Challenge(models.Model):
    """Défis gamifiés pour les utilisateurs"""
    CHALLENGE_TYPES = [
        ('participation', 'Participation'),
        ('donation', 'Don'),
        ('volunteer', 'Bénévolat'),
        ('referral', 'Parrainage'),
        ('learning', 'Apprentissage'),
        ('environmental', 'Environnemental'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    points_reward = models.IntegerField(default=0)
    badge_reward = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    target_value = models.IntegerField()  # Objectif à atteindre
    current_value = models.IntegerField(default=0)  # Progression actuelle
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(User, through='ChallengeParticipation')
    
    def __str__(self):
        return self.title
    
    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min((self.current_value / self.target_value) * 100, 100)
        return 0

class ChallengeParticipation(models.Model):
    """Participation aux défis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'challenge']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"

class LiveUpdate(models.Model):
    """Mises à jour en temps réel pour la carte"""
    UPDATE_TYPES = [
        ('new_donation', 'Nouveau don'),
        ('new_volunteer', 'Nouveau bénévole'),
        ('event_started', 'Événement commencé'),
        ('milestone_reached', 'Objectif atteint'),
        ('new_beneficiary', 'Nouveau bénéficiaire'),
        ('project_completed', 'Projet terminé'),
    ]
    
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)  # Valeur associée (montant, nombre, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    is_displayed = models.BooleanField(default=False)  # Pour éviter de ré-afficher
    
    def __str__(self):
        return f"{self.get_update_type_display()} - {self.title}"

class MutotoBikeChallenge(models.Model):
    """Modèle spécifique pour Mutoto Bike Challenge"""
    AGE_CATEGORIES = [
        ('3', '3 ans'),
        ('4', '4 ans'),
        ('5', '5 ans'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    EDITION_CHOICES = [
        ('noel', 'Vacances de Noël'),
        ('paques', 'Vacances de Pâques'),
        ('grandes', 'Grandes vacances'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    edition = models.CharField(max_length=20, choices=EDITION_CHOICES)
    year = models.IntegerField(default=timezone.now().year)
    date_event = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    max_participants = models.IntegerField(default=100)
    registration_deadline = models.DateField()
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['edition', 'year']
    
    def __str__(self):
        return f"MBC {self.edition} {self.year}"

class MBCParticipant(models.Model):
    """Participants au Mutoto Bike Challenge"""
    event = models.ForeignKey(MutotoBikeChallenge, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    age = models.CharField(max_length=1, choices=MutotoBikeChallenge.AGE_CATEGORIES)
    gender = models.CharField(max_length=1, choices=MutotoBikeChallenge.GENDER_CHOICES)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField()
    school = models.CharField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    medical_info = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    bib_number = models.IntegerField(null=True, blank=True)
    
    # Position et résultats
    finish_time = models.DurationField(null=True, blank=True)
    final_position = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.child_name} - {self.age} ans ({self.gender})"

class MutoScienceAdventure(models.Model):
    """Extension scientifique du MBC"""
    ACTIVITY_TYPES = [
        ('bulles', 'Bulles et air'),
        ('aimants', 'Les aimants'),
        ('couleurs', 'Couleurs en fête'),
        ('observation', "L'œil de l'explorateur"),
        ('equilibre', 'Équilibre naturel'),
    ]
    
    mbc_event = models.ForeignKey(MutotoBikeChallenge, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    age_min = models.IntegerField(default=3)
    age_max = models.IntegerField(default=6)
    materials_needed = models.TextField()
    duration_minutes = models.IntegerField(default=30)
    max_children = models.IntegerField(default=10)
    animator = models.CharField(max_length=100)
    is_girls_focus = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.mbc_event}"

class Event(models.Model):
    """Événements généraux d'AIME"""
    EVENT_TYPES = [
        ('fundraising', 'Collecte de fonds'),
        ('awareness', 'Sensibilisation'),
        ('training', 'Formation'),
        ('competition', 'Compétition'),
        ('meeting', 'Réunion'),
        ('other', 'Autre'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    max_attendees = models.IntegerField(null=True, blank=True)
    registration_required = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    image = models.ImageField(upload_to='events/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Métriques en temps réel
    current_attendees = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title

class Donation(models.Model):
    """Système de dons"""
    PAYMENT_METHODS = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
        ('paypal', 'PayPal'),
        ('cash', 'Espèces'),
        ('other', 'Autre'),
    ]
    
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=DONATION_STATUS, default='pending')
    is_anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Localisation du don
    donor_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.donor_name} - {self.amount} FC"

class ContactMessage(models.Model):
    """Messages de contact"""
    MESSAGE_TYPES = [
        ('general', 'Demande générale'),
        ('partnership', 'Partenariat'),
        ('volunteer', 'Bénévolat'),
        ('donation', 'Don'),
        ('mbc', 'Mutoto Bike Challenge'),
        ('complaint', 'Réclamation'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class NewsletterSubscription(models.Model):
    """Abonnements newsletter"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email

class UserActivity(models.Model):
    """Tracking des activités utilisateur"""
    ACTIVITY_TYPES = [
        ('login', 'Connexion'),
        ('donation', 'Don'),
        ('registration', 'Inscription événement'),
        ('message', 'Message envoyé'),
        ('profile_update', 'Mise à jour profil'),
        ('challenge_completed', 'Défi terminé'),
        ('badge_earned', 'Badge obtenu'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

class Staff(models.Model):
    """Personnel administratif d'AIME"""
    STAFF_POSITIONS = [
        ('coordinator', 'Coordonnateur National'),
        ('admin', 'Administrateur'),
        ('deputy', 'Coordonnateur Adjoint'),
        ('doctor', 'Médecin'),
        ('lawyer', 'Avocat'),
        ('psychologist', 'Psychologue'),
        ('educator', 'Éducateur'),
        ('trainer', 'Entraîneur'),
        ('logistics', 'Logistique'),
        ('security', 'Sécurité'),
        ('finance', 'Financier'),
        ('event', 'Chargé événementiel'),
        ('eco', 'Responsable écologique'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=20, choices=STAFF_POSITIONS)
    department = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='staff/', blank=True)
    hire_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_position_display()}"

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
    location = models.CharField(max_length=200, blank=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def progress_percentage(self):
        if self.goal_amount and self.goal_amount > 0:
            return min((self.raised_amount / self.goal_amount) * 100, 100)
        return 0

class MutotoBikeChallenge(models.Model):
    """Modèle spécifique pour Mutoto Bike Challenge"""
    AGE_CATEGORIES = [
        ('3', '3 ans'),
        ('4', '4 ans'),
        ('5', '5 ans'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    EDITION_CHOICES = [
        ('noel', 'Vacances de Noël'),
        ('paques', 'Vacances de Pâques'),
        ('grandes', 'Grandes vacances'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    edition = models.CharField(max_length=20, choices=EDITION_CHOICES)
    year = models.IntegerField(default=timezone.now().year)
    date_event = models.DateField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=100)
    registration_deadline = models.DateField()
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['edition', 'year']
    
    def __str__(self):
        return f"MBC {self.edition} {self.year}"

class MBCParticipant(models.Model):
    """Participants au Mutoto Bike Challenge"""
    event = models.ForeignKey(MutotoBikeChallenge, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100)
    age = models.CharField(max_length=1, choices=MutotoBikeChallenge.AGE_CATEGORIES)
    gender = models.CharField(max_length=1, choices=MutotoBikeChallenge.GENDER_CHOICES)
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField()
    school = models.CharField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    medical_info = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    bib_number = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.child_name} - {self.age} ans ({self.gender})"

class MutoScienceAdventure(models.Model):
    """Extension scientifique du MBC"""
    ACTIVITY_TYPES = [
        ('bulles', 'Bulles et air'),
        ('aimants', 'Les aimants'),
        ('couleurs', 'Couleurs en fête'),
        ('observation', "L'œil de l'explorateur"),
        ('equilibre', 'Équilibre naturel'),
    ]
    
    mbc_event = models.ForeignKey(MutotoBikeChallenge, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    age_min = models.IntegerField(default=3)
    age_max = models.IntegerField(default=6)
    materials_needed = models.TextField()
    duration_minutes = models.IntegerField(default=30)
    max_children = models.IntegerField(default=10)
    animator = models.CharField(max_length=100)
    is_girls_focus = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.mbc_event}"

class Event(models.Model):
    """Événements généraux d'AIME"""
    EVENT_TYPES = [
        ('fundraising', 'Collecte de fonds'),
        ('awareness', 'Sensibilisation'),
        ('training', 'Formation'),
        ('competition', 'Compétition'),
        ('meeting', 'Réunion'),
        ('other', 'Autre'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    max_attendees = models.IntegerField(null=True, blank=True)
    registration_required = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    image = models.ImageField(upload_to='events/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Donation(models.Model):
    """Système de dons"""
    PAYMENT_METHODS = [
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Virement bancaire'),
        ('paypal', 'PayPal'),
        ('cash', 'Espèces'),
        ('other', 'Autre'),
    ]
    
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=DONATION_STATUS, default='pending')
    is_anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.donor_name} - {self.amount} FC"

class ContactMessage(models.Model):
    """Messages de contact"""
    MESSAGE_TYPES = [
        ('general', 'Demande générale'),
        ('partnership', 'Partenariat'),
        ('volunteer', 'Bénévolat'),
        ('donation', 'Don'),
        ('mbc', 'Mutoto Bike Challenge'),
        ('complaint', 'Réclamation'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='general')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class NewsletterSubscription(models.Model):
    """Abonnements newsletter"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email

class UserActivity(models.Model):
    """Tracking des activités utilisateur"""
    ACTIVITY_TYPES = [
        ('login', 'Connexion'),
        ('donation', 'Don'),
        ('registration', 'Inscription événement'),
        ('message', 'Message envoyé'),
        ('profile_update', 'Mise à jour profil'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

class Staff(models.Model):
    """Personnel administratif d'AIME"""
    STAFF_POSITIONS = [
        ('coordinator', 'Coordonnateur National'),
        ('admin', 'Administrateur'),
        ('deputy', 'Coordonnateur Adjoint'),
        ('doctor', 'Médecin'),
        ('lawyer', 'Avocat'),
        ('psychologist', 'Psychologue'),
        ('educator', 'Éducateur'),
        ('trainer', 'Entraîneur'),
        ('logistics', 'Logistique'),
        ('security', 'Sécurité'),
        ('finance', 'Financier'),
        ('event', 'Chargé événementiel'),
        ('eco', 'Responsable écologique'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=20, choices=STAFF_POSITIONS)
    department = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='staff/', blank=True)
    hire_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_position_display()}"
