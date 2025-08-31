"""
Health check server pour le scraper service
"""
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="AWA Scraper Health Check")

# Status global du service
service_status = {
    "status": "healthy",
    "last_scrape": None,
    "total_scraped": 0,
    "errors": 0,
    "uptime": datetime.utcnow(),
}


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    last_scrape: str = None
    total_scraped: int
    errors: int
    message: str = None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.utcnow() - service_status["uptime"]).total_seconds()
    
    return HealthResponse(
        status=service_status["status"],
        uptime_seconds=uptime,
        last_scrape=service_status["last_scrape"],
        total_scraped=service_status["total_scraped"],
        errors=service_status["errors"],
        message="Scraper service is running"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AWA Scraper Service", "version": "1.0.0"}


@app.post("/update-status")
async def update_status(status: dict):
    """Update service status (called by scrapers)"""
    global service_status
    service_status.update(status)
    return {"message": "Status updated"}


if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)
