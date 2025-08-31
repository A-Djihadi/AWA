"""
Spider FreeWork refactorisé avec architecture propre
"""
import re
from typing import List, Optional
from urllib.parse import urljoin

from .base_spider import BaseJobSpider
from ..models import Job, ContractType, SeniorityLevel, RemotePolicy


class FreeWorkSpiderRefactored(BaseJobSpider):
    """Spider FreeWork avec architecture refactorisée"""
    
    name = 'freework_v2'
    allowed_domains = ['free-work.com']
    start_urls = [
        'https://www.free-work.com/fr/tech-it/jobs?locations=fr~~~'
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuration spécifique à FreeWork
        self.base_url = 'https://www.free-work.com'
        
        # Patterns spécifiques à FreeWork
        self.freework_patterns = {
            'job_links': [
                'a[href*="/job-mission/"]::attr(href)',
                'a[href*="/mission/"]::attr(href)',
                '[class*="job"] a::attr(href)'
            ],
            'pagination': [
                '.pagination a[href]:last-child::attr(href)',
                'a[rel="next"]::attr(href)',
                '.next-page::attr(href)'
            ]
        }
    
    @property
    def custom_settings(self):
        """Settings personnalisés pour FreeWork"""
        base_settings = self.get_custom_settings()
        base_settings.update({
            'USER_AGENT': 'AWA-FreeWork-Scraper/2.0',
            'DOWNLOAD_DELAY': 3,  # Plus conservateur pour FreeWork
        })
        return base_settings
    
    def extract_job_urls(self, response) -> List[str]:
        """Extrait les URLs des offres FreeWork"""
        job_urls = []
        
        # Essayer différents sélecteurs
        for selector in self.freework_patterns['job_links']:
            urls = response.css(selector).getall()
            job_urls.extend(urls)
        
        # Convertir en URLs absolues et dédupliquer
        absolute_urls = []
        seen_urls = set()
        
        for url in job_urls:
            if url and url not in seen_urls:
                absolute_url = urljoin(self.base_url, url)
                absolute_urls.append(absolute_url)
                seen_urls.add(url)
        
        return absolute_urls
    
    def extract_next_page_url(self, response) -> Optional[str]:
        """Extrait l'URL de la page suivante"""
        for selector in self.freework_patterns['pagination']:
            next_url = response.css(selector).get()
            if next_url:
                return urljoin(self.base_url, next_url)
        return None
    
    def extract_source_id(self, response) -> str:
        """Extrait l'ID unique FreeWork"""
        # Pattern URL FreeWork: /job-mission/titre-job-123
        url_parts = response.url.split('/')
        
        # Prendre la dernière partie qui contient souvent l'ID
        if url_parts:
            last_part = url_parts[-1]
            # Extraire les chiffres à la fin
            match = re.search(r'-(\d+)$', last_part)
            if match:
                return f"freework_{match.group(1)}"
            else:
                return f"freework_{last_part}"
        
        return f"freework_{hash(response.url) % 100000}"
    
    def extract_site_specific_data(self, response, job: Job):
        """Extrait des données spécifiques à FreeWork"""
        try:
            # Déterminer le type de contrat
            job.contract_type = self._extract_contract_type(response)
            
            # Déterminer le niveau de séniorité
            job.seniority_level = self._extract_seniority_level(response)
            
            # Déterminer la politique de télétravail
            job.remote_policy = self._extract_remote_policy(response)
            
            # Extraire des métadonnées supplémentaires
            self._extract_freework_metadata(response, job)
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction données FreeWork: {e}")
    
    def _extract_contract_type(self, response) -> ContractType:
        """Détermine le type de contrat"""
        text = response.text.lower()
        
        # FreeWork est principalement orienté freelance
        if any(word in text for word in ['freelance', 'indépendant', 'mission']):
            return ContractType.FREELANCE
        elif any(word in text for word in ['cdi', 'temps plein', 'permanent']):
            return ContractType.PERMANENT
        elif any(word in text for word in ['cdd', 'temporaire', 'contrat court']):
            return ContractType.TEMPORARY
        
        return ContractType.FREELANCE  # Par défaut pour FreeWork
    
    def _extract_seniority_level(self, response) -> Optional[SeniorityLevel]:
        """Détermine le niveau de séniorité"""
        text = response.text.lower()
        
        # Chercher les indicateurs de séniorité
        if any(word in text for word in ['senior', 'expérimenté', 'expert', 'lead', 'principal']):
            return SeniorityLevel.SENIOR
        elif any(word in text for word in ['junior', 'débutant', 'stagiaire']):
            return SeniorityLevel.JUNIOR
        elif any(word in text for word in ['intermédiaire', 'confirmé', 'medior']):
            return SeniorityLevel.INTERMEDIATE
        
        # Analyser les années d'expérience
        exp_pattern = r'(\d+)\s*(?:ans?|années?)\s*(?:d.)?expérience'
        match = re.search(exp_pattern, text)
        if match:
            years = int(match.group(1))
            if years <= 2:
                return SeniorityLevel.JUNIOR
            elif years <= 5:
                return SeniorityLevel.INTERMEDIATE
            else:
                return SeniorityLevel.SENIOR
        
        return None
    
    def _extract_remote_policy(self, response) -> RemotePolicy:
        """Détermine la politique de télétravail"""
        text = response.text.lower()
        
        if any(word in text for word in ['100% remote', 'full remote', 'télétravail complet']):
            return RemotePolicy.REMOTE
        elif any(word in text for word in ['hybride', 'télétravail partiel', 'mixte']):
            return RemotePolicy.HYBRID
        elif any(word in text for word in ['présentiel', 'sur site', 'bureau obligatoire']):
            return RemotePolicy.ONSITE
        elif any(word in text for word in ['flexible', 'télétravail possible']):
            return RemotePolicy.FLEXIBLE
        
        return RemotePolicy.FLEXIBLE  # Par défaut
    
    def _extract_freework_metadata(self, response, job: Job):
        """Extrait des métadonnées spécifiques à FreeWork"""
        # Extraire la durée de mission
        duration = self._extract_mission_duration(response)
        if duration:
            if not hasattr(job, 'metadata'):
                job.metadata = {}
            job.metadata['mission_duration'] = duration
        
        # Extraire le taux de réponse du client
        response_rate = self._extract_client_response_rate(response)
        if response_rate:
            if not hasattr(job, 'metadata'):
                job.metadata = {}
            job.metadata['client_response_rate'] = response_rate
    
    def _extract_mission_duration(self, response) -> Optional[str]:
        """Extrait la durée de la mission"""
        text = response.text
        
        # Patterns pour la durée
        duration_patterns = [
            r'durée[:\s]*([^.]{1,30})',
            r'mission de\s*([^.]{1,30})',
            r'contrat[:\s]*([^.]{1,30})',
            r'(\d+\s*(?:mois|semaines?|jours?))',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                duration = match.group(1).strip()
                if len(duration) < 50:  # Validation
                    return duration
        
        return None
    
    def _extract_client_response_rate(self, response) -> Optional[str]:
        """Extrait le taux de réponse du client (spécifique FreeWork)"""
        # Chercher les indicateurs de qualité du client
        selectors = [
            '[class*="response-rate"]::text',
            '[class*="client-rating"]::text',
            '[class*="rating"]::text'
        ]
        
        for selector in selectors:
            rate = response.css(selector).get()
            if rate and '%' in rate:
                return rate.strip()
        
        return None
    
    def parse_job(self, response):
        """Override pour ajouter des logs spécifiques FreeWork"""
        # Log spécifique avec détails FreeWork
        self.logger.info(f"🎯 Parsing FreeWork mission: {response.url}")
        
        # Appeler la méthode parent
        return super().parse_job(response)
