# Déploiement d'AWA - Guide de production

## Prérequis

### Infrastructure
- **VPS**: 2 vCPU / 4GB RAM minimum
- **OS**: Ubuntu 20.04+ ou Debian 11+
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### Services externes
- **Supabase**: Projet configuré avec Postgres
- **Domain**: Nom de domaine avec certificat SSL
- **Registry**: GitHub Container Registry (GHCR)

## 1. Préparation du VPS

### Installation Docker
```bash
# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Ajout utilisateur au groupe docker
sudo usermod -aG docker $USER
```

### Configuration firewall
```bash
# UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 3000  # Next.js (optionnel si proxy)
```

## 2. Configuration du projet

### Clone du repository
```bash
cd /opt
sudo git clone https://github.com/votre-org/awa.git
sudo chown -R $USER:$USER awa
cd awa
```

### Variables d'environnement
```bash
# Copie des fichiers d'exemple
cp services/frontend/.env.example services/frontend/.env.local
cp services/scraper/.env.example services/scraper/.env
cp services/etl/.env.example services/etl/.env

# Configuration Supabase
nano services/frontend/.env.local
```

Remplir avec vos vraies valeurs:
```bash
NEXT_PUBLIC_SUPABASE_URL=https://votre-projet.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=votre_cle_anon
SUPABASE_SERVICE_ROLE_KEY=votre_cle_service_role
```

## 3. Configuration Supabase

### Migrations base de données
```bash
# Connexion à Supabase
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"

# Exécution migration
\i infra/migrations/001_initial_schema.sql
```

### Politiques RLS (Row Level Security)
```sql
-- Politique lecture publique pour offers
CREATE POLICY "Public read access" ON offers
FOR SELECT USING (true);

-- Politique écriture pour service role uniquement
CREATE POLICY "Service role write access" ON offers
FOR ALL USING (auth.role() = 'service_role');

-- Activer RLS
ALTER TABLE offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshots ENABLE ROW LEVEL SECURITY;
```

## 4. Déploiement avec Docker

### Build des images
```bash
# Build local
docker-compose build

# Ou pull depuis registry
docker login ghcr.io
docker-compose pull
```

### Lancement des services
```bash
# Démarrage
docker-compose up -d

# Vérification
docker-compose ps
docker-compose logs -f
```

### Configuration Nginx (reverse proxy)
```nginx
# /etc/nginx/sites-available/awa
server {
    listen 80;
    server_name votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Frontend Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health checks
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }
}
```

## 5. Scheduling & Automation

### Cron pour scraping
```bash
# Ajout au crontab
crontab -e

# Scraping hebdomadaire le dimanche à 2h
0 2 * * 0 cd /opt/awa && docker-compose exec -T scraper python -m scrapy crawl freelance_informatique

# Purge mensuelle des anciennes données
0 3 1 * * cd /opt/awa && docker-compose exec -T scraper python services/utils/purge_old_data.py
```

### Service systemd
```ini
# /etc/systemd/system/awa.service
[Unit]
Description=AWA TJM Tracker
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/awa
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Activation:
```bash
sudo systemctl enable awa.service
sudo systemctl start awa.service
```

## 6. Monitoring & Maintenance

### Logs centralisés
```bash
# Visualisation logs
docker-compose logs -f --tail=100

# Logs par service
docker-compose logs scraper
docker-compose logs frontend
docker-compose logs etl

# Export logs
docker-compose logs --no-color > /var/log/awa.log
```

### Health checks
```bash
# Script de monitoring
#!/bin/bash
# /opt/awa/scripts/health_check.sh

# Vérification services
if ! curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
    echo "Frontend down" | mail -s "AWA Alert" admin@votre-domaine.com
fi

if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "Scraper down" | mail -s "AWA Alert" admin@votre-domaine.com
fi
```

Cron de surveillance:
```bash
# Toutes les 5 minutes
*/5 * * * * /opt/awa/scripts/health_check.sh
```

### Backup automatique
```bash
#!/bin/bash
# /opt/awa/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/awa"

# Backup base de données (dump Supabase)
pg_dump "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres" > $BACKUP_DIR/awa_db_$DATE.sql

# Backup fichiers de configuration
tar -czf $BACKUP_DIR/awa_config_$DATE.tar.gz /opt/awa/.env* /opt/awa/infra/

# Nettoyage anciens backups (>30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## 7. Mise à jour & CI/CD

### Déploiement automatique
```bash
#!/bin/bash
# /opt/awa/scripts/deploy.sh

# Pull dernière version
cd /opt/awa
git pull origin main

# Update images
docker-compose pull

# Restart services
docker-compose down
docker-compose up -d

# Vérification
sleep 30
curl -f http://localhost:3000/api/health || exit 1
```

### Webhook de déploiement
```bash
# Script appelé par GitHub webhook
#!/bin/bash
# /opt/awa/scripts/webhook_deploy.sh

cd /opt/awa
/opt/awa/scripts/deploy.sh

# Log du déploiement
echo "$(date): Deployment completed" >> /var/log/awa_deploy.log
```

## 8. Sécurité

### SSL/TLS
```bash
# Certbot pour Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

### Sécurisation Docker
```bash
# Création utilisateur non-root pour containers
sudo groupadd -g 1001 awa
sudo useradd -u 1001 -g awa -s /bin/false awa
```

### Rotation des secrets
```bash
# Script de rotation des clés API
#!/bin/bash
# Génération nouvelle clé service Supabase
# Mise à jour variables d'environnement
# Restart des services
```

## 9. Performance

### Optimisation Docker
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  scraper:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    restart: unless-stopped
    
  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped
```

### Cache et CDN
- Vercel Edge Network pour le frontend
- Supabase Edge Functions si nécessaire
- Cache Nginx pour les assets statiques

## 10. Troubleshooting

### Problèmes fréquents
```bash
# Container qui ne démarre pas
docker-compose logs [service_name]

# Espace disque insuffisant
docker system prune -a
docker volume prune

# Base de données inaccessible
# Vérifier variables SUPABASE_URL
# Vérifier politiques RLS

# Scraping bloqué
# Vérifier User-Agent
# Vérifier rate limiting
# Contrôler les proxies
```

### Rollback rapide
```bash
# Retour version précédente
git checkout HEAD~1
docker-compose down
docker-compose build
docker-compose up -d
```

---

**Contact**: admin@votre-domaine.com  
**Documentation**: https://docs.votre-domaine.com  
**Monitoring**: https://monitoring.votre-domaine.com
