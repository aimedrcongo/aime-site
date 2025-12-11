from django.contrib import admin
from .models import (
    UserProfile, Category, Project, MutotoBikeChallenge, MBCParticipant,
    MutoScienceAdventure, Event, Donation, ContactMessage, 
    NewsletterSubscription, UserActivity, Staff
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'is_active_member', 'points']
    list_filter = ['role', 'is_active_member']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'start_date', 'raised_amount', 'goal_amount']
    list_filter = ['status', 'category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MutotoBikeChallenge)
class MutotoBikeChallengeAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'location', 'max_participants', 'is_active']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(MBCParticipant)
class MBCParticipantAdmin(admin.ModelAdmin):
    list_display = ['participant_name', 'age', 'event', 'status', 'registered_at']
    list_filter = ['status', 'event']
    search_fields = ['participant_name', 'participant_email']

@admin.register(MutoScienceAdventure)
class MutoScienceAdventureAdmin(admin.ModelAdmin):
    list_display = ['name', 'age_group', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'is_active']
    list_filter = ['event_type', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['donor_name', 'donor_email']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message_type', 'subject', 'is_read']
    list_filter = ['message_type', 'is_read']
    search_fields = ['name', 'email', 'subject']

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'timestamp']
    list_filter = ['activity_type']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'years_experience', 'is_visible']
    list_filter = ['position', 'is_visible']
