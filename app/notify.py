"""
notify.py
---------
Envoi d'une alerte e-mail en cas d'échec du pipeline.

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

from config import ALERT_EMAIL, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger(__name__)


def notify_failure(error: Exception) -> None:
    """Envoie un e-mail d'alerte si les variables SMTP sont configurées.

    L'envoi est silencieux en cas d'erreur : un simple warning est loggué
    pour ne pas masquer l'erreur originale du pipeline.

    Args:
        error: L'exception qui a causé l'échec du pipeline.
    """
    # --- Vérification de la configuration ---
    if not all([SMTP_USER, SMTP_PASSWORD, ALERT_EMAIL]):
        logger.warning(
            "Notification ignorée : SMTP_USER, SMTP_PASSWORD ou ALERT_EMAIL "
            "non définis dans les variables d'environnement."
        )
        return

    # --- Construction du message ---
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_traceback = traceback.format_exc()

    msg = EmailMessage()
    msg["Subject"] = f"[Pipeline] Échec — {timestamp}"
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL
    msg.set_content(
        f"Le pipeline ETL a rencontré une erreur le {timestamp}.\n\n"
        f"Erreur : {type(error).__name__}: {error}\n\n"
        f"Traceback complet :\n{full_traceback}"
    )

    # --- Envoi via SMTP avec STARTTLS ---
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Alerte e-mail envoyée à %s", ALERT_EMAIL)
    except Exception as smtp_error:
        logger.warning("Échec de l'envoi de l'alerte e-mail : %s", smtp_error)
