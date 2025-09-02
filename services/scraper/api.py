"""
Scraper Service API - Refactored with Clean Code principles
Following SOLID principles and separation of concerns
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
from pathlib import Path

# Import shared modules
import sys
sys.path.append('/app/services')
from shared import (
    ServicePorts, Paths, SpiderNames, HttpStatus,
    setup_service_logging, validate_scrape_request,
    get_current_timestamp, generate_batch_id,
    ScrapingError, ValidationError, ProcessingError
)

# Service setup
SERVICE_NAME = "scraper"
logger_service = setup_service_logging(SERVICE_NAME, port=ServicePorts.SCRAPER.value)
logger = logger_service.logger

app = FastAPI(
    title="AWA Scraper API",
    description="Professional web scraping service with FastAPI",
    version="2.0.0"
)


# Pydantic Models
class ScrapeRequest(BaseModel):
    """Request model for scraping operations"""
    spider: str = Field(..., description="Spider name to execute")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional spider options")
    
    class Config:
        schema_extra = {
            "example": {
                "spider": "freework",
                "options": {
                    "max_pages": 10,
                    "delay": 1
                }
            }
        }


class ScrapeResponse(BaseModel):
    """Response model for scraping operations"""
    success: bool
    message: str
    spider: str
    batch_id: str
    started_at: str
    output_file: Optional[str] = None
    estimated_duration: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    timestamp: str
    version: str
    available_spiders: list


class StatusResponse(BaseModel):
    """Service status response model"""
    service: str
    status: str
    recent_files: list
    available_spiders: list
    system_info: dict


# Business Logic Classes
class ScrapingOrchestrator:
    """Handles scraping orchestration logic"""
    
    def __init__(self):
        self.active_processes = {}
    
    async def start_scraping(self, spider: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Start scraping process"""
        try:
            batch_id = generate_batch_id()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{Paths.DATA_RAW}/{spider}_{timestamp}.jsonl"
            
            # Build scrapy command
            cmd = self._build_scrapy_command(spider, output_file, options)
            
            # Start process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app"
            )
            
            # Store process info
            self.active_processes[batch_id] = {
                "process": process,
                "spider": spider,
                "started_at": get_current_timestamp(),
                "output_file": output_file
            }
            
            logger.info(f"Started scraping: spider={spider}, batch_id={batch_id}")
            
            return {
                "success": True,
                "batch_id": batch_id,
                "spider": spider,
                "output_file": output_file,
                "started_at": get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Failed to start scraping: {e}")
            raise ScrapingError(f"Failed to start scraping: {e}", spider=spider)
    
    def _build_scrapy_command(self, spider: str, output_file: str, options: Dict[str, Any]) -> list:
        """Build scrapy command with options"""
        cmd = [
            "python", "-m", "scrapy", "crawl", spider,
            "-o", output_file,
            "-s", "LOG_LEVEL=INFO"
        ]
        
        # Add custom options
        for key, value in options.items():
            cmd.extend(["-s", f"{key}={value}"])
        
        return cmd
    
    def get_process_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific scraping process"""
        return self.active_processes.get(batch_id)


class FileManager:
    """Handles file operations and status"""
    
    @staticmethod
    def get_recent_files(hours: int = 24) -> list:
        """Get recent output files"""
        try:
            data_dir = Path(Paths.DATA_RAW)
            recent_files = []
            
            if data_dir.exists():
                cutoff_time = datetime.now().timestamp() - (hours * 3600)
                
                for file in data_dir.glob("*.jsonl"):
                    if file.stat().st_mtime > cutoff_time:
                        recent_files.append({
                            "file": file.name,
                            "size": file.stat().st_size,
                            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                        })
            
            return sorted(recent_files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting recent files: {e}")
            return []


# Dependency Injection
def get_scraping_orchestrator() -> ScrapingOrchestrator:
    """Dependency: Get scraping orchestrator instance"""
    return ScrapingOrchestrator()


def get_file_manager() -> FileManager:
    """Dependency: Get file manager instance"""
    return FileManager()


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with comprehensive system info"""
    try:
        return HealthResponse(
            status="healthy",
            service=SERVICE_NAME,
            timestamp=get_current_timestamp(),
            version="2.0.0",
            available_spiders=SpiderNames.get_valid_spiders()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_ERROR,
            detail=f"Health check failed: {e}"
        )


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "AWA Scraper API",
        "version": "2.0.0",
        "description": "Professional web scraping service",
        "endpoints": {
            "health": "/health",
            "scrape": "/api/scrape",
            "status": "/api/status"
        },
        "available_spiders": SpiderNames.get_valid_spiders()
    }


@app.post("/api/scrape", response_model=ScrapeResponse)
async def trigger_scrape(
    request: ScrapeRequest,
    orchestrator: ScrapingOrchestrator = Depends(get_scraping_orchestrator)
):
    """Trigger scraping operation with validation"""
    
    # Validate request
    validation_result = validate_scrape_request(request.dict())
    if not validation_result.is_valid:
        logger.warning(f"Invalid scrape request: {validation_result.errors}")
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "details": validation_result.errors
            }
        )
    
    try:
        # Start scraping
        result = await orchestrator.start_scraping(request.spider, request.options)
        
        return ScrapeResponse(
            success=result["success"],
            message=f"Spider {request.spider} started successfully",
            spider=request.spider,
            batch_id=result["batch_id"],
            started_at=result["started_at"],
            output_file=result["output_file"],
            estimated_duration="5-15 minutes"
        )
        
    except ScrapingError as e:
        logger.error(f"Scraping error: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_ERROR,
            detail=f"Scraping failed: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_ERROR,
            detail=f"Unexpected error: {e}"
        )


@app.get("/api/status", response_model=StatusResponse)
async def get_status(file_manager: FileManager = Depends(get_file_manager)):
    """Get comprehensive service status"""
    try:
        recent_files = file_manager.get_recent_files(24)
        
        system_info = {
            "data_directory": Paths.DATA_RAW,
            "total_recent_files": len(recent_files),
            "service_uptime": "Available via health endpoint"
        }
        
        return StatusResponse(
            service=SERVICE_NAME,
            status="running",
            recent_files=recent_files,
            available_spiders=SpiderNames.get_valid_spiders(),
            system_info=system_info
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=HttpStatus.INTERNAL_ERROR,
            content={
                "error": f"Status check failed: {e}",
                "service": SERVICE_NAME,
                "timestamp": get_current_timestamp()
            }
        )


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=HttpStatus.BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ScrapingError)
async def scraping_exception_handler(request, exc: ScrapingError):
    """Handle scraping errors"""
    return JSONResponse(
        status_code=HttpStatus.INTERNAL_ERROR,
        content={
            "error": "Scraping Error",
            "message": exc.message,
            "details": exc.details
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=ServicePorts.SCRAPER.value,
        log_level="info"
    )
