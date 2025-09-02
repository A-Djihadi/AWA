"""
Shared module initialization
"""

from .constants import *
from .logging_config import setup_service_logging, get_logger
from .validators import validate_scrape_request, validate_etl_request, validate_job_offer
from .utils import *
from .exceptions import *

__version__ = "1.0.0"
__all__ = [
    # Constants
    'ServicePorts', 'Paths', 'SpiderNames', 'FilePatterns', 'QualityThresholds',
    'TimeConstants', 'LogFormats', 'HttpStatus', 'RequiredFields', 'EnvVars',
    
    # Logging
    'setup_service_logging', 'get_logger',
    
    # Validation
    'validate_scrape_request', 'validate_etl_request', 'validate_job_offer',
    
    # Utilities
    'get_current_timestamp', 'format_duration', 'calculate_success_rate',
    'generate_batch_id', 'safe_json_load', 'safe_json_dump',
    
    # Exceptions
    'AWABaseException', 'ConfigurationError', 'ValidationError', 'ProcessingError',
    'ScrapingError', 'APIError', 'FileOperationError'
]
