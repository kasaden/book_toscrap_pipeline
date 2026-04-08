"""
config.py
---------
Configuration centralisée du pipeline ETL.
Modifier ce fichier pour ajuster le comportement sans toucher à la logique métier.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

BASE_URL = "https://books.toscrape.com"
REQUEST_TIMEOUT = 10           # secondes avant abandon d'une requête
DELAY_BETWEEN_REQUESTS = 0.5   # secondes de pause entre chaque appel HTTP

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BookScraper/1.0; educational project)"
    )
}

# ---------------------------------------------------------------------------
# Stockage
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "books.csv"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
