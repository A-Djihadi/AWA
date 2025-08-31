FROM python:3.11-slim

# Métadonnées
LABEL maintainer="awa-team"
LABEL description="AWA ETL Service - Pipeline de traitement des données"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN groupadd -r etl && useradd -r -g etl etl

# Définir le répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les répertoires de données
RUN mkdir -p /app/data/raw /app/data/processed /app/logs
RUN chown -R etl:etl /app

# Changer vers l'utilisateur non-root
USER etl

# Exposer le port pour l'API
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Commande par défaut : lancer l'API FastAPI
CMD ["python", "api.py"]
