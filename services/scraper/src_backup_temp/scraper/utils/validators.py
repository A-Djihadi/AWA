"""
Validateurs pour les données scrapées
"""
import re
from typing import Optional, List
from urllib.parse import urlparse


class URLValidator:
    """Validateur pour les URLs"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Vérifie si une URL est valide"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """Vérifie si deux URLs sont du même domaine"""
        try:
            domain1 = urlparse(url1).netloc
            domain2 = urlparse(url2).netloc
            return domain1 == domain2
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str, base_url: str = "") -> str:
        """Normalise une URL (relative vers absolue)"""
        if not url:
            return ""
        
        if url.startswith(('http://', 'https://')):
            return url
        
        if url.startswith('//'):
            return f"https:{url}"
        
        if base_url and url.startswith('/'):
            base_domain = urlparse(base_url).netloc
            return f"https://{base_domain}{url}"
        
        return url


class DataValidator:
    """Validateur pour les données extraites"""
    
    @staticmethod
    def is_valid_tjm(amount: Optional[int]) -> bool:
        """Valide un montant TJM"""
        if amount is None:
            return False
        return 50 <= amount <= 3000  # Fourchette réaliste
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Valide une adresse email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Valide un numéro de téléphone français"""
        if not phone:
            return False
        
        # Nettoyer le numéro
        clean_phone = re.sub(r'[\s\-\.\(\)]', '', phone)
        
        # Patterns français
        patterns = [
            r'^0[1-9]\d{8}$',  # 0X XX XX XX XX
            r'^\+33[1-9]\d{8}$',  # +33 X XX XX XX XX
            r'^33[1-9]\d{8}$'   # 33 X XX XX XX XX
        ]
        
        return any(re.match(pattern, clean_phone) for pattern in patterns)
    
    @staticmethod
    def is_valid_company_name(name: str) -> bool:
        """Valide un nom d'entreprise"""
        if not name or len(name.strip()) < 2:
            return False
        
        # Ne doit pas contenir que des caractères spéciaux
        if not re.search(r'[a-zA-ZÀ-ÿ]', name):
            return False
        
        # Longueur raisonnable
        return len(name.strip()) <= 100
    
    @staticmethod
    def is_valid_city_name(city: str) -> bool:
        """Valide un nom de ville"""
        if not city or len(city.strip()) < 2:
            return False
        
        # Caractères autorisés pour les villes françaises
        pattern = r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$'
        return bool(re.match(pattern, city.strip())) and len(city.strip()) <= 50
    
    @staticmethod
    def validate_job_data(job_dict: dict) -> List[str]:
        """Valide les données d'un job et retourne les erreurs"""
        errors = []
        
        # Champs obligatoires
        required_fields = ['source', 'source_id', 'title']
        for field in required_fields:
            if not job_dict.get(field):
                errors.append(f"Champ obligatoire manquant: {field}")
        
        # Validation du TJM
        tjm_min = job_dict.get('tjm_min')
        tjm_max = job_dict.get('tjm_max')
        
        if tjm_min is not None and not DataValidator.is_valid_tjm(tjm_min):
            errors.append(f"TJM minimum invalide: {tjm_min}")
        
        if tjm_max is not None and not DataValidator.is_valid_tjm(tjm_max):
            errors.append(f"TJM maximum invalide: {tjm_max}")
        
        if (tjm_min is not None and tjm_max is not None 
            and tjm_min > tjm_max):
            errors.append("TJM minimum supérieur au maximum")
        
        # Validation de l'entreprise
        company = job_dict.get('company')
        if company and not DataValidator.is_valid_company_name(company):
            errors.append(f"Nom d'entreprise invalide: {company}")
        
        # Validation de la ville
        city = job_dict.get('city')
        if city and not DataValidator.is_valid_city_name(city):
            errors.append(f"Nom de ville invalide: {city}")
        
        # Validation de l'URL
        url = job_dict.get('url')
        if url and not URLValidator.is_valid_url(url):
            errors.append(f"URL invalide: {url}")
        
        return errors
