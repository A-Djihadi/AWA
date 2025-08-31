"""
Data Transformers for ETL Pipeline
"""
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from models import JobOffer, Company, Location, TJMRange, QualityMetrics
from models import ContractType, RemotePolicy, SeniorityLevel


logger = logging.getLogger(__name__)


class BaseTransformer(ABC):
    """Base class for data transformers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
    
    @abstractmethod
    def transform(self, record: Dict[str, Any]) -> JobOffer:
        """Transform raw record to JobOffer"""
        pass


class StandardTransformer(BaseTransformer):
    """Standard transformer for job offers"""
    
    def __init__(self):
        super().__init__("standard")
        self.technology_normalizer = TechnologyNormalizer()
        self.location_parser = LocationParser()
        self.tjm_parser = TJMParser()
        self.quality_calculator = QualityCalculator()
    
    def transform(self, record: Dict[str, Any]) -> JobOffer:
        """Transform raw record to standardized JobOffer"""
        
        try:
            # Create base JobOffer
            offer = JobOffer(
                source=record.get('source', ''),
                source_id=str(record.get('source_id', '')),
                url=record.get('url'),
                title=record.get('title', ''),
                description=record.get('description'),
                raw_data=record.copy()
            )
            
            # Parse scraped_at timestamp
            if 'scraped_at' in record:
                try:
                    offer.scraped_at = datetime.fromisoformat(record['scraped_at'].replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    self.logger.warning(f"Invalid scraped_at format: {record.get('scraped_at')}")
            
            # Transform company information
            offer.company = self._transform_company(record)
            
            # Transform TJM information
            offer.tjm = self.tjm_parser.parse_tjm(record)
            
            # Transform technologies
            offer.technologies = self.technology_normalizer.normalize_technologies(
                record.get('technologies', [])
            )
            
            # Transform location
            offer.location = self.location_parser.parse_location(record)
            
            # Transform contract and work info
            offer.contract_type = self._parse_contract_type(record.get('contract_type'))
            offer.remote_policy = self._parse_remote_policy(record.get('remote_policy'))
            offer.seniority_level = self._parse_seniority_level(record.get('seniority_level'))
            
            # Calculate quality metrics
            offer.quality_metrics = self.quality_calculator.calculate_quality(offer)
            
            return offer
            
        except Exception as e:
            self.logger.error(f"Error transforming record {record.get('source_id')}: {e}")
            raise
    
    def _transform_company(self, record: Dict[str, Any]) -> Optional[Company]:
        """Transform company information"""
        
        company_name = record.get('company')
        if not company_name or not company_name.strip():
            return None
        
        return Company(
            name=company_name.strip(),
            industry=record.get('company_industry'),
            size=record.get('company_size'),
            is_client=record.get('is_direct_client', False)
        )
    
    def _parse_contract_type(self, contract_type: Optional[str]) -> ContractType:
        """Parse contract type"""
        if not contract_type:
            return ContractType.FREELANCE
        
        contract_type = contract_type.lower().strip()
        
        mapping = {
            'freelance': ContractType.FREELANCE,
            'cdi': ContractType.CDI,
            'cdd': ContractType.CDD,
            'stage': ContractType.STAGE,
            'apprentissage': ContractType.APPRENTISSAGE,
        }
        
        return mapping.get(contract_type, ContractType.FREELANCE)
    
    def _parse_remote_policy(self, remote_policy: Optional[str]) -> Optional[RemotePolicy]:
        """Parse remote work policy"""
        if not remote_policy:
            return None
        
        remote_policy = remote_policy.lower().strip()
        
        mapping = {
            'on_site': RemotePolicy.ON_SITE,
            'sur site': RemotePolicy.ON_SITE,
            'présentiel': RemotePolicy.ON_SITE,
            'remote': RemotePolicy.REMOTE,
            'télétravail': RemotePolicy.REMOTE,
            '100% remote': RemotePolicy.REMOTE,
            'hybrid': RemotePolicy.HYBRID,
            'hybride': RemotePolicy.HYBRID,
            'mixte': RemotePolicy.HYBRID,
            'negotiable': RemotePolicy.NEGOTIABLE,
            'négociable': RemotePolicy.NEGOTIABLE,
        }
        
        return mapping.get(remote_policy)
    
    def _parse_seniority_level(self, seniority: Optional[str]) -> Optional[SeniorityLevel]:
        """Parse seniority level"""
        if not seniority:
            return None
        
        seniority = seniority.lower().strip()
        
        mapping = {
            'junior': SeniorityLevel.JUNIOR,
            'débutant': SeniorityLevel.JUNIOR,
            'middle': SeniorityLevel.MIDDLE,
            'intermédiaire': SeniorityLevel.MIDDLE,
            'confirmé': SeniorityLevel.MIDDLE,
            'senior': SeniorityLevel.SENIOR,
            'expérimenté': SeniorityLevel.SENIOR,
            'lead': SeniorityLevel.LEAD,
            'expert': SeniorityLevel.EXPERT,
            'architect': SeniorityLevel.EXPERT,
            'architecte': SeniorityLevel.EXPERT,
        }
        
        return mapping.get(seniority)


class TechnologyNormalizer:
    """Normalize and standardize technology names"""
    
    def __init__(self):
        self.technology_map = self._build_technology_map()
        self.valid_technologies = set(self.technology_map.keys())
    
    def normalize_technologies(self, technologies: List[str]) -> List[str]:
        """Normalize technology list"""
        if not technologies:
            return []
        
        normalized = []
        
        for tech in technologies:
            if not tech or not isinstance(tech, str):
                continue
            
            # Clean and normalize
            tech = tech.strip()
            normalized_tech = self._normalize_single_technology(tech)
            
            if normalized_tech and normalized_tech not in normalized:
                normalized.append(normalized_tech)
        
        return sorted(normalized)
    
    def _normalize_single_technology(self, tech: str) -> Optional[str]:
        """Normalize a single technology name"""
        
        # Clean input
        tech = re.sub(r'[^\w\s\.\+\#-]', '', tech)
        tech = re.sub(r'\s+', ' ', tech).strip()
        
        if not tech:
            return None
        
        # Direct match
        tech_lower = tech.lower()
        if tech_lower in self.technology_map:
            return self.technology_map[tech_lower]
        
        # Partial match for common variations
        for key, value in self.technology_map.items():
            if key in tech_lower or tech_lower in key:
                return value
        
        # Return capitalized version if not found
        return tech.title()
    
    def _build_technology_map(self) -> Dict[str, str]:
        """Build technology normalization mapping"""
        return {
            # Programming Languages
            'python': 'Python',
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'typescript': 'TypeScript',
            'ts': 'TypeScript',
            'java': 'Java',
            'c#': 'C#',
            'csharp': 'C#',
            'php': 'PHP',
            'ruby': 'Ruby',
            'go': 'Go',
            'golang': 'Go',
            'rust': 'Rust',
            'kotlin': 'Kotlin',
            'swift': 'Swift',
            'scala': 'Scala',
            'clojure': 'Clojure',
            
            # Frameworks
            'react': 'React',
            'reactjs': 'React',
            'vue': 'Vue.js',
            'vuejs': 'Vue.js',
            'angular': 'Angular',
            'angularjs': 'AngularJS',
            'django': 'Django',
            'flask': 'Flask',
            'spring': 'Spring',
            'spring boot': 'Spring Boot',
            'express': 'Express.js',
            'nodejs': 'Node.js',
            'node.js': 'Node.js',
            'nextjs': 'Next.js',
            'next.js': 'Next.js',
            'nuxt': 'Nuxt.js',
            'nuxtjs': 'Nuxt.js',
            
            # Databases
            'postgresql': 'PostgreSQL',
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'mongo': 'MongoDB',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'cassandra': 'Cassandra',
            'oracle': 'Oracle',
            'sql server': 'SQL Server',
            'sqlserver': 'SQL Server',
            'sqlite': 'SQLite',
            
            # Cloud & DevOps
            'aws': 'AWS',
            'amazon web services': 'AWS',
            'azure': 'Azure',
            'gcp': 'Google Cloud',
            'google cloud': 'Google Cloud',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'terraform': 'Terraform',
            'ansible': 'Ansible',
            'jenkins': 'Jenkins',
            'gitlab ci': 'GitLab CI',
            'github actions': 'GitHub Actions',
            
            # Frontend
            'html': 'HTML',
            'css': 'CSS',
            'sass': 'Sass',
            'scss': 'SCSS',
            'less': 'Less',
            'tailwind': 'Tailwind CSS',
            'tailwindcss': 'Tailwind CSS',
            'bootstrap': 'Bootstrap',
            'material-ui': 'Material-UI',
            'mui': 'Material-UI',
            
            # Tools
            'git': 'Git',
            'github': 'GitHub',
            'gitlab': 'GitLab',
            'jira': 'Jira',
            'confluence': 'Confluence',
            'slack': 'Slack',
            'teams': 'Microsoft Teams',
        }


class LocationParser:
    """Parse and normalize location information"""
    
    def __init__(self):
        self.french_regions = self._build_french_regions()
        self.city_aliases = self._build_city_aliases()
    
    def parse_location(self, record: Dict[str, Any]) -> Optional[Location]:
        """Parse location from record"""
        
        location_text = record.get('location')
        if not location_text or not isinstance(location_text, str):
            return None
        
        location_text = location_text.strip()
        if not location_text:
            return None
        
        # Parse location components
        city, region = self._parse_location_text(location_text)
        
        return Location(
            city=city,
            region=region,
            country="France",  # Default for French job sites
            raw_location=location_text
        )
    
    def _parse_location_text(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """Parse city and region from location text"""
        
        text = text.strip()
        
        # Common patterns
        patterns = [
            r'^(.+?),\s*(.+?)$',  # City, Region
            r'^(.+?)\s*-\s*(.+?)$',  # City - Region
            r'^(.+?)\s*\(\s*(.+?)\s*\)$',  # City (Region)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                city_part = match.group(1).strip()
                region_part = match.group(2).strip()
                
                # Normalize city
                city = self._normalize_city(city_part)
                
                # Normalize region
                region = self._normalize_region(region_part)
                
                return city, region
        
        # Single location (probably a city)
        normalized_city = self._normalize_city(text)
        
        # Try to infer region from city
        region = self._infer_region_from_city(normalized_city)
        
        return normalized_city, region
    
    def _normalize_city(self, city: str) -> str:
        """Normalize city name"""
        city = city.strip().title()
        
        # Apply aliases
        city_lower = city.lower()
        if city_lower in self.city_aliases:
            return self.city_aliases[city_lower]
        
        return city
    
    def _normalize_region(self, region: str) -> Optional[str]:
        """Normalize region name"""
        region = region.strip()
        region_lower = region.lower()
        
        # Check if it's a known French region
        for standard_region, aliases in self.french_regions.items():
            if region_lower == standard_region.lower():
                return standard_region
            if region_lower in [alias.lower() for alias in aliases]:
                return standard_region
        
        return region.title()
    
    def _infer_region_from_city(self, city: str) -> Optional[str]:
        """Infer region from city name"""
        city_lower = city.lower()
        
        # Major cities mapping
        city_to_region = {
            'paris': 'Île-de-France',
            'lyon': 'Auvergne-Rhône-Alpes',
            'marseille': "Provence-Alpes-Côte d'Azur",
            'toulouse': 'Occitanie',
            'nice': "Provence-Alpes-Côte d'Azur",
            'nantes': 'Pays de la Loire',
            'montpellier': 'Occitanie',
            'strasbourg': 'Grand Est',
            'bordeaux': 'Nouvelle-Aquitaine',
            'lille': 'Hauts-de-France',
            'rennes': 'Bretagne',
            'reims': 'Grand Est',
            'nancy': 'Grand Est',
            'dijon': 'Bourgogne-Franche-Comté',
            'angers': 'Pays de la Loire',
            'nîmes': 'Occitanie',
            'villeurbanne': 'Auvergne-Rhône-Alpes',
            'clermont-ferrand': 'Auvergne-Rhône-Alpes',
            'tours': 'Centre-Val de Loire',
            'orléans': 'Centre-Val de Loire',
        }
        
        return city_to_region.get(city_lower)
    
    def _build_french_regions(self) -> Dict[str, List[str]]:
        """Build French regions with aliases"""
        return {
            'Île-de-France': ['idf', 'paris region', 'région parisienne'],
            'Auvergne-Rhône-Alpes': ['aura', 'rhône-alpes', 'auvergne'],
            "Provence-Alpes-Côte d'Azur": ['paca', 'côte d\'azur', 'provence'],
            'Occitanie': ['languedoc', 'midi-pyrénées'],
            'Nouvelle-Aquitaine': ['aquitaine', 'limousin', 'poitou-charentes'],
            'Pays de la Loire': [],
            'Hauts-de-France': ['nord-pas-de-calais', 'picardie'],
            'Grand Est': ['alsace', 'lorraine', 'champagne-ardenne'],
            'Normandie': ['basse-normandie', 'haute-normandie'],
            'Bretagne': [],
            'Centre-Val de Loire': ['centre'],
            'Bourgogne-Franche-Comté': ['bourgogne', 'franche-comté'],
        }
    
    def _build_city_aliases(self) -> Dict[str, str]:
        """Build city aliases mapping"""
        return {
            'paris': 'Paris',
            'lyon': 'Lyon',
            'marseille': 'Marseille',
            'toulouse': 'Toulouse',
            'nice': 'Nice',
            'nantes': 'Nantes',
            'montpellier': 'Montpellier',
            'strasbourg': 'Strasbourg',
            'bordeaux': 'Bordeaux',
            'lille': 'Lille',
            'rennes': 'Rennes',
        }


class TJMParser:
    """Parse TJM (daily rate) information"""
    
    def parse_tjm(self, record: Dict[str, Any]) -> Optional[TJMRange]:
        """Parse TJM range from record"""
        
        tjm_min = self._parse_tjm_value(record.get('tjm_min'))
        tjm_max = self._parse_tjm_value(record.get('tjm_max'))
        currency = record.get('tjm_currency', 'EUR')
        
        # If we have a single TJM value, try to parse from title or description
        if tjm_min is None and tjm_max is None:
            tjm_range = self._extract_tjm_from_text(
                record.get('title', '') + ' ' + record.get('description', '')
            )
            if tjm_range:
                tjm_min, tjm_max = tjm_range
        
        if tjm_min is None and tjm_max is None:
            return None
        
        tjm = TJMRange(min_rate=tjm_min, max_rate=tjm_max, currency=currency)
        
        if tjm.is_valid():
            return tjm
        
        return None
    
    def _parse_tjm_value(self, value: Any) -> Optional[float]:
        """Parse single TJM value"""
        if value is None or value == '':
            return None
        
        if isinstance(value, (int, float)):
            return float(value) if value > 0 else None
        
        if isinstance(value, str):
            # Clean string and extract numeric value
            value = re.sub(r'[^\d,.]', '', value)
            value = value.replace(',', '.')
            
            try:
                return float(value) if value else None
            except ValueError:
                return None
        
        return None
    
    def _extract_tjm_from_text(self, text: str) -> Optional[tuple[Optional[float], Optional[float]]]:
        """Extract TJM range from text"""
        if not text:
            return None
        
        # Patterns for TJM extraction
        patterns = [
            r'(\d+)\s*-\s*(\d+)\s*€',  # 500-600€
            r'(\d+)\s*à\s*(\d+)\s*€',  # 500 à 600€
            r'TJM\s*:?\s*(\d+)\s*-\s*(\d+)',  # TJM: 500-600
            r'(\d+)€\s*-\s*(\d+)€',  # 500€-600€
            r'(\d+)\s*€',  # Single value: 500€
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 2:
                    try:
                        min_val = float(groups[0])
                        max_val = float(groups[1])
                        return min_val, max_val
                    except ValueError:
                        continue
                elif len(groups) == 1:
                    try:
                        val = float(groups[0])
                        return val, val
                    except ValueError:
                        continue
        
        return None


class QualityCalculator:
    """Calculate data quality metrics"""
    
    def calculate_quality(self, offer: JobOffer) -> QualityMetrics:
        """Calculate quality metrics for job offer"""
        
        metrics = QualityMetrics()
        
        # Calculate completeness score
        metrics.completeness_score = self._calculate_completeness(offer)
        
        # Calculate accuracy score
        metrics.accuracy_score = self._calculate_accuracy(offer)
        
        # Calculate consistency score
        metrics.consistency_score = self._calculate_consistency(offer)
        
        # Calculate overall score
        metrics.calculate_overall_score()
        
        # Identify missing fields and issues
        metrics.missing_fields = self._identify_missing_fields(offer)
        metrics.data_issues = self._identify_data_issues(offer)
        
        return metrics
    
    def _calculate_completeness(self, offer: JobOffer) -> float:
        """Calculate completeness score (0-1)"""
        
        # Core fields (weight: 40%)
        core_fields = {
            'source': 1.0 if offer.source else 0.0,
            'source_id': 1.0 if offer.source_id else 0.0,
            'title': 1.0 if offer.title else 0.0,
            'url': 1.0 if offer.url else 0.0,
        }
        
        # Important fields (weight: 40%)
        important_fields = {
            'company': 1.0 if (offer.company and offer.company.is_valid()) else 0.0,
            'tjm': 1.0 if (offer.tjm and offer.tjm.is_valid()) else 0.0,
            'technologies': 1.0 if offer.technologies else 0.0,
            'location': 1.0 if offer.location else 0.0,
        }
        
        # Optional fields (weight: 20%)
        optional_fields = {
            'description': 1.0 if offer.description else 0.0,
            'seniority_level': 1.0 if offer.seniority_level else 0.0,
            'remote_policy': 1.0 if offer.remote_policy else 0.0,
        }
        
        # Calculate weighted score
        core_score = sum(core_fields.values()) / len(core_fields)
        important_score = sum(important_fields.values()) / len(important_fields)
        optional_score = sum(optional_fields.values()) / len(optional_fields)
        
        return 0.4 * core_score + 0.4 * important_score + 0.2 * optional_score
    
    def _calculate_accuracy(self, offer: JobOffer) -> float:
        """Calculate accuracy score (0-1)"""
        
        accuracy_checks = []
        
        # Title should be meaningful
        if offer.title:
            if len(offer.title) > 10 and not re.match(r'^[\d\s\-_]+$', offer.title):
                accuracy_checks.append(1.0)
            else:
                accuracy_checks.append(0.0)
        else:
            accuracy_checks.append(0.0)
        
        # TJM should be reasonable
        if offer.tjm and offer.tjm.is_valid():
            avg_tjm = offer.tjm.get_average()
            if avg_tjm and 100 <= avg_tjm <= 2000:  # Reasonable TJM range
                accuracy_checks.append(1.0)
            else:
                accuracy_checks.append(0.5)
        else:
            accuracy_checks.append(0.7)  # Missing TJM is not necessarily inaccurate
        
        # Technologies should be reasonable
        if offer.technologies:
            if 1 <= len(offer.technologies) <= 15:  # Reasonable tech count
                accuracy_checks.append(1.0)
            else:
                accuracy_checks.append(0.5)
        else:
            accuracy_checks.append(0.7)
        
        # Company name should be meaningful
        if offer.company and offer.company.name:
            if len(offer.company.name) > 2 and offer.company.name != 'N/A':
                accuracy_checks.append(1.0)
            else:
                accuracy_checks.append(0.0)
        else:
            accuracy_checks.append(0.7)
        
        return sum(accuracy_checks) / len(accuracy_checks) if accuracy_checks else 0.0
    
    def _calculate_consistency(self, offer: JobOffer) -> float:
        """Calculate consistency score (0-1)"""
        
        consistency_checks = []
        
        # Check TJM consistency
        if offer.tjm:
            if offer.tjm.min_rate and offer.tjm.max_rate:
                if offer.tjm.min_rate <= offer.tjm.max_rate:
                    consistency_checks.append(1.0)
                else:
                    consistency_checks.append(0.0)
            else:
                consistency_checks.append(0.8)  # Single value is consistent
        
        # Check technology consistency (no obvious duplicates)
        if offer.technologies:
            unique_techs = set([tech.lower() for tech in offer.technologies])
            if len(unique_techs) == len(offer.technologies):
                consistency_checks.append(1.0)
            else:
                consistency_checks.append(0.5)
        
        # Check timestamps
        if offer.scraped_at and offer.processed_at:
            if offer.scraped_at <= offer.processed_at:
                consistency_checks.append(1.0)
            else:
                consistency_checks.append(0.0)
        else:
            consistency_checks.append(0.8)
        
        return sum(consistency_checks) / len(consistency_checks) if consistency_checks else 1.0
    
    def _identify_missing_fields(self, offer: JobOffer) -> List[str]:
        """Identify missing important fields"""
        
        missing = []
        
        if not offer.company or not offer.company.is_valid():
            missing.append('company')
        
        if not offer.tjm or not offer.tjm.is_valid():
            missing.append('tjm')
        
        if not offer.technologies:
            missing.append('technologies')
        
        if not offer.location:
            missing.append('location')
        
        if not offer.description:
            missing.append('description')
        
        return missing
    
    def _identify_data_issues(self, offer: JobOffer) -> List[str]:
        """Identify data quality issues"""
        
        issues = []
        
        # Title issues
        if not offer.title or len(offer.title) < 5:
            issues.append('Title too short or missing')
        
        # TJM issues
        if offer.tjm:
            avg_tjm = offer.tjm.get_average()
            if avg_tjm and (avg_tjm < 50 or avg_tjm > 3000):
                issues.append(f'Unrealistic TJM value: {avg_tjm}')
        
        # Technology issues
        if offer.technologies and len(offer.technologies) > 20:
            issues.append('Too many technologies listed')
        
        # Company issues
        if offer.company and offer.company.name:
            if len(offer.company.name) < 3:
                issues.append('Company name too short')
        
        return issues
