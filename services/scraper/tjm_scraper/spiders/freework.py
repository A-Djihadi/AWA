"""
Spider FreeWork pour AWA - Optimisé pour extraction TJM
"""
import scrapy
import re
import json
from datetime import datetime
from urllib.parse import urljoin

class FreeWorkSpider(scrapy.Spider):
    name = 'freework'
    allowed_domains = ['free-work.com']
    start_urls = [
        'https://www.free-work.com/fr/tech-it/jobs?locations=fr~~~&contracts=contractor'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,
        'USER_AGENT': 'AWA-FreeWork-Scraper/1.0'
    }
    
    def parse(self, response):
        """Parser la page de listing des missions"""
        
        self.logger.info(f"Parsing FreeWork listing: {response.url}")
        
        # Sélecteurs pour les liens de missions basés sur l'analyse
        mission_links = response.css('a[href*="/job-mission/"]::attr(href)').getall()
        
        if not mission_links:
            # Fallback: chercher tous les liens internes avec job ou mission
            all_links = response.css('a[href*="/fr/tech-it/"]::attr(href)').getall()
            mission_links = [link for link in all_links if 'job-mission' in link]
        
        self.logger.info(f"Found {len(mission_links)} mission links")
        
        # Suivre les liens de missions
        for link in mission_links:
            absolute_url = urljoin(response.url, link)
            yield response.follow(absolute_url, self.parse_mission, meta={'listing_url': response.url})
        
        # Pagination
        next_page = response.css('a[href*="page="]::attr(href)').get()
        if next_page:
            self.logger.info(f"Next page found: {next_page}")
            yield response.follow(next_page, self.parse)
    
    def parse_mission(self, response):
        """Parser une page de mission spécifique"""
        
        self.logger.info(f"Parsing mission: {response.url}")
        
        # Extraire l'ID de la mission depuis l'URL
        source_id = self.extract_source_id(response.url)
        
        # Titre de la mission
        title = self.extract_title(response)
        
        # TJM - Pattern spécifique FreeWork
        tjm_min, tjm_max = self.extract_tjm(response)
        
        # Entreprise
        company = self.extract_company(response)
        
        # Technologies
        technologies = self.extract_technologies(response)
        
        # Localisation
        location = self.extract_location(response)
        
        # Séniorité
        seniority_level = self.extract_seniority(response)
        
        # Remote policy
        remote_policy = self.extract_remote_policy(response)
        
        # Description
        description = self.extract_description(response)
        
        # Type de contrat
        contract_type = self.extract_contract_type(response)
        
        yield {
            'source': 'freework',
            'source_id': source_id,
            'title': title,
            'company': company,
            'tjm_min': tjm_min,
            'tjm_max': tjm_max,
            'tjm_currency': 'EUR',
            'technologies': technologies,
            'seniority_level': seniority_level,
            'location': location,
            'remote_policy': remote_policy,
            'contract_type': contract_type,
            'description': description,
            'url': response.url,
            'scraped_at': datetime.now().isoformat()
        }
    
    def extract_source_id(self, url):
        """Extraire l'ID de la mission depuis l'URL"""
        # Pattern: /job-mission/titre-de-la-mission-123
        match = re.search(r'/job-mission/([^?]+)', url)
        return match.group(1) if match else url.split('/')[-1]
    
    def extract_title(self, response):
        """Extraire le titre de la mission - Optimisé FreeWork"""
        # Sélecteurs optimisés basés sur l'analyse
        selectors = [
            'h1::text',
            'meta[property="og:title"]::attr(content)',
            '.job-title::text',
            '[class*="title"]::text'
        ]
        
        for selector in selectors:
            title = response.css(selector).get()
            if title:
                title = title.strip()
                # Nettoyer le titre des métadonnées OG
                if '—' in title:
                    title = title.split('—')[0].strip()
                if '|' in title:
                    title = title.split('|')[0].strip()
                
                # Éviter les titres trop génériques
                if title and len(title) > 5 and title not in ['Offre d\'emploi']:
                    return title
        
        return None
    
    def extract_tjm(self, response):
        """Extraire le TJM (spécifique FreeWork)"""
        text = response.text
        
        # Patterns TJM améliorés pour FreeWork
        tjm_patterns = [
            r'(\d{3,4})\s*[-–]\s*(\d{3,4})\s*€',  # Range: 600-800€
            r'(\d{3,4})\s*€\s*[-–]\s*(\d{3,4})\s*€',  # 600€ - 800€
            r'tjm[:\s]*(\d{3,4})(?:\s*[-–]\s*(\d{3,4}))?\s*€?',  # TJM: 600-800
            r'taux[:\s]*(\d{3,4})(?:\s*[-–]\s*(\d{3,4}))?\s*€?',  # Taux: 600
            r'(\d{3,4})\s*€\s*(?:par\s*jour|\/j)',  # 600€ par jour
            r'(\d{3,4})\s*euros?\s*(?:par\s*jour|\/j)',  # 600 euros par jour
        ]
        
        for pattern in tjm_patterns:
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                groups = matches.groups()
                if len(groups) >= 2 and groups[1]:
                    # Range trouvé
                    return int(groups[0]), int(groups[1])
                else:
                    # Valeur unique
                    tjm = int(groups[0])
                    return tjm, tjm
        
        return None, None
    
    def extract_company(self, response):
        """Extraire l'entreprise - Optimisé FreeWork"""
        # Sélecteurs optimisés
        selectors = [
            '.company-name::text',
            '[class*="company"]::text',
            '.client::text',
            '[class*="client"]::text',
            '.employer::text',
            '.recruiter::text'
        ]
        
        for selector in selectors:
            company = response.css(selector).get()
            if company:
                company = company.strip()
                if 3 < len(company) < 100:  # Filtrer les valeurs aberrantes
                    return company
        
        # Extraction depuis les métadonnées OG
        og_title = response.css('meta[property="og:title"]::attr(content)').get()
        if og_title:
            # Pattern: "Entreprise — Titre | Site"
            if '—' in og_title:
                parts = og_title.split('—')
                if len(parts) >= 2:
                    potential_company = parts[0].strip()
                    if 3 < len(potential_company) < 50:
                        return potential_company
        
        # Chercher dans le texte avec regex améliorés
        text = response.text
        company_patterns = [
            r'(?:Notre client|Client)[:\s]+([A-Z][a-zA-Z\s&.-]{3,30})',
            r'(?:entreprise|société)[:\s]+([A-Z][a-zA-Z\s&.-]{3,30})',
            r'(?:chez|pour)\s+([A-Z][a-zA-Z\s&.-]{3,30})',
            r'cabinet\s+([A-Z][a-zA-Z\s&.-]{3,30})'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if 3 < len(company) < 50:
                    return company
        
        return None
    
    def extract_technologies(self, response):
        """Extraire les technologies - Version corrigée et ciblée"""
        # Technologies courantes à rechercher (liste étendue)
        tech_keywords = [
            # Langages
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'php', 'symfony', 'laravel', 'drupal', 'wordpress',
            'c#', '.net', 'asp.net', 'dotnet', 'typescript',
            'html', 'css', 'go', 'rust', 'kotlin', 'swift',
            
            # Bases de données
            'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis',
            'elasticsearch', 'cassandra', 'neo4j',
            
            # Cloud et DevOps
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'jenkins', 'gitlab', 'github', 'terraform', 'ansible',
            'linux', 'windows', 'unix',
            
            # Frameworks et outils
            'spring', 'django', 'flask', 'express', 'maven', 'gradle',
            'git', 'jira', 'confluence', 'bamboo',
            
            # Systèmes métier
            'erp', 'crm', 'sap', 'salesforce', 'oracle', 'peoplesoft',
            'workday', 'servicenow', 'sharepoint',
            
            # Méthodologies et concepts
            'agile', 'scrum', 'devops', 'ci/cd', 'microservices',
            'api', 'rest', 'soap', 'graphql'
        ]
        
        found_techs = set()
        
        # 1. Extraction depuis JSON-LD (priorité 1)
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, dict) and data.get('@type') == 'JobPosting':
                    # Chercher dans les champs pertinents
                    job_fields = [
                        data.get('description', ''),
                        data.get('skills', ''),
                        data.get('qualifications', ''),
                        data.get('responsibilities', '')
                    ]
                    
                    for field_content in job_fields:
                        if field_content:
                            # Nettoyer le HTML si présent
                            clean_content = re.sub(r'<[^>]+>', '', str(field_content))
                            field_text = clean_content.lower()
                            
                            for tech in tech_keywords:
                                if self._is_tech_mentioned_in_context(tech, field_text):
                                    found_techs.add(tech.title())
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # 2. Extraction depuis les sélecteurs de contenu spécifiques
        content_selectors = [
            '[class*="content"]::text',
            '[class*="description"]::text',
            '[class*="detail"]::text',
            '.job-description::text',
            '.requirements::text',
            '.qualifications::text'
        ]
        
        for selector in content_selectors:
            content_parts = response.css(selector).getall()
            if content_parts:
                content_text = ' '.join(content_parts).lower()
                for tech in tech_keywords:
                    if self._is_tech_mentioned_in_context(tech, content_text):
                        found_techs.add(tech.title())
        
        # 3. Si peu de technologies trouvées, chercher dans les meta tags
        if len(found_techs) < 3:
            meta_desc = response.css('meta[name="description"]::attr(content)').get()
            if meta_desc:
                meta_text = meta_desc.lower()
                for tech in tech_keywords:
                    if self._is_tech_mentioned_in_context(tech, meta_text):
                        found_techs.add(tech.title())
        
        # Nettoyer et normaliser les noms
        normalized_techs = []
        for tech in found_techs:
            normalized = self._normalize_tech_name(tech)
            if normalized:
                normalized_techs.append(normalized)
        
        # Retourner maximum 10 technologies
        return normalized_techs[:10]
    
    def _normalize_tech_name(self, tech: str) -> str:
        """Normalise le nom d'une technologie"""
        if not tech:
            return ""
        
        # Mappings pour normaliser les noms
        normalization_map = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'node': 'Node.js',
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'c#': 'C#',
            '.net': '.NET',
            'dotnet': '.NET',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'erp': 'ERP',
            'crm': 'CRM',
            'api': 'API',
            'ci/cd': 'CI/CD',
            'devops': 'DevOps'
        }
        
        tech_lower = tech.lower().strip()
        
        # Vérifier les mappings
        if tech_lower in normalization_map:
            return normalization_map[tech_lower]
        
        # Capitaliser correctement
        return tech.title().strip()
    
    def _is_tech_mentioned_in_context(self, tech: str, text: str) -> bool:
        """Vérifie si une technologie est mentionnée dans un contexte approprié"""
        if not text or not tech:
            return False
        
        tech_lower = tech.lower()
        text_lower = text.lower()
        
        # Recherche avec limites de mots pour éviter les faux positifs
        pattern = r'\b' + re.escape(tech_lower) + r'\b'
        if not re.search(pattern, text_lower):
            return False
        
        # Vérifier le contexte - éviter SEULEMENT les scripts globaux évidents
        # On utilise un échantillon plus petit pour ne pas exclure du bon contenu
        text_sample = text_lower[:200]  # Vérifier juste le début
        
        # Exclure seulement les indicateurs très évidents de scripts
        exclude_indicators = [
            'window.__nuxt__', 'function(', 'gtm.start', 'analytics.push'
        ]
        
        # Si on trouve des indicateurs clairs de script, exclure
        if any(indicator in text_sample for indicator in exclude_indicators):
            return False
        
        # Sinon, accepter la technologie
        return True
    
    def extract_location(self, response):
        """Extraire la localisation - Optimisé FreeWork"""
        # Sélecteurs optimisés identifiés par l'analyse
        selectors = [
            '[class*="city"]::text',
            '[class*="location"]::text',
            '[class*="address"]::text',
            '.location::text',
            '.address::text',
            '.city::text',
            '[class*="geo"]::text'
        ]
        
        for selector in selectors:
            location = response.css(selector).get()
            if location:
                location = location.strip()
                if 2 < len(location) < 50:  # Filtrer les valeurs aberrantes
                    return self.clean_location(location)
        
        # Extraire depuis les données structurées JSON-LD
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    # Chercher dans jobLocation
                    if 'jobLocation' in data:
                        job_loc = data['jobLocation']
                        if isinstance(job_loc, dict):
                            # Essayer différents champs d'adresse
                            for field in ['name', 'addressLocality', 'addressRegion', 'address']:
                                if field in job_loc and job_loc[field]:
                                    location = str(job_loc[field]).strip()
                                    if 2 < len(location) < 50:
                                        return self.clean_location(location)
                        elif isinstance(job_loc, str):
                            location = job_loc.strip()
                            if 2 < len(location) < 50:
                                return self.clean_location(location)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Extraction depuis les métadonnées OG
        og_title = response.css('meta[property="og:title"]::attr(content)').get()
        if og_title:
            # Pattern: "Titre — Localisation | Site"
            if '—' in og_title:
                parts = og_title.split('—')
                if len(parts) >= 2:
                    # La localisation peut être dans la deuxième partie
                    second_part = parts[1].strip()
                    if '|' in second_part:
                        location_part = second_part.split('|')[0].strip()
                        if 2 < len(location_part) < 50:
                            return self.clean_location(location_part)
        
        # Recherche dans le texte avec patterns améliorés
        text = response.text
        location_patterns = [
            r'(?:localisation|lieu|location|ville)[:\s]+([A-Za-z\s-]{3,30})',
            r'(?:à|en|sur)\s+([A-Z][a-z\s-]{3,30})',
            r'(?:Paris|Lyon|Marseille|Toulouse|Nice|Nantes|Strasbourg|Montpellier|Bordeaux|Lille|Rennes|Reims|Le Havre|Saint-Étienne|Toulon|Grenoble|Dijon|Angers|Nîmes|Villeurbanne)',
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s*(?:,|\(|$)',  # Villes capitalisées
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if 2 < len(location) < 50:
                    return self.clean_location(location)
        
        return None
    
    def clean_location(self, location):
        """Nettoyer la localisation extraite"""
        if not location:
            return None
        
        # Supprimer les mots parasites
        noise_words = ['du', 'd', 'le', 'la', 'les', 'de', 'des', 'et', 'ou', 'à', 'en', 'sur']
        words = location.split()
        clean_words = [word for word in words if word.lower() not in noise_words or len(word) > 2]
        
        if clean_words:
            return ' '.join(clean_words).title()
        
        return location.title()
    
    def extract_seniority(self, response):
        """Extraire le niveau de séniorité"""
        text = response.text.lower()
        
        if any(word in text for word in ['senior', 'expérimenté', 'expert', 'lead']):
            return 'senior'
        elif any(word in text for word in ['junior', 'débutant', 'junior']):
            return 'junior'
        elif any(word in text for word in ['intermédiaire', 'confirmé']):
            return 'intermediate'
        
        return None
    
    def extract_remote_policy(self, response):
        """Extraire la politique de télétravail"""
        text = response.text.lower()
        
        if any(word in text for word in ['100% remote', 'full remote', 'télétravail complet']):
            return 'remote'
        elif any(word in text for word in ['hybride', 'télétravail partiel', 'flexible']):
            return 'flexible'
        elif any(word in text for word in ['présentiel', 'sur site', 'bureau']):
            return 'onsite'
        
        return 'flexible'  # Par défaut
    
    def extract_contract_type(self, response):
        """Extraire le type de contrat"""
        text = response.text.lower()
        
        if any(word in text for word in ['freelance', 'indépendant', 'mission']):
            return 'freelance'
        elif any(word in text for word in ['cdi', 'temps plein']):
            return 'permanent'
        elif any(word in text for word in ['cdd', 'temporaire']):
            return 'temporary'
        
        return 'freelance'  # Par défaut pour FreeWork
    
    def extract_description(self, response):
        """Extraire la description - Optimisé FreeWork"""
        # Sélecteurs optimisés identifiés par l'analyse
        selectors = [
            '[class*="content"] p::text',
            '[class*="description"] p::text',
            '[class*="detail"] p::text',
            '.job-description::text',
            '.offer-description::text',
            '[class*="content"]::text',
            '[class*="description"]::text'
        ]
        
        # Essayer chaque sélecteur
        for selector in selectors:
            descriptions = response.css(selector).getall()
            if descriptions:
                # Joindre et nettoyer
                full_desc = ' '.join([desc.strip() for desc in descriptions if desc.strip()])
                if len(full_desc) > 50:  # Description substantielle
                    return self.clean_text(full_desc)
        
        # Extraire depuis les données structurées JSON-LD
        json_scripts = response.css('script[type="application/ld+json"]::text').getall()
        for script in json_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, dict):
                    # Chercher description dans différents champs
                    for field in ['description', 'jobDescription', 'summary', 'overview']:
                        if field in data and data[field]:
                            desc = data[field].strip()
                            if len(desc) > 50:
                                return self.clean_text(desc)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Extraction depuis les meta tags
        meta_desc = response.css('meta[name="description"]::attr(content)').get()
        if meta_desc:
            meta_desc = meta_desc.strip()
            if len(meta_desc) > 50:
                return self.clean_text(meta_desc)
        
        # Recherche dans le texte brut avec patterns améliorés
        text = response.text
        desc_patterns = [
            r'<p[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*(?:content|description|detail)[^"]*"[^>]*>(.*?)</div>',
            r'Description[:\s]+(.*?)(?:\n|<)',
            r'Profil[:\s]+(.*?)(?:\n|<)',
            r'Missions?[:\s]+(.*?)(?:\n|<)'
        ]
        
        for pattern in desc_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # Nettoyer HTML
                clean_match = re.sub(r'<[^>]+>', '', match).strip()
                if len(clean_match) > 50:
                    return self.clean_text(clean_match)
        
        return None
    
    def clean_text(self, text):
        """Nettoyer le texte extrait"""
        if not text:
            return None
        
        # Supprimer HTML restant
        text = re.sub(r'<[^>]+>', '', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
        
        # Fallback: extraire le texte principal
        main_text = response.css('main::text, .content::text').getall()
        if main_text:
            return ' '.join([text.strip() for text in main_text if text.strip()])
        
        return None
