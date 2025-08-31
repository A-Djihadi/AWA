"""
Utilitaires pour le traitement de texte
"""
import re
import unicodedata
from typing import List, Optional


class TextCleaner:
    """Utilitaires pour nettoyer le texte"""
    
    @staticmethod
    def clean_html(text: str) -> str:
        """Supprime les tags HTML"""
        if not text:
            return ""
        
        # Supprimer les tags HTML
        clean = re.sub(r'<[^>]+>', '', text)
        
        # Décoder les entités HTML communes
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' ',
            '&euro;': '€'
        }
        
        for entity, char in html_entities.items():
            clean = clean.replace(entity, char)
        
        return clean
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalise les espaces"""
        if not text:
            return ""
        
        # Remplacer tous les types d'espaces par des espaces normaux
        normalized = re.sub(r'\s+', ' ', text)
        
        # Supprimer les espaces en début/fin
        return normalized.strip()
    
    @staticmethod
    def remove_control_chars(text: str) -> str:
        """Supprime les caractères de contrôle"""
        if not text:
            return ""
        
        # Supprimer les caractères de contrôle
        return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalise les caractères Unicode"""
        if not text:
            return ""
        
        # Normalisation NFD puis recomposition
        return unicodedata.normalize('NFC', text)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Nettoyage complet du texte"""
        if not text:
            return ""
        
        # Appliquer tous les nettoyages
        cleaned = TextCleaner.clean_html(text)
        cleaned = TextCleaner.remove_control_chars(cleaned)
        cleaned = TextCleaner.normalize_whitespace(cleaned)
        cleaned = TextCleaner.normalize_unicode(cleaned)
        
        return cleaned
    
    @staticmethod
    def extract_sentences(text: str, max_sentences: int = 10) -> List[str]:
        """Extrait les phrases d'un texte"""
        if not text:
            return []
        
        # Découper en phrases
        sentences = re.split(r'[.!?]+', text)
        
        # Nettoyer et filtrer
        clean_sentences = []
        for sentence in sentences:
            cleaned = TextCleaner.normalize_whitespace(sentence)
            if len(cleaned) > 10:  # Phrases substantielles
                clean_sentences.append(cleaned)
                
                if len(clean_sentences) >= max_sentences:
                    break
        
        return clean_sentences
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Tronque un texte intelligemment"""
        if not text or len(text) <= max_length:
            return text
        
        # Essayer de couper à un espace
        truncated = text[:max_length - len(suffix)]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # Si l'espace est assez proche
            truncated = truncated[:last_space]
        
        return truncated + suffix


class RegexHelper:
    """Helper pour les expressions régulières communes"""
    
    # Patterns courants
    EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_PATTERN = r'(?:\+33|0)[1-9](?:[.\-\s]?\d{2}){4}'
    URL_PATTERN = r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'
    
    # Patterns pour TJM
    TJM_PATTERNS = [
        r'(\d{2,4})\s*[-–—]\s*(\d{2,4})\s*€',
        r'(\d{2,4})\s*à\s*(\d{2,4})\s*€',
        r'(\d{2,4})\s*€\s*(?:/\s*jour|par jour)',
    ]
    
    # Patterns pour villes françaises
    CITY_PATTERN = r'[A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+(?:[-\s][A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ][a-zàâäéèêëïîôöùûüÿç]+)*'
    
    @classmethod
    def find_emails(cls, text: str) -> List[str]:
        """Trouve toutes les adresses email dans un texte"""
        return re.findall(cls.EMAIL_PATTERN, text, re.IGNORECASE)
    
    @classmethod
    def find_phones(cls, text: str) -> List[str]:
        """Trouve tous les numéros de téléphone dans un texte"""
        return re.findall(cls.PHONE_PATTERN, text)
    
    @classmethod
    def find_urls(cls, text: str) -> List[str]:
        """Trouve toutes les URLs dans un texte"""
        return re.findall(cls.URL_PATTERN, text, re.IGNORECASE)
    
    @classmethod
    def extract_tjm_ranges(cls, text: str) -> List[tuple]:
        """Extrait les fourchettes de TJM"""
        ranges = []
        for pattern in cls.TJM_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    try:
                        min_val = int(groups[0])
                        max_val = int(groups[1])
                        ranges.append((min_val, max_val))
                    except ValueError:
                        continue
        return ranges
    
    @classmethod
    def find_cities(cls, text: str) -> List[str]:
        """Trouve les noms de villes dans un texte"""
        return re.findall(cls.CITY_PATTERN, text)
    
    @staticmethod
    def escape_for_regex(text: str) -> str:
        """Échappe un texte pour utilisation dans une regex"""
        return re.escape(text)
    
    @staticmethod
    def is_valid_regex(pattern: str) -> bool:
        """Vérifie si un pattern regex est valide"""
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
