#!/bin/bash
# Indique au noyau quel programme utiliser pour exécuter ce script

# Définir le chemin vers l'exécutable
PYTHON=/usr/local/bin/python

# Lancer une première fois immédiatement au démarrage du conteneur
cd /pipeline/app && $PYTHON main.py

# Enregistrer la tâche cron (toutes les deux minutes)
echo "*/2 * * * * cd /pipeline/app && $PYTHON main.py >> /proc/1/fd/1 2>/proc/1/fd/2" | crontab -

# Démarrer cron en foreground (nécessaire pour Docker)
exec cron -f
