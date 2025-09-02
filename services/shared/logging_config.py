"""
Shared logging configuration
Following Clean Code principle: DRY (Don't Repeat Yourself)
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .constants import LogFormats, Paths


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Add color for console output
        if hasattr(record, 'levelname'):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class ServiceLogger:
    """Centralized logging configuration for all services"""
    
    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper())
        self.logger = None
        
    def setup_logger(self, console_output: bool = True, file_output: bool = True) -> logging.Logger:
        """Setup and configure logger for service"""
        
        if self.logger:
            return self.logger
            
        # Create logger
        self.logger = logging.getLogger(self.service_name)
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return self.logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = ColorFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if file_output:
            # Ensure log directory exists
            log_dir = Path(Paths.LOGS)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"{self.service_name}.log"
            
            # Rotating file handler (10MB max, 5 backups)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024, 
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        return self.logger
    
    def log_service_start(self, port: Optional[int] = None):
        """Log service startup"""
        if self.logger:
            message = LogFormats.SERVICE_START.format(
                service=self.service_name,
                port=port or "N/A"
            )
            self.logger.info(message)
    
    def log_service_error(self, error: str):
        """Log service error"""
        if self.logger:
            message = LogFormats.SERVICE_ERROR.format(
                service=self.service_name,
                error=error
            )
            self.logger.error(message)
    
    def log_process_start(self, process: str, count: int):
        """Log process start"""
        if self.logger:
            message = LogFormats.PROCESS_START.format(
                process=process,
                count=count
            )
            self.logger.info(message)
    
    def log_process_success(self, process: str, count: int, duration: float):
        """Log process success"""
        if self.logger:
            message = LogFormats.PROCESS_SUCCESS.format(
                process=process,
                count=count,
                duration=duration
            )
            self.logger.info(message)
    
    def log_process_error(self, process: str, duration: float, error: str):
        """Log process error"""
        if self.logger:
            message = LogFormats.PROCESS_ERROR.format(
                process=process,
                duration=duration,
                error=error
            )
            self.logger.error(message)


def get_logger(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """Convenience function to get configured logger"""
    service_logger = ServiceLogger(service_name, log_level)
    return service_logger.setup_logger()


def setup_service_logging(service_name: str, log_level: str = "INFO", port: Optional[int] = None) -> ServiceLogger:
    """Setup complete logging for a service"""
    service_logger = ServiceLogger(service_name, log_level)
    service_logger.setup_logger()
    service_logger.log_service_start(port)
    return service_logger
