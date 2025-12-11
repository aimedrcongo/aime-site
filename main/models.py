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
    
    # Préférences utilisateur
    newsletter_subscription = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    language_preference = models.CharField(max_length=10, default='fr', choices=[('fr', 'Français'), ('en', 'English')])
    
    # Statistiques personnelles
    total_donations = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    events_participated = models.IntegerField(default=0)
    challenges_completed = models.IntegerField(default=0)
    
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
    
    def calculate_level(self):
        """Calculer le niveau basé sur les points"""
        if self.points < 100:
            return 1
        elif self.points < 500:
            return 2
        elif self.points < 1000:
            return 3
        elif self.points < 2500:
            return 4
        else:
            return 5
    
    def add_points(self, points):
        """Ajouter des points et mettre à jour le niveau"""
        self.points += points
        self.level = self.calculate_level()
        self.save()

class Category(models.Model):
    """Catégories pour les projets et causes"""
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Pour les icônes CSS
    color = models.CharField(max_length=7, default='#007bff')  # Code couleur hex
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['is_active', 'name']),
        ]
    
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
    
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/', blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning', db_index=True)
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Métriques d'impact
    beneficiaries_count = models.IntegerField(default=0)
    volunteers_count = models.IntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']
    
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
    
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    max_attendees = models.IntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/', blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'date']),
            models.Index(fields=['event_type', 'is_active']),
            models.Index(fields=['-date']),
        ]
        ordering = ['-date']
    
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
    donor_email = models.EmailField(db_index=True)
    donor_phone = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='CDF')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=DONATION_STATUS, default='pending', db_index=True)
    transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['donor_email', 'status']),
            models.Index(fields=['project', 'status']),
        ]
        ordering = ['-created_at']
    
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
        ('event_participation', 'Participation événement'),
        ('challenge_completed', 'Défi terminé'),
        ('profile_updated', 'Profil mis à jour'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

class UserNotification(models.Model):
    """Notifications utilisateur"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('badge', 'Nouveau badge'),
        ('event', 'Événement'),
        ('donation', 'Don'),
        ('message', 'Message'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link_url = models.URLField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class EventParticipation(models.Model):
    """Participation aux événements"""
    PARTICIPATION_STATUS = [
        ('registered', 'Inscrit'),
        ('confirmed', 'Confirmé'),
        ('attended', 'Présent'),
        ('cancelled', 'Annulé'),
        ('no_show', 'Absent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS, default='registered')
    registration_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'event']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

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

# --- Chat Assistant Models ---
class ChatConversation(models.Model):
    """Session de conversation entre un utilisateur et le staff/l'assistant."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_conversations')
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return f"Conversation avec {self.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class ChatMessage(models.Model):
    """Message dans une conversation de chat."""
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_assistant = models.BooleanField(default=False, help_text="Message envoyé par l'assistant AI")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = self.sender.username if self.sender else ("Assistant" if self.is_assistant else "Inconnu")
        return f"{sender}: {self.content[:30]}... ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

# --- Contribution Staff ---
class StaffContribution(models.Model):
    """Contribution mensuelle ou ponctuelle d'un membre du staff."""
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_contributions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=20)  # ex: '2025-07' ou 'Juillet 2025'
    object = models.CharField(max_length=200, blank=True)  # Objet de la contribution
    is_recorded = models.BooleanField(default=False, help_text="Validée par le responsable caisse")
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_contributions')

    def __str__(self):
        return f"{self.staff.get_full_name()} - {self.amount} ({self.month})"

# --- Messagerie interne staff ---
class StaffInternalMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_staff_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_staff_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.sender.username} → {self.recipient.username})"

# --- Système de tickets utilisateur ---
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('in_progress', 'En cours'),
        ('closed', 'Fermé'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='closed_tickets')

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} ({self.get_status_display()})"

# --- Impact Social Centralisé ---
class ImpactPoint(models.Model):
    TYPE_CHOICES = [
        ('donation', 'Don'),
        ('event', 'Événement'),
        ('participation', 'Participation'),
        ('contribution', 'Contribution Staff'),
        ('project', 'Projet'),
        ('other', 'Autre'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    related_id = models.IntegerField(null=True, blank=True)  # ID de l'objet lié (don, event, etc.)
    related_model = models.CharField(max_length=50, blank=True)  # Nom du modèle lié
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # Montant, score, etc.
    status = models.CharField(max_length=30, blank=True)  # ex: 'completed', 'pending', 'active'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Impact {self.type} ({self.related_model} #{self.related_id})"


class VisitorFeedback(models.Model):
    """Avis et retours des visiteurs du site"""
    CONTRIBUTION_CHOICES = [
        ('ideas', 'Partager des idées'),
        ('member', 'Devenir membre'),
        ('volunteer', 'Participer aux activités'),
        ('donate', 'Faire un don'),
        ('partner', 'Devenir partenaire'),
        ('other', 'Autre'),
    ]
    
    # Informations du visiteur
    name = models.CharField(max_length=100, blank=True, verbose_name="Nom")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    
    # Avis et contribution
    opinion = models.TextField(verbose_name="Avis sur le site/projet")
    contribution_type = models.CharField(
        max_length=20, 
        choices=CONTRIBUTION_CHOICES,
        verbose_name="Type de contribution souhaitée"
    )
    contribution_details = models.TextField(blank=True, verbose_name="Détails de la contribution")
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_contacted = models.BooleanField(default=False, verbose_name="Contacté")
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, verbose_name="Notes internes")
    
    class Meta:
        verbose_name = "Avis visiteur"
        verbose_name_plural = "Avis visiteurs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Avis de {self.name or 'Anonyme'} - {self.created_at.strftime('%d/%m/%Y')}"


class DailyInformation(models.Model):
    """Article d'information pour la section "Information du Jour" sur la page d'accueil"""
    
    CATEGORY_CHOICES = [
        ('news', 'Actualité'),
        ('event', 'Événement'),
        ('announcement', 'Annonce'),
        ('success_story', 'Témoignage'),
        ('program', 'Programme'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre de l'article")
    content = models.TextField(verbose_name="Contenu de l'article")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='news',
        verbose_name="Catégorie"
    )
    featured_image = models.ImageField(
        upload_to='daily_info/', 
        blank=True, 
        null=True,
        verbose_name="Image (optionnelle)"
    )
    
    # Dates
    publication_date = models.DateField(auto_now_add=True, verbose_name="Date de publication")
    display_date = models.DateField(default=timezone.now, verbose_name="Date d'affichage")
    
    # Lien optionnel
    link_url = models.URLField(blank=True, null=True, verbose_name="Lien externe")
    link_text = models.CharField(max_length=100, blank=True, default="En savoir plus →", verbose_name="Texte du lien")
    
    # Métadonnées
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    is_featured = models.BooleanField(default=False, verbose_name="Épinglé (priorité d'affichage)")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    # Suivi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Information du Jour"
        verbose_name_plural = "Informations du Jour"
        ordering = ['-is_featured', '-display_date', '-order']
        indexes = [
            models.Index(fields=['is_published', 'display_date']),
            models.Index(fields=['is_featured', 'order']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.display_date.strftime('%d/%m/%Y')})"

