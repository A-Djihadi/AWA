"""
Shared validation utilities
Following Clean Code principles: Single Responsibility, Clear Function Names
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import re
import os
from dataclasses import dataclass

from .constants import RequiredFields, SpiderNames, FilePatterns, QualityThresholds


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    def add_error(self, error: str):
        """Add an error to the validation result"""
        self.is_valid = False
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add a warning to the validation result"""
        self.warnings.append(warning)


class BaseValidator:
    """Base class for validators"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def _reset(self):
        """Reset validation state"""
        self.errors = []
        self.warnings = []
    
    def _create_result(self) -> ValidationResult:
        """Create validation result"""
        is_valid = len(self.errors) == 0
        return ValidationResult(is_valid, self.errors.copy(), self.warnings.copy())


class RequestValidator(BaseValidator):
    """Validates API requests"""
    
    def validate_scrape_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Validate scrape request"""
        self._reset()
        
        # Check required fields
        for field in RequiredFields.SCRAPE_REQUEST:
            if field not in request_data or not request_data[field]:
                self.errors.append(f"Required field '{field}' is missing or empty")
        
        # Validate spider name
        spider = request_data.get('spider')
        if spider and spider not in SpiderNames.get_valid_spiders():
            self.errors.append(
                f"Invalid spider '{spider}'. Valid spiders: {SpiderNames.get_valid_spiders()}"
            )
        
        # Validate options if present
        options = request_data.get('options', {})
        if options and not isinstance(options, dict):
            self.errors.append("Options must be a dictionary")
        
        return self._create_result()
    
    def validate_etl_request(self, request_data: Dict[str, Any]) -> ValidationResult:
        """Validate ETL request"""
        self._reset()
        
        # Validate source directory
        source_dir = request_data.get('source_directory')
        if source_dir:
            if not isinstance(source_dir, str):
                self.errors.append("Source directory must be a string")
            elif not Path(source_dir).exists():
                self.errors.append(f"Source directory does not exist: {source_dir}")
        
        # Validate file pattern
        file_pattern = request_data.get('file_pattern', FilePatterns.JSONL)
        if not isinstance(file_pattern, str):
            self.errors.append("File pattern must be a string")
        
        # Validate force_reprocess flag
        force_reprocess = request_data.get('force_reprocess', False)
        if not isinstance(force_reprocess, bool):
            self.errors.append("force_reprocess must be a boolean")
        
        return self._create_result()


class DataValidator(BaseValidator):
    """Validates data content"""
    
    def validate_job_offer(self, offer_data: Dict[str, Any]) -> ValidationResult:
        """Validate job offer data"""
        self._reset()
        
        # Check required fields
        for field in RequiredFields.JOB_OFFER:
            if field not in offer_data or not offer_data[field]:
                self.errors.append(f"Required field '{field}' is missing or empty")
        
        # Validate title
        title = offer_data.get('title')
        if title:
            if len(title.strip()) < 3:
                self.errors.append("Title must be at least 3 characters long")
            if len(title) > 200:
                self.warnings.append("Title is very long (>200 characters)")
        
        # Validate source_id
        source_id = offer_data.get('source_id')
        if source_id and not str(source_id).strip():
            self.errors.append("source_id cannot be empty string")
        
        # Validate description length
        description = offer_data.get('description', '')
        if description and len(description) > 10000:
            self.warnings.append("Description is very long (>10000 characters)")
        
        # Validate URL format if present
        url = offer_data.get('url')
        if url and not self._is_valid_url(url):
            self.warnings.append("URL format appears invalid")
        
        return self._create_result()
    
    def validate_offer_quality(self, offer_data: Dict[str, Any]) -> ValidationResult:
        """Validate offer quality metrics"""
        self._reset()
        
        required_count = len([
            field for field in RequiredFields.JOB_OFFER 
            if offer_data.get(field)
        ])
        
        if required_count < QualityThresholds.MIN_REQUIRED_FIELDS:
            self.errors.append(
                f"Insufficient required fields: {required_count}/{QualityThresholds.MIN_REQUIRED_FIELDS}"
            )
        
        # Check data richness
        optional_fields = ['description', 'location', 'company', 'salary', 'technologies']
        filled_optional = len([
            field for field in optional_fields 
            if offer_data.get(field)
        ])
        
        if filled_optional < 2:
            self.warnings.append("Low data richness: few optional fields filled")
        
        return self._create_result()
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL format is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class PathValidator(BaseValidator):
    """Validates file paths and directories"""
    
    def validate_source_directory(self, directory_path: str) -> ValidationResult:
        """Validate source directory"""
        self._reset()
        
        if not directory_path:
            self.errors.append("Directory path cannot be empty")
            return self._create_result()
        
        path = Path(directory_path)
        
        if not path.exists():
            self.errors.append(f"Directory does not exist: {directory_path}")
        elif not path.is_dir():
            self.errors.append(f"Path is not a directory: {directory_path}")
        elif not os.access(path, os.R_OK):
            self.errors.append(f"Directory is not readable: {directory_path}")
        
        return self._create_result()
    
    def validate_file_permissions(self, file_path: str, write_access: bool = False) -> ValidationResult:
        """Validate file permissions"""
        self._reset()
        
        path = Path(file_path)
        
        if path.exists():
            if not os.access(path, os.R_OK):
                self.errors.append(f"File is not readable: {file_path}")
            
            if write_access and not os.access(path, os.W_OK):
                self.errors.append(f"File is not writable: {file_path}")
        
        return self._create_result()


# Convenience functions
def validate_scrape_request(request_data: Dict[str, Any]) -> ValidationResult:
    """Validate scrape request data"""
    validator = RequestValidator()
    return validator.validate_scrape_request(request_data)


def validate_etl_request(request_data: Dict[str, Any]) -> ValidationResult:
    """Validate ETL request data"""
    validator = RequestValidator()
    return validator.validate_etl_request(request_data)


def validate_job_offer(offer_data: Dict[str, Any]) -> ValidationResult:
    """Validate job offer data"""
    validator = DataValidator()
    return validator.validate_job_offer(offer_data)


def validate_directory(directory_path: str) -> ValidationResult:
    """Validate directory path"""
    validator = PathValidator()
    return validator.validate_source_directory(directory_path)
