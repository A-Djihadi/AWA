#!/usr/bin/env python3
"""
AWA Scraper Runner

Optimized script to run the TJM scraper with proper configuration.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def setup_logging(debug=False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )


def run_scraper(output_file=None, settings_overrides=None):
    """
    Run the FreeWork spider
    
    Args:
        output_file: Output JSON file path
        settings_overrides: Dict of setting overrides
    """
    logger = logging.getLogger(__name__)
    
    # Get default settings
    settings = get_project_settings()
    
    # Apply overrides
    if settings_overrides:
        for key, value in settings_overrides.items():
            settings.set(key, value)
    
    # Set output file
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"freework_jobs_{timestamp}.json"
    
    # Configure output
    settings.set('FEEDS', {
        output_file: {
            'format': 'json',
            'encoding': 'utf8',
            'store_empty': False,
            'indent': 2
        }
    })
    
    logger.info(f"Starting scraper with output: {output_file}")
    
    # Run spider
    process = CrawlerProcess(settings)
    process.crawl('freework')
    process.start()
    
    logger.info(f"Scraping completed. Output saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run AWA TJM Scraper")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--delay", type=int, help="Download delay in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--limit", type=int, help="Limit number of items to scrape")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.debug)
    
    # Prepare settings overrides
    overrides = {}
    if args.delay:
        overrides['DOWNLOAD_DELAY'] = args.delay
    if args.debug:
        overrides['LOG_LEVEL'] = 'DEBUG'
    if args.limit:
        overrides['CLOSESPIDER_ITEMCOUNT'] = args.limit
    
    run_scraper(output_file=args.output, settings_overrides=overrides)


if __name__ == "__main__":
    main()
