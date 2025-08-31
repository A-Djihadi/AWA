"""
ETL Orchestrator - Main ETL Pipeline Controller
"""
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from extractors import DirectoryExtractor, create_extractors
from transformers import StandardTransformer
from loaders import create_multi_loader
from models import JobOffer, ETLBatch
from config import CONFIG


class ETLOrchestrator:
    """Main ETL pipeline orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.extractor = DirectoryExtractor(create_extractors())
        self.transformer = StandardTransformer()
        self.loader = create_multi_loader()
        
        # Pipeline state
        self.current_batch: Optional[ETLBatch] = None
        self.pipeline_stats = {
            "runs": 0,
            "total_processed": 0,
            "total_loaded": 0,
            "last_run": None,
            "avg_processing_time": 0.0
        }
    
    def run(self, source_directory: Optional[str] = None, file_pattern: str = "*.jsonl") -> Dict[str, Any]:
        """Run complete ETL pipeline"""
        
        start_time = time.time()
        source_dir = source_directory or CONFIG.data_source_dir
        
        self.logger.info(f"Starting ETL pipeline run - Source: {source_dir}")
        
        try:
            # Health checks
            if not self._run_health_checks():
                return {
                    "success": False,
                    "error": "Health checks failed",
                    "duration": time.time() - start_time
                }
            
            # Extract phase
            self.logger.info("PHASE 1: Extracting data...")
            extraction_result = self._extract_data(source_dir, file_pattern)
            
            if not extraction_result["success"]:
                return {
                    "success": False,
                    "error": f"Extraction failed: {extraction_result.get('error')}",
                    "duration": time.time() - start_time
                }
            
            raw_records = extraction_result["data"]
            self.current_batch = extraction_result["batch"]
            
            if not raw_records:
                return {
                    "success": True,
                    "message": "No data to process",
                    "duration": time.time() - start_time,
                    "batch_id": self.current_batch.batch_id if self.current_batch else None
                }
            
            # Transform phase
            self.logger.info(f"PHASE 2: Transforming {len(raw_records)} records...")
            transformation_result = self._transform_data(raw_records)
            
            if not transformation_result["success"]:
                return {
                    "success": False,
                    "error": f"Transformation failed: {transformation_result.get('error')}",
                    "duration": time.time() - start_time,
                    "batch_id": self.current_batch.batch_id
                }
            
            transformed_offers = transformation_result["offers"]
            
            # Load phase
            self.logger.info(f"PHASE 3: Loading {len(transformed_offers)} offers...")
            load_result = self._load_data(transformed_offers)
            
            # Update batch statistics
            if self.current_batch:
                self.current_batch.valid_records = load_result.get("loaded_count", 0)
                self.current_batch.processing_time = time.time() - start_time
            
            # Update pipeline statistics
            self._update_pipeline_stats(start_time, len(raw_records), load_result.get("loaded_count", 0))
            
            # Prepare final result
            result = {
                "success": load_result.get("success", False),
                "batch_id": self.current_batch.batch_id if self.current_batch else None,
                "duration": time.time() - start_time,
                "statistics": {
                    "extracted_records": len(raw_records),
                    "transformed_offers": len(transformed_offers),
                    "loaded_offers": load_result.get("loaded_count", 0),
                    "failed_offers": load_result.get("failed_count", 0),
                    "success_rate": load_result.get("success_rate", 0.0)
                },
                "extraction": extraction_result,
                "transformation": transformation_result,
                "loading": load_result
            }
            
            # Log final result
            if result["success"]:
                self.logger.info(
                    f"ETL pipeline completed successfully in {result['duration']:.2f}s - "
                    f"Loaded {result['statistics']['loaded_offers']} offers"
                )
            else:
                self.logger.error(
                    f"ETL pipeline failed after {result['duration']:.2f}s - "
                    f"Error: {load_result.get('error', 'Unknown error')}"
                )
            
            return result
        
        except Exception as e:
            error_msg = f"ETL pipeline failed with exception: {e}"
            self.logger.error(error_msg, exc_info=True)
            
            return {
                "success": False,
                "error": error_msg,
                "duration": time.time() - start_time,
                "batch_id": self.current_batch.batch_id if self.current_batch else None
            }
    
    def _run_health_checks(self) -> bool:
        """Run health checks on all components"""
        
        self.logger.info("Running health checks...")
        
        # Check loader health
        if not self.loader.health_check():
            self.logger.error("Loader health check failed")
            return False
        
        # Check source directory
        source_path = Path(CONFIG.data_source_dir)
        if not source_path.exists():
            self.logger.error(f"Source directory does not exist: {CONFIG.data_source_dir}")
            return False
        
        self.logger.info("All health checks passed")
        return True
    
    def _extract_data(self, source_directory: str, file_pattern: str) -> Dict[str, Any]:
        """Extract data from source directory"""
        
        try:
            batch, raw_records = self.extractor.extract_from_directory(source_directory, file_pattern)
            
            return {
                "success": True,
                "batch": batch,
                "data": raw_records,
                "source_files": batch.source_files,
                "extracted_count": len(raw_records)
            }
        
        except Exception as e:
            error_msg = f"Data extraction failed: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "data": []
            }
    
    def _transform_data(self, raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Transform raw records to job offers"""
        
        offers = []
        transformation_errors = []
        
        for i, record in enumerate(raw_records):
            try:
                offer = self.transformer.transform(record)
                
                # Apply quality filter
                if offer.quality_metrics and offer.quality_metrics.overall_score >= CONFIG.min_quality_score:
                    offers.append(offer)
                else:
                    quality_score = offer.quality_metrics.overall_score if offer.quality_metrics else 0.0
                    self.logger.debug(
                        f"Filtered out low quality offer {offer.get_unique_id()} "
                        f"(score: {quality_score:.2f})"
                    )
            
            except Exception as e:
                error_msg = f"Failed to transform record {i}: {e}"
                self.logger.warning(error_msg)
                transformation_errors.append(error_msg)
        
        success_rate = len(offers) / len(raw_records) if raw_records else 1.0
        
        result = {
            "success": True,
            "offers": offers,
            "transformed_count": len(offers),
            "error_count": len(transformation_errors),
            "success_rate": success_rate
        }
        
        if transformation_errors:
            result["errors"] = transformation_errors[:10]  # Limit error list
        
        self.logger.info(
            f"Transformation completed: {len(offers)} valid offers from {len(raw_records)} records "
            f"(success rate: {success_rate:.2%})"
        )
        
        return result
    
    def _load_data(self, offers: List[JobOffer]) -> Dict[str, Any]:
        """Load transformed offers to target systems"""
        
        try:
            return self.loader.load(offers)
        
        except Exception as e:
            error_msg = f"Data loading failed: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "loaded_count": 0,
                "failed_count": len(offers)
            }
    
    def _update_pipeline_stats(self, start_time: float, processed_count: int, loaded_count: int):
        """Update pipeline statistics"""
        
        duration = time.time() - start_time
        
        self.pipeline_stats["runs"] += 1
        self.pipeline_stats["total_processed"] += processed_count
        self.pipeline_stats["total_loaded"] += loaded_count
        self.pipeline_stats["last_run"] = datetime.utcnow().isoformat()
        
        # Update average processing time
        total_time = self.pipeline_stats["avg_processing_time"] * (self.pipeline_stats["runs"] - 1) + duration
        self.pipeline_stats["avg_processing_time"] = total_time / self.pipeline_stats["runs"]
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return self.pipeline_stats.copy()
    
    def get_current_batch_info(self) -> Optional[Dict[str, Any]]:
        """Get information about current batch"""
        
        if not self.current_batch:
            return None
        
        return {
            "batch_id": self.current_batch.batch_id,
            "source_files": self.current_batch.source_files,
            "total_records": self.current_batch.total_records,
            "processed_records": self.current_batch.processed_records,
            "valid_records": self.current_batch.valid_records,
            "error_records": self.current_batch.error_records,
            "success_rate": self.current_batch.get_success_rate(),
            "processing_time": self.current_batch.processing_time,
            "errors": self.current_batch.errors[:5] if self.current_batch.errors else []
        }


# Convenience function for simple ETL runs
def run_etl(source_directory: Optional[str] = None, file_pattern: str = "*.jsonl") -> Dict[str, Any]:
    """Run ETL pipeline with default configuration"""
    
    orchestrator = ETLOrchestrator()
    return orchestrator.run(source_directory, file_pattern)
