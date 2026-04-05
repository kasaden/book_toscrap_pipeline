# Book to Scrape Pipeline

Pipeline ETL en Python qui scrape le catalogue [Books to Scrape](https://books.toscrape.com), nettoie les données et les exporte en CSV.

## Architecture

```
app/
├── scraper.py      # Extract  — scraping par catégorie avec pagination
├── transform.py    # Transform — nettoyage des prix et notes + validation
└── main.py         # Orchestration du pipeline ETL
data/
└── books.csv       # Fichier de sortie
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Utilisation

```bash
cd app
python main.py
```

Le pipeline extrait 1000 livres avec 4 champs : **titre**, **prix**, **note** (1-5), **catégorie**.

Le CSV est généré dans `data/books.csv`.

## Gestion des erreurs

- Erreurs réseau / timeout : le pipeline continue avec les données disponibles
- Champ HTML manquant : valeur ignorée, log warning
- Changement de structure HTML : alerte qualité si > 5% de valeurs manquantes sur un champ
