# Book to Scrape Pipeline

Pipeline ETL en Python qui scrape le catalogue [Books to Scrape](https://books.toscrape.com), nettoie les données et les exporte en CSV.

## Architecture

```
app/
├── config.py       # Configuration centralisée (URLs, timeouts, retry, chemins)
├── scraper.py      # Extract  — scraping par catégorie avec pagination
├── transform.py    # Transform — nettoyage des prix et notes + validation
└── main.py         # Orchestration du pipeline ETL
data/
└── books.csv       # Fichier de sortie (alimenté en append à chaque run)
Dockerfile          # Image Python 3.12-slim + cron
docker-compose.yml  # Monte data/ en volume persistant
crontab.sh          # Entrypoint : lance le pipeline puis planifie via cron
```

## Utilisation

### Avec Docker (recommandé)

```bash
docker compose up --build
```

Le pipeline tourne **immédiatement** au démarrage, puis **tous les jours à 3 heures** en automatique.

Les données sont persistées dans `data/books.csv` sur la machine hôte via un volume.

Pour arrêter le conteneur :

```bash
docker compose down
```

### En local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd app
python main.py
```

## Ce que fait le pipeline

Le pipeline extrait ~1000 livres avec 4 champs : **titre**, **prix**, **note** (1-5), **catégorie**.

Chaque run **ajoute** les nouvelles lignes au CSV existant (mode append) sans écraser l'historique.

## Logs

Les logs sont visibles en temps réel :

```bash
docker compose logs -f
```

## Gestion des erreurs

- Erreurs réseau / timeout : retry automatique avec backoff exponentiel (3 tentatives, 2–10s entre chaque)
- Toutes les tentatives échouent : le pipeline continue avec les données disponibles
- Champ HTML manquant : valeur ignorée, log warning
- Changement de structure HTML : alerte qualité si > 5% de valeurs manquantes sur un champ
