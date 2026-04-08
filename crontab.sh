#!/bin/bash
# Indique au noyau quel programme utiliser pour exécuter ce script

# Définir le chemin vers l'exécutable
PYTHON=/usr/local/bin/python

# Rendre les variables du .env dispo pour cron 
# Export uniquement de SPTM et ALERT pour éviter de polluer avec le reste
printenv | grep -E "^(SMTP_|ALERT_)" >> /etc/environment

# Lancer une première fois immédiatement au démarrage du conteneur
cd /pipeline/app && $PYTHON main.py

# Enregistrer la tâche cron (tous les jours à 3h)
# ". /etc/environment" recharge les vars persistées avant chaque exécution
echo "0 3 * * * . /etc/environment; cd /pipeline/app && $PYTHON main.py >> /proc/1/fd/1 2>/proc/1/fd/2" | crontab -

# Démarrer cron en foreground (nécessaire pour Docker)
exec cron -f
