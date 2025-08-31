#!/bin/bash
SCRAPER_URL="${SCRAPER_SERVICE_URL:-http://scraper:8000}"
ETL_URL="${ETL_SERVICE_URL:-http://etl:8001}"

echo "$(date): Health check des services"

# Check scraper
if curl -f "$SCRAPER_URL/health" > /dev/null 2>&1; then
  echo "$(date): ✅ Scraper OK"
else
  echo "$(date): ❌ Scraper DOWN"
fi

# Check ETL  
if curl -f "$ETL_URL/health" > /dev/null 2>&1; then
  echo "$(date): ✅ ETL OK"
else
  echo "$(date): ❌ ETL DOWN"
fi
