"""
ETL Service API - Refactored with Clean Code principles
Following SOLID principles and dependency injection
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import sys
from datetime import datetime
from pathlib import Path

# Import shared modules
sys.path.append('/app/services')
from shared import (
    ServicePorts, Paths, FilePatterns, HttpStatus,
    setup_service_logging, validate_etl_request,
    get_current_timestamp, generate_batch_id, format_duration,
    ProcessingError, ValidationError, ConfigurationError
)

# Add ETL modules to path
sys.path.insert(0, '/app')

# Service setup
SERVICE_NAME = "etl"
logger_service = setup_service_logging(SERVICE_NAME, port=ServicePorts.ETL.value)
logger = logger_service.logger

app = FastAPI(
    title="AWA ETL API",
    description="Professional ETL pipeline service",
    version="2.0.0"
)


# Pydantic Models
class ETLRequest(BaseModel):
    """ETL processing request model"""
    source_directory: Optional[str] = Field(default=None, description="Source data directory")
    file_pattern: str = Field(default=FilePatterns.JSONL, description="File pattern to process")
    force_reprocess: bool = Field(default=False, description="Force reprocess existing files")
    batch_size: Optional[int] = Field(default=None, description="Processing batch size")
    
    class Config:
        schema_extra = {
            "example": {
                "source_directory": "/app/data/raw",
                "file_pattern": "*.jsonl",
                "force_reprocess": False,
                "batch_size": 100
            }
        }


class ETLResponse(BaseModel):
    """ETL processing response model"""
    success: bool
    message: str
    batch_id: str
    started_at: str
    processing_stats: Dict[str, Any]
    duration: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    timestamp: str
    version: str
    supabase_configured: bool
    database_connection: str


class StatusResponse(BaseModel):
    """Service status response model"""
    service: str
    status: str
    supabase_configured: bool
    recent_processed: list
    pending_files: list
    system_info: dict


# Business Logic Classes
class ETLOrchestrationService:
    """Handles ETL orchestration and configuration"""
    
    def __init__(self):
        self.config = None
        self.orchestrator = None
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize ETL configuration"""
        try:
            from config import CONFIG
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv()
            CONFIG.supabase_url = os.getenv('SUPABASE_URL', '')
            CONFIG.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
            
            self.config = CONFIG
            logger.info("ETL configuration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ETL config: {e}")
            raise ConfigurationError(f"ETL configuration failed: {e}")
    
    def get_orchestrator(self):
        """Get or create ETL orchestrator instance"""
        if not self.orchestrator:
            try:
                from orchestrator import ETLOrchestrator
                self.orchestrator = ETLOrchestrator()
                logger.info("ETL orchestrator created successfully")
            except Exception as e:
                logger.error(f"Failed to create ETL orchestrator: {e}")
                raise ProcessingError(f"ETL orchestrator creation failed: {e}")
        
        return self.orchestrator
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            # Check configuration
            config_ok = bool(self.config and self.config.supabase_url)
            
            # Test database connection
            db_status = "connected" if config_ok else "not_configured"
            
            return {
                "config_loaded": bool(self.config),
                "supabase_configured": config_ok,
                "database_status": db_status
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "config_loaded": False,
                "supabase_configured": False,
                "database_status": "error"
            }
    
    async def process_data(self, request: ETLRequest) -> Dict[str, Any]:
        """Process data through ETL pipeline"""
        start_time = datetime.now()
        batch_id = generate_batch_id()
        
        try:
            # Get orchestrator
            orchestrator = self.get_orchestrator()
            
            # Determine source directory
            source_dir = request.source_directory or self.config.data_source_dir
            source_path = Path(source_dir)
            
            if not source_path.exists():
                raise ValidationError(
                    f"Source directory does not exist: {source_dir}",
                    field="source_directory",
                    value=source_dir
                )
            
            logger.info(f"Starting ETL processing: batch_id={batch_id}, source={source_dir}")
            
            # Run ETL pipeline
            result = orchestrator.run(
                source_directory=str(source_path),
                file_pattern=request.file_pattern
            )
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Prepare response
            processing_stats = {
                "extracted_records": result.get("statistics", {}).get("extracted_records", 0),
                "transformed_offers": result.get("statistics", {}).get("transformed_offers", 0),
                "loaded_offers": result.get("statistics", {}).get("loaded_offers", 0),
                "success_rate": result.get("statistics", {}).get("success_rate", 0.0),
                "duration_formatted": format_duration(duration)
            }
            
            if result.get("success", False):
                logger.info(f"ETL processing completed successfully: batch_id={batch_id}")
                return {
                    "success": True,
                    "batch_id": batch_id,
                    "result": result,
                    "processing_stats": processing_stats,
                    "duration": duration
                }
            else:
                error_msg = result.get("error", "Unknown ETL error")
                logger.error(f"ETL processing failed: batch_id={batch_id}, error={error_msg}")
                raise ProcessingError(f"ETL pipeline failed: {error_msg}")
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"ETL processing exception: batch_id={batch_id}, error={e}")
            raise ProcessingError(f"ETL processing failed: {e}")


