"""Context processors globaux (paramètres du site éditables)."""
from django.core.cache import cache
from .models import SiteSettings


def site_settings(request):
    """Injecte `site_settings` dans tous les templates (cache 1h)."""
    obj = cache.get('cms_site_settings')
    if obj is None:
        obj = SiteSettings.load()
        cache.set('cms_site_settings', obj, 3600)
    return {'site_settings': obj}
