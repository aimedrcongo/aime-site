"""Tags template pour le contenu CMS éditable (avec cache)."""
from django import template
from django.core.cache import cache
from main.models import HeroSection, ProgramCard, GalleryImage, ImpactStat

register = template.Library()

_SENTINEL = '__none__'


@register.simple_tag
def get_hero(page):
    """Retourne la HeroSection active de la page (None si absente). Mise en cache."""
    key = f'cms_hero_{page}'
    cached = cache.get(key)
    if cached == _SENTINEL:
        return None
    if cached is not None:
        return cached
    hero = HeroSection.objects.filter(page=page, is_active=True).first()
    cache.set(key, hero if hero is not None else _SENTINEL, 3600)
    return hero


@register.simple_tag
def get_programs():
    """Cartes programmes actives (page d'accueil), triées par ordre."""
    items = cache.get('cms_programs')
    if items is None:
        items = list(ProgramCard.objects.filter(is_active=True))
        cache.set('cms_programs', items, 3600)
    return items


@register.simple_tag
def get_gallery():
    """Images galerie actives (page d'accueil), triées par ordre."""
    items = cache.get('cms_gallery')
    if items is None:
        items = list(GalleryImage.objects.filter(is_active=True))
        cache.set('cms_gallery', items, 3600)
    return items


@register.simple_tag
def get_impact_stats():
    """Compteurs d'impact actifs (page d'accueil), triés par ordre."""
    items = cache.get('cms_impact_stats')
    if items is None:
        items = list(ImpactStat.objects.filter(is_active=True))
        cache.set('cms_impact_stats', items, 3600)
    return items
