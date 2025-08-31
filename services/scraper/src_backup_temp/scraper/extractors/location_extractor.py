"""
Extracteur spécialisé pour les localisations
"""
import re
from typing import Optional
from ..models.job import Location
from .base_extractor import BaseExtractor


class LocationExtractor(BaseExtractor):
    """Extracteur pour les localisations géographiques"""
    
    def __init__(self):
        super().__init__()
        
        # Villes françaises principales
        self.french_cities = {
            'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes',
            'strasbourg', 'montpellier', 'bordeaux', 'lille', 'rennes',
            'reims', 'saint-étienne', 'toulon', 'grenoble', 'dijon',
            'angers', 'nîmes', 'villeurbanne', 'clermont-ferrand',
            'aix-en-provence', 'brest', 'limoges', 'tours', 'amiens',
            'perpignan', 'metz', 'besançon', 'orléans', 'rouen',
            'mulhouse', 'caen', 'nancy', 'argenteuil', 'montreuil'
        }
        
        # Régions françaises
        self.french_regions = {
            'île-de-france', 'auvergne-rhône-alpes', 'hauts-de-france',
            'nouvelle-aquitaine', 'occitanie', 'grand-est', 'provence-alpes-côte-d-azur',
            'pays-de-la-loire', 'bretagne', 'normandie', 'bourgogne-franche-comté',
            'centre-val-de-loire', 'corse'
        }
        
        # Sélecteurs CSS pour la localisation
        self.css_selectors = [
            '[class*="city"]::text',
            '[class*="location"]::text',
            '[class*="address"]::text',
            '.location::text',
            '.address::text',
            '.city::text',
            '.region::text',
            '[class*="geo"]::text',
            '[class*="place"]::text'
        ]
        
        # Patterns regex pour extraction
        self.location_patterns = [
            r'(?:localisation|lieu|location|ville|city)[:\s]+([A-Za-zÀ-ÿ\s\-\']{2,50})',
            r'(?:basé|situé|implanté)\s+(?:à|en|sur)\s+([A-Za-zÀ-ÿ\s\-\']{2,50})',
            r'(?:à|en|sur)\s+([A-Z][a-zÀ-ÿ\s\-\']{2,50})',
            r'([A-Z][a-zÀ-ÿ\-\']+)(?:\s*,\s*France)?',
            r'(\d{5})\s+([A-Za-zÀ-ÿ\s\-\']{2,50})',  # Code postal + ville
        ]
        
        # Mots parasites à supprimer
        self.noise_words = {
            'du', 'd', 'le', 'la', 'les', 'de', 'des', 'et', 'ou', 'à', 'en', 'sur',
            'dans', 'avec', 'pour', 'par', 'sans', 'sous', 'entre', 'chez',
            'france', 'français', 'française'
        }
    
    def extract(self, response) -> Location:
        """Extrait la localisation depuis une page"""
        location = Location()
        
        # 1. Extraction depuis les sélecteurs CSS
        location_text = self.extract_from_selectors(response, self.css_selectors)
        if location_text:
            parsed_location = self._parse_location_text(location_text)
            if parsed_location.is_valid:
                return parsed_location
        
        # 2. Extraction depuis JSON-LD
        json_location = self.extract_from_json_ld(response, [
            'jobLocation.addressLocality',
            'jobLocation.addressRegion', 
            'jobLocation.name',
            'location.name',
            'address.addressLocality',
            'address.addressRegion'
        ])
        if json_location:
            parsed_location = self._parse_location_text(json_location)
            if parsed_location.is_valid:
                return parsed_location
        
        # 3. Extraction depuis les métadonnées OG
        og_title = self.extract_from_meta_tags(response, ['og:title'])
        if og_title:
            location_from_title = self._extract_location_from_title(og_title)
            if location_from_title.is_valid:
                return location_from_title
        
        # 4. Recherche dans le texte complet
        full_text = response.text
        text_location = self._extract_location_from_text(full_text)
        if text_location.is_valid:
            return text_location
        
        return location
    
    def _parse_location_text(self, text: str) -> Location:
        """Parse un texte pour extraire la localisation"""
        if not text:
            return Location()
        
        cleaned_text = self.clean_text(text)
        location = Location()
        
        # Nettoyer les mots parasites
        words = cleaned_text.split()
        clean_words = [
            word for word in words 
            if word.lower() not in self.noise_words and len(word) > 1
        ]
        
        if not clean_words:
            return location
        
        cleaned_location = ' '.join(clean_words)
        
        # Vérifier si c'est une ville connue
        location_lower = cleaned_location.lower()
        
        for city in self.french_cities:
            if city in location_lower:
                location.city = city.title()
                # Extraire la région si possible
                location.region = self._guess_region_from_city(city)
                break
        
        # Si pas de ville trouvée, vérifier les régions
        if not location.city:
            for region in self.french_regions:
                if region in location_lower:
                    location.region = region.title()
                    break
        
        # Si rien trouvé mais le texte semble valide, l'utiliser comme ville
        if not location.city and not location.region and len(cleaned_location) > 2:
            location.city = cleaned_location.title()
        
        return location
    
    def _extract_location_from_title(self, title: str) -> Location:
        """Extrait la localisation depuis un titre OG"""
        location = Location()
        
        # Pattern pour titre type "Job — Location | Site"
        if '—' in title:
            parts = title.split('—')
            if len(parts) >= 2:
                location_part = parts[1].strip()
                if '|' in location_part:
                    location_part = location_part.split('|')[0].strip()
                
                return self._parse_location_text(location_part)
        
        return location
    
    def _extract_location_from_text(self, text: str) -> Location:
        """Extrait la localisation depuis le texte complet"""
        location = Location()
        
        # Essayer les patterns regex
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location_text = match.group(1) if match.groups() else match.group(0)
                parsed = self._parse_location_text(location_text)
                if parsed.is_valid:
                    return parsed
        
        # Recherche directe des villes dans le texte
        text_lower = text.lower()
        for city in self.french_cities:
            if re.search(r'\b' + re.escape(city) + r'\b', text_lower):
                location.city = city.title()
                location.region = self._guess_region_from_city(city)
                break
        
        return location
    
    def _guess_region_from_city(self, city: str) -> Optional[str]:
        """Devine la région à partir de la ville"""
        # Mapping simplifié ville -> région
        city_to_region = {
            'paris': 'Île-de-France',
            'lyon': 'Auvergne-Rhône-Alpes',
            'marseille': 'Provence-Alpes-Côte d\'Azur',
            'toulouse': 'Occitanie',
            'nice': 'Provence-Alpes-Côte d\'Azur',
            'nantes': 'Pays de la Loire',
            'strasbourg': 'Grand Est',
            'montpellier': 'Occitanie',
            'bordeaux': 'Nouvelle-Aquitaine',
            'lille': 'Hauts-de-France',
            'rennes': 'Bretagne',
            'reims': 'Grand Est',
            'saint-étienne': 'Auvergne-Rhône-Alpes',
            'toulon': 'Provence-Alpes-Côte d\'Azur',
            'grenoble': 'Auvergne-Rhône-Alpes',
            'dijon': 'Bourgogne-Franche-Comté',
            'angers': 'Pays de la Loire',
            'nîmes': 'Occitanie'
        }
        
        return city_to_region.get(city.lower())
    
    def _is_valid_location_text(self, text: str) -> bool:
        """Vérifie si un texte peut être une localisation valide"""
        if not text or len(text) < 2:
            return False
        
        # Vérifier qu'il n'y a pas que des mots parasites
        words = text.lower().split()
        meaningful_words = [w for w in words if w not in self.noise_words]
        
        return len(meaningful_words) > 0 and len(text) <= 50
