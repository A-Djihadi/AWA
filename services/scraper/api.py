"""
API FastAPI pour le service Scraper
Permet de déclencher les spiders via HTTP
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import json
from datetime import datetime
import asyncio
from pathlib import Path

app = FastAPI(title="AWA Scraper API", version="1.0.0")

class ScrapeRequest(BaseModel):
    spider: str
    options: Optional[dict] = {}

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    spider: str
    started_at: str
    output_file: Optional[str] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "scraper",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint avec info sur l'API"""
    return {
        "service": "AWA Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "scrape": "/api/scrape",
            "status": "/api/status"
        }
    }

@app.post("/api/scrape", response_model=ScrapeResponse)
async def trigger_scrape(request: ScrapeRequest):
    """Déclenche un spider de scraping"""
    
    valid_spiders = ["freework", "malt", "comet"]
    
    if request.spider not in valid_spiders:
        raise HTTPException(
            status_code=400, 
            detail=f"Spider '{request.spider}' non supporté. Spiders disponibles: {valid_spiders}"
        )
    
    try:
        # Préparer la commande scrapy
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/app/data/raw/{request.spider}_{timestamp}.jsonl"
        
        # Construire la commande
        cmd = [
            "python", "-m", "scrapy", "crawl", request.spider,
            "-o", output_file,
            "-s", "LOG_LEVEL=INFO"
        ]
        
        # Ajouter les options custom si fournies
        for key, value in request.options.items():
            cmd.extend(["-s", f"{key}={value}"])
        
        # Lancer le spider en arrière-plan
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/app"
        )
        
        # Ne pas attendre la fin, retourner immédiatement
        return ScrapeResponse(
            success=True,
            message=f"Spider {request.spider} démarré avec succès",
            spider=request.spider,
            started_at=datetime.now().isoformat(),
            output_file=output_file
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du lancement du spider: {str(e)}"
        )

@app.get("/api/status")
async def get_status():
    """Statut du service scraper"""
    try:
        # Vérifier les fichiers de sortie récents
        data_dir = Path("/app/data/raw")
        recent_files = []
        
        if data_dir.exists():
            for file in data_dir.glob("*.jsonl"):
                if file.stat().st_mtime > (datetime.now().timestamp() - 86400):  # 24h
                    recent_files.append({
                        "file": file.name,
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
        
        return {
            "service": "scraper",
            "status": "running",
            "recent_files": recent_files,
            "available_spiders": ["freework", "malt", "comet"]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur lors de la récupération du statut: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
