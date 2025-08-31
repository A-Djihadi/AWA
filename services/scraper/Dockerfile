# Dockerfile pour Scraper Service (Python/Scrapy)
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="awa-team"
LABEL description="AWA Scraper Service - Scrapy/Playwright pour extraction TJM"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Installation de Chrome pour Playwright
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt pyproject.toml ./

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Installation des navigateurs Playwright
RUN playwright install --with-deps chromium

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs data/raw data/processed

# Création d'un utilisateur non-root pour la sécurité
RUN groupadd -r scraper && useradd -r -g scraper scraper
RUN chown -R scraper:scraper /app
USER scraper

# Port d'exposition (pour health checks)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Script d'entrée
COPY entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh
USER scraper

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "scrapy", "list"]
