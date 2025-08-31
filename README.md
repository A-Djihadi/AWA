# AWA - Another Weather Application

Un tracker de taux journaliers moyens (TJM) pour développeurs freelance avec architecture cloud moderne.

## 🏗️ Architecture

### Option C: Supabase + VPS Docker

- **Frontend**: Next.js (Vercel/VPS) avec Supabase client
- **Backend**: Microservices Docker sur VPS
- **Database**: Supabase Postgres managé
- **Storage**: Supabase Storage pour archives
- **Scraping**: Scrapy/Playwright containers avec cron hebdomadaire

## 🚀 Quick Start

```bash
# Clone & setup
git clone <repo>
cd awa

# Setup environment
cp services/frontend/.env.example services/frontend/.env.local
cp services/scraper/.env.example services/scraper/.env
cp services/etl/.env.example services/etl/.env

# Development
docker-compose up -d
cd services/frontend && npm run dev
```

## 📊 Flux de données

```
[Sites TJM] → [Scrapers] → [ETL] → [Supabase] → [Next.js Dashboard]
     ↓           ↓          ↓         ↓            ↓
  HTTP req   Raw JSON   Normalized  Postgres    UI/Graphs
```

## 🏃‍♂️ Services

| Service | Tech | Port | Description |
|---------|------|------|-------------|
| Frontend | Next.js | 3000 | Dashboard TJM avec graphiques |
| Scraper | Python/Scrapy | - | Extraction hebdomadaire |
| ETL | Python/Pandas | - | Normalisation & mapping |
| Scheduler | Cron | - | Orchestration jobs |

## 📚 Documentation

- [Architecture détaillée](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)
- [API Documentation](./docs/api.md)
- [Monitoring & Logs](./docs/monitoring.md)

## 🧪 Tests

```bash
# Unit tests scrapers
cd services/scraper && python -m pytest

# Frontend tests
cd services/frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up
```

## 🔧 Maintenance

```bash
# DB migrations
psql $SUPABASE_URL -f infra/migrations/XXX_migration.sql

# Purge old data
docker run --rm awa-utils python scripts/purge_old_data.py

# Manual scraping
docker run --rm awa-scraper python -m scrapy crawl freelance_tjm
```

## 🛡️ Security

- Supabase RLS policies
- Secrets via environment variables
- Rate limiting sur scrapers
- TLS partout

## 📈 Monitoring

- Logs centralisés (JSON format)
- Health checks containers
- Alertes Sentry pour échecs scraping
- Métriques Supabase

---

**Maintainers**: [@votre-username]  
**License**: MIT
