# 🔄 Cycle de Vie du Logiciel AWA - Analyse Complète

## 📋 État Actuel du Projet

### ✅ Composants Fonctionnels
- **Scraper** : Scrapy fonctionnel (16 offres Freework collectées)
- **ETL** : Pipeline opérationnel (41 records traités, 23 offres en base)
- **Base de données** : Supabase configuré et connecté
- **Frontend** : Structure Next.js avec connexion Supabase
- **Configuration** : Système centralisé refactorisé

### ⚠️ Composants Manquants/Incomplets
- **Service Scheduler** : Absent (référencé dans docker-compose mais pas implémenté)
- **Cron Jobs** : Pas d'orchestration automatique
- **Frontend complet** : API routes existantes mais composants UI à finaliser
- **Déploiement** : GitHub Actions configuré mais déploiement non implémenté

## 🔄 Scénario Type du Cycle de Vie

### 1. **Développement Local** 
```bash
# Setup initial
python scripts/setup.py --interactive
python scripts/env_manager.py validate

# Tests manuels
cd services/scraper && python -m scrapy crawl freework
cd services/etl && python run_simple_etl.py
cd services/frontend && npm run dev
```

### 2. **Intégration Continue (GitHub Actions)**
```yaml
# Déclenché sur : push main, pull requests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

# Pipeline :
1. test-scraper → Tests unitaires Python/Scrapy
2. test-frontend → Tests Jest/TypeScript, linting
3. build-and-push → Build Docker images et push vers GHCR
4. deploy → Déploiement production (non implémenté)
```

### 3. **Production (Scénario Cible)**
```bash
# Déploiement via Docker Compose
docker-compose up -d

# Services actifs :
- scraper:8000     (Scrapy + API)  
- etl:8001         (Pipeline ETL)
- scheduler:8002   (Cron orchestration) ⚠️ MANQUANT
- frontend:3000    (Next.js dashboard)
- monitoring:9100  (Node exporter)
```

## 🕐 Orchestration par Cron (PROBLÈME IDENTIFIÉ)

### ❌ Problème Actuel
Le **service scheduler** est référencé dans le `docker-compose.yml` mais **n'existe pas** :

```yaml
# services/scheduler/Dockerfile - INEXISTANT
# services/scheduler/crontab - INEXISTANT  
# services/scheduler/scripts/ - INEXISTANT
```

### 🎯 Cron Workflow Cible (À Implémenter)
```bash
# Crontab dans le service scheduler
# Extraction hebdomadaire le dimanche à 2h
0 2 * * 0 /app/scripts/run_scraper.sh freework
0 3 * * 0 /app/scripts/run_scraper.sh malt  
0 4 * * 0 /app/scripts/run_scraper.sh comet

# ETL quotidien à 6h
0 6 * * * /app/scripts/run_etl.sh

# Nettoyage mensuel le 1er à 1h
0 1 1 * * /app/scripts/cleanup_old_data.sh
```

## 🔗 Connexion Frontend ↔ Supabase

### ✅ Configuration Existante
```typescript
// lib/supabase.ts - FONCTIONNEL
export const supabase = createClient(supabaseUrl, supabaseKey)
export const createServerClient = () => createClient(url, serviceRoleKey)
```

### ✅ API Routes Existantes
```typescript
// app/api/offers/route.ts - FONCTIONNEL
GET /api/offers?limit=50&tech=React&location=Paris
POST /api/offers (création d'offres)

// app/api/stats/route.ts - À VÉRIFIER
GET /api/stats (statistiques globales)
```

### ⚠️ Composants UI Manquants
```typescript
// À créer/compléter :
- Dashboard principal avec graphiques TJM
- Filtres par technologie/localisation  
- Tables d'offres avec pagination
- Graphiques évolution temporelle
- Cartes/géolocalisation
```

## 📊 Flux de Données Complet

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Sites TJM     │───▶│   Scrapers   │───▶│     ETL     │───▶│   Supabase   │───▶│  Frontend   │
│                 │    │              │    │             │    │              │    │             │
│ • Freework      │    │ • Scrapy     │    │ • Transform │    │ • PostgreSQL │    │ • Next.js   │
│ • Malt          │    │ • Playwright │    │ • Validate  │    │ • RLS        │    │ • Dashboard │
│ • Comet         │    │ • JSON out   │    │ • Load      │    │ • 23 offers  │    │ • API       │
└─────────────────┘    └──────────────┘    └─────────────┘    └──────────────┘    └─────────────┘
                              ▲                    ▲                                        
                              │                    │                                        
                       ┌──────────────┐    ┌─────────────┐                                 
                       │  Scheduler   │    │  Monitoring │                                 
                       │              │    │             │                                 
                       │ • Cron jobs  │    │ • Logs      │                                 
                       │ • Webhook    │    │ • Metrics   │                                 
                       │ ⚠️ MANQUANT  │    │ • Alerts    │                                 
                       └──────────────┘    └─────────────┘                                 
