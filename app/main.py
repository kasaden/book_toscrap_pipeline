"""
main.py
-------
Point d'entrée du pipeline ETL.
    Extract  → scraper.py   (récupération des données brutes)
    Transform → transform.py (nettoyage des prix et notes)
    Load     → export CSV    (sauvegarde dans data/)
"""

import logging
import sys

from config import DATA_DIR, LOG_FORMAT, LOG_LEVEL, OUTPUT_FILE
from notify import notify_failure, notify_success
from scraper import scrape_all_books
from transform import transform_books

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline ETL
# ---------------------------------------------------------------------------

def run_pipeline() -> None:
    """Exécute le pipeline ETL complet : Extract → Transform → Load."""
    try:
        # --- Extract ---
        logger.info("=== EXTRACT ===")
        raw_books = scrape_all_books()
        if not raw_books:
            raise RuntimeError("Aucune donnée extraite.")

        # --- Transform ---
        logger.info("=== TRANSFORM ===")
        df = transform_books(raw_books)
        if df.empty:
            raise RuntimeError("Aucune donnée après transformation.")

        # --- Load ---
        logger.info("=== LOAD ===")
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Append au fichier existant pour conserver l'historique des runs.
        # Si le fichier n'existe pas encore, on écrit l'en-tête.
        write_header = not OUTPUT_FILE.exists()
        df.to_csv(
            OUTPUT_FILE,
            mode="a",
            header=write_header,
            index=False,
            encoding="utf-8",
        )

        logger.info(
            "Fichier CSV enrichi : %s (+%d lignes ce run)", OUTPUT_FILE, len(df)
        )
        logger.info("=== Pipeline terminé avec succès ===")
        notify_success(len(df))

    except Exception as e:
        logger.exception("=== Pipeline en ÉCHEC : %s ===", e)
        notify_failure(e)
        sys.exit(1)   # code de sortie non-zéro → cron sait que ça a échoué


if __name__ == "__main__":
    run_pipeline()
