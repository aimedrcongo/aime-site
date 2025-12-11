from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from .models import (
    ContactMessage, NewsletterSubscription, MBCParticipant, 
    Donation, MutotoBikeChallenge, UserProfile, VisitorFeedback
)

class UserProfileForm(forms.ModelForm):
    """Formulaire de profil utilisateur"""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address', 'date_of_birth', 'role', 'profile_image',
            'newsletter_subscription', 'email_notifications', 'sms_notifications',
            'language_preference'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'language_preference': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Sauvegarder les données de l'utilisateur
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile

class ContactForm(forms.ModelForm):
    """Formulaire de contact"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243 XXX XXX XXX'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet de votre message'
            }),
            'message_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre message...'
            }),
        }

class NewsletterForm(forms.ModelForm):
    """Formulaire d'abonnement newsletter"""
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre email'
            }),
        }

class MBCRegistrationForm(forms.ModelForm):
    """Formulaire d'inscription au Mutoto Bike Challenge"""
    
    phone_validator = RegexValidator(
        regex=r'^\+?243?[0-9]{9,10}$',
        message="Numéro de téléphone invalide. Format: +243XXXXXXXXX"
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        label="J'accepte les conditions de participation"
    )
    
    class Meta:
        model = MBCParticipant
        fields = [
            'participant_name', 'participant_email', 'participant_phone', 'age', 
            'parent_name', 'parent_phone', 'emergency_contact', 'emergency_phone'
        ]
        widgets = {
            'participant_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet du participant'
            }),
            'participant_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'participant_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243 XXX XXX XXX'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 8,
                'max': 18
            }),
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet du parent/tuteur'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243 XXX XXX XXX'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact d\'urgence'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243 XXX XXX XXX'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participant_phone'].validators = [self.phone_validator]
        self.fields['parent_phone'].validators = [self.phone_validator]
        self.fields['emergency_phone'].validators = [self.phone_validator]

class DonationForm(forms.ModelForm):
    """Formulaire de don"""
    
    AMOUNT_CHOICES = [
        ('5000', '5 000 FC'),
        ('10000', '10 000 FC'),
        ('25000', '25 000 FC'),
        ('50000', '50 000 FC'),
        ('100000', '100 000 FC'),
        ('custom', 'Montant personnalisé'),
    ]
    
    amount_choice = forms.ChoiceField(
        choices=AMOUNT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'amount-choice'}),
        required=False,
        label="Montant suggéré"
    )
    
    custom_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Montant en FC',
            'min': '1000'
        }),
        label="Montant personnalisé (FC)"
    )
    
    class Meta:
        model = Donation
        fields = [
            'donor_name', 'donor_email', 'donor_phone', 'project',
            'amount', 'is_anonymous', 'message'
        ]
        widgets = {
            'donor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'donor_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com'
            }),
            'donor_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243 XXX XXX XXX'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Montant en FC',
                'min': '1000'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Message d\'encouragement (optionnel)'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        amount_choice = cleaned_data.get('amount_choice')
        custom_amount = cleaned_data.get('custom_amount')
        amount = cleaned_data.get('amount')
        
        if amount_choice == 'custom':
            if not custom_amount:
                raise forms.ValidationError("Veuillez spécifier un montant personnalisé.")
            cleaned_data['amount'] = custom_amount
        elif amount_choice and amount_choice != 'custom':
            cleaned_data['amount'] = int(amount_choice)
        
        return cleaned_data

class EventRegistrationForm(forms.Form):
    """Formulaire d'inscription aux événements"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom complet'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@email.com'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+243 XXX XXX XXX'
        })
    )
    organization = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Organisation (optionnel)'
        })
    )
    dietary_requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Régimes alimentaires spéciaux ou allergies'
        })
    )


class VisitorFeedbackForm(forms.ModelForm):
    """Formulaire d'avis et de retour des visiteurs"""
    class Meta:
        model = VisitorFeedback
        fields = ['name', 'email', 'phone', 'opinion', 'contribution_type', 'contribution_details']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom (optionnel)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'votre@email.com (optionnel)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+243 XXX XXX XXX (optionnel)'
            }),
            'opinion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Partagez votre avis sur notre site ou notre projet...',
                'required': True
            }),
            'contribution_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'contribution_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dites-nous en plus sur comment vous souhaitez contribuer... (optionnel)'
            }),
        }
        labels = {
            'name': 'Votre nom',
            'email': 'Email',
            'phone': 'Téléphone',
            'opinion': 'Que pensez-vous de notre site ou projet ? *',
            'contribution_type': 'Comment souhaitez-vous contribuer ? *',
            'contribution_details': 'Détails supplémentaires',
        }
