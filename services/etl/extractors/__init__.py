"""
Data Extractors for ETL Pipeline
"""
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional
from datetime import datetime

from models import JobOffer, ETLBatch


logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """Base class for data extractors"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{source_name}")
    
    @abstractmethod
    def extract(self, source_path: str) -> Iterator[Dict[str, Any]]:
        """Extract raw data from source"""
        pass
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate a single record"""
        required_fields = ['source', 'source_id', 'title']
        return all(field in record for field in required_fields)


class JSONLExtractor(BaseExtractor):
    """Extractor for JSONL files from Scrapy spiders"""
    
    def __init__(self, source_name: str = "jsonl"):
        super().__init__(source_name)
    
    def extract(self, source_path: str) -> Iterator[Dict[str, Any]]:
        """Extract data from JSONL file"""
        
        file_path = Path(source_path)
        if not file_path.exists():
            self.logger.error(f"Source file not found: {source_path}")
            return
        
        self.logger.info(f"Extracting data from: {source_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                line_number = 0
                for line in file:
                    line_number += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:
                        record = json.loads(line)
                        
                        if self.validate_record(record):
                            yield record
                        else:
                            self.logger.warning(f"Invalid record at line {line_number}: missing required fields")
                    
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON decode error at line {line_number}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error reading file {source_path}: {e}")


class FreeWorkExtractor(JSONLExtractor):
    """Specialized extractor for FreeWork data"""
    
    def __init__(self):
        super().__init__("freework")
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """Validate FreeWork specific record"""
        if not super().validate_record(record):
            return False
        
        # FreeWork specific validations
        if record.get('source') != 'freework':
            self.logger.warning(f"Record source is not 'freework': {record.get('source')}")
            return False
        
        return True
    
    def extract(self, source_path: str) -> Iterator[Dict[str, Any]]:
        """Extract FreeWork data with additional processing"""
        
        for record in super().extract(source_path):
            # Add FreeWork specific processing
            record = self._normalize_freework_data(record)
            yield record
    
    def _normalize_freework_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize FreeWork specific data"""
        
        # Ensure technologies is a list
        if 'technologies' in record and isinstance(record['technologies'], str):
            record['technologies'] = [record['technologies']]
        
        # Normalize TJM fields
        if 'tjm_min' in record and record['tjm_min'] == '':
            record['tjm_min'] = None
        if 'tjm_max' in record and record['tjm_max'] == '':
            record['tjm_max'] = None
        
        # Add extraction timestamp if missing
        if 'scraped_at' not in record:
            record['scraped_at'] = datetime.utcnow().isoformat()
        
        return record


class DirectoryExtractor:
    """Extract data from multiple files in a directory"""
    
    def __init__(self, extractors: Dict[str, BaseExtractor]):
        self.extractors = extractors
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_from_directory(self, directory_path: str, pattern: str = "*.jsonl") -> ETLBatch:
        """Extract data from all matching files in directory"""
        
        directory = Path(directory_path)
        if not directory.exists():
            self.logger.error(f"Directory not found: {directory_path}")
            return ETLBatch(batch_id="error", source_files=[])
        
        # Find matching files
        source_files = list(directory.glob(pattern))
        
        if not source_files:
            self.logger.warning(f"No files found matching pattern '{pattern}' in {directory_path}")
            return ETLBatch(batch_id="empty", source_files=[])
        
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch = ETLBatch(
            batch_id=batch_id,
            source_files=[str(f) for f in source_files]
        )
        
        self.logger.info(f"Starting extraction batch {batch_id} with {len(source_files)} files")
        
        all_records = []
        
        for file_path in source_files:
            self.logger.info(f"Processing file: {file_path}")
            
            # Determine extractor based on filename
            extractor = self._get_extractor_for_file(file_path)
            
            if not extractor:
                self.logger.warning(f"No suitable extractor found for: {file_path}")
                continue
            
            try:
                file_records = list(extractor.extract(str(file_path)))
                all_records.extend(file_records)
                batch.processed_records += len(file_records)
                
            except Exception as e:
                error_msg = f"Failed to extract from {file_path}: {e}"
                self.logger.error(error_msg)
                batch.add_error(error_msg)
        
        batch.total_records = len(all_records)
        
        self.logger.info(f"Extraction completed: {batch.processed_records} records from {len(source_files)} files")
        
        return batch, all_records
    
    def _get_extractor_for_file(self, file_path: Path) -> Optional[BaseExtractor]:
        """Get appropriate extractor for file"""
        
        filename = file_path.name.lower()
        
        # Check for specific source patterns
        if 'freework' in filename:
            return self.extractors.get('freework')
        
        # Default to generic JSONL extractor
        if filename.endswith('.jsonl'):
            return self.extractors.get('jsonl')
        
        return None


def create_extractors() -> Dict[str, BaseExtractor]:
    """Create standard set of extractors"""
    return {
        'jsonl': JSONLExtractor(),
        'freework': FreeWorkExtractor(),
    }
