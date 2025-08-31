# Guide de test du scraper en local

## Prérequis

### Installation Python
Assurez-vous d'avoir Python 3.11+ installé :
```bash
python --version
```

### Installation des dépendances
```bash
cd services/scraper
pip install -r requirements.txt
```

## Configuration

### 1. Variables d'environnement
Le fichier `.env` est déjà configuré pour les tests locaux. Modifiez-le si nécessaire :
```bash
# services/scraper/.env
TEST_MODE=true
LOG_LEVEL=DEBUG
```

### 2. Création des dossiers de données
```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs
```

## Tests disponibles

### 1. Test de configuration Scrapy
Vérifiez que Scrapy est correctement configuré :
```bash
cd services/scraper
python -m scrapy list
```
*Résultat attendu : liste des spiders (test, freelance_informatique)*

### 2. Test du spider de base
Testez avec le spider simple :
```bash
python -m scrapy crawl test
```
*Ce spider fait un test basique avec httpbin.org*

### 3. Test du spider Freelance Informatique (mode dry-run)
```bash
python -m scrapy crawl freelance_informatique -s TEST_MODE=true -s CONCURRENT_REQUESTS=1
```

### 4. Test avec sauvegarde fichier uniquement
```bash
python -m scrapy crawl freelance_informatique -s ITEM_PIPELINES='{"tjm_scraper.pipelines.ValidationPipeline": 300, "tjm_scraper.pipelines.JsonFilesPipeline": 600}'
```

### 5. Test avec limite de pages
```bash
python -m scrapy crawl freelance_informatique -s CLOSESPIDER_PAGECOUNT=2
```

## Debugging

### Logs détaillés
```bash
python -m scrapy crawl test -L DEBUG
```

### Utilisation du shell Scrapy
Pour tester l'extraction sur une page spécifique :
```bash
python -m scrapy shell "https://httpbin.org/html"
```

### Profiling des performances
```bash
python -m scrapy crawl test -s STATS_CLASS=scrapy.statscollectors.MemoryStatsCollector
```

## Structure des fichiers de sortie

### Fichiers JSON générés
Les données scrappées sont sauvées dans :
```
data/raw/
├── test_20250831_142030.jsonl
├── freelance_informatique_20250831_142130.jsonl
└── ...
```

### Format des données
```json
{
  "source": "test",
  "source_id": "test_001",
  "title": "Test Job Offer",
  "company": "Test Company",
  "tjm_min": 400,
  "tjm_max": 600,
  "tjm_currency": "EUR",
  "technologies": ["Python", "Scrapy"],
  "seniority_level": "mid",
  "location": "Paris",
  "remote_policy": "hybrid",
  "contract_type": "freelance",
  "description": "...",
  "url": "...",
  "scraped_at": "2025-08-31T14:20:30"
}
```

## Tests unitaires

### Lancement des tests
```bash
cd ../../  # Retour à la racine du projet
python -m pytest tests/scraper/ -v
```

### Tests avec couverture
```bash
python -m pytest tests/scraper/ --cov=tjm_scraper --cov-report=html
```

## Troubleshooting

### Erreur "Module not found"
```bash
# Assurez-vous d'être dans le bon répertoire
cd services/scraper
export PYTHONPATH=.
```

### Problème de User-Agent
Si vous êtes bloqué, modifiez le User-Agent dans `settings.py`

### Problème de connexion
En mode test, la connexion Supabase n'est pas requise.

### Logs trop verbeux
Réduisez le niveau de log :
```bash
python -m scrapy crawl test -L INFO
```

## Commandes utiles

### Lister les spiders
```bash
python -m scrapy list
```

### Obtenir des infos sur un spider
```bash
python -m scrapy info freelance_informatique
```

### Tester une URL spécifique
```bash
python -m scrapy parse https://httpbin.org/html --spider=test
```

### Nettoyer les caches
```bash
rm -rf data/.scrapy_cache
```
