from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserActivity, UserNotification, StaffContribution, Donation, EventParticipation, ImpactPoint
# --- ImpactPoint sync: DONATION ---
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Donation)
def sync_impact_donation(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        ImpactPoint.objects.update_or_create(
            type='donation',
            related_id=instance.id,
            related_model='Donation',
            defaults={
                'latitude': None,
                'longitude': None,
                'description': instance.message or f"Don de {instance.donor_name}",
                'value': instance.amount,
                'status': instance.status,
            }
        )

# --- ImpactPoint sync: EVENT PARTICIPATION ---
@receiver(post_save, sender=EventParticipation)
def sync_impact_event_participation(sender, instance, created, **kwargs):
    if instance.status in ['confirmed', 'attended']:
        ImpactPoint.objects.update_or_create(
            type='participation',
            related_id=instance.id,
            related_model='EventParticipation',
            defaults={
                'latitude': None,
                'longitude': None,
                'description': f"Participation à {instance.event.title}",
                'value': None,
                'status': instance.status,
            }
        )

# --- ImpactPoint sync: STAFF CONTRIBUTION ---
@receiver(post_save, sender=StaffContribution)
def sync_impact_staff_contribution(sender, instance, created, **kwargs):
    if instance.is_recorded and instance.validated_at:
        ImpactPoint.objects.update_or_create(
            type='contribution',
            related_id=instance.id,
            related_model='StaffContribution',
            defaults={
                'latitude': None,
                'longitude': None,
                'description': instance.object or f"Contribution staff {instance.month}",
                'value': instance.amount,
                'status': 'completed',
            }
        )
# --- Notification automatique lors de la validation d'une contribution staff ---
@receiver(post_save, sender=StaffContribution)
def notify_staff_contribution(sender, instance, created, **kwargs):
    # On ne notifie que si la contribution vient d'être validée (is_recorded=True et validated_at non nul)
    if instance.is_recorded and instance.validated_at:
        # Notification pour le contributeur
        UserNotification.objects.get_or_create(
            user=instance.staff,
            title=f"Contribution enregistrée pour {instance.month}",
            message=f"Votre contribution de {instance.amount} CDF pour '{instance.object or 'cotisation'}' a été enregistrée. Merci !",
            notification_type='success',
        )
        # Notification pour le responsable caisse (si différent)
        if instance.validated_by and instance.validated_by != instance.staff:
            UserNotification.objects.get_or_create(
                user=instance.validated_by,
                title=f"Contribution staff validée",
                message=f"Vous avez validé la contribution de {instance.staff.get_full_name()} ({instance.amount} CDF, {instance.month}).",
                notification_type='info',
            )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil utilisateur lors de l'inscription"""
    if created:
        profile = UserProfile.objects.create(
            user=instance,
            role='member',
            points=50,  # Points de bienvenue
            level=1,
        )
        
        # Ajouter badge de bienvenue
        profile.add_badge('new_member')
        
        # Enregistrer l'activité
        UserActivity.objects.create(
            user=instance,
            activity_type='registration',
            description='Inscription sur la plateforme AIME'
        )
        
        # Notification de bienvenue
        UserNotification.objects.create(
            user=instance,
            title='Bienvenue chez AIME !',
            message=f'Bonjour {instance.first_name or instance.username}, merci de rejoindre notre communauté. Découvrez votre tableau de bord et nos projets.',
            notification_type='success'
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarder le profil utilisateur"""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
