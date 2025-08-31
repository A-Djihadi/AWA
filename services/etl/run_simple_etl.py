#!/usr/bin/env python3
"""
Simple ETL Runner for AWA TJM Scraper
"""
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from orchestrator import run_etl


def main():
    """Run ETL pipeline for scraped data"""
    
    # Configuration
    input_file = "../scraper/data/freework_offers.json" 
    source = "freework"
    
    print(f"🚀 Démarrage de l'ETL pour {source}")
    print(f"📁 Fichier d'entrée: {input_file}")
    
    # Validate Supabase configuration
    if not CONFIG.supabase_url or not CONFIG.supabase_key:
        print("❌ Configuration Supabase manquante!")
        print(f"   SUPABASE_URL: {'✅' if CONFIG.supabase_url else '❌'}")
        print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅' if CONFIG.supabase_key else '❌'}")
        return 1
    
    # Load scraped data
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        print(f"✅ {len(raw_data)} offres chargées depuis {input_file}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement du fichier: {e}")
        return 1
    
    # Prepare data directory
    data_dir = Path("../scraper/data/raw")
    data_dir.mkdir(exist_ok=True)
    
    # Save data in JSONL format (one JSON object per line)
    jsonl_file = data_dir / "freework_temp.jsonl"
    try:
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for offer in raw_data:
                f.write(json.dumps(offer, ensure_ascii=False) + '\n')
        print(f"✅ Données converties en JSONL: {jsonl_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la conversion JSONL: {e}")
        return 1
    
    # Set correct paths for Windows  
    data_dir = Path("../scraper/data/raw")
    source_directory = str(data_dir.absolute())
    
    # Force update CONFIG with correct paths
    CONFIG.data_source_dir = source_directory
    CONFIG.supabase_url = os.getenv('SUPABASE_URL', '')
    CONFIG.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
    
    print(f"📂 Répertoire source: {source_directory}")
    print(f"🔗 Supabase URL: {CONFIG.supabase_url[:20]}...")
    print(f"🔑 Supabase Key: {'✅ Configuré' if CONFIG.supabase_key else '❌ Manquant'}")
    
    # Validate configuration again
    if not CONFIG.supabase_url or not CONFIG.supabase_key:
        print("❌ Configuration Supabase toujours manquante après rechargement!")
        return 1
    
    # Run ETL pipeline
    try:
        print("🔄 Démarrage du pipeline ETL...")
        result = run_etl(source_directory=source_directory, file_pattern="*.jsonl")
        
        if result.get('success', False):
            print(f"✅ Pipeline ETL terminé avec succès!")
            print(f"📊 Offres traitées: {result.get('processed_count', 0)}")
            print(f"📈 Offres chargées: {result.get('loaded_count', 0)}")
            print(f"⏱️  Durée: {result.get('duration', 0):.2f}s")
        else:
            print(f"❌ Pipeline ETL échoué: {result.get('error', 'Erreur inconnue')}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur durant l'exécution ETL: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
