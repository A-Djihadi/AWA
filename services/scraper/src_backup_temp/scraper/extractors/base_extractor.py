"""
Extracteur de base avec fonctionnalités communes
"""
import re
import json
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Classe de base pour tous les extracteurs"""
    
    def __init__(self):
        self.logger = None  # À configurer par le spider
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte extrait"""
        if not text:
            return ""
        
        # Supprimer HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def extract_from_selectors(self, response, selectors: List[str]) -> Optional[str]:
        """Extrait du texte en testant plusieurs sélecteurs CSS"""
        for selector in selectors:
            try:
                result = response.css(selector).get()
                if result:
                    cleaned = self.clean_text(result)
                    if cleaned and len(cleaned) > 0:
                        return cleaned
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Erreur sélecteur {selector}: {e}")
                continue
        return None
    
    def extract_from_json_ld(self, response, field_names: List[str]) -> Optional[str]:
        """Extrait des données depuis JSON-LD"""
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        
        for script in json_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    for field in field_names:
                        value = self._get_nested_value(data, field)
                        if value:
                            cleaned = self.clean_text(str(value))
                            if cleaned:
                                return cleaned
            except (json.JSONDecodeError, AttributeError) as e:
                if self.logger:
                    self.logger.debug(f"Erreur JSON-LD: {e}")
                continue
        
        return None
    
    def extract_from_meta_tags(self, response, meta_names: List[str]) -> Optional[str]:
        """Extrait depuis les meta tags"""
        for meta_name in meta_names:
            # Meta name
            content = response.css(f'meta[name="{meta_name}"]::attr(content)').get()
            if content:
                cleaned = self.clean_text(content)
                if cleaned:
                    return cleaned
            
            # Meta property (OpenGraph)
            content = response.css(f'meta[property="{meta_name}"]::attr(content)').get()
            if content:
                cleaned = self.clean_text(content)
                if cleaned:
                    return cleaned
        
        return None
    
    def extract_with_regex(self, text: str, patterns: List[str], flags: int = re.IGNORECASE) -> Optional[str]:
        """Extrait du texte avec des patterns regex"""
        for pattern in patterns:
            try:
                match = re.search(pattern, text, flags)
                if match:
                    # Prendre le premier groupe s'il existe, sinon le match complet
                    result = match.group(1) if match.groups() else match.group(0)
                    cleaned = self.clean_text(result)
                    if cleaned:
                        return cleaned
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Erreur regex {pattern}: {e}")
                continue
        
        return None
    
    def _get_nested_value(self, data: dict, field_path: str) -> Any:
        """Récupère une valeur imbriquée dans un dictionnaire"""
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    @abstractmethod
    def extract(self, response) -> Any:
        """Méthode d'extraction principale à implémenter"""
        pass
