from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from .models import (
    UserProfile, Donation, Event, EventParticipation, 
    MutotoBikeChallenge, MBCParticipant, UserNotification, 
    UserActivity, Project, ChatConversation, ChatMessage
)
from .forms import UserProfileForm
import json

from django.contrib.auth.decorators import user_passes_test

# --- DASHBOARD CHAT VIEWS ---
def is_staff_or_superuser(user):
    return user.is_superuser or user.is_staff or (hasattr(user, 'userprofile') and user.userprofile.role == 'staff')

@login_required
@user_passes_test(is_staff_or_superuser)
def dashboard_chat_conversations(request):
    """Vue staff/admin : liste et accès à toutes les conversations du chat assistant."""
    conversations = ChatConversation.objects.all().order_by('-created_at')
    context = {
        'conversations': conversations,
    }
    return render(request, 'main/dashboard/chat_conversations.html', context)

@login_required
def dashboard_my_conversations(request):
    """Vue utilisateur : liste et accès à ses propres conversations de chat assistant."""
    conversations = ChatConversation.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'conversations': conversations,
    }
    return render(request, 'main/dashboard/my_conversations.html', context)
from .forms import UserProfileForm
import json

@login_required
def dashboard_home(request):
    """Page principale du tableau de bord"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Statistiques utilisateur
    total_donations = Donation.objects.filter(donor_email=user.email).aggregate(
        total=Sum('amount'), count=Count('id')
    )
    
    events_participated = EventParticipation.objects.filter(
        user=user, status__in=['confirmed', 'attended']
    ).count()
    
    challenges_completed = MBCParticipant.objects.filter(
        participant_email=user.email, status='confirmed'
    ).count()
    
    # Activités récentes
    recent_activities = UserActivity.objects.filter(user=user)[:10]
    
    # Notifications non lues
    unread_notifications = UserNotification.objects.filter(
        user=user, is_read=False
    ).count()
    
    # Prochains événements
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).order_by('date')[:5]
    
    # Challenges actifs
    active_challenges = MutotoBikeChallenge.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:3]
    
    # Classement utilisateur (basé sur les points)
    user_ranking = UserProfile.objects.filter(
        points__gt=profile.points
    ).count() + 1
    
    context = {
        'profile': profile,
        'total_donations': total_donations,
        'events_participated': events_participated,
        'challenges_completed': challenges_completed,
        'recent_activities': recent_activities,
        'unread_notifications': unread_notifications,
        'upcoming_events': upcoming_events,
        'active_challenges': active_challenges,
        'user_ranking': user_ranking,
    }
    
    return render(request, 'main/dashboard/home.html', context)

@login_required
def dashboard_profile(request):
    """Gestion du profil utilisateur"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Enregistrer l'activité
            UserActivity.objects.create(
                user=request.user,
                activity_type='profile_updated',
                description='Profil mis à jour'
            )
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('main:dashboard_profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'main/dashboard/profile.html', context)

@login_required
def dashboard_donations(request):
    """Historique des donations"""
    donations = Donation.objects.filter(donor_email=request.user.email).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(donations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_donated = donations.aggregate(total=Sum('amount'))['total'] or 0
    donation_count = donations.count()
    
    context = {
        'page_obj': page_obj,
        'total_donated': total_donated,
        'donation_count': donation_count,
    }
    
    return render(request, 'main/dashboard/donations.html', context)

@login_required
def dashboard_events(request):
    """Événements et participations"""
    # Participations utilisateur
    participations = EventParticipation.objects.filter(user=request.user).order_by('-registration_date')
    
    # Challenges MBC
    mbc_participations = MBCParticipant.objects.filter(participant_email=request.user.email).order_by('-registered_at')
    
    # Événements disponibles
    available_events = Event.objects.filter(
        date__gte=timezone.now(),
        is_active=True
    ).exclude(
        id__in=participations.values_list('event_id', flat=True)
    ).order_by('date')
    
    context = {
        'participations': participations,
        'mbc_participations': mbc_participations,
        'available_events': available_events,
    }
    
    return render(request, 'main/dashboard/events.html', context)

@login_required
def dashboard_notifications(request):
    """Centre de notifications"""
    notifications = UserNotification.objects.filter(user=request.user)
    
    # Marquer comme lues si demandé
    if request.GET.get('mark_read'):
        notifications.filter(is_read=False).update(is_read=True)
        return redirect('main:dashboard_notifications')
    
    # Pagination
    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    
    return render(request, 'main/dashboard/notifications.html', context)

@login_required
def dashboard_badges(request):
    """Badges et classements"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Badges disponibles
    available_badges = {
        'first_donation': {
            'name': 'Premier Don',
            'description': 'Effectué votre premier don',
            'icon': 'fas fa-heart',
            'color': 'text-danger'
        },
        'generous_donor': {
            'name': 'Donateur Généreux',
            'description': 'Plus de 5 donations',
            'icon': 'fas fa-hand-holding-heart',
            'color': 'text-success'
        },
        'event_participant': {
            'name': 'Participant Actif',
            'description': 'Participé à un événement',
            'icon': 'fas fa-calendar-check',
            'color': 'text-primary'
        },
        'bike_challenger': {
            'name': 'Cycliste AIME',
            'description': 'Participé au Mutoto Bike Challenge',
            'icon': 'fas fa-bicycle',
            'color': 'text-warning'
        },
        'volunteer': {
            'name': 'Bénévole',
            'description': 'Inscrit comme bénévole',
            'icon': 'fas fa-hands-helping',
            'color': 'text-info'
        },
        'level_5': {
            'name': 'Expert AIME',
            'description': 'Atteint le niveau 5',
            'icon': 'fas fa-star',
            'color': 'text-warning'
        }
    }
    
    user_badges = profile.get_badges_list()
    
    # Classement général
    leaderboard = UserProfile.objects.filter(
        points__gt=0
    ).order_by('-points')[:10]
    
    # Position de l'utilisateur
    user_position = UserProfile.objects.filter(
        points__gt=profile.points
    ).count() + 1
    
    context = {
        'profile': profile,
        'available_badges': available_badges,
        'user_badges': user_badges,
        'leaderboard': leaderboard,
        'user_position': user_position,
    }
    
    return render(request, 'main/dashboard/badges.html', context)

@login_required
def dashboard_settings(request):
    """Paramètres et préférences"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_preferences':
            # Mise à jour des préférences
            profile.newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
            profile.email_notifications = request.POST.get('email_notifications') == 'on'
            profile.sms_notifications = request.POST.get('sms_notifications') == 'on'
            profile.language_preference = request.POST.get('language_preference', 'fr')
            profile.save()
            messages.success(request, 'Préférences mises à jour!')
            
        elif action == 'change_password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Mot de passe modifié avec succès!')
            else:
                for error in form.errors.values():
                    messages.error(request, error)
        
        return redirect('main:dashboard_settings')
    
    password_form = PasswordChangeForm(request.user)
    
    context = {
        'profile': profile,
        'password_form': password_form,
    }
    
    return render(request, 'main/dashboard/settings.html', context)

@login_required
def dashboard_activities(request):
    """Historique des activités"""
    activities = UserActivity.objects.filter(user=request.user)
    
    # Filtrage par type d'activité
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    # Pagination
    paginator = Paginator(activities, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Types d'activités pour le filtre
    activity_types = UserActivity.ACTIVITY_TYPES
    
    context = {
        'page_obj': page_obj,
        'activity_types': activity_types,
        'current_filter': activity_type,
    }
    
    return render(request, 'main/dashboard/activities.html', context)

@login_required
def join_event(request, event_id):
    """Inscription à un événement"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id, is_active=True)
        
        participation, created = EventParticipation.objects.get_or_create(
            user=request.user,
            event=event,
            defaults={'status': 'registered'}
        )
        
        if created:
            # Ajouter des points
            profile = request.user.userprofile
            profile.add_points(50)
            
            # Enregistrer l'activité
            UserActivity.objects.create(
                user=request.user,
                activity_type='registration',
                description=f'Inscription à l\'événement: {event.name}'
            )
            
            # Notification
            UserNotification.objects.create(
                user=request.user,
                title='Inscription confirmée',
                message=f'Vous êtes inscrit à l\'événement "{event.name}"',
                notification_type='success'
            )
            
            messages.success(request, f'Inscription à "{event.name}" confirmée!')
        else:
            messages.info(request, 'Vous êtes déjà inscrit à cet événement.')
    
    return redirect('main:dashboard_events')

@login_required
def join_challenge(request, challenge_id):
    """Inscription à un challenge MBC"""
    if request.method == 'POST':
        challenge = get_object_or_404(MutotoBikeChallenge, id=challenge_id, is_active=True)
        
        # Vérifier si déjà inscrit
        existing = MBCParticipant.objects.filter(
            event=challenge,
            participant_email=request.user.email
        ).first()
        
        if not existing:
            # Créer nouvelle participation
            participation = MBCParticipant.objects.create(
                event=challenge,
                participant_name=request.user.get_full_name() or request.user.username,
                participant_email=request.user.email,
                participant_phone=getattr(request.user.userprofile, 'phone', ''),
                age=25,  # Valeur par défaut
                emergency_contact='Contact d\'urgence',
                emergency_phone='000000000',
                status='pending'
            )
            
            # Ajouter des points et badge
            profile = request.user.userprofile
            profile.add_points(100)
            profile.add_badge('bike_challenger')
            
            # Enregistrer l'activité
            UserActivity.objects.create(
                user=request.user,
                activity_type='registration',
                description=f'Inscription au Mutoto Bike Challenge: {challenge.name}'
            )
            
            # Notification
            UserNotification.objects.create(
                user=request.user,
                title='Challenge MBC',
                message=f'Inscription au challenge "{challenge.name}" confirmée!',
                notification_type='success'
            )
            
            messages.success(request, f'Inscription au challenge "{challenge.name}" confirmée!')
        else:
            messages.info(request, 'Vous êtes déjà inscrit à ce challenge.')
    
    return redirect('main:dashboard_events')

@login_required
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    if request.method == 'POST':
        notification = get_object_or_404(
            UserNotification, 
            id=notification_id, 
            user=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})
