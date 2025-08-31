"""
Script principal pour lancer le scraper refactorisé
"""
import argparse
import sys
import os
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Import des spiders refactorisés
from scraper.spiders.freework_spider import FreeWorkSpiderRefactored


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='AWA TJM Scraper v2.0 - Refactorisé')
    parser.add_argument('spider', choices=['freework'], help='Spider à lancer')
    parser.add_argument('--env', choices=['development', 'production', 'testing'], 
                       default='development', help='Environnement d\'exécution')
    parser.add_argument('--limit', type=int, help='Limite d\'items à scraper')
    parser.add_argument('--output', help='Fichier de sortie personnalisé')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbose')
    
    args = parser.parse_args()
    
    # Configuration de l'environnement
    os.environ['SCRAPY_ENV'] = args.env
    
    # Charger les settings
    settings = get_project_settings()
    
    # Ajustements basés sur les arguments
    if args.limit:
        settings.set('CLOSESPIDER_ITEMCOUNT', args.limit)
    
    if args.verbose:
        settings.set('LOG_LEVEL', 'DEBUG')
    
    if args.output:
        # Configurer un export personnalisé
        settings.set('FEEDS', {
            args.output: {
                'format': 'jsonlines',
                'encoding': 'utf8',
            }
        })
    
    # Mapper les noms de spiders
    spider_mapping = {
        'freework': FreeWorkSpiderRefactored,
    }
    
    spider_class = spider_mapping.get(args.spider)
    if not spider_class:
        print(f"❌ Spider '{args.spider}' non trouvé")
        return 1
    
    print(f"Starting spider {args.spider} in {args.env} mode")
    print(f"📁 Données exportées vers: data/processed/")
    
    # Lancer le crawler
    process = CrawlerProcess(settings)
    process.crawl(spider_class)
    process.start()
    
    print("✅ Scraping terminé!")
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
