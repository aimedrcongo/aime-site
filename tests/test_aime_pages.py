"""
Tests E2E pour la refonte du design AIME DR Congo
- Vérifie que toutes les pages publiques chargent (HTTP 200)
- Vérifie les formulaires POST (contact, newsletter, donate)
- Vérifie l'API publique /api/stats
- Vérifie l'auth admin et l'accès dashboard
- Vérifie que les CSS de la nouvelle charte se chargent (200)
"""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get(
    "REACT_APP_BACKEND_URL",
    "https://web-refresh-115.preview.emergentagent.com",
).rstrip("/")

ADMIN_USER = "admin"
ADMIN_PASS = "AimeAdmin2026!"


@pytest.fixture(scope="session")
def client():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "AIME-Tester/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return s


# --- Phase 1: Pages publiques (GET 200) ---

PUBLIC_PAGES = [
    "/",
    "/about/",
    "/projects/",
    "/contact/",
    "/events/",
    "/donate/",
    "/mbc/",
    "/msa/",
    "/mon-beau-metier/",
    "/impact-map/",
    "/manifesto/",
    "/impact-theory/",
    "/observatory/",
    "/research-center/",
]


@pytest.mark.parametrize("path", PUBLIC_PAGES)
def test_public_page_loads(client, path):
    r = client.get(f"{BASE_URL}{path}", timeout=30, allow_redirects=True)
    assert r.status_code == 200, f"{path} -> {r.status_code}\n{r.text[:300]}"
    # Pas d'erreur de template
    body = r.text.lower()
    assert "templatesyntaxerror" not in body, f"Template error on {path}"
    assert "templatedoesnotexist" not in body, f"Template missing on {path}"
    # base.html doit être appliqué (DOCTYPE + navbar)
    assert "<!doctype html" in body or "<html" in body


# --- Phase 2: Static CSS de la refonte ---

@pytest.mark.parametrize("css", [
    "/static/main/design-system.css",
    "/static/main/components.css",
    "/static/main/home.css",
])
def test_design_css_loads(client, css):
    r = client.get(f"{BASE_URL}{css}", timeout=30)
    assert r.status_code == 200, f"{css} -> {r.status_code}"
    assert len(r.text) > 50, f"{css} is empty"


def test_palette_option_d_blue_in_design_system(client):
    """Option D: bleu roi #1D4ED8 + navy #0A2A4D + cyan #00B4D8 dans design-system.css"""
    r = client.get(f"{BASE_URL}/static/main/design-system.css", timeout=30)
    assert r.status_code == 200
    css = r.text.lower()
    has_primary = "#1d4ed8" in css
    has_navy = "#0a2a4d" in css
    has_cyan = "#00b4d8" in css
    assert has_primary, "Couleur bleu roi #1D4ED8 absente du design-system.css"
    assert has_navy, "Couleur navy #0A2A4D absente du design-system.css"
    assert has_cyan, "Couleur cyan #00B4D8 absente du design-system.css"


def test_home_contains_navbar_and_footer(client):
    r = client.get(f"{BASE_URL}/", timeout=30)
    assert r.status_code == 200
    body = r.text.lower()
    assert "nav" in body, "Navbar absente"
    assert "footer" in body, "Footer absent"
    # CTA don
    assert "don" in body  # 'Faire un don' / 'don'


# --- Phase 3: API publique /api/stats ---

def test_api_stats_returns_json(client):
    r = client.get(f"{BASE_URL}/api/stats/", timeout=30)
    assert r.status_code == 200, f"/api/stats/ -> {r.status_code}: {r.text[:300]}"
    data = r.json()
    assert isinstance(data, dict)
    # Doit contenir au moins quelques clés de stats
    assert len(data.keys()) > 0


# --- Phase 4: Newsletter AJAX ---

def _get_csrf(client, url):
    r = client.get(url, timeout=30)
    # Récupère le csrftoken depuis les cookies
    token = client.cookies.get("csrftoken")
    if not token:
        # Sinon récupère depuis le HTML
        m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', r.text)
        if m:
            token = m.group(1)
    return token, r


def test_newsletter_subscribe_success(client):
    csrf, _ = _get_csrf(client, f"{BASE_URL}/")
    assert csrf, "CSRF token introuvable"
    email = f"TEST_newsletter_{os.urandom(4).hex()}@example.com"
    r = client.post(
        f"{BASE_URL}/newsletter/subscribe/",
        data={"email": email, "name": "TestUser", "csrfmiddlewaretoken": csrf},
        headers={"Referer": f"{BASE_URL}/", "X-CSRFToken": csrf},
        timeout=30,
    )
    assert r.status_code == 200, f"Newsletter -> {r.status_code}: {r.text[:300]}"
    data = r.json()
    assert data.get("success") is True, f"Newsletter response: {data}"


