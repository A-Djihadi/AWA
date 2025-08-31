"""
Extracteur spécialisé pour les TJM
"""
import re
from typing import Optional, Tuple
from ..models.job import TJMRange
from .base_extractor import BaseExtractor


class TJMExtractor(BaseExtractor):
    """Extracteur pour les tarifs journaliers (TJM)"""
    
    def __init__(self):
        super().__init__()
        
        # Patterns pour extraire les TJM
        self.tjm_patterns = [
            # Fourchettes avec tiret
            r'(\d{2,4})\s*[-–—]\s*(\d{2,4})\s*€?\s*(?:/\s*jour|par jour|€)?',
            # Fourchettes avec "à"
            r'(\d{2,4})\s*à\s*(\d{2,4})\s*€?\s*(?:/\s*jour|par jour|€)?',
            # TJM unique avec contexte
            r'(?:tjm|tarif|prix|coût|daily rate)[:\s]*(\d{2,4})\s*€',
            # TJM avec symbole euro
            r'(\d{2,4})\s*€\s*(?:/\s*jour|par jour|daily)',
            # Montants en milliers
            r'(\d{1,3})k\s*[-–—]\s*(\d{1,3})k\s*€?',
            # Format "entre X et Y"
            r'entre\s*(\d{2,4})\s*et\s*(\d{2,4})\s*€',
        ]
        
        # Sélecteurs CSS spécifiques
        self.css_selectors = [
            '.tjm::text',
            '.price::text',
            '.rate::text',
            '.daily-rate::text',
            '[class*="tjm"]::text',
            '[class*="price"]::text',
            '[class*="rate"]::text',
            '.salary::text',
            '.compensation::text'
        ]
        
        # Champs JSON-LD
        self.json_fields = [
            'baseSalary.value',
            'baseSalary.minValue',
            'baseSalary.maxValue',
            'salary',
            'dailyRate',
            'rate'
        ]
        
        # Meta tags
        self.meta_tags = [
            'daily-rate',
            'tjm',
            'price',
            'salary'
        ]
    
    def extract(self, response) -> TJMRange:
        """Extrait le TJM depuis une page"""
        tjm_range = TJMRange()
        
        # 1. Essayer les sélecteurs CSS
        tjm_text = self.extract_from_selectors(response, self.css_selectors)
        if tjm_text:
            min_tjm, max_tjm = self._parse_tjm_text(tjm_text)
            if min_tjm or max_tjm:
                tjm_range.min_amount = min_tjm
                tjm_range.max_amount = max_tjm
                return tjm_range
        
        # 2. Essayer JSON-LD
        for field in self.json_fields:
            value = self.extract_from_json_ld(response, [field])
            if value:
                min_tjm, max_tjm = self._parse_tjm_text(value)
                if min_tjm or max_tjm:
                    tjm_range.min_amount = min_tjm
                    tjm_range.max_amount = max_tjm
                    return tjm_range
        
        # 3. Essayer les meta tags
        meta_value = self.extract_from_meta_tags(response, self.meta_tags)
        if meta_value:
            min_tjm, max_tjm = self._parse_tjm_text(meta_value)
            if min_tjm or max_tjm:
                tjm_range.min_amount = min_tjm
                tjm_range.max_amount = max_tjm
                return tjm_range
        
        # 4. Recherche dans tout le texte de la page
        full_text = response.text
        min_tjm, max_tjm = self._extract_tjm_from_text(full_text)
        if min_tjm or max_tjm:
            tjm_range.min_amount = min_tjm
            tjm_range.max_amount = max_tjm
        
        return tjm_range
    
    def _parse_tjm_text(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Parse un texte pour extraire min/max TJM"""
        if not text:
            return None, None
        
        # Nettoyer le texte
        clean_text = self.clean_text(text.lower())
        
        # Essayer chaque pattern
        for pattern in self.tjm_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) >= 2 and groups[1]:
                    # Fourchette trouvée
                    try:
                        min_val = int(groups[0])
                        max_val = int(groups[1])
                        
                        # Conversion si en milliers
                        if 'k' in match.group(0):
                            min_val *= 1000
                            max_val *= 1000
                        
                        # Validation des valeurs
                        if self._is_valid_tjm(min_val) and self._is_valid_tjm(max_val):
                            return min(min_val, max_val), max(min_val, max_val)
                            
                    except (ValueError, IndexError):
                        continue
                
                elif len(groups) >= 1:
                    # Valeur unique
                    try:
                        value = int(groups[0])
                        
                        # Conversion si en milliers
                        if 'k' in match.group(0):
                            value *= 1000
                        
                        if self._is_valid_tjm(value):
                            return value, value
                            
                    except (ValueError, IndexError):
                        continue
        
        return None, None
    
    def _extract_tjm_from_text(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extrait TJM depuis le texte complet de la page"""
        # Rechercher tous les montants possibles
        amounts = []
        
        # Pattern global pour capturer tous les montants avec contexte
        global_pattern = r'(?:tjm|tarif|daily\s*rate|prix|coût)[:\s]*(\d{2,4})\s*(?:€|euros?)'
        
        matches = re.finditer(global_pattern, text.lower(), re.IGNORECASE)
        for match in matches:
            try:
                amount = int(match.group(1))
                if self._is_valid_tjm(amount):
                    amounts.append(amount)
            except ValueError:
                continue
        
        # Si on a trouvé des montants, prendre min/max
        if amounts:
            return min(amounts), max(amounts) if len(amounts) > 1 else min(amounts)
        
        return None, None
    
    def _is_valid_tjm(self, amount: int) -> bool:
        """Valide qu'un montant peut être un TJM réaliste"""
        return 100 <= amount <= 2000  # TJM réalistes entre 100€ et 2000€
