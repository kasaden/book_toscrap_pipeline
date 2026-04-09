"""
config.py
---------
Configuration centralisée du pipeline ETL.
Modifier ce fichier pour ajuster le comportement sans toucher à la logique métier.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

BASE_URL = "https://books.toscrape.com"
REQUEST_TIMEOUT = 10           # secondes avant abandon d'une requête
DELAY_BETWEEN_REQUESTS = 0.5   # secondes de pause entre chaque appel HTTP

RETRY_ATTEMPTS = 3             # nombre de tentatives avant abandon
RETRY_WAIT_MIN = 2             # secondes d'attente minimum entre deux tentatives
RETRY_WAIT_MAX = 10            # secondes d'attente maximum entre deux tentatives

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

# ---------------------------------------------------------------------------
# Notifications e-mail (valeurs lues depuis les variables d'environnement)
# ---------------------------------------------------------------------------

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER")        # expéditeur
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")    # mot de passe d'application Gmail
ALERT_EMAIL   = [a.strip() for a in os.getenv("ALERT_EMAIL", "").split(",") if a.strip()]
