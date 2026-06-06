"""Idempotent seed for live preview (replaces buggy create_sample_data)."""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aimesite.settings')
django.setup()

from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta
from django.contrib.auth import get_user_model
from main.models import (
    Category, Project, Event, MutotoBikeChallenge, MutoScienceAdventure,
    Staff, DailyInformation,
)

User = get_user_model()
now = timezone.now()

# --- Admin / superuser ---
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@aime-rdc.org', 'first_name': 'Admin', 'last_name': 'AIME',
              'is_staff': True, 'is_superuser': True},
)
admin.is_staff = True
admin.is_superuser = True
admin.set_password('AimeAdmin2026!')
admin.save()
print('Admin ready:', admin.username)

# --- Categories ---
cats = {}
for name, color in [('Éducation', '#003366'), ('Sport', '#00B4D8'), ('Formation', '#0077B6')]:
    c, _ = Category.objects.get_or_create(name=name, defaults={'description': f'Projets {name}', 'color': color})
    cats[name] = c

# --- Projects ---
projects = [
    ('École Numérique AIME', 'Éducation', 'Formation informatique et programmation pour les jeunes de Kinshasa afin de réduire la fracture numérique.', 50000, 32000, True),
    ('Atelier de Mécanique Vélo', 'Sport', 'Apprentissage de la réparation de vélos pour créer des emplois durables et soutenir le Bike Challenge.', 25000, 18500, True),
    ('Formation Entrepreneuriat Jeunes', 'Formation', "Accompagnement des jeunes vers l'autonomie économique par la formation aux métiers porteurs.", 40000, 12000, True),
]
for name, cat, desc, goal, raised, feat in projects:
    Project.objects.get_or_create(
        slug=slugify(name),
        defaults={'name': name, 'description': desc, 'category': cats[cat],
                  'goal_amount': goal, 'raised_amount': raised, 'start_date': now.date(),
                  'status': 'active', 'is_featured': feat, 'coordinator': admin,
                  'beneficiaries_count': 120, 'volunteers_count': 15},
    )

# --- Events ---
events = [
    ('Journée Portes Ouvertes AIME', 'community', 'Découvrez nos programmes et activités au siège AIME.', 15, 'Siège AIME, Kinshasa - Gombe'),
    ("Formation Entrepreneuriat Jeunes", 'workshop', "Atelier intensif de formation à l'entrepreneuriat.", 45, 'Centre AIME, Kinshasa'),
    ('Conférence Droits de l\'Enfant', 'conference', "Table ronde sur la protection et les droits des enfants en RDC.", 60, 'Lubumbashi - Ruashi'),
]
for title, etype, desc, days, loc in events:
    Event.objects.get_or_create(
        slug=slugify(title),
        defaults={'title': title, 'description': desc, 'event_type': etype,
                  'date': now + timedelta(days=days), 'location': loc,
                  'organizer': admin, 'is_active': True, 'is_public': True, 'is_free': True},
    )

# --- MBC ---
MutotoBikeChallenge.objects.get_or_create(
    slug='mutoto-bike-challenge-2026',
    defaults={'name': 'Mutoto Bike Challenge 2026', 'description': "Grand défi cycliste annuel pour sensibiliser les jeunes à la protection de l'environnement.",
              'date': now + timedelta(days=30), 'location': 'Parc de la Vallée de la Nsele, Kinshasa',
              'max_participants': 100, 'registration_fee': 5000, 'is_active': True},
)

# --- MSA ---
MutoScienceAdventure.objects.get_or_create(
    slug='mutoto-science-adventure-2026',
    defaults={'name': 'Mutoto Science Adventure 2026', 'description': "Ateliers scientifiques et technologiques pour éveiller la curiosité des enfants.",
              'age_group': '8-14 ans', 'duration': '3 mois', 'start_date': now.date(),
              'end_date': (now + timedelta(days=90)).date(), 'max_participants': 30, 'is_active': True},
)

