FROM python:3.11-slim

# Installer cron et curl
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