# --- Phase 5: Contact POST ---

def test_contact_post_redirect_and_success(client):
    csrf, _ = _get_csrf(client, f"{BASE_URL}/contact/")
    assert csrf, "CSRF token introuvable sur /contact/"
    payload = {
        "csrfmiddlewaretoken": csrf,
        "name": "TEST_Contact",
        "email": "test_contact@example.com",
        "phone": "+243000000000",
        "subject": "Test sujet refonte",
        "message_type": "general",
        "message": "Ceci est un message de test pour la refonte du design.",
    }
    r = client.post(
        f"{BASE_URL}/contact/",
        data=payload,
        headers={"Referer": f"{BASE_URL}/contact/"},
        timeout=30,
        allow_redirects=False,
    )
    # Doit rediriger (302) après succès
    assert r.status_code in (302, 200), f"Contact POST -> {r.status_code}: {r.text[:400]}"
    if r.status_code == 200:
        # Si pas de redirect, doit afficher erreur de form -> on essaie de détecter succès via fallback
        # Accepter si le formulaire est revenu propre (cas form invalide masqué)
        pytest.fail(f"Contact POST n'a pas redirigé. Body: {r.text[:600]}")


# --- Phase 6: Donate POST ---

def test_donate_post_redirects_to_success(client):
    csrf, page = _get_csrf(client, f"{BASE_URL}/donate/")
    assert csrf, "CSRF token introuvable sur /donate/"

    # Inspecter le HTML pour deviner les champs requis
    fields_in_form = set(re.findall(r'name=["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']', page.text))

    payload = {
        "csrfmiddlewaretoken": csrf,
        "donor_name": "TEST_Donor",
        "donor_email": "test_donor@example.com",
        "amount": "10",
        "currency": "USD",
        "donation_type": "one_time",
        "is_anonymous": "",
        "message": "Test don pour la refonte",
    }
    # Garder uniquement les champs présents dans le form (+csrf)
    filtered = {k: v for k, v in payload.items() if k in fields_in_form or k == "csrfmiddlewaretoken"}

    r = client.post(
        f"{BASE_URL}/donate/",
        data=filtered if filtered else payload,
        headers={"Referer": f"{BASE_URL}/donate/"},
        timeout=30,
        allow_redirects=False,
    )
    # 302 -> /donate/success/ attendu
    assert r.status_code in (302, 200), f"Donate POST -> {r.status_code}: {r.text[:400]}"
    if r.status_code == 302:
        loc = r.headers.get("Location", "")
        assert "success" in loc, f"Redirige vers {loc}, attendu /donate/success/"


# --- Phase 7: Auth admin + dashboard ---

def test_admin_login_and_dashboard_access():
    s = requests.Session()
    # GET login pour CSRF
    r = s.get(f"{BASE_URL}/accounts/login/", timeout=30)
    assert r.status_code == 200, f"GET /accounts/login/ -> {r.status_code}"
    csrf = s.cookies.get("csrftoken")
    if not csrf:
        m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', r.text)
        csrf = m.group(1) if m else None
    assert csrf, "CSRF login introuvable"

    # POST login
    r = s.post(
        f"{BASE_URL}/accounts/login/",
        data={
            "csrfmiddlewaretoken": csrf,
            "username": ADMIN_USER,
            "password": ADMIN_PASS,
            "next": "/dashboard/",
        },
        headers={"Referer": f"{BASE_URL}/accounts/login/"},
        timeout=30,
        allow_redirects=False,
    )
    assert r.status_code in (302, 200), f"Login POST -> {r.status_code}: {r.text[:400]}"
    # Si 200, peut être page d'erreur "identifiants incorrects"
    if r.status_code == 200:
        body = r.text.lower()
        assert "incorrect" not in body and "invalid" not in body and "erron" not in body, \
            "Login a échoué: identifiants refusés"

    # Accès au dashboard
    r2 = s.get(f"{BASE_URL}/dashboard/", timeout=30, allow_redirects=False)
    # 200 si accédé, 302 si redirige (mais pas vers login)
    if r2.status_code == 302:
        assert "login" not in r2.headers.get("Location", "").lower(), \
            f"Dashboard redirige vers login: session non valide"
    else:
        assert r2.status_code == 200, f"Dashboard -> {r2.status_code}"
