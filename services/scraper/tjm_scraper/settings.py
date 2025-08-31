"""
Configuration Scrapy pour AWA TJM Scraper
"""

# Scrapy settings for tjm_scraper project
BOT_NAME = 'awa-tjm-scraper'

SPIDER_MODULES = ['tjm_scraper.spiders']
NEWSPIDER_MODULE = 'tjm_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Configure delays
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Configure item pipelines (simplifié pour tests)
ITEM_PIPELINES = {
    'tjm_scraper.pipelines.ValidationPipeline': 300,
    'tjm_scraper.pipelines.DuplicatesPipeline': 400,
    'tjm_scraper.pipelines.JsonFilesPipeline': 600,
}

# Configure logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(levelname)s: %(message)s'

# Request meta
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Files storage
FILES_STORE = './data/raw'

# Custom settings
FEEDS = {
    './data/raw/%(name)s_%(time)s.jsonl': {
        'format': 'jsonlines',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
    },
}

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Supabase configuration (from environment)
import os
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Test mode
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'
