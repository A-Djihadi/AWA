"""
Extracteur spécialisé pour les technologies
"""
import re
from typing import List
from .base_extractor import BaseExtractor


class TechnologyExtractor(BaseExtractor):
    """Extracteur pour les technologies et compétences"""
    
    def __init__(self):
        super().__init__()
        
        # Base de données des technologies
        self.technologies_db = {
            # Langages de programmation
            'languages': [
                'javascript', 'typescript', 'python', 'java', 'php', 'c#', 'c++', 'c',
                'go', 'rust', 'ruby', 'scala', 'kotlin', 'swift', 'dart',
                'html', 'css', 'sql', 'bash', 'powershell'
            ],
            
            # Frameworks frontend
            'frontend': [
                'react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt.js',
                'gatsby', 'ember', 'backbone', 'jquery'
            ],
            
            # Frameworks backend
            'backend': [
                'spring', 'django', 'flask', 'express', 'fastapi', 'laravel',
                'symfony', 'rails', 'asp.net', 'node.js', 'gin', 'echo'
            ],
            
            # Bases de données
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'oracle', 'sqlite', 'cassandra', 'neo4j', 'dynamodb'
            ],
            
            # Cloud et DevOps
            'cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
                'ansible', 'jenkins', 'gitlab', 'github', 'circleci'
            ],
            
            # Outils et autres
            'tools': [
                'git', 'webpack', 'vite', 'maven', 'gradle', 'npm', 'yarn',
                'linux', 'windows', 'unix', 'nginx', 'apache'
            ]
        }
        
        # Créer une liste plate de toutes les technologies
        self.all_technologies = []
        for category in self.technologies_db.values():
            self.all_technologies.extend(category)
        
        # Sélecteurs CSS pour les technologies
        self.css_selectors = [
            '.technologies::text',
            '.skills::text',
            '.tech-stack::text',
            '[class*="technolog"]::text',
            '[class*="skill"]::text',
            '[class*="tech"]::text',
            '.requirements::text',
            '.qualifications::text'
        ]
        
        # Patterns regex pour extraction contextuelle
        self.tech_patterns = [
            r'(?:technolog|compétenc|skill|stack|outil)[^:]*:([^.]+)',
            r'(?:maîtrise|connaissance|expérience)(?:\s+(?:de|en))?\s+([^.]+)',
            r'(?:avec|using|utilisant)\s+([^.]+)',
        ]
    
    def extract(self, response) -> List[str]:
        """Extrait les technologies depuis une page"""
        found_technologies = set()
        
        # 1. Extraction depuis les sélecteurs CSS
        for selector in self.css_selectors:
            tech_text = self.extract_from_selectors(response, [selector])
            if tech_text:
                techs = self._extract_technologies_from_text(tech_text)
                found_technologies.update(techs)
        
        # 2. Extraction depuis JSON-LD
        json_techs = self.extract_from_json_ld(response, [
            'skills', 'technologies', 'requirements', 'qualifications'
        ])
        if json_techs:
            techs = self._extract_technologies_from_text(json_techs)
            found_technologies.update(techs)
        
        # 3. Extraction contextuelle depuis le texte complet
        full_text = response.text
        contextual_techs = self._extract_contextual_technologies(full_text)
        found_technologies.update(contextual_techs)
        
        # 4. Recherche directe dans le texte
        direct_techs = self._extract_technologies_from_text(full_text)
        found_technologies.update(direct_techs)
        
        # Nettoyer et retourner
        return self._clean_and_rank_technologies(list(found_technologies))
    
    def _extract_technologies_from_text(self, text: str) -> List[str]:
        """Extrait les technologies depuis un texte"""
        if not text:
            return []
        
        found = []
        text_lower = text.lower()
        
        for tech in self.all_technologies:
            # Recherche avec des limites de mots pour éviter les faux positifs
            pattern = r'\b' + re.escape(tech.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found.append(tech)
        
        return found
    
    def _extract_contextual_technologies(self, text: str) -> List[str]:
        """Extrait les technologies avec leur contexte"""
        found = []
        
        for pattern in self.tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_text = match.group(1)
                if context_text:
                    techs = self._extract_technologies_from_text(context_text)
                    found.extend(techs)
        
        return found
    
    def _clean_and_rank_technologies(self, technologies: List[str]) -> List[str]:
        """Nettoie et classe les technologies par pertinence"""
        if not technologies:
            return []
        
        # Supprimer les doublons et normaliser
        unique_techs = {}
        for tech in technologies:
            normalized = self._normalize_technology_name(tech)
            if normalized:
                unique_techs[normalized] = tech
        
        # Limiter le nombre de technologies
        sorted_techs = list(unique_techs.values())[:15]
        
        return sorted_techs
    
    def _normalize_technology_name(self, tech: str) -> str:
        """Normalise le nom d'une technologie"""
        if not tech:
            return ""
        
        # Mappings pour normaliser les noms
        normalization_map = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'node': 'Node.js',
            'react.js': 'React',
            'vue.js': 'Vue',
            'angular.js': 'Angular',
            'c#': 'C#',
            '.net': 'ASP.NET',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'mongodb': 'MongoDB'
        }
        
        tech_lower = tech.lower().strip()
        
        # Vérifier les mappings
        if tech_lower in normalization_map:
            return normalization_map[tech_lower]
        
        # Capitaliser correctement
        return tech.title().strip()
    
    def get_technologies_by_category(self, technologies: List[str]) -> dict:
        """Classe les technologies par catégorie"""
        categorized = {
            'languages': [],
            'frontend': [],
            'backend': [],
            'databases': [],
            'cloud': [],
            'tools': []
        }
        
        for tech in technologies:
            tech_lower = tech.lower()
            for category, tech_list in self.technologies_db.items():
                if tech_lower in tech_list:
                    categorized[category].append(tech)
                    break
        
        return categorized
