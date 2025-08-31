"""
ETL Pipeline Main Module
"""

from .orchestrator import ETLOrchestrator, run_etl
from .models import JobOffer, ETLBatch, TJMRange, Location, Company
from .config import CONFIG, get_config
from .extractors import create_extractors
from .transformers import StandardTransformer
from .loaders import create_loaders, create_multi_loader

__version__ = "1.0.0"

__all__ = [
    "ETLOrchestrator",
    "run_etl", 
    "JobOffer",
    "ETLBatch",
    "TJMRange",
    "Location", 
    "Company",
    "CONFIG",
    "get_config",
    "create_extractors",
    "StandardTransformer",
    "create_loaders",
    "create_multi_loader"
]
