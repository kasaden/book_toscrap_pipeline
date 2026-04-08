"""
scraper.py
----------
Récupérer les données brutes depuis books.toscrape.com.
- Navigation par catégories
- Pagination
- Extraction brute des champs (titre, prix, note, catégorie)
"""

# déja présentes par défaut, on importe pour la clarté
import logging
import time

# bibliothèques externes — à installer via pip
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, before_log, after_log

from config import BASE_URL, DELAY_BETWEEN_REQUESTS, HEADERS, REQUEST_TIMEOUT, RETRY_ATTEMPTS, RETRY_WAIT_MIN, RETRY_WAIT_MAX

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CATALOGUE_URL = f"{BASE_URL}/catalogue"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Couche HTTP — une seule fonction fait les requêtes
# ---------------------------------------------------------------------------

@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_WAIT_MIN, max=RETRY_WAIT_MAX),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.WARNING),
    reraise=False,
)
def _fetch_page_with_retry(url: str) -> requests.Response:
    """
    Effectue la requête HTTP avec retry automatique.
    Lève une exception si le statut n'est pas 200, ce qui déclenche un retry.
    """
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"Statut inattendu {response.status_code} pour : {url}"
        )
    return response


def fetch_page(url: str) -> BeautifulSoup | None:
    """
    Télécharge une page et retourne un objet BeautifulSoup.
    Réessaie jusqu'à RETRY_ATTEMPTS fois avec backoff exponentiel.

    Retourne None si toutes les tentatives échouent.
    Ne lève jamais d'exception vers l'appelant.
    """
    try:
        response = _fetch_page_with_retry(url)
    except requests.exceptions.ConnectionError:
        logger.error("Impossible de joindre le site : %s (erreur réseau)", url)
        return None
    except requests.exceptions.Timeout:
        logger.error("Délai dépassé pour : %s (timeout %ss)", url, REQUEST_TIMEOUT)
        return None
    except requests.exceptions.RequestException as exc:
        logger.error("Échec après %d tentatives pour %s : %s", RETRY_ATTEMPTS, url, exc)
        return None

    time.sleep(DELAY_BETWEEN_REQUESTS)
    return BeautifulSoup(response.text, "html.parser")


# ---------------------------------------------------------------------------
# Extraction des catégories
# ---------------------------------------------------------------------------

def get_categories(soup: BeautifulSoup) -> list[dict]:
    """
    Extrait toutes les catégories depuis le menu latéral de la page d'accueil.

    Retourne une liste de dicts : [{"name": str, "url": str}, ...]
    Retourne une liste vide si le menu est introuvable.
    """
    categories = []

    nav = soup.find("ul", class_="nav-list")
    if not nav:
        logger.error("Menu des catégories introuvable dans le HTML.")
        return categories

    # Le premier <li> est "Books" (toutes catégories) — on le saute
    for link in nav.find_all("a")[1:]:
        name = link.get_text(strip=True)
        relative_url = link.get("href", "")

        if not relative_url:
            logger.warning("Catégorie '%s' ignorée : URL manquante.", name)
            continue

        categories.append({
            "name": name,
            "url": f"{BASE_URL}/{relative_url}",
        })

    logger.info("%d catégories trouvées.", len(categories))
    return categories


# ---------------------------------------------------------------------------
# Extraction des livres — une page de catégorie
# ---------------------------------------------------------------------------

def get_books_from_page(soup: BeautifulSoup, category_name: str) -> list[dict]:
    """
    Extrait les données brutes de tous les livres présents sur une page.

    Chaque livre est un dict :
    {
        "title"    : str | None,
        "price"    : str | None,   # ex. "£12.99" — nettoyé dans transform.py
        "rating"   : str | None,   # ex. "Three"  — converti dans transform.py
        "category" : str,
    }
    """
    books = []
    articles = soup.find_all("article", class_="product_pod")

    if not articles:
        logger.warning(
            "Aucun livre trouvé sur cette page (catégorie : %s).", category_name
        )
        return books

    for article in articles:
        book = _extract_book_fields(article, category_name)
        books.append(book)

    return books


