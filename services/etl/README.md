"""
ETL Pipeline for TJM Scraper Data Processing
============================================

A comprehensive ETL (Extract, Transform, Load) system that processes
scraped job data from various sources and loads it into a structured database.

## Architecture Overview

### Extract (E)
- Raw data extraction from JSONL files
- Support for multiple data sources (FreeWork, etc.)
- Data validation and format checking

### Transform (T)
- Data normalization and cleaning
- Technology extraction and standardization
- Salary range processing and validation
- Location normalization
- Company information processing
- Quality scoring and enrichment

### Load (L)
- Database operations (Supabase/PostgreSQL)
- Data deduplication
- Incremental updates
- Error handling and logging

## Components

1. **Extractors**: Read data from various sources
2. **Transformers**: Clean and normalize data
3. **Loaders**: Write data to target systems
4. **Orchestrator**: Manage the entire ETL process
5. **Quality**: Data validation and quality checks
6. **Monitoring**: Logging and metrics

## Usage

```python
from etl.orchestrator import ETLOrchestrator

# Run complete ETL pipeline
orchestrator = ETLOrchestrator()
results = orchestrator.run()
```

## Configuration

The ETL system uses environment variables for configuration:
- SUPABASE_URL: Database connection
- SUPABASE_SERVICE_ROLE_KEY: Database credentials
- ETL_LOG_LEVEL: Logging level
- ETL_BATCH_SIZE: Processing batch size
"""
