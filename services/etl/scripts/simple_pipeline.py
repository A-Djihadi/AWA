#!/usr/bin/env python3
"""
Script simplifié pour nettoyer la BDD et scraper les données
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Configuration
ETL_DIR = Path(__file__).parent.parent
SCRAPER_DIR = ETL_DIR.parent / 'scraper'
DATA_DIR = SCRAPER_DIR / 'data'

# Charger l'environnement
load_dotenv(ETL_DIR / '.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def clean_database():
    """Nettoie la table offers"""
    print("\n" + "="*70)
    print("🗑️  NETTOYAGE DE LA BASE DE DONNÉES")
    print("="*70 + "\n")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Compter les offres
        result = supabase.table('offers').select('id', count='exact').execute()
        count = len(result.data)
        
        print(f"📊 Offres actuelles: {count}")
        
        if count > 0:
            # Supprimer par source
            sources = ['freework', 'collective_work', 'generated_data', 'test', 'test_deduplication']
            for source in sources:
                try:
                    supabase.table('offers').delete().eq('source', source).execute()
                    print(f"   ✅ Supprimé: {source}")
                except Exception as e:
                    print(f"   ⚠️  {source}: {e}")
            
            print(f"\n✅ Base de données nettoyée")
        else:
            print("ℹ️  Base de données déjà vide")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def run_scrapers_manual():
    """Instructions pour lancer les scrapers manuellement"""
    print("\n" + "="*70)
    print("🕷️  LANCEMENT DES SCRAPERS")
    print("="*70 + "\n")
    
    print("📝 Exécutez les commandes suivantes dans un terminal séparé :\n")
    print(f"cd {SCRAPER_DIR}")
    print("scrapy crawl freework -O data/freework.json --loglevel=INFO")
    print("scrapy crawl collective_work -O data/collective_work.json --loglevel=INFO")
    print("\n⏳ Attendez que les scrapers se terminent, puis revenez ici...")
    
    input("\n▶️  Appuyez sur ENTRÉE quand les scrapers sont terminés...")
    return True


def count_scraped_data():
    """Compte les données scrapées"""
    print("\n" + "="*70)
    print("📊 DONNÉES SCRAPÉES")
    print("="*70 + "\n")
    
    total = 0
    for spider_name in ['freework', 'collective_work']:
        json_file = DATA_DIR / f'{spider_name}.json'
        
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    count = len(data) if isinstance(data, list) else 1
                    total += count
                    print(f"✅ {spider_name}: {count} offres")
            except Exception as e:
                print(f"⚠️  {spider_name}: Erreur de lecture - {e}")
        else:
            print(f"❌ {spider_name}: Fichier non trouvé")
    
    print(f"\n📊 Total: {total} offres scrapées")
    return total > 0


def load_to_database():
    """Charge les données dans Supabase"""
    print("\n" + "="*70)
    print("📤 CHARGEMENT DANS SUPABASE")
    print("="*70 + "\n")
    
    # Ajouter ETL au path
    sys.path.insert(0, str(ETL_DIR))
    
    try:
        from run_full_pipeline import main as run_etl
        
        print("🔄 Transformation et chargement...")
        result = run_etl()
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_database():
    """Vérifie les données chargées"""
    print("\n" + "="*70)
    print("✅ VÉRIFICATION")
    print("="*70 + "\n")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Total
        result = supabase.table('offers').select('source', count='exact').execute()
        total = len(result.data)
        
        print(f"📊 Total: {total} offres\n")
        
        # Par source
        sources = {}
        for offer in result.data:
            source = offer.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("📋 Par source:")
        for source, count in sorted(sources.items()):
            print(f"   • {source}: {count}")
        
        # Villes
        locations = supabase.table('offers').select('location').execute()
        unique_locations = set(o['location'] for o in locations.data if o.get('location'))
        
        print(f"\n🏙️  Villes: {len(unique_locations)}")
        
        # Technologies
        techs = supabase.table('offers').select('technologies').execute()
        all_techs = set()
        for offer in techs.data:
            if offer.get('technologies'):
                all_techs.update(offer['technologies'])
        
        print(f"💻 Technologies: {len(all_techs)}")
        
        # TJM
        tjms = supabase.table('offers').select('tjm_min, tjm_max').execute()
        valid_tjms = [
            (o['tjm_min'] + o['tjm_max']) / 2
            for o in tjms.data
            if o.get('tjm_min') and o.get('tjm_max')
        ]
        
        if valid_tjms:
            print(f"💰 TJM moyen: {sum(valid_tjms) / len(valid_tjms):.0f}€/jour")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Pipeline simplifié"""
    print("\n" + "="*70)
    print("🚀 AWA - Pipeline de données")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Configuration Supabase manquante dans .env")
        return False
    
    start = time.time()
    
    # Étape 1: Nettoyer
    if not clean_database():
        print("\n⚠️  Erreur de nettoyage, mais on continue...")
    
    # Étape 2: Scraper (manuel)
    run_scrapers_manual()
    
    # Étape 3: Vérifier les données scrapées
    if not count_scraped_data():
        print("\n❌ Pas de données scrapées. Abandon.")
        return False
    
    # Étape 4: Charger
    if not load_to_database():
        print("\n❌ Erreur de chargement")
        return False
    
    # Étape 5: Vérifier
    verify_database()
    
    duration = time.time() - start
    
    print("\n" + "="*70)
    print("✅ PIPELINE TERMINÉ")
    print(f"⏱️  Durée: {duration:.1f}s ({duration/60:.1f} min)")
    print("="*70 + "\n")
    
    return True


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
