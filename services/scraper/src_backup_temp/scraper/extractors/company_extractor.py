"""
Extracteur spécialisé pour les entreprises
"""
import re
from typing import Optional
from ..models.job import Company
from .base_extractor import BaseExtractor


class CompanyExtractor(BaseExtractor):
    """Extracteur pour les informations d'entreprise"""
    
    def __init__(self):
        super().__init__()
        
        # Sélecteurs CSS pour l'entreprise
        self.css_selectors = [
            '.company-name::text',
            '[class*="company"]::text',
            '.client::text',
            '[class*="client"]::text',
            '.employer::text',
            '.recruiter::text',
            '.organization::text',
            '[class*="employer"]::text'
        ]
        
        # Patterns regex pour extraction
        self.company_patterns = [
            r'(?:Notre client|Client)[:\s]+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s&.\-]{2,50})',
            r'(?:entreprise|société|company)[:\s]+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s&.\-]{2,50})',
            r'(?:chez|pour|with)\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s&.\-]{2,50})',
            r'cabinet\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s&.\-]{2,50})',
            r'groupe\s+([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s&.\-]{2,50})',
            r'([A-ZÀ-Ÿ][a-zA-ZÀ-ÿ\s&.\-]{2,50})\s+(?:recherche|recrute|cherche)'
        ]
        
        # Mots-clés à éviter (trop génériques)
        self.blacklist_words = {
            'client', 'entreprise', 'société', 'company', 'cabinet', 'groupe',
            'startup', 'agence', 'équipe', 'service', 'département', 'division',
            'notre', 'votre', 'cette', 'grande', 'petite', 'moyenne', 'international',
            'français', 'française', 'leader', 'spécialisé', 'spécialisée'
        }
        
        # Types d'entreprises reconnus
        self.company_types = {
            'SSII', 'ESN', 'Consulting', 'Cabinet', 'Agence', 'Startup',
            'Groupe', 'Société', 'Entreprise', 'Organisation'
        }
    
    def extract(self, response) -> Company:
        """Extrait les informations d'entreprise depuis une page"""
        company = Company()
        
        # 1. Extraction depuis les sélecteurs CSS
        company_text = self.extract_from_selectors(response, self.css_selectors)
        if company_text:
            name = self._parse_company_name(company_text)
            if name:
                company.name = name
                company.description = self._extract_company_description(response, name)
                return company
        
        # 2. Extraction depuis JSON-LD
        json_company = self.extract_from_json_ld(response, [
            'hiringOrganization.name',
            'company.name',
            'employer.name',
            'organization.name'
        ])
        if json_company:
            name = self._parse_company_name(json_company)
            if name:
                company.name = name
                # Essayer d'extraire plus d'infos depuis JSON-LD
                company.description = self.extract_from_json_ld(response, [
                    'hiringOrganization.description',
                    'company.description',
                    'employer.description'
                ])
                return company
        
        # 3. Extraction depuis les métadonnées OG
        og_title = self.extract_from_meta_tags(response, ['og:title', 'og:site_name'])
        if og_title:
            name = self._extract_company_from_title(og_title)
            if name:
                company.name = name
                return company
        
        # 4. Recherche dans le texte avec patterns
        full_text = response.text
        name = self._extract_company_from_text(full_text)
        if name:
            company.name = name
            company.description = self._extract_company_description(response, name)
        
        return company
    
    def _parse_company_name(self, text: str) -> Optional[str]:
        """Parse un texte pour extraire le nom d'entreprise"""
        if not text:
            return None
        
        cleaned = self.clean_text(text)
        
        # Filtrer si trop court ou trop long
        if len(cleaned) < 2 or len(cleaned) > 100:
            return None
        
        # Filtrer les mots blacklistés
        cleaned_lower = cleaned.lower()
        for blackword in self.blacklist_words:
            if blackword == cleaned_lower:
                return None
        
        # Nettoyer les préfixes courants
        prefixes_to_remove = [
            'notre client', 'client :', 'entreprise :', 'société :',
            'chez ', 'pour ', 'cabinet ', 'groupe '
        ]
        
        for prefix in prefixes_to_remove:
            if cleaned_lower.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        # Validation finale
        if len(cleaned) >= 2 and self._is_valid_company_name(cleaned):
            return cleaned
        
        return None
    
    def _extract_company_from_title(self, title: str) -> Optional[str]:
        """Extrait l'entreprise depuis un titre OG"""
        # Pattern pour titre type "Entreprise — Job | Site"
        if '—' in title:
            parts = title.split('—')
            if len(parts) >= 2:
                potential_company = parts[0].strip()
                name = self._parse_company_name(potential_company)
                if name and len(name) < 50:
                    return name
        
        # Pattern pour site_name
        if '|' in title:
            parts = title.split('|')
            if len(parts) >= 2:
                potential_company = parts[-1].strip()  # Dernière partie
                name = self._parse_company_name(potential_company)
                if name and len(name) < 50:
                    return name
        
        return None
    
    def _extract_company_from_text(self, text: str) -> Optional[str]:
        """Extrait l'entreprise depuis le texte complet"""
        # Essayer les patterns regex
        for pattern in self.company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                company_text = match.group(1) if match.groups() else match.group(0)
                name = self._parse_company_name(company_text)
                if name:
                    return name
        
        return None
    
    def _extract_company_description(self, response, company_name: str) -> Optional[str]:
        """Extrait la description de l'entreprise"""
        # Chercher une description dans JSON-LD
        json_desc = self.extract_from_json_ld(response, [
            'hiringOrganization.description',
            'company.description',
            'employer.description'
        ])
        if json_desc:
            return json_desc
        
        # Chercher dans les meta tags
        meta_desc = self.extract_from_meta_tags(response, [
            'description', 'og:description'
        ])
        if meta_desc and company_name.lower() in meta_desc.lower():
            return meta_desc
        
        # Chercher dans le texte autour du nom de l'entreprise
        text = response.text
        company_pattern = re.escape(company_name)
        
        # Chercher un paragraphe contenant le nom de l'entreprise
        paragraph_pattern = f'([^.]*{company_pattern}[^.]*{{0,200}})'
        match = re.search(paragraph_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            description = self.clean_text(match.group(1))
            if len(description) > 50:
                return description
        
        return None
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Valide qu'un nom peut être un nom d'entreprise"""
        if not name or len(name) < 2:
            return False
        
        # Doit commencer par une majuscule ou un chiffre
        if not (name[0].isupper() or name[0].isdigit()):
            return False
        
        # Ne doit pas être que des mots courants
        name_lower = name.lower()
        common_words = {
            'recherche', 'recrute', 'cherche', 'propose', 'offre',
            'mission', 'poste', 'opportunité', 'carrière', 'emploi'
        }
        
        for word in common_words:
            if word in name_lower:
                return False
        
        # Vérifier la présence de caractères spéciaux d'entreprise
        has_company_chars = any(char in name for char in ['&', '.', '-', 'SAS', 'SARL', 'SA'])
        
        # Ou des mots-clés d'entreprise
        has_company_keywords = any(keyword.lower() in name_lower for keyword in self.company_types)
        
        return len(name) <= 50 and (has_company_chars or has_company_keywords or len(name.split()) <= 4)