# --- Staff (need users) ---
staff_data = [
    ('mmulamba', 'Marie', 'Mulamba', 'director', 'Experte en développement communautaire avec plus de 15 ans d\'expérience.', 15),
    ('jbkalonji', 'Jean-Baptiste', 'Kalonji', 'coordinator', 'Spécialiste en éducation et formation professionnelle.', 10),
    ('akabongo', 'Alice', 'Kabongo', 'communication', 'Responsable communication et partenariats.', 7),
]
for i, (uname, fn, ln, pos, bio, yrs) in enumerate(staff_data):
    u, _ = User.objects.get_or_create(username=uname, defaults={'first_name': fn, 'last_name': ln, 'email': f'{uname}@aime-rdc.org'})
    Staff.objects.get_or_create(user=u, defaults={'position': pos, 'bio': bio, 'years_experience': yrs, 'is_visible': True, 'order': i})

# --- Daily info ---
infos = [
    ('Lancement de la nouvelle saison du Bike Challenge', 'event', "Les inscriptions pour l'édition 2026 du Mutoto Bike Challenge sont ouvertes !", True),
    ('250 jeunes formés cette année', 'success_story', "Grâce à vos dons, 250 jeunes ont bénéficié de nos formations professionnelles.", False),
    ('Nouveau partenariat éducatif', 'announcement', "AIME signe un partenariat avec plusieurs écoles de Kinshasa.", False),
]
for title, cat, content, feat in infos:
    DailyInformation.objects.get_or_create(
        title=title,
        defaults={'content': content, 'category': cat, 'is_published': True, 'is_featured': feat, 'display_date': now.date()},
    )

print('Seed complete. Projects:', Project.objects.count(), 'Events:', Event.objects.count(), 'Staff:', Staff.objects.count())

# --- Statistiques attrayantes pour la page d'accueil (données de démo) ---
from main.models import Donation, MBCParticipant, UserProfile

mbc = MutotoBikeChallenge.objects.first()
if mbc and MBCParticipant.objects.count() < 40:
    for i in range(40):
        MBCParticipant.objects.get_or_create(
            event=mbc, participant_email=f'rider{i}@aime-rdc.org',
            defaults={'participant_name': f'Participant {i+1}', 'participant_phone': '+243000000000',
                      'age': 12 + (i % 6), 'emergency_contact': 'Parent', 'emergency_phone': '+243111111111',
                      'status': 'confirmed'},
        )

if Donation.objects.filter(status='completed').count() < 25:
    proj = Project.objects.first()
    for i in range(25):
        Donation.objects.get_or_create(
            donor_email=f'donor{i}@example.com', transaction_id=f'SEED-{i}',
            defaults={'donor_name': f'Donateur {i+1}', 'amount': 15000 + i * 2500,
                      'currency': 'CDF', 'project': proj, 'status': 'completed'},
        )

# Profils: enfants & parents (UserProfile créé via signal, on ajuste le rôle)
def ensure_profiles(prefix, role, n):
    for i in range(n):
        u, _ = User.objects.get_or_create(username=f'{prefix}{i}', defaults={'email': f'{prefix}{i}@aime-rdc.org'})
        prof, _ = UserProfile.objects.get_or_create(user=u)
        prof.role = role
        prof.save()

ensure_profiles('enfant', 'child', 80)
ensure_profiles('parent', 'parent', 45)

from django.core.cache import cache
cache.delete('site_statistics_v1')
print('Stats enrichies. Dons completes:', Donation.objects.filter(status="completed").count(),
      '| MBC confirmes:', MBCParticipant.objects.filter(status="confirmed").count(),
      '| Enfants:', UserProfile.objects.filter(role="child").count())

# --- CMS: Hero sections & paramètres du site (éditables depuis l'admin) ---
from main.models import HeroSection, SiteSettings

SiteSettings.load()  # crée le singleton avec les valeurs par défaut

