"""
Shared exception classes
Following Clean Code principles: Meaningful exception names, Clear error messages
"""

from typing import Optional, Dict, Any


class AWABaseException(Exception):
    """Base exception for AWA application"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(AWABaseException):
    """Raised when configuration is invalid or missing"""
    pass


class ValidationError(AWABaseException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        self.field = field
        self.value = value
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = value
        super().__init__(message, details)


class ProcessingError(AWABaseException):
    """Raised when data processing fails"""
    pass


class ExtractionError(ProcessingError):
    """Raised when data extraction fails"""
    pass


class TransformationError(ProcessingError):
    """Raised when data transformation fails"""
    pass


class LoadingError(ProcessingError):
    """Raised when data loading fails"""
    pass


class DatabaseConnectionError(AWABaseException):
    """Raised when database connection fails"""
    pass


class ScrapingError(AWABaseException):
    """Raised when web scraping fails"""
    
    def __init__(self, message: str, spider: Optional[str] = None, url: Optional[str] = None):
        self.spider = spider
        self.url = url
        details = {}
        if spider:
            details['spider'] = spider
        if url:
            details['url'] = url
        super().__init__(message, details)


class APIError(AWABaseException):
    """Raised when API calls fail"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None):
        self.status_code = status_code
        self.endpoint = endpoint
        details = {}
        if status_code:
            details['status_code'] = status_code
        if endpoint:
            details['endpoint'] = endpoint
        super().__init__(message, details)


class FileOperationError(AWABaseException):
    """Raised when file operations fail"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None):
        self.file_path = file_path
        self.operation = operation
        details = {}
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        super().__init__(message, details)


class ServiceUnavailableError(AWABaseException):
    """Raised when a service is unavailable"""
    
    def __init__(self, message: str, service: Optional[str] = None):
        self.service = service
        details = {}
        if service:
            details['service'] = service
        super().__init__(message, details)


class TimeoutError(AWABaseException):
    """Raised when operations timeout"""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None):
        self.timeout_seconds = timeout_seconds
        details = {}
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        super().__init__(message, details)


class QualityError(ProcessingError):
    """Raised when data quality checks fail"""
    
    def __init__(self, message: str, quality_score: Optional[float] = None, threshold: Optional[float] = None):
        self.quality_score = quality_score
        self.threshold = threshold
        details = {}
        if quality_score is not None:
            details['quality_score'] = quality_score
        if threshold is not None:
            details['threshold'] = threshold
        super().__init__(message, details)
