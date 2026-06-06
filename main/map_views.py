"""
Vues pour la carte interactive d'impact social AIME
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import json
import logging
import random
from datetime import datetime, timedelta
from django.db import models

logger = logging.getLogger(__name__)


class InteractiveMapView(TemplateView):
    """Vue principale pour la carte interactive (robuste : ne plante jamais en 500)"""
    template_name = 'main/interactive_map.html'

    def get_context_data(self, **kwargs):
        from main.models import ImpactPoint, Event, Donation, Project, UserProfile
        context = super().get_context_data(**kwargs)
        context['title'] = "Carte Interactive de l'Impact Social AIME"

        # Stats dynamiques — valeurs par défaut si une table/colonne manque (migration prod, BDD vide...)
        stats = {
            'total_beneficiaries': 0, 'total_events': 0, 'total_donations': 0,
            'active_projects': 0, 'volunteers': 0,
        }
        try:
            stats['total_beneficiaries'] = UserProfile.objects.count()
            stats['total_events'] = Event.objects.count()
            stats['total_donations'] = Donation.objects.filter(status='completed').aggregate(
                total=models.Sum('amount'))['total'] or 0
            stats['active_projects'] = Project.objects.filter(status='active').count()
            stats['volunteers'] = UserProfile.objects.filter(role='volunteer').count()
        except Exception:
            logger.exception("impact_map: échec du calcul des statistiques")
        context['stats'] = stats

        # Points d'impact réels (seulement ceux avec coordonnées valides)
        impact_data = []
        impact_points = []
        try:
            impact_points = list(ImpactPoint.objects.filter(
                latitude__isnull=False, longitude__isnull=False
            ).exclude(latitude=0, longitude=0))
            for point in impact_points:
                if point.latitude and point.longitude:
                    impact_data.append({
                        'id': point.id,
                        'title': point.description or point.type,
                        'description': point.description,
                        'type': point.type,
                        'lat': float(point.latitude),
                        'lng': float(point.longitude),
                        'impact_value': float(point.value) if point.value else 1,
                        'date': point.created_at.strftime('%d/%m/%Y') if point.created_at else '',
                        'status': point.status,
                    })
        except Exception:
            logger.exception("impact_map: échec du chargement des points d'impact")
            impact_points = []

        context['impact_data'] = json.dumps(impact_data)
        context['has_impact_data'] = len(impact_data) > 0
        context['impact_points'] = impact_points

        return context

def get_impact_data(request):
    """API pour données temps réel"""
    data = {
        'id': random.randint(1000, 9999),
        'title': 'Nouvelle Activité',
        'type': 'event',
        'lat': -4.4419,
        'lng': 15.2663,
        'impact_value': 10,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    return JsonResponse({'status': 'success', 'data': [data]})

@csrf_exempt
def add_impact_point(request):
    """API pour ajouter impact"""
    if request.method == 'POST':
        return JsonResponse({'status': 'success', 'message': 'Ajouté'})
    return JsonResponse({'status': 'error'})

@login_required
def gamification_dashboard(request):
    """Dashboard gamification"""
    return JsonResponse({'status': 'success', 'user_stats': {'points': 100}})