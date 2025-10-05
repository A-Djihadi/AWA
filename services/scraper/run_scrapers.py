#!/usr/bin/env python3
"""
Script de scraping complet pour AWA
Lance les scrapers et sauvegarde les résultats
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# Chemins
SCRAPER_DIR = Path(__file__).parent
DATA_DIR = SCRAPER_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Configuration des spiders
SPIDERS = [
    {
        'name': 'freework',
        'output': DATA_DIR / 'freework_offers.json',
        'pages': 15  # Scraper 15 pages
    },
    {
        'name': 'collective_work',
        'output': DATA_DIR / 'collective_work_offers.json',
        'pages': 15  # Scraper 15 pages
    }
]


def run_spider(spider_config):
    """Exécute un spider Scrapy"""
    spider_name = spider_config['name']
    output_file = spider_config['output']
    
    print(f"\n🕷️  Lancement du spider: {spider_name}")
    print(f"   Sortie: {output_file}")
    
    try:
        # Construire la commande scrapy
        cmd = [
            sys.executable, '-m', 'scrapy', 'crawl', spider_name,
            '-o', str(output_file),
            '-s', 'LOG_LEVEL=INFO',
            '-s', 'FEED_EXPORT_ENCODING=utf-8'
        ]
        
        # Exécuter le spider
        result = subprocess.run(
            cmd,
            cwd=SCRAPER_DIR,
            capture_output=True,
            text=True,
            timeout=300  # Timeout de 5 minutes
        )
        
        if result.returncode == 0:
            print(f"   ✅ Spider {spider_name} terminé avec succès")
            return True
        else:
            print(f"   ❌ Erreur lors de l'exécution du spider {spider_name}")
            print(f"   Stderr: {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout pour le spider {spider_name}")
        return False
    except Exception as e:
        print(f"   ❌ Exception lors de l'exécution du spider {spider_name}: {e}")
        return False


def main():
    """Fonction principale"""
    print("="*60)
    print("🚀 AWA - Scraping Complet des Offres TJM")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Répertoire de sortie: {DATA_DIR}")
    print()
    
    # Statistiques
    success_count = 0
    total_count = len(SPIDERS)
    
    # Exécuter chaque spider
    for spider_config in SPIDERS:
        success = run_spider(spider_config)
        if success:
            success_count += 1
    
    # Résumé
    print("\n" + "="*60)
    print("📊 Résumé du Scraping")
    print("="*60)
    print(f"   ✅ Spiders réussis: {success_count}/{total_count}")
    print(f"   📁 Fichiers générés:")
    
    for spider_config in SPIDERS:
        output_file = spider_config['output']
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"      - {output_file.name} ({size_kb:.2f} KB)")
    
    print("\n🎉 Scraping terminé!")
    
    if success_count == total_count:
        print("   Vous pouvez maintenant exécuter l'ETL pour charger les données dans Supabase")
        return 0
    else:
        print("   ⚠️  Certains scrapers ont échoué, vérifiez les logs")
        return 1


if __name__ == "__main__":
    sys.exit(main())
