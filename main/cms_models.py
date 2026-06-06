"""
Modèles CMS éditables depuis l'admin Django.
Permettent de modifier textes, images et overlays sans toucher au code.
"""
from django.db import models
from django.core.validators import MaxValueValidator


PAGE_CHOICES = [
    ('home', 'Accueil'),
    ('about', 'À propos'),
    ('projects', 'Nos Projets'),
    ('events', 'Événements'),
    ('contact', 'Contact'),
    ('donate', 'Faire un don'),
    ('mbc', 'Mutoto Bike Challenge'),
    ('mbc_registration', 'Inscription MBC'),
    ('msa', 'Mutoto Science Adventure'),
    ('mon_beau_metier', 'Mon Beau Métier'),
    ('manifesto', 'Manifeste'),
    ('impact_theory', 'Théorie du Changement'),
    ('observatory', 'Observatoire des Droits'),
    ('research_center', 'Centre de Recherche'),
]

OVERLAY_TYPES = [
    ('solid', 'Couleur unie'),
    ('linear', 'Dégradé linéaire'),
    ('radial', 'Dégradé radial'),
]


def _hex_to_rgba(hex_color, opacity):
    """Convertit #RRGGBB + opacité (0-100) en rgba()."""
    h = (hex_color or '#000000').lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except (ValueError, IndexError):
        r, g, b = 10, 42, 77
    a = max(0, min(100, opacity)) / 100.0
    return f'rgba({r}, {g}, {b}, {a:.2f})'


