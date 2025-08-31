"""
Pipelines refactorisées pour le traitement des données
"""
import json
import logging
from typing import Dict, Any, Set
from datetime import datetime
from pathlib import Path

from ..models import Job
from ..utils import DataValidator, TextCleaner


class ValidationPipeline:
    """Pipeline de validation des données"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_stats = {
            'total_items': 0,
            'valid_items': 0,
            'invalid_items': 0,
            'validation_errors': {}
        }
    
    def process_item(self, item: Dict[str, Any], spider):
        """Valide un item"""
        self.validation_stats['total_items'] += 1
        
        # Validation des données
        errors = DataValidator.validate_job_data(item)
        
        if errors:
            self.validation_stats['invalid_items'] += 1
            
            # Compter les types d'erreurs
            for error in errors:
                error_type = error.split(':')[0] if ':' in error else error
                self.validation_stats['validation_errors'][error_type] = (
                    self.validation_stats['validation_errors'].get(error_type, 0) + 1
                )
            
            # Log des erreurs en mode strict
            if spider.settings.get('VALIDATION_CONFIG', {}).get('strict_mode', False):
                self.logger.warning(f"Item invalide rejeté: {errors}")
                raise DropItem(f"Validation échouée: {errors}")
            else:
                self.logger.debug(f"Item avec erreurs conservé: {errors}")
        
        self.validation_stats['valid_items'] += 1
        return item
    
    def close_spider(self, spider):
        """Log des statistiques de validation"""
        stats = self.validation_stats
        self.logger.info(f"📊 Validation - Total: {stats['total_items']}, "
                        f"Valides: {stats['valid_items']}, "
                        f"Invalides: {stats['invalid_items']}")
        
        if stats['validation_errors']:
            self.logger.info("❌ Erreurs de validation:")
            for error_type, count in stats['validation_errors'].items():
                self.logger.info(f"  - {error_type}: {count}")


class DeduplicationPipeline:
    """Pipeline de déduplication"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seen_items: Set[str] = set()
        self.duplicate_count = 0
    
    def process_item(self, item: Dict[str, Any], spider):
        """Déduplique les items"""
        # Créer une clé unique basée sur source + source_id
        unique_key = f"{item.get('source', '')}:{item.get('source_id', '')}"
        
        if unique_key in self.seen_items:
            self.duplicate_count += 1
            self.logger.debug(f"🔄 Doublon détecté: {unique_key}")
            raise DropItem(f"Doublon: {unique_key}")
        
        self.seen_items.add(unique_key)
        return item
    
    def close_spider(self, spider):
        """Log des statistiques de déduplication"""
        total_unique = len(self.seen_items)
        self.logger.info(f"🔄 Déduplication - Uniques: {total_unique}, "
                        f"Doublons supprimés: {self.duplicate_count}")


class EnrichmentPipeline:
    """Pipeline d'enrichissement des données"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.enrichment_count = 0
    
    def process_item(self, item: Dict[str, Any], spider):
        """Enrichit les données"""
        enriched = False
        
        # Nettoyage du texte
        if item.get('description'):
            clean_desc = TextCleaner.clean_text(item['description'])
            if clean_desc != item['description']:
                item['description'] = clean_desc
                enriched = True
        
        if item.get('title'):
            clean_title = TextCleaner.clean_text(item['title'])
            if clean_title != item['title']:
                item['title'] = clean_title
                enriched = True
        
        # Normalisation des technologies
        if item.get('technologies'):
            normalized_techs = self._normalize_technologies(item['technologies'])
            if normalized_techs != item['technologies']:
                item['technologies'] = normalized_techs
                enriched = True
        
        # Calcul du score de qualité
        item['quality_score'] = self._calculate_quality_score(item)
        
        # Ajout de métadonnées
        item['processed_at'] = datetime.now().isoformat()
        item['enriched'] = enriched
        
        if enriched:
            self.enrichment_count += 1
        
        return item
    
    def _normalize_technologies(self, technologies):
        """Normalise les noms de technologies"""
        if not technologies:
            return []
        
        # Mapping de normalisation
        tech_mapping = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'react.js': 'React',
            'vue.js': 'Vue',
            'node.js': 'Node.js',
            'c#': 'C#',
            '.net': 'ASP.NET'
        }
        
        normalized = []
        for tech in technologies:
            if isinstance(tech, str):
                tech_lower = tech.lower()
                normalized_tech = tech_mapping.get(tech_lower, tech.title())
                if normalized_tech not in normalized:
                    normalized.append(normalized_tech)
        
        return normalized[:10]  # Limiter à 10 technologies
    
    def _calculate_quality_score(self, item):
        """Calcule un score de qualité pour l'item"""
        score = 0.0
        max_score = 6.0
        
        # Titre présent et substantiel
        if item.get('title') and len(item['title']) > 10:
            score += 1.0
        
        # Description présente et substantielle
        if item.get('description') and len(item['description']) > 50:
            score += 1.0
        
        # TJM présent
        if item.get('tjm_min') or item.get('tjm_max'):
            score += 1.0
        
        # Entreprise présente
        if item.get('company'):
            score += 1.0
        
        # Localisation présente
        if item.get('city') or item.get('location'):
            score += 1.0
        
        # Technologies présentes
        if item.get('technologies') and len(item['technologies']) > 0:
            score += 1.0
        
        return round(score / max_score, 3)
    
    def close_spider(self, spider):
        """Log des statistiques d'enrichissement"""
        self.logger.info(f"✨ Enrichissement - Items enrichis: {self.enrichment_count}")