def _extract_book_fields(article: BeautifulSoup, category_name: str) -> dict:
    """
    Extrait les champs bruts d'un article HTML individuel.
    Chaque champ est extrait indépendamment : un échec n'annule pas les autres.
    """
    title = _extract_title(article)
    price = _extract_price(article)
    rating = _extract_rating(article)

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "category": category_name,
    }


def _extract_title(article: BeautifulSoup) -> str | None:
    """Extrait le titre depuis l'attribut 'title' de la balise <a>."""
    try:
        return article.h3.a["title"]
    except (AttributeError, KeyError, TypeError):
        logger.warning("Titre introuvable pour un article.")
        return None


def _extract_price(article: BeautifulSoup) -> str | None:
    """Extrait le prix brut (ex. '£12.99') depuis la balise .price_color."""
    try:
        return article.find("p", class_="price_color").get_text(strip=True)
    except AttributeError:
        logger.warning("Prix introuvable pour un article.")
        return None


def _extract_rating(article: BeautifulSoup) -> str | None:
    """
    Extrait la note textuelle (ex. 'Three') depuis la classe CSS du tag <p>.
    La note est encodée comme : class="star-rating Three".
    """
    try:
        rating_tag = article.find("p", class_="star-rating")
        classes = rating_tag.get("class", [])
        # classes = ["star-rating", "Three"] → on veut le 2e élément
        return classes[1] if len(classes) > 1 else None
    except AttributeError:
        logger.warning("Note introuvable pour un article.")
        return None


# ---------------------------------------------------------------------------
# Pagination — parcourt toutes les pages d'une catégorie
# ---------------------------------------------------------------------------

def get_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    """
    Détecte l'URL de la page suivante dans la pagination.
    Retourne None s'il n'y a pas de page suivante.
    """
    next_btn = soup.find("li", class_="next")
    if not next_btn:
        return None

    next_link = next_btn.find("a")
    if not next_link:
        return None

    relative_next = next_link.get("href", "")
    # L'URL suivante est relative à la page courante, pas à la racine
    base = current_url.rsplit("/", 1)[0]
    return f"{base}/{relative_next}"


def scrape_category(category: dict) -> list[dict]:
    """
    Scrape tous les livres d'une catégorie en gérant la pagination.

    Paramètre :
        category : {"name": str, "url": str}

    Retourne une liste de dicts de livres bruts.
    """
    books = []
    url = category["url"]
    name = category["name"]
    page_number = 1

    logger.info("Début scraping — catégorie : '%s'", name)

    while url:
        logger.debug("  Page %d : %s", page_number, url)

        soup = fetch_page(url)
        if soup is None:
            logger.warning(
                "Page %d ignorée pour '%s' — arrêt de la catégorie.", page_number, name
            )
            break  # On s'arrête sur cette catégorie mais le pipeline continue

        page_books = get_books_from_page(soup, name)
        books.extend(page_books)

        url = get_next_page_url(soup, url)
        page_number += 1

    logger.info(
        "Fin scraping — catégorie : '%s' | %d livres récupérés.", name, len(books)
    )
    return books


# ---------------------------------------------------------------------------
# Point d'entrée du module — appelé par main.py
# ---------------------------------------------------------------------------

def scrape_all_books() -> list[dict]:
    """
    Fonction principale du module.
    Scrape l'intégralité du catalogue et retourne tous les livres bruts.

    Retourne une liste vide si la page d'accueil est inaccessible.
    """
    logger.info("=== Démarrage du scraping ===")

    home_soup = fetch_page(BASE_URL)
    if home_soup is None:
        logger.error("Impossible d'accéder à la page d'accueil. Abandon.")
        return []

    categories = get_categories(home_soup)
    if not categories:
        logger.error("Aucune catégorie trouvée. Abandon.")
        return []

    all_books = []
    for category in categories:
        category_books = scrape_category(category)
        all_books.extend(category_books)

    logger.info(
        "=== Scraping terminé | %d livres au total ===", len(all_books)
    )
    return all_books