"""
Spider pour scraper Freelance Informatique
"""
import scrapy
import re
from urllib.parse import urljoin, urlparse
from tjm_scraper.items import TjmOfferItem


class FreelanceInformatiqueSpider(scrapy.Spider):
    name = 'freelance_informatique'
    allowed_domains = ['freelance-informatique.fr']
    start_urls = [
        'https://www.freelance-informatique.fr/offres-freelance?page=1'
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def parse(self, response):
        """Parse mission listings page"""
        # Extract mission links (mise à jour avec les vrais sélecteurs)
        mission_links = response.css('.job-card-line .job-title a::attr(href)').getall()
        
        self.logger.info(f"Found {len(mission_links)} mission links on page")
        
        for link in mission_links:
            mission_url = urljoin(response.url, link)
            self.logger.info(f"Following mission: {mission_url}")
            yield response.follow(
                mission_url, 
                self.parse_mission,
                meta={'source_url': response.url}
            )
        
        # Pagination (chercher le bon sélecteur pour pagination)
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            self.logger.info(f"Found next page: {next_page}")
            yield response.follow(next_page, self.parse)

    def parse_mission(self, response):
        """Parse individual mission page"""
        try:
            # Extract basic info
            title = self.clean_text(response.css('h1::text').get())
            company = self.clean_text(response.css('.company-name::text').get())
            
            # Extract TJM from description
            tjm_info = self.extract_tjm(response)
            
            # Extract technologies
            technologies = self.extract_technologies(response)
            
            # Extract location
            location = self.extract_location(response)
            
            # Extract seniority
            seniority = self.extract_seniority(response)
            
            # Description
            description = self.clean_text(
                ' '.join(response.css('.mission-description ::text').getall())
            )
            
            # Create item
            item = TjmOfferItem(
                source='freelance_informatique',
                source_id=self.extract_source_id(response.url),
                title=title,
                company=company,
                tjm_min=tjm_info.get('min'),
                tjm_max=tjm_info.get('max'),
                tjm_currency=tjm_info.get('currency', 'EUR'),
                technologies=technologies,
                seniority_level=seniority,
                location=location,
                remote_policy=self.extract_remote_policy(response),
                contract_type='freelance',
                description=description,
                url=response.url
            )
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error parsing mission {response.url}: {e}")

    def extract_tjm(self, response):
        """Extract TJM information from text"""
        text = ' '.join(response.css('::text').getall()).lower()
        
        # Patterns pour détecter le TJM
        patterns = [
            r'tjm[:\s]*(\d+)(?:\s*[-à]\s*(\d+))?\s*[€k]?',
            r'taux[:\s]*(\d+)(?:\s*[-à]\s*(\d+))?\s*[€k]?',
            r'(\d+)(?:\s*[-à]\s*(\d+))?\s*[€k]?\s*\/\s*jour',
            r'(\d+)(?:\s*[-à]\s*(\d+))?\s*k?\s*€\s*par\s*jour',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                match = matches[0]
                if isinstance(match, tuple):
                    min_val = int(match[0]) if match[0] else None
                    max_val = int(match[1]) if match[1] else min_val
                else:
                    min_val = max_val = int(match)
                
                # Conversion si en milliers
                if 'k' in text and min_val and min_val < 10:
                    min_val *= 1000
                    max_val *= 1000
                
                return {
                    'min': min_val,
                    'max': max_val,
                    'currency': 'EUR'
                }
        
        return {'min': None, 'max': None, 'currency': 'EUR'}

    def extract_technologies(self, response):
        """Extract technologies from text"""
        # Technologies communes dans le domaine
        tech_keywords = [
            # Frontend
            'react', 'angular', 'vue', 'vuejs', 'javascript', 'typescript',
            'next.js', 'nuxt.js', 'svelte', 'html', 'css', 'sass', 'scss',
            
            # Backend
            'python', 'django', 'flask', 'fastapi', 'java', 'spring',
            'node.js', 'express', 'php', 'laravel', 'symfony', 'c#',
            '.net', 'ruby', 'rails', 'go', 'golang', 'rust',
            
            # Database
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'sqlite', 'oracle',
            
            # DevOps
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform',
            'ansible', 'jenkins', 'gitlab', 'github', 'ci/cd',
            
            # Mobile
            'react native', 'flutter', 'ios', 'android', 'swift', 'kotlin',
        ]
        
        text = ' '.join(response.css('::text').getall()).lower()
        found_techs = []
        
        for tech in tech_keywords:
            if tech in text:
                found_techs.append(tech.title())
        
        return list(set(found_techs))  # Remove duplicates

    def extract_location(self, response):
        """Extract location information"""
        location_text = response.css('.location::text').get()
        if location_text:
            return self.clean_text(location_text)
        
        # Fallback: search in text
        text = ' '.join(response.css('::text').getall())
        location_patterns = [
            r'(?:lieu|localisation|adresse)[:\s]*([^,\n]+)',
            r'(paris|lyon|marseille|toulouse|nantes|strasbourg|bordeaux|lille)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        
        return None

    def extract_seniority(self, response):
        """Extract seniority level"""
        text = ' '.join(response.css('::text').getall()).lower()
        
        if any(word in text for word in ['senior', 'expert', 'lead', 'principal']):
            return 'senior'
        elif any(word in text for word in ['junior', 'débutant', 'entry']):
            return 'junior'
        elif any(word in text for word in ['confirmé', 'intermédiaire', 'mid']):
            return 'mid'
        
        return None

    def extract_remote_policy(self, response):
        """Extract remote work policy"""
        text = ' '.join(response.css('::text').getall()).lower()
        
        if any(word in text for word in ['100% remote', 'full remote', 'télétravail']):
            return 'remote'
        elif any(word in text for word in ['hybride', 'hybrid', 'partiel']):
            return 'hybrid'
        elif any(word in text for word in ['sur site', 'présentiel', 'on-site']):
            return 'on-site'
        
        return 'flexible'

    def extract_source_id(self, url):
        """Extract unique ID from URL"""
        # Extract ID from URL path or query params
        url_parts = urlparse(url)
        path_parts = url_parts.path.split('/')
        
        # Try to find numeric ID in path
        for part in reversed(path_parts):
            if part.isdigit():
                return part
        
        # Fallback: use last part of path
        return path_parts[-1] if path_parts[-1] else url

    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return None
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text if text else None
