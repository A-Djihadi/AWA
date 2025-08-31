# Architecture AWA - Another Weather Application

## 1. Schéma fonctionnel - Flux de données

```
[UTILISATEUR] 
    └─ (navigue) -> [Next.js Dashboard (UI)]
                          ├─ Requêtes -> (Serverless API / Supabase client)
                          └─ Affiche -> Graphes TJM / filtres par techno, séniorité, période
                                 ^
                                 │
                                 │ (lecture)
                                 │
                       [Supabase Postgres (offers, snapshots)]
                                 ^
                                 │ (insert / update / read)
                                 │
                       [ETL Normalization Service]  <-- (consumes)
                                 ^                         raw JSON
                                 │
                                 │ (push raw data)
                       [Scrapers hebdo (Spiders Docker)]  <- Cron hebdo (scheduler)
                                 │
                                 └─(raw JSON files OR direct DB writes + raw table archive)
```

### Points d'entrée / sortie

- **Entrée principale**: Sites cibles (HTTP) → spiders naviguent et produisent JSON/NDJSON
- **Sortie principale**: Supabase Postgres (tables: offers, snapshots, raw_offers)
- **Interface utilisateur**: Next.js dashboard avec agrégations via Supabase

## 2. Schéma technique - Architecture

### Cloud (Supabase)
```
CLOUD (Supabase)
 ├─ Postgres managé (Supabase) 
 │    ├─ tables: offers, snapshots, raw_offers, techs_map
 │    └─ storage: backups / archived raw files (.ndjson)
 └─ Auth + Storage (fichiers exports/archives)
```

### VPS Docker (2vCPU/4GB)
```
VPS (Docker Compose)
 ├─ scraper-service (docker)   # Scrapy / Playwright
 │     └─ cron hebdomadaire
 ├─ etl-service (docker)       # pandas, currency conversion, tech mapping
 │     └─ triggered après scraping
 ├─ uploader-service (docker)  # archivage vers Supabase Storage
 ├─ scheduler (docker)         # cron ou GitHub Actions webhook
 └─ monitoring (docker)        # health-checks, logs
```

### Frontend Deployment
```
Next.js
 ├─ Vercel hosting (ou VPS container)
 │    └─ Supabase client (server-side + API routes)
 └─ Serverless API pour requêtes sécurisées
```

## 3. Stack technique

| Composant | Technologies | Justification |
|-----------|-------------|---------------|
| **Frontend** | Next.js 14, TypeScript, Tailwind, Recharts | SSR, performance, DX moderne |
| **Scraping** | Python, Scrapy, Playwright, BeautifulSoup | Robustesse, anti-détection |
| **ETL** | Python, Pandas, Pydantic | Transformation données, validation |
| **Database** | Supabase Postgres, RLS policies | Managé, sécurisé, scalable |
| **Storage** | Supabase Storage | Archives, backups, intégration |
| **Containers** | Docker, Docker Compose | Isolation, déploiement simple |
| **Monitoring** | Sentry, Logflare, Health checks | Observabilité production |
| **CI/CD** | GitHub Actions | Tests automatisés, déploiement |

## 4. Modèle de données

### Table `offers`
```sql
CREATE TABLE offers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(200),
    tjm_min INTEGER,
    tjm_max INTEGER,
    tjm_currency VARCHAR(3) DEFAULT 'EUR',
    technologies TEXT[],
    seniority_level VARCHAR(20),
    location VARCHAR(200),
    remote_policy VARCHAR(20),
    contract_type VARCHAR(20),
    description TEXT,
    url VARCHAR(1000),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    normalized_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(source, source_id)
);
```

### Table `snapshots`
```sql
CREATE TABLE snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    technology VARCHAR(100) NOT NULL,
    seniority VARCHAR(20),
    tjm_median INTEGER,
    tjm_avg INTEGER,
    tjm_p25 INTEGER,
    tjm_p75 INTEGER,
    sample_size INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(period_start, period_end, technology, seniority)
);
```

## 5. Sécurité & Monitoring

### Sécurité
- **Supabase RLS**: Policies par utilisateur/rôle
- **Rate limiting**: Anti-DDoS sur scrapers
- **Secrets management**: Environment variables, GitHub Secrets
- **TLS**: Partout (Vercel, Supabase, VPS)

### Monitoring
- **Logs structurés**: JSON format, niveaux, contexte
- **Health checks**: Endpoints pour chaque service
- **Alertes**: Sentry pour erreurs critiques
- **Métriques**: Supabase dashboard, Docker stats

### Backup & Recovery
- **Daily snapshots**: Supabase automatic backups
- **Raw data archive**: NDJSON vers Supabase Storage
- **Migration scripts**: SQL versionnées
- **Disaster recovery**: Procédures documentées

## 6. Évolutivité

### Phase 1 (MVP)
- Sites de référence (2-3 sources)
- Dashboard basique avec filtres
- Scraping hebdomadaire manuel

### Phase 2 (Production)
- 10+ sources de données
- ML pour détection anomalies TJM
- API publique avec rate limiting
- Notifications utilisateurs

### Phase 3 (Scale)
- Migration Kubernetes si besoin
- Cache Redis pour performances
- Streaming data avec Apache Kafka
- Multi-tenant SaaS
