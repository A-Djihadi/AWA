"""
Modèle pour les résultats de scraping
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .job import Job


@dataclass
class ScraperStats:
    """Statistiques de scraping"""
    total_pages_visited: int = 0
    total_jobs_found: int = 0
    total_jobs_valid: int = 0
    total_jobs_with_tjm: int = 0
    errors_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Durée du scraping en secondes"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Taux de succès (jobs valides / jobs trouvés)"""
        if self.total_jobs_found > 0:
            return self.total_jobs_valid / self.total_jobs_found
        return 0.0
    
    @property
    def tjm_rate(self) -> float:
        """Taux de jobs avec TJM"""
        if self.total_jobs_valid > 0:
            return self.total_jobs_with_tjm / self.total_jobs_valid
        return 0.0


@dataclass
class ScraperResult:
    """Résultat complet d'une session de scraping"""
    source: str
    jobs: List[Job] = field(default_factory=list)
    stats: ScraperStats = field(default_factory=ScraperStats)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_job(self, job: Job) -> None:
        """Ajoute un job et met à jour les stats"""
        self.jobs.append(job)
        self.stats.total_jobs_found += 1
        
        if job.is_valid:
            self.stats.total_jobs_valid += 1
        
        if job.tjm.is_valid:
            self.stats.total_jobs_with_tjm += 1
    
    def add_error(self, error: str) -> None:
        """Ajoute une erreur et met à jour les stats"""
        self.errors.append(error)
        self.stats.errors_count += 1
    
    @property
    def quality_jobs(self) -> List[Job]:
        """Jobs avec un score de qualité élevé (>0.7)"""
        return [job for job in self.jobs if job.quality_score > 0.7]
    
    @property
    def average_quality_score(self) -> float:
        """Score de qualité moyen"""
        if not self.jobs:
            return 0.0
        return sum(job.quality_score for job in self.jobs) / len(self.jobs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Résumé des résultats"""
        return {
            'source': self.source,
            'total_jobs': len(self.jobs),
            'valid_jobs': len([job for job in self.jobs if job.is_valid]),
            'quality_jobs': len(self.quality_jobs),
            'average_quality': round(self.average_quality_score, 3),
            'tjm_coverage': round(self.stats.tjm_rate, 3),
            'success_rate': round(self.stats.success_rate, 3),
            'errors': len(self.errors),
            'duration_seconds': self.stats.duration_seconds,
            'technologies_found': len(set(tech for job in self.jobs for tech in job.technologies)),
        }
