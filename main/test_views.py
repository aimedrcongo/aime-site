from django.http import JsonResponse
from .utils import get_site_statistics

def test_stats(request):
    """Vue de test pour vérifier les statistiques"""
    try:
        stats = get_site_statistics()
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
