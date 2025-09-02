"""
Shared constants across all services
Following Clean Code principle: Avoid magic numbers and strings
"""

from enum import Enum
from typing import Dict, List


class ServicePorts(Enum):
    """Service port configuration"""
    SCRAPER = 8000
    ETL = 8001
    FRONTEND = 3000
    SCHEDULER = 8002


class Paths:
    """File system paths configuration"""
    DATA_RAW = "/app/data/raw"
    DATA_PROCESSED = "/app/data/processed"
    LOGS = "/app/logs"
    TEMP = "/app/temp"


class SpiderNames(Enum):
    """Available spider names"""
    FREEWORK = "freework"
    MALT = "malt"
    COMET = "comet"
    
    @classmethod
    def get_valid_spiders(cls) -> List[str]:
        """Get list of valid spider names"""
        return [spider.value for spider in cls]


class FilePatterns:
    """File pattern constants"""
    JSONL = "*.jsonl"
    JSON = "*.json"
    LOG = "*.log"


class QualityThresholds:
    """Data quality thresholds"""
    MIN_QUALITY_SCORE = 0.6
    MIN_REQUIRED_FIELDS = 3
    MAX_ERROR_RATE = 0.1


class TimeConstants:
    """Time-related constants in seconds"""
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000


class LogFormats:
    """Standardized log message formats"""
    SERVICE_START = "{service} service started on port {port}"
    SERVICE_ERROR = "{service} service error: {error}"
    PROCESS_START = "Starting {process} with {count} items"
    PROCESS_SUCCESS = "{process} completed successfully: {count} items processed in {duration:.2f}s"
    PROCESS_ERROR = "{process} failed after {duration:.2f}s: {error}"


class HttpStatus:
    """HTTP status codes for consistent API responses"""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class RequiredFields:
    """Required fields for data validation"""
    JOB_OFFER = ['title', 'source', 'source_id']
    ETL_REQUEST = ['source_directory']
    SCRAPE_REQUEST = ['spider']


# Environment variable names
class EnvVars:
    """Environment variable names"""
    SUPABASE_URL = "SUPABASE_URL"
    SUPABASE_KEY = "SUPABASE_SERVICE_ROLE_KEY"
    ETL_BATCH_SIZE = "ETL_BATCH_SIZE"
    ETL_MAX_WORKERS = "ETL_MAX_WORKERS"
    LOG_LEVEL = "LOG_LEVEL"
    DEBUG_MODE = "DEBUG_MODE"
