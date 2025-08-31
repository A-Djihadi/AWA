#!/bin/bash
echo "$(date): Nettoyage des anciennes données"

# Supprimer les fichiers de plus de 30 jours
find /app/data/raw -name "*.json" -mtime +30 -delete 2>/dev/null || true
find /app/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true

echo "$(date): Nettoyage terminé"
