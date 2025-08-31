"""
Modèles de données pour le scraper TJM
"""
from .job import Job, TJMRange, Company, Location
from .scraper_result import ScraperResult

__all__ = ['Job', 'TJMRange', 'Company', 'Location', 'ScraperResult']
