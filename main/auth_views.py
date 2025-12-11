from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, UserActivity, UserNotification

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['username'].widget.attrs['placeholder'] = 'Nom d\'utilisateur'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Prénom'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Nom'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Mot de passe'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirmer le mot de passe'

def signup_view(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Créer le profil utilisateur
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'member',
                    'points': 50,  # Points de bienvenue
                    'level': 1,
                }
            )
            
            # Ajouter badge de bienvenue
            profile.add_badge('new_member')
            
            # Enregistrer l'activité
            UserActivity.objects.create(
                user=user,
                activity_type='registration',
                description='Inscription sur la plateforme AIME'
            )
            
            # Notification de bienvenue
            UserNotification.objects.create(
                user=user,
                title='Bienvenue chez AIME !',
                message='Merci de rejoindre notre communauté. Découvrez votre tableau de bord et nos projets.',
                notification_type='success'
            )
            
            # Connexion automatique
            login(request, user)
            messages.success(request, 'Compte créé avec succès ! Bienvenue chez AIME.')
            return redirect('main:dashboard_home')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})


def logout_view(request):
    """Vue de déconnexion personnalisée"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('main:home')

