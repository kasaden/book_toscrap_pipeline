"""
main.py
-------
Point d'entrée du pipeline ETL.
    Extract  → scraper.py   (récupération des données brutes)
    Transform → transform.py (nettoyage des prix et notes)
    Load     → export CSV    (sauvegarde dans data/)
"""

import logging
from pathlib import Path

from scraper import scrape_all_books
from transform import transform_books

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "books.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline ETL
# ---------------------------------------------------------------------------

def run_pipeline() -> None:
    """Exécute le pipeline ETL complet : Extract → Transform → Load."""

    # --- Extract ---
    logger.info("=== EXTRACT ===")
    raw_books = scrape_all_books()
    if not raw_books:
        logger.error("Aucune donnée extraite. Arrêt du pipeline.")
        return

    # --- Transform ---
    logger.info("=== TRANSFORM ===")
    df = transform_books(raw_books)
    if df.empty:
        logger.error("Aucune donnée après transformation. Arrêt du pipeline.")
        return

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


if __name__ == "__main__":
    run_pipeline()
