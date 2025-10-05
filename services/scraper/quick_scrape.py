#!/usr/bin/env python3
"""Script rapide pour scraper avec Scrapy"""

import subprocess
import sys
from pathlib import Path

SCRAPER_DIR = Path(__file__).parent
DATA_DIR = SCRAPER_DIR / 'data'

def main():
    print("\n" + "="*70)
    print("🕷️  Scraping FreeWork et Collective.work")
    print("="*70 + "\n")
    
    # Nettoyer les anciens fichiers
    DATA_DIR.mkdir(exist_ok=True)
    for json_file in DATA_DIR.glob('*.json'):
        json_file.unlink()
        print(f"🗑️  Supprimé: {json_file.name}")
    
    scrapers = [
        ('freework', 'FreeWork'),
        ('collective_work', 'Collective.work')
    ]
    
    total = 0
    
    for spider_name, display_name in scrapers:
        print(f"\n{'='*70}")
        print(f"🚀 {display_name} (15 pages)")
        print(f"{'='*70}\n")
        
        output_file = DATA_DIR / f'{spider_name}.json'
        
        try:
            # Utiliser python -m scrapy
            cmd = [
                sys.executable, '-m', 'scrapy', 'crawl', spider_name,
                '-O', str(output_file),
                '--loglevel=INFO'
            ]
            
            print(f"Commande: {' '.join(cmd)}\n")
            
            result = subprocess.run(
                cmd,
                cwd=str(SCRAPER_DIR),
                text=True
            )
            
            if result.returncode == 0 or output_file.exists():
                if output_file.exists():
                    import json
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        count = len(data) if isinstance(data, list) else 1
                    
                    print(f"\n✅ {display_name}: {count} offres scrapées")
                    total += count
                else:
                    print(f"\n⚠️  Aucun fichier créé")
            else:
                print(f"\n❌ Erreur (code: {result.returncode})")
                
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
    
    print(f"\n{'='*70}")
    print(f"✅ Total: {total} offres scrapées")
    print(f"{'='*70}\n")
    
    return 0 if total > 0 else 1

if __name__ == '__main__':
    sys.exit(main())
