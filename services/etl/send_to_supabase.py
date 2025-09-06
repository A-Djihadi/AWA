#!/usr/bin/env python3
"""
Script d'envoi direct des données scrapées vers Supabase
"""

import json
import os
from pathlib import Path
from supabase import create_client
from datetime import datetime
import sys
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Supabase depuis les variables d'environnement
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Erreur: Variables d'environnement Supabase manquantes")
    print("Vérifiez SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY dans .env")
    sys.exit(1)

def load_jsonl_file(file_path):
    """Charge un fichier JSONL et retourne la liste des items"""
    items = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    items.append(json.loads(line))
        print(f"✅ {len(items)} items chargés depuis {file_path}")
        return items
    except Exception as e:
        print(f"❌ Erreur lors du chargement de {file_path}: {e}")
        return []

def transform_item(item):
    """Transforme un item pour l'adapter au schéma Supabase"""
    return {
        'source': item.get('source', 'unknown'),
        'source_id': item.get('source_id', ''),
        'title': item.get('title', ''),
        'company': item.get('company', ''),
        'tjm_min': item.get('tjm_min'),
        'tjm_max': item.get('tjm_max'),
        'tjm_currency': item.get('tjm_currency', 'EUR'),
        'technologies': item.get('technologies', []),
        'seniority_level': item.get('seniority_level'),
        'location': item.get('location', ''),
        'remote_policy': item.get('remote_policy'),
        'contract_type': item.get('contract_type', 'freelance'),
        'description': item.get('description', ''),
        'url': item.get('url', ''),  # Changé de source_url à url
        'scraped_at': item.get('scraped_at', datetime.now().isoformat())
    }

def send_to_supabase(items):
    """Envoie les items vers Supabase"""
    try:
        # Créer le client Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Transformer les items
        transformed_items = [transform_item(item) for item in items]
        
        # Envoyer par batch de 50
        batch_size = 50
        total_sent = 0
        
        for i in range(0, len(transformed_items), batch_size):
            batch = transformed_items[i:i + batch_size]
            
            try:
                response = supabase.table('offers').upsert(
                    batch,
                    on_conflict='source,source_id'
                ).execute()
                
                total_sent += len(batch)
                print(f"✅ Batch {i//batch_size + 1}: {len(batch)} items envoyés")
                
            except Exception as e:
                print(f"❌ Erreur batch {i//batch_size + 1}: {e}")
                continue
        
        print(f"🎉 Total envoyé vers Supabase: {total_sent}/{len(items)}")
        return total_sent
        
    except Exception as e:
        print(f"❌ Erreur connexion Supabase: {e}")
        return 0

def main():
    """Fonction principale"""
    print("🚀 Script d'envoi des données vers Supabase")
    
    # Chemins des fichiers
    scraper_dir = Path("../scraper/data/raw")
    
    # Chercher les fichiers JSONL récents
    jsonl_files = list(scraper_dir.glob("*.jsonl"))
    
    if not jsonl_files:
        print("❌ Aucun fichier JSONL trouvé")
        return
    
    # Trier par date de modification (plus récents en premier)
    jsonl_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📁 Fichiers trouvés: {[f.name for f in jsonl_files]}")
    
    all_items = []
    
    # Charger tous les fichiers
    for file_path in jsonl_files:
        items = load_jsonl_file(file_path)
        all_items.extend(items)
    
    if not all_items:
        print("❌ Aucune donnée à traiter")
        return
    
    print(f"📊 Total des items à traiter: {len(all_items)}")
    
    # Envoyer vers Supabase
    sent_count = send_to_supabase(all_items)
    
    print(f"✅ Mission accomplie! {sent_count} items envoyés vers Supabase")

if __name__ == "__main__":
    main()
