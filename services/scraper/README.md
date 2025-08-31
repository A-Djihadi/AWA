# AWA Scraper

TJM job scraper for FreeWork platform.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper
scrapy crawl freework -o jobs.json

# With custom settings
scrapy crawl freework -s LOG_LEVEL=INFO -o jobs.json
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Scraping settings
DOWNLOAD_DELAY=2
USER_AGENT=AWA-TJM-Scraper/1.0

# Database (optional)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
```

## Output

The scraper extracts:
- Job title and description
- Company information
- TJM (daily rate)
- Technologies
- Location
- Contract details

## Architecture

- `tjm_scraper/spiders/freework.py` - Main spider
- `tjm_scraper/items.py` - Data models
- `tjm_scraper/pipelines.py` - Data processing
- `tjm_scraper/settings.py` - Configuration
