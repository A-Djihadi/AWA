"""
Extracteur spécialisé pour le texte (titre, description)
"""
import re
from typing import Optional
from .base_extractor import BaseExtractor


class TextExtractor(BaseExtractor):
    """Extracteur pour le contenu textuel (titres, descriptions)"""
    
    def __init__(self):
        super().__init__()
        
        # Sélecteurs pour les titres
        self.title_selectors = [
            'h1::text',
            '.job-title::text',
            '.title::text',
            '[class*="title"]::text',
            '.position::text',
            '[class*="position"]::text',
            '.heading::text'
        ]
        
        # Sélecteurs pour les descriptions
        self.description_selectors = [
            '[class*="content"] p::text',
            '[class*="description"] p::text',
            '[class*="detail"] p::text',
            '.job-description::text',
            '.offer-description::text',
            '[class*="content"]::text',
            '[class*="description"]::text',
            'main p::text',
            '.description::text'
        ]
        
        # Patterns pour nettoyer les titres
        self.title_cleanup_patterns = [
            r'\s*[-–—]\s*.*$',  # Supprimer tout après un tiret
            r'\s*\|.*$',        # Supprimer tout après un pipe
            r'\s*\(.*?\)\s*',   # Supprimer les parenthèses
            r'^\s*Offre\s*[:\s]*',  # Supprimer "Offre:"
            r'^\s*Job\s*[:\s]*',    # Supprimer "Job:"
            r'^\s*Mission\s*[:\s]*' # Supprimer "Mission:"
        ]
        
        # Patterns pour identifier les descriptions de qualité
        self.quality_description_indicators = [
            r'(?:mission|poste|profil|recherchons|recherche)',
            r'(?:compétenc|skill|expérience|maîtrise)',
            r'(?:responsabilit|tâche|activit)',
            r'(?:technolog|outil|langag|framework)'
        ]
    
    def extract_title(self, response) -> Optional[str]:
        """Extrait le titre de l'offre"""
        # 1. Essayer les sélecteurs CSS
        title = self.extract_from_selectors(response, self.title_selectors)
        if title and self._is_valid_title(title):
            return self._clean_title(title)
        
        # 2. Essayer les métadonnées OG
        og_title = self.extract_from_meta_tags(response, ['og:title'])
        if og_title:
            cleaned_title = self._extract_title_from_og(og_title)
            if cleaned_title and self._is_valid_title(cleaned_title):
                return cleaned_title
        
        # 3. Essayer JSON-LD
        json_title = self.extract_from_json_ld(response, [
            'title', 'name', 'jobTitle', 'position'
        ])
        if json_title and self._is_valid_title(json_title):
            return self._clean_title(json_title)
        
        # 4. Essayer le titre de la page HTML
        page_title = response.css('title::text').get()
        if page_title:
            cleaned_title = self._extract_title_from_page_title(page_title)
            if cleaned_title and self._is_valid_title(cleaned_title):
                return cleaned_title
        
        return None
    
    def extract_description(self, response) -> Optional[str]:
        """Extrait la description de l'offre"""
        # 1. Essayer les sélecteurs CSS multiples
        descriptions = []
        for selector in self.description_selectors:
            desc_parts = response.css(selector).getall()
            if desc_parts:
                descriptions.extend(desc_parts)
        
        if descriptions:
            full_desc = ' '.join([self.clean_text(part) for part in descriptions if part.strip()])
            if len(full_desc) > 50:
                return self._clean_description(full_desc)
        
        # 2. Essayer JSON-LD
        json_desc = self.extract_from_json_ld(response, [
            'description', 'jobDescription', 'summary', 'overview'
        ])
        if json_desc and len(json_desc) > 50:
            return self._clean_description(json_desc)
        
        # 3. Essayer les meta tags
        meta_desc = self.extract_from_meta_tags(response, [
            'description', 'og:description'
        ])
        if meta_desc and len(meta_desc) > 50:
            return self._clean_description(meta_desc)
        
        # 4. Extraction depuis le HTML brut
        html_desc = self._extract_description_from_html(response)
        if html_desc and len(html_desc) > 50:
            return self._clean_description(html_desc)
        
        return None
    
    def _clean_title(self, title: str) -> str:
        """Nettoie un titre extrait"""
        if not title:
            return ""
        
        cleaned = self.clean_text(title)
        
        # Appliquer les patterns de nettoyage
        for pattern in self.title_cleanup_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Nettoyer les espaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def _extract_title_from_og(self, og_title: str) -> Optional[str]:
        """Extrait le titre depuis un og:title"""
        # Pattern: "Site — Titre de l'offre"
        if '—' in og_title:
            parts = og_title.split('—')
            if len(parts) >= 2:
                # Prendre la partie qui semble être le titre
                for part in parts:
                    cleaned = self._clean_title(part)
                    if len(cleaned) > 10 and not self._is_site_name(cleaned):
                        return cleaned
        
        # Pattern: "Titre | Site"
        if '|' in og_title:
            parts = og_title.split('|')
            if len(parts) >= 2:
                potential_title = self._clean_title(parts[0])
                if len(potential_title) > 10:
                    return potential_title
        
        # Si pas de séparateur, vérifier si c'est un titre valide
        cleaned = self._clean_title(og_title)
        if len(cleaned) > 10 and not self._is_site_name(cleaned):
            return cleaned
        
        return None
    
    def _extract_title_from_page_title(self, page_title: str) -> Optional[str]:
        """Extrait le titre depuis le title HTML"""
        # Similaire à og:title
        return self._extract_title_from_og(page_title)
    
    def _clean_description(self, description: str) -> str:
        """Nettoie une description extraite"""
        if not description:
            return ""
        
        cleaned = self.clean_text(description)
        
        # Supprimer les répétitions
        sentences = cleaned.split('.')
        unique_sentences = []
        seen = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in seen and len(sentence) > 10:
                unique_sentences.append(sentence)
                seen.add(sentence)
        
        return '. '.join(unique_sentences)
    
    def _extract_description_from_html(self, response) -> Optional[str]:
        """Extrait la description depuis le HTML brut"""
        text = response.text
        
        # Patterns pour identifier les blocs de description
        desc_patterns = [
            r'<p[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*(?:content|description|detail)[^"]*"[^>]*>(.*?)</div>',
            r'Description[:\s]+(.*?)(?:\n|<)',
            r'Profil[:\s]+(.*?)(?:\n|<)',
            r'Missions?[:\s]+(.*?)(?:\n|<)'
        ]
        
        descriptions = []
        for pattern in desc_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                clean_match = self.clean_text(match)
                if len(clean_match) > 30:
                    descriptions.append(clean_match)
        
        if descriptions:
            return ' '.join(descriptions[:3])  # Limiter à 3 paragraphes
        
        return None
    
    def _is_valid_title(self, title: str) -> bool:
        """Vérifie si un titre est valide"""
        if not title:
            return False
        
        cleaned = title.strip()
        
        # Trop court ou trop long
        if len(cleaned) < 5 or len(cleaned) > 200:
            return False
        
        # Ne doit pas être que des mots génériques
        generic_words = {'offre', 'emploi', 'job', 'mission', 'poste', 'recrutement'}
        words = set(cleaned.lower().split())
        
        return not words.issubset(generic_words)
    
    def _is_site_name(self, text: str) -> bool:
        """Vérifie si un texte est probablement un nom de site"""
        site_indicators = [
            'free-work', 'freelance', 'job', 'emploi', 'recrutement',
            '.com', '.fr', 'www', 'site', 'plateforme'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in site_indicators)
    
    def _assess_description_quality(self, description: str) -> float:
        """Évalue la qualité d'une description (0-1)"""
        if not description:
            return 0.0
        
        score = 0.0
        max_score = 4.0
        
        # Longueur appropriée
        if 100 <= len(description) <= 2000:
            score += 1.0
        
        # Présence d'indicateurs de qualité
        desc_lower = description.lower()
        for pattern in self.quality_description_indicators:
            if re.search(pattern, desc_lower):
                score += 1.0
                break
        
        # Structure (présence de phrases)
        sentences = description.split('.')
        if len(sentences) >= 3:
            score += 1.0
        
        # Diversité du vocabulaire
        words = set(description.lower().split())
        if len(words) >= 20:
            score += 1.0
        
        return score / max_score