_hero_defaults = [
    ('home', {
        'eyebrow': 'ONG · RDC · Depuis Kinshasa & Lubumbashi',
        'title': 'Agissons ici et maintenant pour les',
        'title_highlight': 'enfants',
        'subtitle': "Développement socio-éducatif, entrepreneuriat et formation aux métiers : nous bâtissons l'avenir des enfants et des jeunes de la République Démocratique du Congo.",
        'cta_primary_label': 'Faire un don', 'cta_primary_url': '/donate/',
        'cta_secondary_label': 'Découvrir nos projets', 'cta_secondary_url': '/projects/',
        'overlay_enabled': False,
    }),
    ('events', {
        'eyebrow': 'Agenda',
        'title': 'Nos Événements',
        'subtitle': "Découvrez tous nos événements, ateliers et activités organisés pour le développement et l'épanouissement des enfants en RDC.",
        'cta_primary_label': 'Voir les événements', 'cta_primary_url': '#upcoming-events',
        'overlay_enabled': True, 'overlay_type': 'linear', 'overlay_color': '#0A2A4D',
        'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60, 'overlay_angle': 135,
    }),
    ('about', {
        'eyebrow': 'Qui sommes-nous', 'title': "À propos d'AIME",
        'subtitle': "Agissons Ici et Maintenant pour les Enfants — une organisation dédiée au développement et à l'épanouissement des enfants en République Démocratique du Congo.",
        'overlay_enabled': True, 'overlay_color': '#0A2A4D', 'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60,
    }),
    ('projects', {
        'eyebrow': 'Nos initiatives', 'title': 'Nos Projets',
        'subtitle': "Découvrez nos initiatives pour l'épanouissement des enfants.",
        'overlay_enabled': True, 'overlay_color': '#0A2A4D', 'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60,
    }),
    ('contact', {
        'eyebrow': 'Contact', 'title': 'Contactez-nous',
        'subtitle': "Nous sommes là pour vous écouter et répondre à vos questions.",
        'overlay_enabled': True, 'overlay_color': '#0A2A4D', 'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60,
    }),
    ('donate', {
        'eyebrow': 'Soutenir AIME', 'title': 'Faire un don',
        'subtitle': "Votre générosité peut transformer la vie d'un enfant.",
        'overlay_enabled': True, 'overlay_color': '#0A2A4D', 'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60,
    }),
    ('impact_theory', {
        'eyebrow': 'Notre approche', 'title': 'Notre Théorie du Changement',
        'subtitle': "De l'enfant d'aujourd'hui au leader de demain : comment AIME transforme des vies et construit l'avenir de la RDC.",
        'overlay_enabled': True, 'overlay_color': '#0A2A4D', 'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60,
    }),
    ('mbc_registration', {
        'eyebrow': 'Inscription', 'title': 'Mutoto Bike Challenge',
        'subtitle': "Rejoignez-nous pour cette aventure cycliste éducative et solidaire !",
        'overlay_enabled': True, 'overlay_color': '#0A2A4D', 'overlay_color_2': '#1D4ED8', 'overlay_opacity': 60,
    }),
]
for _page, _defaults in _hero_defaults:
    HeroSection.objects.get_or_create(page=_page, defaults=_defaults)

