"""
API FastAPI pour le service ETL
Permet de déclencher le pipeline ETL via HTTP
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire ETL au path
sys.path.insert(0, '/app')

app = FastAPI(title="AWA ETL API", version="1.0.0")

class ETLRequest(BaseModel):
    source_directory: Optional[str] = None
    file_pattern: str = "*.jsonl"
    force_reprocess: bool = False

class ETLResponse(BaseModel):
    success: bool
    message: str
    batch_id: Optional[str] = None
    processed_count: int = 0
    loaded_count: int = 0
    duration: float = 0.0
    started_at: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test rapide de l'import des modules ETL
        from orchestrator import ETLOrchestrator
        from config import CONFIG
        
        return {
            "status": "ok",
            "service": "etl", 
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "supabase_configured": bool(CONFIG.supabase_url)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "service": "etl",
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    """Root endpoint avec info sur l'API"""
    return {
        "service": "AWA ETL API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process": "/api/process",
            "status": "/api/status"
        }
    }

@app.post("/api/process", response_model=ETLResponse)
async def trigger_etl(request: ETLRequest):
    """Déclenche le pipeline ETL"""
    
    started_at = datetime.now()
    
    try:
        # Import des modules ETL
        from orchestrator import ETLOrchestrator
        from config import CONFIG
        from dotenv import load_dotenv
        
        # Charger la configuration
        load_dotenv()
        CONFIG.supabase_url = os.getenv('SUPABASE_URL', '')
        CONFIG.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
        
        # Définir le répertoire source
        source_dir = request.source_directory or "/app/data/raw"
        source_path = Path(source_dir)
        
        if not source_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Répertoire source inexistant: {source_dir}"
            )
        
        # Créer et lancer l'orchestrateur ETL
        etl = ETLOrchestrator()
        result = etl.run(
            source_directory=str(source_path),
            file_pattern=request.file_pattern
        )
        
        # Calculer la durée
        duration = (datetime.now() - started_at).total_seconds()
        
        if result.get("success", False):
            return ETLResponse(
                success=True,
                message="Pipeline ETL exécuté avec succès",
                batch_id=result.get("batch_id"),
                processed_count=result.get("processed_count", 0),
                loaded_count=result.get("loaded_count", 0),
                duration=duration,
                started_at=started_at.isoformat()
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Échec du pipeline ETL: {result.get('error', 'Erreur inconnue')}"
            )
            
    except Exception as e:
        duration = (datetime.now() - started_at).total_seconds()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement ETL: {str(e)}"
        )

@app.get("/api/status")
async def get_status():
    """Statut du service ETL"""
    try:
        from config import CONFIG
        
        # Vérifier les fichiers traités récents
        processed_dir = Path("/app/data/processed")
        raw_dir = Path("/app/data/raw")
        
        recent_processed = []
        pending_files = []
        
        # Fichiers traités récemment
        if processed_dir.exists():
            for file in processed_dir.glob("*.json"):
                if file.stat().st_mtime > (datetime.now().timestamp() - 86400):  # 24h
                    recent_processed.append({
                        "file": file.name,
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
        
        # Fichiers en attente de traitement
        if raw_dir.exists():
            for file in raw_dir.glob("*.jsonl"):
                pending_files.append({
                    "file": file.name,
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
        
        return {
            "service": "etl",
            "status": "running",
            "supabase_configured": bool(CONFIG.supabase_url),
            "recent_processed": recent_processed,
            "pending_files": pending_files,
            "directories": {
                "raw": str(raw_dir),
                "processed": str(processed_dir)
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur lors de la récupération du statut: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
