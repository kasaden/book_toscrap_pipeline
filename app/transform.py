"""
transform.py
------------
Nettoyer et transformer les données brutes extraites par le scraper.
- Prix : "£12.99" → 12.99 (float)
- Note : "Three" → 3 (int)
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Correspondance note textuelle → valeur numérique
# ---------------------------------------------------------------------------

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


# ---------------------------------------------------------------------------
# Fonctions de nettoyage unitaires
# ---------------------------------------------------------------------------

def clean_price(raw_price: str | None) -> float | None:
    """Convertit '£12.99' en 12.99. Retourne None si le format est invalide."""
    if not raw_price:
        return None
    try:
        cleaned = raw_price.replace("£", "").replace("Â", "").strip()
        return float(cleaned)
    except ValueError:
        logger.warning("Prix invalide ignoré : '%s'", raw_price)
        return None


def clean_rating(raw_rating: str | None) -> int | None:
    """Convertit 'Three' en 3. Retourne None si la valeur est inconnue."""
    if not raw_rating:
        return None
    value = RATING_MAP.get(raw_rating)
    if value is None:
        logger.warning("Note inconnue ignorée : '%s'", raw_rating)
    return value


# ---------------------------------------------------------------------------
# Transformation du jeu de données complet
# ---------------------------------------------------------------------------

def transform_books(raw_books: list[dict]) -> pd.DataFrame:
    """
    Transforme la liste brute de livres en DataFrame propre.

    Étapes :
    1. Conversion en DataFrame
    2. Nettoyage des prix et des notes
    3. Suppression des lignes sans titre
    """
    if not raw_books:
        logger.warning("Aucune donnée brute à transformer.")
        return pd.DataFrame(columns=["title", "price", "rating", "category"])

    df = pd.DataFrame(raw_books)

    df["price"] = df["price"].apply(clean_price)
    df["rating"] = df["rating"].apply(clean_rating)

    rows_before = len(df)
    df = df.dropna(subset=["title"])
    rows_dropped = rows_before - len(df)
    if rows_dropped:
        logger.warning("%d lignes sans titre supprimées.", rows_dropped)

    logger.info("Transformation terminée : %d livres nettoyés.", len(df))
    return df
