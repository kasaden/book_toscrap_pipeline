"""
notify.py
---------
Envoi d'e-mails de statut (succès ou échec) du pipeline.

Utilise uniquement la bibliothèque standard (smtplib + email),
aucune dépendance supplémentaire n'est requise.

Les paramètres SMTP sont lus depuis config.py, lui-même alimenté
par les variables d'environnement définies dans le fichier .env.
"""

import logging
import smtplib
import traceback
from datetime import datetime
from email.message import EmailMessage

from config import ALERT_EMAIL, OUTPUT_FILE, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger(__name__)


def _send(subject: str, body: str) -> None:
    """Fonction interne : construit et envoie un e-mail via SMTP/STARTTLS."""
    if not all([SMTP_USER, SMTP_PASSWORD]) or not ALERT_EMAIL:
        logger.warning(
            "Notification ignorée : SMTP_USER, SMTP_PASSWORD ou ALERT_EMAIL "
            "non définis dans les variables d'environnement."
        )
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join(ALERT_EMAIL)
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("E-mail envoyé à %s — %s", ", ".join(ALERT_EMAIL), subject)
    except Exception as smtp_error:
        logger.warning("Échec de l'envoi de l'e-mail : %s", smtp_error)


def notify_success(row_count: int) -> None:
    """Envoie un e-mail de confirmation quand le pipeline s'est bien déroulé.

    Args:
        row_count: Nombre de livres exportés lors de ce run.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _send(
        subject=f"[Book to scrap] Success — {timestamp}",
        body=(
            f"The ETL pipeline completed successfully on {timestamp}.\n\n"
            f"Books exported this run: {row_count}\n"
            f"Output file: {OUTPUT_FILE}"
        ),
    )


def notify_failure(error: Exception) -> None:
    """Envoie un e-mail d'alerte si les variables SMTP sont configurées.

    L'envoi est silencieux en cas d'erreur : un simple warning est loggué
    pour ne pas masquer l'erreur originale du pipeline.

    Args:
        error: L'exception qui a causé l'échec du pipeline.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_traceback = traceback.format_exc()
    _send(
        subject=f"[Book to scrap] Failure — {timestamp}",
        body=(
            f"The ETL pipeline failed on {timestamp}.\n\n"
            f"Error: {type(error).__name__}: {error}\n\n"
            f"Full traceback:\n{full_traceback}"
        ),
    )
