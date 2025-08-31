"""
Modèles pour les offres d'emploi TJM
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum
from datetime import datetime


class ContractType(Enum):
    """Types de contrats"""
    FREELANCE = "freelance"
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"


class SeniorityLevel(Enum):
    """Niveaux de séniorité"""
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


class RemotePolicy(Enum):
    """Politiques de télétravail"""
    ONSITE = "onsite"
    REMOTE = "remote"
    FLEXIBLE = "flexible"
    HYBRID = "hybrid"


@dataclass
class TJMRange:
    """Représente une fourchette de TJM"""
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None
    currency: str = "EUR"
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.min_amount is not None and self.min_amount < 0:
            raise ValueError("Le TJM minimum ne peut pas être négatif")
        if self.max_amount is not None and self.max_amount < 0:
            raise ValueError("Le TJM maximum ne peut pas être négatif")
        if (self.min_amount is not None and self.max_amount is not None 
            and self.min_amount > self.max_amount):
            raise ValueError("Le TJM minimum ne peut pas être supérieur au maximum")
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si le TJM est valide"""
        return self.min_amount is not None or self.max_amount is not None
    
    @property
    def average(self) -> Optional[float]:
        """Calcule la moyenne si les deux valeurs sont présentes"""
        if self.min_amount is not None and self.max_amount is not None:
            return (self.min_amount + self.max_amount) / 2
        return None
    
    def __str__(self) -> str:
        if self.min_amount is not None and self.max_amount is not None:
            return f"{self.min_amount}-{self.max_amount}€"
        elif self.min_amount is not None:
            return f"À partir de {self.min_amount}€"
        elif self.max_amount is not None:
            return f"Jusqu'à {self.max_amount}€"
        return "TJM non spécifié"


@dataclass
class Company:
    """Informations sur l'entreprise"""
    name: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    sector: Optional[str] = None
    website: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si l'entreprise a des informations valides"""
        return self.name is not None and len(self.name.strip()) > 0


@dataclass
class Location:
    """Informations de localisation"""
    city: Optional[str] = None
    region: Optional[str] = None
    country: str = "France"
    postal_code: Optional[str] = None
    remote_friendly: bool = False
    
    @property
    def display_name(self) -> str:
        """Nom d'affichage de la localisation"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.region and self.region != self.city:
            parts.append(self.region)
        if self.country != "France":
            parts.append(self.country)
        return ", ".join(parts) if parts else "Non spécifié"
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si la localisation est valide"""
        return self.city is not None and len(self.city.strip()) > 0


@dataclass
class Job:
    """Modèle principal pour une offre d'emploi"""
    # Identifiants
    source: str
    source_id: str
    url: Optional[str] = None
    
    # Informations principales
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Entreprise
    company: Company = field(default_factory=Company)
    
    # Localisation
    location: Location = field(default_factory=Location)
    
    # TJM et contrat
    tjm: TJMRange = field(default_factory=TJMRange)
    contract_type: ContractType = ContractType.FREELANCE
    
    # Détails techniques
    technologies: List[str] = field(default_factory=list)
    seniority_level: Optional[SeniorityLevel] = None
    remote_policy: RemotePolicy = RemotePolicy.FLEXIBLE
    
    # Métadonnées
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validation après initialisation"""
        if not self.source or not self.source_id:
            raise ValueError("Source et source_id sont obligatoires")
        
        # Nettoyage des technologies
        self.technologies = [tech.strip().title() for tech in self.technologies if tech.strip()]
    
    @property
    def is_valid(self) -> bool:
        """Vérifie si l'offre est valide pour l'export"""
        return (
            self.title is not None 
            and len(self.title.strip()) > 0
            and self.tjm.is_valid
        )
    
    @property
    def quality_score(self) -> float:
        """Score de qualité de l'offre (0-1)"""
        score = 0.0
        max_score = 8.0
        
        # Titre (obligatoire)
        if self.title and len(self.title.strip()) > 10:
            score += 1.0
        
        # Description
        if self.description and len(self.description.strip()) > 50:
            score += 1.0
        
        # TJM
        if self.tjm.is_valid:
            score += 1.0
        
        # Entreprise
        if self.company.is_valid:
            score += 1.0
        
        # Localisation
        if self.location.is_valid:
            score += 1.0
        
        # Technologies
        if len(self.technologies) > 0:
            score += 1.0
        
        # Séniorité
        if self.seniority_level is not None:
            score += 1.0
        
        # URL
        if self.url:
            score += 1.0
        
        return score / max_score
    
    def to_dict(self) -> dict:
        """Convertit l'offre en dictionnaire pour l'export"""
        return {
            'source': self.source,
            'source_id': self.source_id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'company': self.company.name,
            'company_description': self.company.description,
            'company_size': self.company.size,
            'company_sector': self.company.sector,
            'location': self.location.display_name,
            'city': self.location.city,
            'region': self.location.region,
            'country': self.location.country,
            'tjm_min': self.tjm.min_amount,
            'tjm_max': self.tjm.max_amount,
            'tjm_currency': self.tjm.currency,
            'contract_type': self.contract_type.value,
            'technologies': self.technologies,
            'seniority_level': self.seniority_level.value if self.seniority_level else None,
            'remote_policy': self.remote_policy.value,
            'scraped_at': self.scraped_at.isoformat(),
            'quality_score': self.quality_score
        }