```

## 🚧 Étapes Restantes pour Finaliser

### 1. **Créer le Service Scheduler** (CRITIQUE)

<function_calls>
<invoke name="create_file">
<parameter name="content">#!/bin/bash
# Script pour créer le service scheduler manquant

echo "🏗️ Création du service scheduler..."

# Créer la structure
mkdir -p services/scheduler/{scripts,cron,logs}

# Dockerfile pour le scheduler
cat > services/scheduler/Dockerfile << 'EOF'
FROM python:3.11-slim

# Installer cron
RUN apt-get update && apt-get install -y cron curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier les scripts
COPY scripts/ ./scripts/
COPY cron/crontab /etc/cron.d/awa-scheduler

# Permissions
RUN chmod 0644 /etc/cron.d/awa-scheduler
RUN chmod +x ./scripts/*.sh

# Logs
RUN touch /var/log/cron.log

# Démarrage
CMD cron && tail -f /var/log/cron.log
EOF

# Requirements du scheduler
cat > services/scheduler/requirements.txt << 'EOF'
requests==2.31.0
docker==6.1.3
python-crontab==3.0.0
pydantic==2.4.2
EOF

# Crontab
cat > services/scheduler/cron/crontab << 'EOF'
# AWA Scheduler Crontab
# Extraction hebdomadaire le dimanche à 2h
0 2 * * 0 /app/scripts/run_scraper.sh freework >> /var/log/cron.log 2>&1
0 3 * * 0 /app/scripts/run_scraper.sh malt >> /var/log/cron.log 2>&1  
0 4 * * 0 /app/scripts/run_scraper.sh comet >> /var/log/cron.log 2>&1

# ETL quotidien à 6h
0 6 * * * /app/scripts/run_etl.sh >> /var/log/cron.log 2>&1

# Nettoyage mensuel le 1er à 1h
0 1 1 * * /app/scripts/cleanup_old_data.sh >> /var/log/cron.log 2>&1

# Health check toutes les heures
0 * * * * /app/scripts/health_check.sh >> /var/log/cron.log 2>&1
EOF

# Script de lancement du scraper
cat > services/scheduler/scripts/run_scraper.sh << 'EOF'
#!/bin/bash
SCRAPER_URL="${SCRAPER_SERVICE_URL:-http://scraper:8000}"
SPIDER_NAME="${1:-freework}"

echo "$(date): Lancement scraper $SPIDER_NAME"

# Déclencher le scraper via API
curl -X POST "$SCRAPER_URL/api/scrape" \
  -H "Content-Type: application/json" \
  -d "{\"spider\": \"$SPIDER_NAME\"}" \
  || echo "$(date): Erreur scraper $SPIDER_NAME"
EOF

# Script ETL
cat > services/scheduler/scripts/run_etl.sh << 'EOF'  
#!/bin/bash
ETL_URL="${ETL_SERVICE_URL:-http://etl:8001}"

echo "$(date): Lancement ETL"

# Déclencher l'ETL via API
curl -X POST "$ETL_URL/api/process" \
  -H "Content-Type: application/json" \
  || echo "$(date): Erreur ETL"
EOF

# Script de nettoyage
cat > services/scheduler/scripts/cleanup_old_data.sh << 'EOF'
#!/bin/bash
echo "$(date): Nettoyage des anciennes données"

# Supprimer les fichiers de plus de 30 jours
find /app/data/raw -name "*.json" -mtime +30 -delete
find /app/logs -name "*.log" -mtime +7 -delete

echo "$(date): Nettoyage terminé"
EOF

# Script health check
cat > services/scheduler/scripts/health_check.sh << 'EOF'
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
EOF

# Permissions
chmod +x services/scheduler/scripts/*.sh

echo "✅ Service scheduler créé!"
echo "📋 Prochaines étapes:"
echo "  1. Implémenter les endpoints /api/scrape et /api/process"
echo "  2. Tester : docker-compose up scheduler"
echo "  3. Vérifier les logs : docker logs awa-scheduler"
