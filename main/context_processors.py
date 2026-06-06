"""Context processors globaux (paramètres du site + SEO/Open Graph éditables)."""
from django.core.cache import cache
from .models import SiteSettings, HeroSection

_SENTINEL = '__none__'

# Mappe le nom d'URL Django vers la clé de page HeroSection
URLNAME_TO_PAGE = {
    'home': 'home', 'about': 'about', 'projects': 'projects', 'events': 'events',
    'contact': 'contact', 'donate': 'donate', 'manifesto': 'manifesto',
    'observatory': 'observatory', 'research_center': 'research_center',
    'impact_theory': 'impact_theory', 'mbc_registration': 'mbc_registration',
    'mutoto_bike_challenge': 'mbc', 'mutoto_science_adventure': 'msa',
    'mon_beau_metier': 'mon_beau_metier',
}


def _hero_for(page):
    key = f'cms_hero_{page}'
    cached = cache.get(key)
    if cached == _SENTINEL:
        return None
    if cached is not None:
        return cached
    hero = HeroSection.objects.filter(page=page, is_active=True).first()
    cache.set(key, hero if hero is not None else _SENTINEL, 3600)
    return hero


def site_settings(request):
    """Injecte `site_settings` dans tous les templates (cache 1h)."""
    obj = cache.get('cms_site_settings')
    if obj is None:
        obj = SiteSettings.load()
        cache.set('cms_site_settings', obj, 3600)
    return {'site_settings': obj}


def seo_context(request):
    """Données Open Graph / partage social, résolues automatiquement par page."""
    page_key = None
    rm = getattr(request, 'resolver_match', None)
    if rm and rm.url_name:
        page_key = URLNAME_TO_PAGE.get(rm.url_name)

    hero = _hero_for(page_key) if page_key else None
    settings_obj = cache.get('cms_site_settings') or SiteSettings.load()

    title = hero.title if hero and hero.title else 'AIME'
    description = (hero.meta_description if hero and hero.meta_description
                   else settings_obj.footer_tagline)

    image = ''
    if hero:
        img = hero.og_image or hero.background_image
        if img:
            try:
                image = request.build_absolute_uri(img.url)
            except Exception:
                image = ''

    return {'seo': {
        'title': title,
        'description': description,
        'image': image,
        'url': request.build_absolute_uri(),
    }}
