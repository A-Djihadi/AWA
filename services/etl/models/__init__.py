"""
Data Models for ETL Pipeline
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ContractType(Enum):
    """Contract types"""
    FREELANCE = "freelance"
    CDI = "cdi"
    CDD = "cdd"
    STAGE = "stage"
    APPRENTISSAGE = "apprentissage"


class RemotePolicy(Enum):
    """Remote work policies"""
    ON_SITE = "on_site"
    REMOTE = "remote"
    HYBRID = "hybrid"
    NEGOTIABLE = "negotiable"


class SeniorityLevel(Enum):
    """Seniority levels"""
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
    EXPERT = "expert"


@dataclass
class TJMRange:
    """TJM (Daily Rate) range"""
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    currency: str = "EUR"
    
    def is_valid(self) -> bool:
        """Check if TJM range is valid"""
        if self.min_rate is None and self.max_rate is None:
            return False
        if self.min_rate and self.min_rate <= 0:
            return False
        if self.max_rate and self.max_rate <= 0:
            return False
        if self.min_rate and self.max_rate and self.min_rate > self.max_rate:
            return False
        return True
    
    def get_average(self) -> Optional[float]:
        """Get average TJM"""
        if self.min_rate and self.max_rate:
            return (self.min_rate + self.max_rate) / 2
        return self.min_rate or self.max_rate


@dataclass
class Location:
    """Location information"""
    city: Optional[str] = None
    region: Optional[str] = None
    country: str = "France"
    raw_location: Optional[str] = None
    
    def normalize(self) -> str:
        """Get normalized location string"""
        parts = [self.city, self.region, self.country]
        return ", ".join([p for p in parts if p])


@dataclass
class Company:
    """Company information"""
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    is_client: bool = False  # True if direct client, False if ESN
    
    def is_valid(self) -> bool:
        """Check if company info is valid"""
        return bool(self.name and self.name.strip())


@dataclass
class QualityMetrics:
    """Data quality metrics"""
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    overall_score: float = 0.0
    
    missing_fields: List[str] = field(default_factory=list)
    data_issues: List[str] = field(default_factory=list)
    
    def calculate_overall_score(self):
        """Calculate overall quality score"""
        scores = [self.completeness_score, self.accuracy_score, self.consistency_score]
        self.overall_score = sum(scores) / len(scores) if scores else 0.0


@dataclass
class JobOffer:
    """Standardized job offer model"""
    
    # Identifiers
    source: str
    source_id: str
    url: Optional[str] = None
    
    # Basic Information
    title: str = ""
    description: Optional[str] = None
    company: Optional[Company] = None
    
    # Financial
    tjm: Optional[TJMRange] = None
    
    # Technical
    technologies: List[str] = field(default_factory=list)
    seniority_level: Optional[SeniorityLevel] = None
    
    # Location and Work
    location: Optional[Location] = None
    remote_policy: Optional[RemotePolicy] = None
    contract_type: ContractType = ContractType.FREELANCE
    
    # Metadata
    scraped_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    quality_metrics: Optional[QualityMetrics] = None
    
    # Raw data for debugging
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post initialization processing"""
        if self.processed_at is None:
            self.processed_at = datetime.utcnow()
        
        if self.quality_metrics is None:
            self.quality_metrics = QualityMetrics()
    
    def get_unique_id(self) -> str:
        """Get unique identifier for the job offer"""
        return f"{self.source}:{self.source_id}"
    
    def is_valid(self) -> bool:
        """Check if job offer meets minimum requirements"""
        if not self.source or not self.source_id or not self.title:
            return False
        
        if self.quality_metrics and self.quality_metrics.overall_score < 0.3:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        # Combine location fields into single location string
        location_parts = []
        if self.location:
            if self.location.city:
                location_parts.append(self.location.city)
            if self.location.region:
                location_parts.append(self.location.region)
            if self.location.country:
                location_parts.append(self.location.country)
        
        location_str = ", ".join(location_parts) if location_parts else None
        
        return {
            'source': self.source,
            'source_id': self.source_id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'company': self.company.name if self.company else None,
            'tjm_min': int(self.tjm.min_rate) if self.tjm and self.tjm.min_rate else None,
            'tjm_max': int(self.tjm.max_rate) if self.tjm and self.tjm.max_rate else None,
            'tjm_currency': self.tjm.currency if self.tjm else 'EUR',
            'technologies': self.technologies,
            'seniority_level': self.seniority_level.value if self.seniority_level else None,
            'location': location_str,
            'remote_policy': self.remote_policy.value if self.remote_policy else None,
            'contract_type': self.contract_type.value,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'normalized_at': self.processed_at.isoformat() if self.processed_at else None,
        }


@dataclass
class ETLBatch:
    """ETL processing batch"""
    batch_id: str
    source_files: List[str]
    total_records: int = 0
    processed_records: int = 0
    valid_records: int = 0
    error_records: int = 0
    processing_time: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """Get processing success rate"""
        if self.total_records == 0:
            return 0.0
        return self.valid_records / self.total_records
    
    def add_error(self, error: str):
        """Add error to batch"""
        self.errors.append(error)
        self.error_records += 1
