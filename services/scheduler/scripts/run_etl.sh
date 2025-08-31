#!/bin/bash
ETL_URL="${ETL_SERVICE_URL:-http://etl:8001}"

echo "$(date): Lancement ETL"

# Déclencher l'ETL via API
curl -X POST "$ETL_URL/api/process" \
  -H "Content-Type: application/json" \
  || echo "$(date): Erreur ETL"
