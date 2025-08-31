#!/bin/bash
SCRAPER_URL="${SCRAPER_SERVICE_URL:-http://scraper:8000}"
SPIDER_NAME="${1:-freework}"

echo "$(date): Lancement scraper $SPIDER_NAME"

# Déclencher le scraper via API
curl -X POST "$SCRAPER_URL/api/scrape" \
  -H "Content-Type: application/json" \
  -d "{\"spider\": \"$SPIDER_NAME\"}" \
  || echo "$(date): Erreur scraper $SPIDER_NAME"