class ExportPipeline:
    """Pipeline d'export vers différents formats"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.items = []
        self.export_count = 0
    
    def process_item(self, item: Dict[str, Any], spider):
        """Collecte les items pour export"""
        self.items.append(item)
        self.export_count += 1
        return item
    
    def close_spider(self, spider):
        """Exporte les données collectées"""
        if not self.items:
            self.logger.warning("❌ Aucun item à exporter")
            return
        
        try:
            # Créer les dossiers si nécessaire
            data_config = spider.settings.get('DATA_CONFIG', {})
            output_dir = Path(data_config.get('output_dir', 'data/processed'))
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Générer le nom de fichier avec timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"{spider.name}_{timestamp}"
            
            # Export JSON complet
            json_file = output_dir / f"{base_filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=2)
            
            # Export JSONL pour traitement stream
            jsonl_file = output_dir / f"{base_filename}.jsonl"
            with open(jsonl_file, 'w', encoding='utf-8') as f:
                for item in self.items:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            # Export CSV pour analyse
            self._export_csv(output_dir / f"{base_filename}.csv")
            
            # Export statistiques
            self._export_stats(output_dir / f"{base_filename}_stats.json", spider)
            
            self.logger.info(f"📁 Export terminé - {self.export_count} items exportés")
            self.logger.info(f"📁 Fichiers: {json_file}, {jsonl_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur export: {e}")
    
    def _export_csv(self, csv_file):
        """Export CSV pour analyse facile"""
        try:
            import pandas as pd
            
            # Aplatir les données pour CSV
            flattened_items = []
            for item in self.items:
                flat_item = {}
                for key, value in item.items():
                    if isinstance(value, list):
                        flat_item[key] = ', '.join(str(v) for v in value)
                    else:
                        flat_item[key] = value
                flattened_items.append(flat_item)
            
            df = pd.DataFrame(flattened_items)
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
        except ImportError:
            self.logger.warning("pandas non disponible - export CSV ignoré")
        except Exception as e:
            self.logger.error(f"Erreur export CSV: {e}")
    
    def _export_stats(self, stats_file, spider):
        """Export des statistiques de scraping"""
        try:
            stats = {
                'spider_name': spider.name,
                'execution_time': datetime.now().isoformat(),
                'total_items': len(self.items),
                'quality_distribution': self._get_quality_distribution(),
                'technology_stats': self._get_technology_stats(),
                'location_stats': self._get_location_stats(),
                'tjm_stats': self._get_tjm_stats()
            }
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erreur export stats: {e}")
    
    def _get_quality_distribution(self):
        """Statistiques de distribution de qualité"""
        quality_scores = [item.get('quality_score', 0) for item in self.items]
        if not quality_scores:
            return {}
        
        return {
            'average': round(sum(quality_scores) / len(quality_scores), 3),
            'min': min(quality_scores),
            'max': max(quality_scores),
            'high_quality_count': len([s for s in quality_scores if s > 0.7])
        }
    
    def _get_technology_stats(self):
        """Statistiques des technologies"""
        tech_count = {}
        for item in self.items:
            technologies = item.get('technologies', [])
            for tech in technologies:
                tech_count[tech] = tech_count.get(tech, 0) + 1
        
        # Top 10 technologies
        sorted_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_techs[:10])
    
    def _get_location_stats(self):
        """Statistiques des localisations"""
        location_count = {}
        for item in self.items:
            city = item.get('city')
            if city:
                location_count[city] = location_count.get(city, 0) + 1
        
        # Top 10 villes
        sorted_locations = sorted(location_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_locations[:10])
    
    def _get_tjm_stats(self):
        """Statistiques des TJM"""
        tjm_values = []
        for item in self.items:
            if item.get('tjm_min'):
                tjm_values.append(item['tjm_min'])
            if item.get('tjm_max'):
                tjm_values.append(item['tjm_max'])
        
        if not tjm_values:
            return {}
        
        return {
            'average': round(sum(tjm_values) / len(tjm_values), 2),
            'min': min(tjm_values),
            'max': max(tjm_values),
            'count_with_tjm': len([item for item in self.items if item.get('tjm_min') or item.get('tjm_max')])
        }


# Exception pour rejeter un item
class DropItem(Exception):
    """Exception pour signaler qu'un item doit être rejeté"""
    pass
