"""
Data Loaders for ETL Pipeline
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from supabase import create_client, Client

from models import JobOffer, ETLBatch
from config import CONFIG


logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """Base class for data loaders"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
    
    @abstractmethod
    def load(self, offers: List[JobOffer]) -> Dict[str, Any]:
        """Load job offers to target system"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if loader is healthy and ready"""
        pass


class SupabaseLoader(BaseLoader):
    """Load data into Supabase database"""
    
    def __init__(self):
        super().__init__("supabase")
        self.client: Optional[Client] = None
        self.table_name = "offers"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            if not CONFIG.supabase_url or not CONFIG.supabase_key:
                self.logger.warning("Supabase credentials not configured")
                return
            
            self.client = create_client(CONFIG.supabase_url, CONFIG.supabase_key)
            self.logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None
    
    def health_check(self) -> bool:
        """Check Supabase connection health"""
        if not self.client:
            return False
        
        try:
            # Simple query to check connection
            result = self.client.table(self.table_name).select("id").limit(1).execute()
            return True
        except Exception as e:
            self.logger.error(f"Supabase health check failed: {e}")
            return False
    
    def load(self, offers: List[JobOffer]) -> Dict[str, Any]:
        """Load job offers into Supabase"""
        
        if not self.client:
            return {
                "success": False,
                "error": "Supabase client not initialized",
                "loaded_count": 0,
                "failed_count": len(offers)
            }
        
        if not offers:
            return {
                "success": True,
                "loaded_count": 0,
                "failed_count": 0,
                "message": "No offers to load"
            }
        
        loaded_count = 0
        failed_count = 0
        errors = []
        
        # Process in batches
        batch_size = CONFIG.batch_size
        
        for i in range(0, len(offers), batch_size):
            batch = offers[i:i + batch_size]
            batch_result = self._load_batch(batch)
            
            loaded_count += batch_result["loaded_count"]
            failed_count += batch_result["failed_count"]
            errors.extend(batch_result.get("errors", []))
        
        success = failed_count == 0
        
        result = {
            "success": success,
            "loaded_count": loaded_count,
            "failed_count": failed_count,
            "total_count": len(offers),
            "success_rate": loaded_count / len(offers) if offers else 1.0
        }
        
        if errors:
            result["errors"] = errors[:10]  # Limit error list
        
        self.logger.info(
            f"Load completed: {loaded_count} loaded, {failed_count} failed, "
            f"success rate: {result['success_rate']:.2%}"
        )
        
        return result
    
    def _load_batch(self, offers: List[JobOffer]) -> Dict[str, Any]:
        """Load a batch of offers"""
        
        try:
            # Convert offers to database format
            records = []
            for offer in offers:
                if offer.is_valid():
                    record = offer.to_dict()
                    records.append(record)
                else:
                    self.logger.warning(f"Skipping invalid offer: {offer.get_unique_id()}")
            
            if not records:
                return {"loaded_count": 0, "failed_count": len(offers), "errors": ["No valid records in batch"]}
            
            # Process records one by one to handle conflicts properly
            loaded_count = 0
            failed_count = 0
            errors = []
            
            for record in records:
                try:
                    # Try to insert first
                    result = self.client.table(self.table_name).insert(record).execute()
                    if result.data:
                        loaded_count += 1
                except Exception as e:
                    error_str = str(e)
                    if 'duplicate key value violates unique constraint' in error_str:
                        # Record exists, try to update it
                        try:
                            update_result = self.client.table(self.table_name).update(record).eq('source', record['source']).eq('source_id', record['source_id']).execute()
                            if update_result.data:
                                loaded_count += 1
                            else:
                                failed_count += 1
                                errors.append(f"Update failed for {record['source']}:{record['source_id']}")
                        except Exception as update_e:
                            failed_count += 1
                            errors.append(f"Update error for {record['source']}:{record['source_id']}: {update_e}")
                    else:
                        failed_count += 1
                        errors.append(f"Insert error for {record['source']}:{record['source_id']}: {e}")
            
            return {
                "loaded_count": loaded_count,
                "failed_count": failed_count,
                "errors": errors
            }
        
        except Exception as e:
            error_msg = f"Batch load failed: {e}"
            self.logger.error(error_msg)
            return {
                "loaded_count": 0,
                "failed_count": len(offers),
                "errors": [error_msg]
            }
    
    def create_tables(self) -> bool:
        """Create database tables if they don't exist"""
        
        if not self.client:
            self.logger.error("Cannot create tables: Supabase client not initialized")
            return False
        
        # Table creation is typically handled by Supabase migrations
        # This method can be extended for custom table creation logic
        
        self.logger.info("Database tables should be created via Supabase migrations")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        
        if not self.client:
            return {"error": "Client not initialized"}
        
        try:
            # Count total records
            total_result = self.client.table(self.table_name).select("id", count="exact").execute()
            total_count = total_result.count if hasattr(total_result, 'count') else 0
            
            # Count by source
            source_result = self.client.table(self.table_name).select("source", count="exact").execute()
            
            # Recent records (last 24 hours)
            yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            recent_result = self.client.table(self.table_name).select("id", count="exact").gte(
                "processed_at", yesterday.isoformat()
            ).execute()
            recent_count = recent_result.count if hasattr(recent_result, 'count') else 0
            
            return {
                "total_records": total_count,
                "recent_records_24h": recent_count,
                "last_updated": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get database statistics: {e}")
            return {"error": str(e)}


class JSONFileLoader(BaseLoader):
    """Load data to JSON files (backup/debug loader)"""
    
    def __init__(self, output_dir: str):
        super().__init__("json_file")
        self.output_dir = output_dir
    
    def health_check(self) -> bool:
        """Check if output directory is writable"""
        try:
            from pathlib import Path
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = output_path / "health_check.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            return True
        except Exception as e:
            self.logger.error(f"JSON file loader health check failed: {e}")
            return False
    
    def load(self, offers: List[JobOffer]) -> Dict[str, Any]:
        """Load offers to JSON file"""
        
        if not offers:
            return {
                "success": True,
                "loaded_count": 0,
                "failed_count": 0,
                "message": "No offers to load"
            }
        
        try:
            from pathlib import Path
            import json
            
            # Create output directory
            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_offers_{timestamp}.json"
            file_path = output_path / filename
            
            # Convert offers to dictionaries
            offers_data = []
            for offer in offers:
                if offer.is_valid():
                    offers_data.append(offer.to_dict())
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(offers_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Loaded {len(offers_data)} offers to {file_path}")
            
            return {
                "success": True,
                "loaded_count": len(offers_data),
                "failed_count": len(offers) - len(offers_data),
                "output_file": str(file_path)
            }
        
        except Exception as e:
            error_msg = f"Failed to load to JSON file: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "loaded_count": 0,
                "failed_count": len(offers),
                "error": error_msg
            }


class MultiLoader(BaseLoader):
    """Load data to multiple targets"""
    
    def __init__(self, loaders: List[BaseLoader]):
        super().__init__("multi")
        self.loaders = loaders
    
    def health_check(self) -> bool:
        """Check health of all loaders"""
        results = []
        for loader in self.loaders:
            try:
                result = loader.health_check()
                results.append(result)
                self.logger.info(f"Loader {loader.name} health: {'OK' if result else 'FAIL'}")
            except Exception as e:
                self.logger.error(f"Health check failed for {loader.name}: {e}")
                results.append(False)
        
        # Return True if at least one loader is healthy
        return any(results)
    
    def load(self, offers: List[JobOffer]) -> Dict[str, Any]:
        """Load to all configured loaders"""
        
        results = {}
        overall_success = True
        total_loaded = 0
        
        for loader in self.loaders:
            try:
                self.logger.info(f"Loading to {loader.name}...")
                result = loader.load(offers)
                results[loader.name] = result
                
                if result.get("success", False):
                    total_loaded = max(total_loaded, result.get("loaded_count", 0))
                else:
                    overall_success = False
                    self.logger.warning(f"Loader {loader.name} failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                error_msg = f"Loader {loader.name} exception: {e}"
                self.logger.error(error_msg)
                results[loader.name] = {
                    "success": False,
                    "error": error_msg,
                    "loaded_count": 0,
                    "failed_count": len(offers)
                }
                overall_success = False
        
        return {
            "success": overall_success,
            "loaded_count": total_loaded,
            "total_count": len(offers),
            "loader_results": results,
            "summary": f"Loaded to {sum(1 for r in results.values() if r.get('success', False))} of {len(self.loaders)} loaders"
        }


def create_loaders() -> List[BaseLoader]:
    """Create standard set of loaders"""
    loaders = []
    
    # Always add Supabase loader
    supabase_loader = SupabaseLoader()
    loaders.append(supabase_loader)
    
    # Add JSON file loader for backup
    json_loader = JSONFileLoader(CONFIG.processed_dir)
    loaders.append(json_loader)
    
    return loaders


def create_multi_loader() -> MultiLoader:
    """Create multi-loader with all available loaders"""
    loaders = create_loaders()
    return MultiLoader(loaders)
