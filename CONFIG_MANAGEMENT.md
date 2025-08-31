# 🔧 AWA Environment Configuration Management

Ce document décrit la nouvelle approche centralisée pour gérer les configurations d'environnement dans le projet AWA.

## 🎯 Objectifs

- **Centralisation** : Configuration partagée entre tous les services
- **Cohérence** : Éviter la duplication et les incohérences
- **Sécurité** : Gestion appropriée des secrets et clés sensibles
- **Maintenabilité** : Faciliter les mises à jour et la synchronisation

## 📁 Structure des fichiers

```
awa/
├── .env.shared                 # ✨ Configuration partagée (nouveau)
├── scripts/
│   └── env_manager.py         # 🔧 Utilitaire de gestion (nouveau)
└── services/
    ├── scraper/
    │   ├── .env               # 🔄 Configuration spécifique (refactorisé)
    │   └── .env.example       # 📋 Template (mis à jour)
    ├── etl/
    │   ├── .env               # 🔄 Configuration spécifique (refactorisé)
    │   └── .env.example       # 📋 Template (mis à jour)
    └── frontend/
        ├── .env.local         # 🔄 Configuration spécifique
        └── .env.example       # 📋 Template
```

## 🚀 Utilisation

### Configuration initiale

1. **Copier la configuration partagée :**
   ```bash
   cp .env.shared services/scraper/.env
   cp .env.shared services/etl/.env
   ```

2. **Adapter chaque service selon ses besoins spécifiques**

### Gestion avec l'utilitaire

```bash
# Vérifier la cohérence des configurations
python scripts/env_manager.py validate

# Voir le status des configurations
python scripts/env_manager.py status

# Synchroniser depuis la config partagée (simulation)
python scripts/env_manager.py sync --dry-run

# Synchroniser réellement
python scripts/env_manager.py sync

# Générer les fichiers .env.example
python scripts/env_manager.py examples
```

## 📋 Variables par service

### 🔗 Variables partagées (`.env.shared`)

- `SUPABASE_URL` : URL du projet Supabase
- `SUPABASE_ANON_KEY` : Clé publique Supabase
- `SUPABASE_SERVICE_ROLE_KEY` : Clé de service Supabase
- `LOG_LEVEL` : Niveau de logging global
- `APP_NAME` : Nom de l'application
- Configurations de chemins et limites par défaut

### 🕷️ Scraper spécifique

- `SCRAPY_*` : Configuration Scrapy
- `SCRAPER_*` : Paramètres du scraper
- `HTTP_PROXY`, `HTTPS_PROXY` : Configuration proxy
- `SENTRY_DSN` : Monitoring

### ⚙️ ETL spécifique

- `ETL_*` : Configuration pipeline ETL
- `BATCH_SIZE`, `PARALLEL_WORKERS` : Ancienne nomenclature supportée
- Settings de base de données et performance

### 🖥️ Frontend spécifique

- `NEXT_PUBLIC_*` : Variables publiques Next.js
- `NODE_ENV` : Environnement Node.js
- `GA_*` : Analytics

## 🔐 Sécurité

### Variables sensibles

⚠️ **Ne jamais commiter** les vraies valeurs de :
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_ANON_KEY`
- `SENTRY_DSN`
- Toute variable contenant `PASSWORD`, `SECRET`, `TOKEN`, `KEY`

### Fichiers à ignorer

Ajouter dans `.gitignore` :
```gitignore
# Environment files
.env
.env.local
.env.*.local
.env.shared

# Keep templates
!.env.example
!.env.*.example
```

## 🔄 Workflow de mise à jour

### Pour une nouvelle variable globale

1. Ajouter dans `.env.shared`
2. Exécuter `python scripts/env_manager.py sync`
3. Vérifier avec `python scripts/env_manager.py validate`
4. Générer les examples : `python scripts/env_manager.py examples`

### Pour une variable spécifique à un service

1. Ajouter directement dans le `.env` du service
2. S'assurer que le préfixe est dans `service_specific_vars` de `env_manager.py`

## 🧪 Tests et validation

### Vérification manuelle

```bash
# Vérifier que Supabase est accessible
python -c "
import os
from dotenv import load_dotenv
load_dotenv('services/etl/.env')
print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
print('Key configurée:', bool(os.getenv('SUPABASE_SERVICE_ROLE_KEY')))
"
```

### Tests automatisés

```bash
# Tester la cohérence
python scripts/env_manager.py validate

# Vérifier que tous les services ont les variables requises
for service in scraper etl frontend; do
    echo "=== $service ==="
    cd services/$service
    python -c "
import os
from dotenv import load_dotenv
load_dotenv()
required = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
for var in required:
    print(f'{var}: {\"✅\" if os.getenv(var) else \"❌\"}')"
    cd ../..
done
```

## 📚 Bonnes pratiques

### 🔄 Synchronisation régulière

- Exécuter `sync` après chaque modification de `.env.shared`
- Valider après chaque synchronisation
- Tenir à jour les fichiers `.env.example`

### 🏷️ Nomenclature

- Préfixer les variables par le nom du service : `ETL_`, `SCRAPER_`, etc.
- Utiliser UPPER_CASE avec underscores
- Grouper logiquement (DATABASE_, API_, CACHE_, etc.)

### 📝 Documentation

- Documenter les nouvelles variables dans ce README
- Maintenir les commentaires dans les fichiers .env
- Expliquer les valeurs par défaut et les impacts

## 🔧 Dépannage

### Problème : Variables non trouvées

```bash
# Vérifier la présence du fichier
ls -la services/*/,env

# Vérifier le contenu
python scripts/env_manager.py status
```

### Problème : Incohérences entre services

```bash
# Identifier les différences
python scripts/env_manager.py validate

# Synchroniser
python scripts/env_manager.py sync
```

### Problème : Variables sensibles exposées

1. Vérifier `.gitignore`
2. Supprimer du commit : `git rm --cached .env`
3. Utiliser `.env.example` avec valeurs masquées

## 🚀 Évolutions futures

- [ ] Intégration avec Docker Compose
- [ ] Support pour différents environnements (dev, staging, prod)
- [ ] Chiffrement des valeurs sensibles
- [ ] Validation automatique dans CI/CD
- [ ] Interface web pour la gestion des configs
