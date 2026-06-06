"""Tags template pour le contenu CMS éditable (avec cache)."""
from django import template
from django.core.cache import cache
from main.models import HeroSection

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