class HeroSection(models.Model):
    """Section hero (bannière) éditable par page."""
    page = models.CharField("Page", max_length=50, choices=PAGE_CHOICES, unique=True)

    # Contenu texte
    eyebrow = models.CharField("Petit label (au-dessus du titre)", max_length=120, blank=True)
    title = models.CharField("Titre principal", max_length=200)
    title_highlight = models.CharField(
        "Mot mis en évidence", max_length=100, blank=True,
        help_text="Mot/groupe affiché en couleur accent (optionnel)."
    )
    subtitle = models.TextField("Sous-titre / description", blank=True)

    # Image de fond
    background_image = models.ImageField(
        "Image de fond", upload_to='heroes/', blank=True, null=True
    )

    # CTA principal
    cta_primary_label = models.CharField("Bouton 1 — texte", max_length=60, blank=True)
    cta_primary_url = models.CharField("Bouton 1 — lien", max_length=300, blank=True)
    # CTA secondaire
    cta_secondary_label = models.CharField("Bouton 2 — texte", max_length=60, blank=True)
    cta_secondary_url = models.CharField("Bouton 2 — lien", max_length=300, blank=True)

    # Overlay configurable
    overlay_enabled = models.BooleanField("Activer l'overlay", default=True)
    overlay_type = models.CharField("Type d'overlay", max_length=10, choices=OVERLAY_TYPES, default='linear')
    overlay_color = models.CharField("Couleur overlay", max_length=7, default='#0A2A4D')
    overlay_color_2 = models.CharField(
        "2e couleur (dégradé)", max_length=7, blank=True,
        help_text="Utilisée pour les dégradés. Laisser vide = même couleur."
    )
    overlay_opacity = models.PositiveIntegerField(
        "Opacité (%)", default=55, validators=[MaxValueValidator(100)]
    )
    overlay_angle = models.PositiveIntegerField(
        "Angle dégradé (deg)", default=135, validators=[MaxValueValidator(360)]
    )

    # SEO / Open Graph (partage social)
    meta_description = models.CharField(
        "Description SEO / partage", max_length=300, blank=True,
        help_text="Texte affiché lors du partage (WhatsApp, Facebook...) et pour le référencement."
    )
    og_image = models.ImageField(
        "Image de partage (Open Graph)", upload_to='og/', blank=True, null=True,
        help_text="Image affichée lors du partage. Si vide, l'image de fond est utilisée."
    )

    is_active = models.BooleanField("Actif", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Section Hero"
        verbose_name_plural = "Sections Hero"
        ordering = ['page']

    def __str__(self):
        return f"Hero — {self.get_page_display()}"

    def overlay_css(self):
        """Retourne la valeur CSS background-image de l'overlay (gradient)."""
        if not self.overlay_enabled:
            return ''
        c1 = _hex_to_rgba(self.overlay_color, self.overlay_opacity)
        if self.overlay_type == 'solid':
            return f'linear-gradient({c1}, {c1})'
        c2 = _hex_to_rgba(self.overlay_color_2 or self.overlay_color, self.overlay_opacity)
        if self.overlay_type == 'radial':
            return f'radial-gradient(circle at center, {c1}, {c2})'
        return f'linear-gradient({self.overlay_angle}deg, {c1}, {c2})'


class SiteSettings(models.Model):
    """Paramètres globaux du site (singleton) : contact, réseaux sociaux, footer."""
    contact_email = models.EmailField("Email principal", default='contact@aime-rdc.org')
    contact_email_2 = models.EmailField("Email secondaire", blank=True, default='kinshasa@aime-rdc.org')
    phone_1 = models.CharField("Téléphone 1", max_length=30, default='+243 844 444 411')
    phone_2 = models.CharField("Téléphone 2", max_length=30, blank=True, default='+243 823 090 002')
    address_1 = models.CharField("Adresse 1", max_length=150, default='Kinshasa - Gombe')
    address_2 = models.CharField("Adresse 2", max_length=150, blank=True, default='Lubumbashi - Ruashi')

    facebook_url = models.URLField("Facebook", blank=True)
    twitter_url = models.URLField("Twitter / X", blank=True)
    instagram_url = models.URLField("Instagram", blank=True)
    linkedin_url = models.URLField("LinkedIn", blank=True)

    footer_tagline = models.CharField(
        "Slogan footer", max_length=250,
        default="Organisation dédiée au développement et épanouissement des enfants en RDC."
    )

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return "Paramètres du site"

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ProgramCard(models.Model):
    """Carte programme affichée sur la page d'accueil (section 'Nos programmes')."""
    title = models.CharField("Titre", max_length=120)
    description = models.TextField("Description")
    image = models.ImageField("Image", upload_to='programs/', blank=True, null=True)
    image_url = models.URLField("URL image (si pas d'upload)", blank=True)
    badge_label = models.CharField("Badge — texte", max_length=60, blank=True)
    badge_icon = models.CharField("Badge — icône FontAwesome", max_length=40, blank=True,
                                  default='fa-star', help_text="Ex: fa-bicycle, fa-flask, fa-briefcase")
    link_url = models.CharField("Lien", max_length=300, blank=True)
    link_label = models.CharField("Lien — texte", max_length=60, default='Découvrir')
    order = models.PositiveIntegerField("Ordre", default=0)
    is_active = models.BooleanField("Actif", default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Programme (accueil)"
        verbose_name_plural = "Programmes (accueil)"

    def __str__(self):
        return self.title

    def get_image(self):
        return self.image.url if self.image else self.image_url


class GalleryImage(models.Model):
    """Image de la galerie/carrousel de la page d'accueil."""
    title = models.CharField("Titre", max_length=120, blank=True)
    caption = models.CharField("Légende", max_length=200, blank=True)
    image = models.ImageField("Image", upload_to='gallery/', blank=True, null=True)
    image_url = models.URLField("URL image (si pas d'upload)", blank=True)
    order = models.PositiveIntegerField("Ordre", default=0)
    is_active = models.BooleanField("Actif", default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Image galerie (accueil)"
        verbose_name_plural = "Images galerie (accueil)"

    def __str__(self):
        return self.title or self.caption or f"Image #{self.pk}"

    def get_image(self):
        return self.image.url if self.image else self.image_url


class ImpactStat(models.Model):
    """Compteur d'impact public (page d'accueil) — éditable par l'équipe ONG."""
    label = models.CharField("Libellé", max_length=120)
    value = models.PositiveIntegerField("Valeur", default=0)
    icon = models.CharField(
        "Icône FontAwesome", max_length=40, default='fa-heart',
        help_text="Ex: fa-child, fa-hand-holding-heart, fa-diagram-project, fa-users"
    )
    prefix = models.CharField("Préfixe", max_length=10, blank=True, help_text='Ex: "≈"')
    suffix = models.CharField("Suffixe", max_length=10, blank=True, help_text='Ex: "+", "K", "FC"')
    order = models.PositiveIntegerField("Ordre", default=0)
    is_active = models.BooleanField("Actif", default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Statistique d'impact"
        verbose_name_plural = "Statistiques d'impact"

    def __str__(self):
        return f"{self.label} : {self.value}"