class FileStatusService:
    """Handles file status and monitoring"""
    
    @staticmethod
    def get_recent_processed_files(hours: int = 24) -> list:
        """Get recently processed files"""
        try:
            processed_dir = Path(Paths.DATA_PROCESSED)
            recent_files = []
            
            if processed_dir.exists():
                cutoff_time = datetime.now().timestamp() - (hours * 3600)
                
                for file in processed_dir.glob("*.json"):
                    if file.stat().st_mtime > cutoff_time:
                        recent_files.append({
                            "file": file.name,
                            "size": file.stat().st_size,
                            "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                        })
            
            return sorted(recent_files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting recent processed files: {e}")
            return []
    
    @staticmethod
    def get_pending_files() -> list:
        """Get files pending processing"""
        try:
            raw_dir = Path(Paths.DATA_RAW)
            pending_files = []
            
            if raw_dir.exists():
                for file in raw_dir.glob("*.jsonl"):
                    pending_files.append({
                        "file": file.name,
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            
            return sorted(pending_files, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting pending files: {e}")
            return []


# Dependency Injection
def get_etl_service() -> ETLOrchestrationService:
    """Dependency: Get ETL orchestration service"""
    return ETLOrchestrationService()


def get_file_service() -> FileStatusService:
    """Dependency: Get file status service"""
    return FileStatusService()


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check(etl_service: ETLOrchestrationService = Depends(get_etl_service)):
    """Comprehensive health check"""
    try:
        health_info = etl_service.health_check()
        
        return HealthResponse(
            status="healthy" if health_info["config_loaded"] else "degraded",
            service=SERVICE_NAME,
            timestamp=get_current_timestamp(),
            version="2.0.0",
            supabase_configured=health_info["supabase_configured"],
            database_connection=health_info["database_status"]
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_ERROR,
            detail=f"Health check failed: {e}"
        )


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "service": "AWA ETL API",
        "version": "2.0.0",
        "description": "Professional ETL pipeline service",
        "endpoints": {
            "health": "/health",
            "process": "/api/process",
            "status": "/api/status"
        },
        "supported_formats": [FilePatterns.JSONL, FilePatterns.JSON]
    }


@app.post("/api/process", response_model=ETLResponse)
async def trigger_etl(
    request: ETLRequest,
    background_tasks: BackgroundTasks,
    etl_service: ETLOrchestrationService = Depends(get_etl_service)
):
    """Trigger ETL processing with validation"""
    
    # Validate request
    validation_result = validate_etl_request(request.dict())
    if not validation_result.is_valid:
        logger.warning(f"Invalid ETL request: {validation_result.errors}")
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "details": validation_result.errors
            }
        )
    
    try:
        # Process data
        result = await etl_service.process_data(request)
        
        return ETLResponse(
            success=result["success"],
            message="ETL processing completed successfully",
            batch_id=result["batch_id"],
            started_at=get_current_timestamp(),
            processing_stats=result["processing_stats"],
            duration=result["duration"]
        )
        
    except (ProcessingError, ValidationError) as e:
        logger.error(f"ETL processing error: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_ERROR,
            detail=f"ETL processing failed: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected ETL error: {e}")
        raise HTTPException(
            status_code=HttpStatus.INTERNAL_ERROR,
            detail=f"Unexpected error: {e}"
        )


@app.get("/api/status", response_model=StatusResponse)
async def get_status(
    etl_service: ETLOrchestrationService = Depends(get_etl_service),
    file_service: FileStatusService = Depends(get_file_service)
):
    """Get comprehensive service status"""
    try:
        health_info = etl_service.health_check()
        recent_processed = file_service.get_recent_processed_files(24)
        pending_files = file_service.get_pending_files()
        
        system_info = {
            "raw_directory": Paths.DATA_RAW,
            "processed_directory": Paths.DATA_PROCESSED,
            "total_recent_processed": len(recent_processed),
            "total_pending_files": len(pending_files)
        }
        
        return StatusResponse(
            service=SERVICE_NAME,
            status="running",
            supabase_configured=health_info["supabase_configured"],
            recent_processed=recent_processed,
            pending_files=pending_files,
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


@app.exception_handler(ProcessingError)
async def processing_exception_handler(request, exc: ProcessingError):
    """Handle processing errors"""
    return JSONResponse(
        status_code=HttpStatus.INTERNAL_ERROR,
        content={
            "error": "Processing Error",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ConfigurationError)
async def config_exception_handler(request, exc: ConfigurationError):
    """Handle configuration errors"""
    return JSONResponse(
        status_code=HttpStatus.SERVICE_UNAVAILABLE,
        content={
            "error": "Configuration Error",
            "message": exc.message,
            "details": exc.details
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=ServicePorts.ETL.value,
        log_level="info"
    )
