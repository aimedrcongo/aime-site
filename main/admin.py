from django.contrib import admin
from .models import (
    UserProfile, Category, Project, MutotoBikeChallenge, MBCParticipant,
    MutoScienceAdventure, Event, Donation, ContactMessage, 
    NewsletterSubscription, UserActivity, Staff, VisitorFeedback, DailyInformation
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


@admin.register(VisitorFeedback)
class VisitorFeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'contribution_type', 'created_at', 'is_contacted']
    list_filter = ['contribution_type', 'is_contacted', 'created_at']
    search_fields = ['name', 'email', 'phone', 'opinion']
    readonly_fields = ['ip_address', 'user_agent', 'created_at']
    fieldsets = (
        ('Informations du visiteur', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Avis et contribution', {
            'fields': ('opinion', 'contribution_type', 'contribution_details')
        }),
        ('Suivi', {
            'fields': ('is_contacted', 'contacted_at', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_contacted']
    
    def mark_as_contacted(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_contacted=True, contacted_at=timezone.now())
        self.message_user(request, f"{updated} avis marqué(s) comme contacté(s).")
    mark_as_contacted.short_description = "Marquer comme contacté"


@admin.register(DailyInformation)
class DailyInformationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'display_date', 'is_published', 'is_featured', 'order']
    list_filter = ['category', 'is_published', 'is_featured', 'display_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'publication_date']
    
    fieldsets = (
        ('Titre et contenu', {
            'fields': ('title', 'content', 'category')
        }),
        ('Image et lien', {
            'fields': ('featured_image', 'link_url', 'link_text')
        }),
        ('Publication', {
            'fields': ('is_published', 'is_featured', 'display_date', 'order')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'publication_date'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-is_featured', '-display_date', '-order']
    
    actions = ['publish_articles', 'unpublish_articles', 'toggle_featured']
    
    def publish_articles(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} article(s) publié(s).")
    publish_articles.short_description = "Publier les articles sélectionnés"
    
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} article(s) dépublié(s).")
    unpublish_articles.short_description = "Dépublier les articles sélectionnés"
    
    def toggle_featured(self, request, queryset):
        for article in queryset:
            article.is_featured = not article.is_featured
            article.save()
        self.message_user(request, f"{queryset.count()} article(s) mis à jour.")
    toggle_featured.short_description = "Basculer l'épinglage des articles"



# ==============================================================================
# CMS — Contenu éditable (Hero, Paramètres du site)
# ==============================================================================
from django import forms
from django.utils.html import format_html
from .models import HeroSection, SiteSettings


class HeroSectionForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = '__all__'
        widgets = {
            'overlay_color': forms.TextInput(attrs={'type': 'color', 'style': 'width:70px;height:38px;padding:2px;'}),
            'overlay_color_2': forms.TextInput(attrs={'type': 'color', 'style': 'width:70px;height:38px;padding:2px;'}),
            'overlay_opacity': forms.NumberInput(attrs={'type': 'range', 'min': 0, 'max': 100, 'step': 5,
                                                        'oninput': "this.nextElementSibling && (this.nextElementSibling.value=this.value)"}),
        }


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    form = HeroSectionForm
    list_display = ['get_page_display', 'title', 'overlay_preview', 'is_active', 'updated_at']
    list_filter = ['is_active', 'overlay_type']
    readonly_fields = ['image_preview', 'updated_at']
    fieldsets = (
        ("Page", {'fields': ('page', 'is_active')}),
        ("Contenu", {'fields': ('eyebrow', 'title', 'title_highlight', 'subtitle')}),
        ("Image de fond", {'fields': ('background_image', 'image_preview')}),
        ("Boutons (CTA)", {'fields': ('cta_primary_label', 'cta_primary_url',
                                       'cta_secondary_label', 'cta_secondary_url')}),
        ("Overlay (filtre couleur sur l'image)", {
            'fields': ('overlay_enabled', 'overlay_type', 'overlay_color', 'overlay_color_2',
                       'overlay_opacity', 'overlay_angle'),
            'description': "Active un filtre coloré sur l'image de fond pour améliorer la lisibilité du texte.",
        }),
        (None, {'fields': ('updated_at',)}),
    )

    def image_preview(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" style="max-height:180px;border-radius:8px;" />', obj.background_image.url)
        return "Aucune image"
    image_preview.short_description = "Aperçu"

    def overlay_preview(self, obj):
        if not obj.overlay_enabled:
            return "—"
        return format_html(
            '<span style="display:inline-block;width:60px;height:20px;border-radius:4px;'
            'background:{};border:1px solid #ccc;"></span>', obj.overlay_color
        )
    overlay_preview.short_description = "Overlay"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Contact", {'fields': ('contact_email', 'contact_email_2', 'phone_1', 'phone_2', 'address_1', 'address_2')}),
        ("Réseaux sociaux", {'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')}),
        ("Footer", {'fields': ('footer_tagline',)}),
    )

    def has_add_permission(self, request):
        # Singleton : interdit d'ajouter plusieurs instances
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


from .models import ProgramCard, GalleryImage


@admin.register(ProgramCard)
class ProgramCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'badge_label', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    readonly_fields = ['image_preview']
    fields = ('title', 'description', 'image', 'image_url', 'image_preview',
              'badge_label', 'badge_icon', 'link_url', 'link_label', 'order', 'is_active')

    def image_preview(self, obj):
        url = obj.get_image()
        if url:
            return format_html('<img src="{}" style="max-height:140px;border-radius:8px;" />', url)
        return "Aucune image"
    image_preview.short_description = "Aperçu"


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'caption', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    readonly_fields = ['image_preview']
    fields = ('title', 'caption', 'image', 'image_url', 'image_preview', 'order', 'is_active')

    def image_preview(self, obj):
        url = obj.get_image()
        if url:
            return format_html('<img src="{}" style="max-height:140px;border-radius:8px;" />', url)
        return "Aucune image"
    image_preview.short_description = "Aperçu"
