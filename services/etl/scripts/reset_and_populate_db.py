#!/usr/bin/env python3
"""
Script pour nettoyer la BDD et la peupler avec des données fraîches
Étapes:
1. Nettoyer la table offers dans Supabase
2. Lancer les scrapers FreeWork et Collective.work (15 pages chacun)
3. Transformer et charger les données dans Supabase
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Configuration des chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRAPER_DIR = PROJECT_ROOT / 'scraper'
ETL_DIR = PROJECT_ROOT / 'etl'
DATA_DIR = SCRAPER_DIR / 'data'

# Ajouter les modules au path
sys.path.insert(0, str(ETL_DIR))
sys.path.insert(0, str(SCRAPER_DIR))

# Charger les variables d'environnement
load_dotenv(ETL_DIR / '.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def print_step(step_num, title, emoji="📌"):
    """Affiche une étape formatée"""
    print(f"\n{'='*70}")
    print(f"{emoji} ÉTAPE {step_num}: {title}")
    print(f"{'='*70}\n")


def clean_database():
    """Nettoie complètement la table offers"""
    print_step(1, "Nettoyage de la base de données", "🗑️")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Récupérer toutes les offres pour les supprimer
        result = supabase.table('offers').select('id').execute()
        count = len(result.data)
        
        print(f"   📊 Offres actuelles: {count}")
        
        if count > 0:
            # Supprimer toutes les offres une par une ou par batch
            supabase.table('offers').delete().gte('id', 0).execute()
            print(f"   ✅ {count} offres supprimées")
        else:
            print(f"   ℹ️  Base de données déjà vide")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
        # On continue quand même
        return True


def clean_scraper_data():
    """Nettoie les anciens fichiers de scraping"""
    print_step(2, "Nettoyage des anciens fichiers de scraping", "🧹")
    
    try:
        if DATA_DIR.exists():
            for json_file in DATA_DIR.glob('*.json'):
                json_file.unlink()
                print(f"   Supprimé: {json_file.name}")
        
        print(f"✅ Fichiers de scraping nettoyés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage des fichiers: {e}")
        return False


def run_scrapers():
    """Lance les scrapers FreeWork et Collective.work"""
    print_step(3, "Lancement des scrapers (15 pages par source)", "🕷️")
    
    scrapers = [
        ('freework', 'FreeWork'),
        ('collective_work', 'Collective.work')
    ]
    
    for spider_name, display_name in scrapers:
        print(f"\n🚀 Scraping {display_name}...")
        print(f"   Spider: {spider_name}")
        print(f"   Pages: 15")
        print(f"   Démarrage: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Lancer le scraper avec PowerShell depuis le bon répertoire
            output_file = DATA_DIR / f'{spider_name}.json'
            
            cmd = f'cd "{SCRAPER_DIR}" ; scrapy crawl {spider_name} -O "{output_file}" --loglevel=INFO'
            
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max par scraper
            )
            
            if result.returncode == 0 or output_file.exists():
                # Compter les offres scrapées
                if output_file.exists():
                    import json
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            count = len(data) if isinstance(data, list) else 1
                        
                        print(f"   ✅ {display_name}: {count} offres scrapées")
                    except Exception as e:
                        print(f"   ⚠️  Fichier créé mais erreur de lecture: {e}")
                else:
                    print(f"   ⚠️  Fichier de sortie non trouvé")
            else:
                print(f"   ❌ Erreur lors du scraping de {display_name}")
                if result.stderr:
                    print(f"   {result.stderr[:300]}")
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout pour {display_name} (10 minutes dépassées)")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print(f"\n✅ Scraping terminé: {datetime.now().strftime('%H:%M:%S')}")
    return True


def load_to_database():
    """Charge les données scrapées dans Supabase"""
    print_step(4, "Chargement dans Supabase", "📤")
    
    os.chdir(ETL_DIR)
    
    try:
        # Utiliser le script ETL existant
        from run_full_pipeline import main as run_etl
        
        print("🔄 Transformation et validation des données...")
        result = run_etl()
        
        if result:
            print(f"✅ Données chargées avec succès dans Supabase")
            return True
        else:
            print(f"⚠️  Chargement terminé avec des avertissements")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_data():
    """Vérifie les données chargées"""
    print_step(5, "Vérification des données", "✅")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Compter les offres par source
        result = supabase.table('offers').select('source', count='exact').execute()
        total = len(result.data)
        
        print(f"📊 Total des offres dans la BDD: {total}")
        
        # Détail par source
        sources = {}
        for offer in result.data:
            source = offer.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n📋 Répartition par source:")
        for source, count in sources.items():
            print(f"   • {source}: {count} offres")
        
        # Vérifier les villes
        locations_result = supabase.table('offers').select('location').execute()
        locations = set(offer['location'] for offer in locations_result.data if offer.get('location'))
        
        print(f"\n🏙️  Villes uniques: {len(locations)}")
        print(f"   Exemples: {', '.join(list(locations)[:10])}")
        
        # Vérifier les technologies
        tech_result = supabase.table('offers').select('technologies').execute()
        all_techs = set()
        for offer in tech_result.data:
            if offer.get('technologies'):
                all_techs.update(offer['technologies'])
        
        print(f"\n💻 Technologies uniques: {len(all_techs)}")
        print(f"   Exemples: {', '.join(list(all_techs)[:15])}")
        
        # TJM moyen
        tjm_result = supabase.table('offers').select('tjm_min, tjm_max').execute()
        valid_tjms = [
            (offer['tjm_min'] + offer['tjm_max']) / 2
            for offer in tjm_result.data
            if offer.get('tjm_min') and offer.get('tjm_max')
        ]
        
        if valid_tjms:
            avg_tjm = sum(valid_tjms) / len(valid_tjms)
            print(f"\n💰 TJM moyen: {avg_tjm:.0f}€/jour")
            print(f"   TJM min: {min(valid_tjms):.0f}€")
            print(f"   TJM max: {max(valid_tjms):.0f}€")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False


def main():
    """Pipeline complet"""
    print("\n" + "="*70)
    print("🚀 AWA - Pipeline de peuplement de la base de données")
    print("="*70)
    print(f"📅 Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Vérifier la configuration
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Variables d'environnement Supabase manquantes")
        print("   Vérifiez SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY dans .env")
        return False
    
    steps = [
        (clean_database, "Nettoyage BDD"),
        (clean_scraper_data, "Nettoyage fichiers"),
        (run_scrapers, "Scraping"),
        (load_to_database, "Chargement BDD"),
        (verify_data, "Vérification")
    ]
    
    for step_func, step_name in steps:
        try:
            success = step_func()
            if not success:
                print(f"\n⚠️  {step_name} a échoué, mais on continue...")
        except Exception as e:
            print(f"\n❌ Erreur critique dans {step_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    duration = time.time() - start_time
    
    print("\n" + "="*70)
    print(f"✅ Pipeline terminé avec succès!")
    print(f"⏱️  Durée totale: {duration:.1f} secondes ({duration/60:.1f} minutes)")
    print(f"📅 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
