"""
ETL Configuration and Settings
"""
import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ETLConfig:
    """ETL Configuration settings"""
    
    # Database Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Processing Configuration
    batch_size: int = 100
    max_workers: int = 4
    
    # Data Sources
    data_source_dir: str = "/app/data/raw"
    processed_dir: str = "/app/data/processed"
    
    # Quality Thresholds
    min_quality_score: float = 0.6
    required_fields: list = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/app/logs/etl.log"
    
    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = ['title', 'source', 'source_id']


def get_config() -> ETLConfig:
    """Get ETL configuration from environment variables"""
    
    config = ETLConfig()
    
    # Database
    config.supabase_url = os.getenv('SUPABASE_URL', '')
    config.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    
    # Processing
    config.batch_size = int(os.getenv('ETL_BATCH_SIZE', '100'))
    config.max_workers = int(os.getenv('ETL_MAX_WORKERS', '4'))
    
    # Paths
    config.data_source_dir = os.getenv('ETL_SOURCE_DIR', '/app/data/raw')
    config.processed_dir = os.getenv('ETL_PROCESSED_DIR', '/app/data/processed')
    
    # Quality
    config.min_quality_score = float(os.getenv('ETL_MIN_QUALITY', '0.6'))
    
    # Logging
    config.log_level = os.getenv('ETL_LOG_LEVEL', 'INFO')
    config.log_file = os.getenv('ETL_LOG_FILE', '/app/logs/etl.log')
    
    return config


# Global configuration instance
CONFIG = get_config()