# Heros des pages au design custom (texte editable, design conserve)
_hero_rich = [
    ('mbc', {'title': 'Mutoto Bike Challenge', 'subtitle': "Défi cycliste annuel pour sensibiliser les jeunes à la protection de l'environnement tout en promouvant le sport et la cohésion sociale.", 'overlay_enabled': False}),
    ('msa', {'title': 'Mutoto Science Adventure', 'subtitle': "Éveiller la curiosité scientifique des enfants de 3 à 6 ans et promouvoir l'égalité des genres dans les STEM", 'overlay_enabled': False}),
    ('mon_beau_metier', {'title': 'Mon Beau Métier', 'subtitle': "Reconnaître, valoriser et accompagner les métiers exercés par les étudiants pour leur autonomisation économique et professionnelle", 'overlay_enabled': False}),
    ('manifesto', {'title': 'MANIFESTE AIME', 'eyebrow': '"L\'Afrique de demain se construit aujourd\'hui dans les mains de nos enfants"', 'subtitle': "Nous croyons en une Afrique où chaque enfant, peu importe son origine, sa condition sociale ou son genre, peut devenir l'architecte de son destin et le bâtisseur d'un continent prospère.", 'overlay_enabled': False}),
    ('observatory', {'title': "Observatoire International des Droits de l'Enfant", 'subtitle': "AIME surveille, documente et agit pour la protection des droits fondamentaux des enfants en RDC et dans la région des Grands Lacs", 'overlay_enabled': False}),
    ('research_center', {'title': 'Centre de Recherche & Innovation AIME', 'subtitle': '"L\'avenir de l\'enfance se construit aujourd\'hui dans nos laboratoires"', 'overlay_enabled': False}),
]
for _page, _defaults in _hero_rich:
    HeroSection.objects.get_or_create(page=_page, defaults=_defaults)
print('CMS seeded: heroes =', HeroSection.objects.count(), '| site settings OK')

# --- CMS: Programmes & Galerie (page d'accueil) ---
from main.models import ProgramCard, GalleryImage

_programs = [
    ("Mutoto Bike Challenge", "Un défi cycliste annuel qui sensibilise les jeunes à l'environnement tout en renforçant la cohésion sociale.",
     "https://images.unsplash.com/photo-1515658323406-25d61c141a6e?auto=format&fit=crop&w=900&q=80",
     "Sport & Écologie", "fa-bicycle", "/mutoto-bike-challenge/", 1),
    ("Mutoto Science Adventure", "Des ateliers scientifiques qui éveillent la curiosité, développent l'esprit critique et inspirent les vocations.",
     "https://images.pexels.com/photos/8471835/pexels-photo-8471835.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=600&w=900",
     "Sciences & Tech", "fa-flask", "/mutoto-science-adventure/", 2),
    ("Mon Beau Métier", "La valorisation et la formation aux métiers porteurs pour ouvrir aux jeunes la voie de l'autonomie économique.",
     "https://images.pexels.com/photos/9301461/pexels-photo-9301461.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=600&w=900",
     "Métiers & Avenir", "fa-briefcase", "/mon-beau-metier/", 3),
]
for _t, _d, _img, _badge, _icon, _link, _o in _programs:
    ProgramCard.objects.get_or_create(title=_t, defaults={
        'description': _d, 'image_url': _img, 'badge_label': _badge,
        'badge_icon': _icon, 'link_url': _link, 'link_label': 'Découvrir', 'order': _o,
    })

_gallery = [
    ("Mutoto Science Adventure", "Ateliers scientifiques pour éveiller la curiosité des enfants",
     "https://images.pexels.com/photos/14554003/pexels-photo-14554003.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=600&w=1200", 1),
    ("Mon Beau Métier", "Formation et valorisation des métiers étudiants en RDC",
     "https://images.pexels.com/photos/9301461/pexels-photo-9301461.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=600&w=1200", 2),
    ("Engagement communautaire", "Un travail collectif pour un impact durable",
     "https://images.unsplash.com/photo-1515658323406-25d61c141a6e?auto=format&fit=crop&w=1200&q=80", 3),
    ("Jeunesse & éducation", "Accompagner les jeunes vers l'autonomie",
     "https://images.pexels.com/photos/8617843/pexels-photo-8617843.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=600&w=1200", 4),
]
for _t, _c, _img, _o in _gallery:
    GalleryImage.objects.get_or_create(title=_t, defaults={'caption': _c, 'image_url': _img, 'order': _o})

print('CMS seeded: programs =', ProgramCard.objects.count(), '| gallery =', GalleryImage.objects.count())
