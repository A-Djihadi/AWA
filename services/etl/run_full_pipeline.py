#!/usr/bin/env python3
"""
Pipeline complet: Transformation → Validation → Chargement Supabase
Utilise le validateur de localisations pour garantir des villes françaises valides
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, UTC
from supabase import create_client
from dotenv import load_dotenv

# Ajouter le répertoire du scraper au path pour importer le validateur
SCRAPER_DIR = Path(__file__).parent.parent / 'scraper'
sys.path.insert(0, str(SCRAPER_DIR))

from tjm_scraper.location_validator import normalize_location, is_valid_french_location

# Chargement des variables d'environnement
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def load_scraped_data(scraper_dir):
    """Charge les données scrapées depuis les fichiers JSON"""
    data_dir = Path(scraper_dir) / 'data'
    items = []
    
    # Chercher tous les fichiers JSON
    json_files = list(data_dir.glob('*.json'))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                # Essayer de charger comme JSON
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        items.extend(data)
                    else:
                        items.append(data)
                except json.JSONDecodeError:
                    # Essayer comme JSONL
                    f.seek(0)
                    for line in f:
                        if line.strip():
                            items.append(json.loads(line))
            
            print(f"✅ {json_file.name}: {len(items)} items chargés")
        except Exception as e:
            print(f"❌ Erreur avec {json_file.name}: {e}")
    
    return items


def transform_and_validate_item(item):
    """Transforme et valide un item"""
    # Normaliser la localisation avec le validateur
    raw_location = item.get('location')
    location = normalize_location(raw_location) if raw_location else None
    
    # Si la localisation n'est pas valide, on la rejette
    if raw_location and not location:
        print(f"⚠️  Item rejeté - localisation invalide: {raw_location}")
        return None
    
    # Extraire et nettoyer les technologies
    technologies = item.get('technologies', [])
    if isinstance(technologies, str):
        technologies = [t.strip() for t in technologies.split(',')]
    
    # Nettoyer les valeurs None ou vides
    technologies = [t for t in technologies if t]
    
    return {
        'source': item.get('source', 'unknown'),
        'source_id': str(item.get('source_id', '')),
        'title': item.get('title', ''),
        'company': item.get('company', ''),
        'tjm_min': item.get('tjm_min'),
        'tjm_max': item.get('tjm_max'),
        'tjm_currency': item.get('tjm_currency', 'EUR'),
        'technologies': technologies,
        'seniority_level': item.get('seniority_level'),
        'location': location,
        'remote_policy': item.get('remote_policy'),
        'contract_type': item.get('contract_type'),
        'description': item.get('description', ''),
        'url': item.get('url', ''),
        'scraped_at': item.get('scraped_at', datetime.now(UTC).isoformat())
    }


def send_to_supabase(items):
    """Envoie les items vers Supabase"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Configuration Supabase manquante")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Transformation et validation
        transformed_items = []
        rejected_count = 0
        
        for item in items:
            try:
                transformed = transform_and_validate_item(item)
                if transformed:
                    transformed_items.append(transformed)
                else:
                    rejected_count += 1
            except Exception as e:
                print(f"⚠️  Erreur transformation: {e}")
                rejected_count += 1
        
        print(f"\n📊 Validation:")
        print(f"   ✅ Items validés: {len(transformed_items)}")
        print(f"   ❌ Items rejetés: {rejected_count}")
        print(f"   📦 Total items: {len(items)}")
        
        if not transformed_items:
            print("\n⚠️  Aucun item valide à envoyer")
            return False
        
        # Statistiques de localisation
        locations = {}
        for item in transformed_items:
            loc = item.get('location', 'Unknown')
            locations[loc] = locations.get(loc, 0) + 1
        
        print("\n📍 Répartition des localisations valides:")
        for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True):
            print(f"   {loc}: {count} missions")
        
        # Envoi par batch
        batch_size = 50
        success_count = 0
        
        for i in range(0, len(transformed_items), batch_size):
            batch = transformed_items[i:i + batch_size]
            
            try:
                response = supabase.table('offers').upsert(
                    batch,
                    on_conflict='source,source_id'
                ).execute()
                
                success_count += len(batch)
                print(f"✅ Batch {i//batch_size + 1}: {len(batch)} items envoyés")
            except Exception as e:
                print(f"❌ Erreur batch {i//batch_size + 1}: {e}")
        
        print(f"\n🎉 Total: {success_count}/{len(transformed_items)} items chargés dans Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("🚀 Pipeline ETL - Transformation et Chargement Supabase\n")
    
    # Chemins
    base_dir = Path(__file__).parent.parent
    scraper_dir = base_dir / 'scraper'
    
    # Étape 1: Charger les données existantes
    print("📥 Chargement des données scrapées...")
    items = load_scraped_data(scraper_dir)
    
    if not items:
        print("⚠️  Aucune donnée trouvée. Exécutez d'abord les scrapers.")
        print("   Utilisez: python services/scraper/run_scrapers.py")
        return 1
    
    print(f"\n✅ {len(items)} items chargés\n")
    
    # Étape 2: Envoi vers Supabase avec validation
    print("📤 Transformation et envoi vers Supabase...")
    success = send_to_supabase(items)
    
    if success:
        print("\n✅ Pipeline terminé avec succès!")
        return 0
    else:
        print("\n❌ Le pipeline a rencontré des erreurs")
        return 1


if __name__ == "__main__":
    sys.exit(main())
