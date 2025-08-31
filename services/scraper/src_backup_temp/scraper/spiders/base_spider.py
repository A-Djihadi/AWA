"""
Spider de base avec architecture propre
"""
import scrapy
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..models import Job, ScraperResult, TJMRange, Company, Location
from ..extractors import (
    TJMExtractor, TechnologyExtractor, LocationExtractor,
    CompanyExtractor, TextExtractor
)
from ..utils import DataValidator, URLValidator


class BaseJobSpider(scrapy.Spider, ABC):
    """Spider de base pour tous les sites d'emploi"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuration des extracteurs
        self.tjm_extractor = TJMExtractor()
        self.tech_extractor = TechnologyExtractor()
        self.location_extractor = LocationExtractor()
        self.company_extractor = CompanyExtractor()
        self.text_extractor = TextExtractor()
        
        # Configuration du logging
        self.setup_logging()
        
        # Statistiques
        self.stats = {
            'pages_visited': 0,
            'jobs_found': 0,
            'jobs_valid': 0,
            'errors': 0
        }
        
        # Résultats
        self.scraper_result = ScraperResult(source=self.name)
        self.scraper_result.stats.start_time = datetime.now()
    
    def setup_logging(self):
        """Configure le logging pour le spider"""
        self.logger = logging.getLogger(self.name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def parse(self, response):
        """Méthode principale de parsing"""
        self.stats['pages_visited'] += 1
        self.logger.info(f"🔍 Parsing listing: {response.url}")
        
        try:
            # Extraire les liens vers les offres
            job_urls = self.extract_job_urls(response)
            self.logger.info(f"✅ Trouvé {len(job_urls)} liens de missions")
            
            # Suivre chaque lien
            for url in job_urls:
                if URLValidator.is_valid_url(url):
                    yield response.follow(url, self.parse_job)
                else:
                    self.logger.warning(f"❌ URL invalide: {url}")
            
            # Pagination si nécessaire
            next_page = self.extract_next_page_url(response)
            if next_page:
                yield response.follow(next_page, self.parse)
                
        except Exception as e:
            self.handle_error(f"Erreur parsing listing {response.url}: {e}")
    
    def parse_job(self, response):
        """Parse une page d'offre d'emploi"""
        self.logger.info(f"🎯 Parsing mission: {response.url}")
        
        try:
            job = self.extract_job_data(response)
            
            if job and job.is_valid:
                self.stats['jobs_valid'] += 1
                self.scraper_result.add_job(job)
                
                # Log des informations importantes
                self.logger.info(
                    f"✅ Job extrait: {job.title} | "
                    f"TJM: {job.tjm} | "
                    f"Qualité: {job.quality_score:.2f}"
                )
                
                yield job.to_dict()
            else:
                self.logger.warning(f"❌ Job invalide ou incomplet: {response.url}")
                
        except Exception as e:
            self.handle_error(f"Erreur parsing job {response.url}: {e}")
    
    def extract_job_data(self, response) -> Optional[Job]:
        """Extrait toutes les données d'un job"""
        try:
            # Créer l'objet Job
            job = Job(
                source=self.name,
                source_id=self.extract_source_id(response),
                url=response.url
            )
            
            # Extraire le titre
            job.title = self.text_extractor.extract_title(response)
            
            # Extraire la description
            job.description = self.text_extractor.extract_description(response)
            
            # Extraire le TJM
            job.tjm = self.tjm_extractor.extract(response)
            
            # Extraire l'entreprise
            job.company = self.company_extractor.extract(response)
            
            # Extraire la localisation
            job.location = self.location_extractor.extract(response)
            
            # Extraire les technologies
            job.technologies = self.tech_extractor.extract(response)
            
            # Extraire les métadonnées spécifiques au site
            self.extract_site_specific_data(response, job)
            
            # Validation finale
            validation_errors = DataValidator.validate_job_data(job.to_dict())
            if validation_errors:
                for error in validation_errors:
                    self.logger.warning(f"⚠️ Validation: {error}")
            
            self.stats['jobs_found'] += 1
            return job
            
        except Exception as e:
            self.handle_error(f"Erreur extraction job: {e}")
            return None
    
    def extract_source_id(self, response) -> str:
        """Extrait l'ID unique de l'offre pour ce site"""
        # Par défaut, utiliser l'URL ou une partie de l'URL
        url_parts = response.url.split('/')
        return url_parts[-1] if url_parts else response.url
    
    def handle_error(self, error_message: str):
        """Gère les erreurs de manière centralisée"""
        self.stats['errors'] += 1
        self.scraper_result.add_error(error_message)
        self.logger.error(error_message)
    
    def closed(self, reason):
        """Appelé à la fermeture du spider"""
        self.scraper_result.stats.end_time = datetime.now()
        
        # Log du résumé final
        summary = self.scraper_result.get_summary()
        self.logger.info("="*80)
        self.logger.info("📊 RÉSUMÉ FINAL DU SCRAPING")
        self.logger.info("="*80)
        
        for key, value in summary.items():
            self.logger.info(f"{key}: {value}")
        
        self.logger.info(f"Raison de fermeture: {reason}")
    
    # Méthodes abstraites à implémenter par les spiders concrets
    
    @abstractmethod
    def extract_job_urls(self, response) -> List[str]:
        """Extrait les URLs des offres depuis une page de listing"""
        pass
    
    def extract_next_page_url(self, response) -> Optional[str]:
        """Extrait l'URL de la page suivante (optionnel)"""
        return None
    
    def extract_site_specific_data(self, response, job: Job):
        """Extrait des données spécifiques au site (optionnel)"""
        pass
    
    # Méthodes utilitaires
    
    def get_custom_settings(self) -> Dict[str, Any]:
        """Retourne les settings personnalisés pour ce spider"""
        return {
            'DOWNLOAD_DELAY': 2,
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            'COOKIES_ENABLED': True,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
            'USER_AGENT': f'AWA-{self.name.title()}-Scraper/2.0'
        }
