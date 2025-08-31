"""
Configuration principale du scraper refactorisé
"""
import os
from datetime import datetime


# Configuration Scrapy
BOT_NAME = 'awa-tjm-scraper-v2'

SPIDER_MODULES = ['src.scraper.spiders']
NEWSPIDER_MODULE = 'src.scraper.spiders'

# Respect des robots.txt
ROBOTSTXT_OBEY = False

# Configuration des requêtes
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Cookies et sessions
COOKIES_ENABLED = True

# User-Agent
USER_AGENT = 'AWA-Scraper/2.0 (+https://awa-project.com)'

# Configuration des middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 110,
}

# Codes de statut pour retry
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]
RETRY_TIMES = 3

# Configuration des pipelines
ITEM_PIPELINES = {
    'src.scraper.pipelines.ValidationPipeline': 300,
    'src.scraper.pipelines.DeduplicationPipeline': 400,
    'src.scraper.pipelines.EnrichmentPipeline': 500,
    'src.scraper.pipelines.ExportPipeline': 800,
}

# Configuration du logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(levelname)s: %(message)s'

# Génération automatique du nom de fichier avec timestamp
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# Configuration des exports
FEEDS = {
    f'data/processed/jobs_{TIMESTAMP}.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 2,
    },
    f'data/processed/jobs_{TIMESTAMP}.jsonl': {
        'format': 'jsonlines',
        'encoding': 'utf8',
        'store_empty': False,
    },
}

# Extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'src.scraper.extensions.StatsExtension': 500,
}

# Configuration AutoThrottle pour adaptation automatique
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Headers par défaut
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Configuration de cache (pour développement)
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'data/cache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403, 404]

# Métriques et monitoring
STATS_CLASS = 'src.scraper.stats.CustomStatsCollector'

# Configuration des données
DATA_CONFIG = {
    'output_dir': 'data/processed',
    'backup_dir': 'data/backup',
    'temp_dir': 'data/temp',
    'max_file_size_mb': 100,
    'compression': True,
}

# Configuration de validation
VALIDATION_CONFIG = {
    'strict_mode': False,
    'required_fields': ['source', 'source_id', 'title'],
    'tjm_range': (50, 3000),
    'max_title_length': 200,
    'max_description_length': 5000,
}

# Configuration d'enrichissement
ENRICHMENT_CONFIG = {
    'enable_geocoding': False,
    'enable_company_matching': True,
    'enable_skill_normalization': True,
    'api_timeout': 10,
}

# Configuration par environnement
ENVIRONMENT = os.getenv('SCRAPY_ENV', 'development')

if ENVIRONMENT == 'production':
    # Configuration production
    CONCURRENT_REQUESTS = 8
    DOWNLOAD_DELAY = 1
    LOG_LEVEL = 'WARNING'
    HTTPCACHE_ENABLED = False
    
elif ENVIRONMENT == 'development':
    # Configuration développement
    LOG_LEVEL = 'DEBUG'
    HTTPCACHE_ENABLED = True
    
elif ENVIRONMENT == 'testing':
    # Configuration test
    CONCURRENT_REQUESTS = 1
    DOWNLOAD_DELAY = 5
    CLOSESPIDER_ITEMCOUNT = 10
