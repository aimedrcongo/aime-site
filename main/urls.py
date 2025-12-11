from django.urls import path
from django.shortcuts import render
from . import views
from . import map_views
from . import dashboard_views
from . import auth_views
from . import test_views

app_name = 'main'

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Nouvelles sections stratégiques
    path('impact-theory/', views.impact_theory, name='impact_theory'),
    path('observatory/', views.observatory, name='observatory'),
    path('research-center/', views.research_center, name='research_center'),
    path('manifesto/', views.manifesto, name='manifesto'),
    
    # Authentification
    path('signup/', auth_views.signup_view, name='signup'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # Projets
    path('projects/', views.projects, name='projects'),
    path('project/<slug:slug>/', views.project_detail, name='project_detail'),
    
    # Mutoto Bike Challenge
    path('mbc/', views.mutoto_bike_challenge, name='mutoto_bike_challenge'),
    path('mbc/inscription/', views.mbc_registration, name='mbc_registration'),
    
    # Mutoto Science Adventure
    path('msa/', views.mutoto_science_adventure, name='mutoto_science_adventure'),
    
    # Mon Beau Métier
    path('mon-beau-metier/', views.mon_beau_metier, name='mon_beau_metier'),
    
    # Événements
    path('events/', views.events, name='events'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    
    # Dons
    path('donate/', views.donate, name='donate'),
    path('donate/<slug:project_slug>/', views.donate, name='donate_project'),
    path('donate/success/', views.donate_success, name='donate_success'),
    
    # AJAX
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Carte Interactive d'Impact Social
    path('impact-map/', map_views.InteractiveMapView.as_view(), name='interactive_map'),
    path('api/impact-data/', map_views.get_impact_data, name='api_impact_data'),
    path('api/add-impact/', map_views.add_impact_point, name='api_add_impact'),
    path('dashboard/gamification/', map_views.gamification_dashboard, name='gamification_dashboard'),
    
    # Dashboard utilisateur
    path('dashboard/', dashboard_views.dashboard_home, name='dashboard_home'),
    path('dashboard/profile/', dashboard_views.dashboard_profile, name='dashboard_profile'),
    path('dashboard/donations/', dashboard_views.dashboard_donations, name='dashboard_donations'),
    path('dashboard/events/', dashboard_views.dashboard_events, name='dashboard_events'),
    path('dashboard/notifications/', dashboard_views.dashboard_notifications, name='dashboard_notifications'),
    path('dashboard/badges/', dashboard_views.dashboard_badges, name='dashboard_badges'),
    path('dashboard/settings/', dashboard_views.dashboard_settings, name='dashboard_settings'),
    path('dashboard/activities/', dashboard_views.dashboard_activities, name='dashboard_activities'),
    
    # Actions dashboard
    path('dashboard/join-event/<int:event_id>/', dashboard_views.join_event, name='join_event'),
    path('dashboard/join-challenge/<int:challenge_id>/', dashboard_views.join_challenge, name='join_challenge'),
    path('dashboard/notification/<int:notification_id>/read/', dashboard_views.mark_notification_read, name='mark_notification_read'),

    # Chat assistant (dashboard)
    path('dashboard/chat/', dashboard_views.dashboard_chat_conversations, name='dashboard_chat_conversations'),
    path('dashboard/my-chats/', dashboard_views.dashboard_my_conversations, name='dashboard_my_conversations'),
    
    # Test des statistiques
    path('test-stats/', test_views.test_stats, name='test_stats'),
    path('test-images/', lambda request: render(request, 'main/test_images.html'), name='test_images'),
    
    # Chat Assistant - Notifications et administration
    path('api/chat/notification/', views.chat_notification, name='chat_notification'),
    path('admin/chat/', views.chat_admin, name='chat_admin'),
    path('admin/chat/reply/<int:conversation_id>/', views.chat_reply, name='chat_reply'),
    path('admin/chat/close/<int:conversation_id>/', views.close_conversation, name='close_conversation'),
    
    # Avis visiteurs
    path('api/visitor-feedback/', views.submit_visitor_feedback, name='submit_visitor_feedback'),
]
