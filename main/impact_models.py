"""
Modèles pour la carte interactive d'impact social
Fichier séparé pour éviter les conflits de migration
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Location(models.Model):
    """Modèle pour les localisations géographiques"""
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, default='Kinshasa')
    province = models.CharField(max_length=50, default='Kinshasa')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'main_location'
    
    def __str__(self):
        return f"{self.name} ({self.city})"

class ImpactPoint(models.Model):
    """Points d'impact pour la carte interactive"""
    IMPACT_TYPES = [
        ('event', 'Événement'),
        ('project', 'Projet'),
        ('donation', 'Don'),
        ('volunteer', 'Bénévolat'),
        ('education', 'Éducation'),
        ('health', 'Santé'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    impact_type = models.CharField(max_length=20, choices=IMPACT_TYPES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    impact_value = models.IntegerField(default=1)  # Nombre de bénéficiaires ou mesure d'impact
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Données supplémentaires pour l'affichage
    category = models.CharField(max_length=50, blank=True)
    beneficiaries_count = models.IntegerField(default=0)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'main_impact_point'
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.title} ({self.impact_type})"

class UserImpactProfile(models.Model):
    """Profil d'impact pour la gamification"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    impact_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    badges = models.JSONField(default=list)
    total_donations = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    events_attended = models.IntegerField(default=0)
    volunteer_hours = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'main_user_impact_profile'
    
    def __str__(self):
        return f"Profil impact de {self.user.username}"
    
    def add_impact_points(self, points):
        """Ajouter des points d'impact et vérifier les montées de niveau"""
        self.impact_points += points
        new_level = (self.impact_points // 100) + 1
        if new_level > self.level:
            self.level = new_level
            # Ajouter un badge de niveau
            if f"Niveau {new_level}" not in self.badges:
                self.badges.append(f"Niveau {new_level}")
        self.save()

class LiveUpdate(models.Model):
    """Mises à jour en temps réel pour la carte"""
    title = models.CharField(max_length=200)
    message = models.TextField()
    impact_point = models.ForeignKey(ImpactPoint, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_displayed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'main_live_update'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Update: {self.title}"

class Challenge(models.Model):
    """Défis communautaires pour la gamification"""
    CHALLENGE_TYPES = [
        ('donation', 'Défi de don'),
        ('participation', 'Défi de participation'),
        ('volunteer', 'Défi bénévolat'),
        ('education', 'Défi éducation'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    target_value = models.IntegerField()  # Objectif à atteindre
    current_value = models.IntegerField(default=0)  # Valeur actuelle
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reward_points = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'main_challenge'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)
