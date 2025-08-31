"""
Script d'analyse des données scrapées
"""
import json
import pandas as pd
from pathlib import Path
from date    print("\n" + "="*60)
    print("TECHNOLOGY ANALYSIS")
    print("="*60)e import datetime
import argparse


def analyze_scraped_data(data_file: Path):
    """Analyse les données scrapées"""
    print(f"Analysis of file: {data_file}")
    
    # Charger les données
    if data_file.suffix == '.json':
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif data_file.suffix == '.jsonl':
        data = []
        with open(data_file, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line.strip()))
    else:
        print("ERROR: Unsupported file format")
        return
    
    if not data:
        print("ERROR: No data found")
        return
    
    print(f"Total offers: {len(data)}")
    
    # Analyser la qualité
    analyze_quality(data)
    
    # Analyser les TJM
    analyze_tjm(data)
    
    # Analyser les technologies
    analyze_technologies(data)
    
    # Analyser les localisations
    analyze_locations(data)
    
    # Analyser les entreprises
    analyze_companies(data)


def analyze_quality(data):
    """Analyse la qualité des données"""
    print("\n" + "="*50)
    print("QUALITY ANALYSIS")
    print("="*50)
    
    quality_scores = [item.get('quality_score', 0) for item in data]
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        high_quality = len([s for s in quality_scores if s > 0.7])
        medium_quality = len([s for s in quality_scores if 0.4 <= s <= 0.7])
        low_quality = len([s for s in quality_scores if s < 0.4])
        
        print(f"Score moyen: {avg_quality:.3f}")
        print(f"Haute qualité (>0.7): {high_quality}/{len(data)} ({high_quality/len(data)*100:.1f}%)")
        print(f"Qualité moyenne (0.4-0.7): {medium_quality}/{len(data)} ({medium_quality/len(data)*100:.1f}%)")
        print(f"Faible qualité (<0.4): {low_quality}/{len(data)} ({low_quality/len(data)*100:.1f}%)")
    
    # Analyser la complétude des champs
    fields = ['title', 'description', 'company', 'location', 'tjm_min', 'tjm_max', 'technologies']
    
    print(f"\nField completeness:")
    for field in fields:
        count = len([item for item in data if item.get(field)])
        percentage = count / len(data) * 100
        print(f"{field}: {count}/{len(data)} ({percentage:.1f}%)")


def analyze_tjm(data):
    """Analyse les TJM"""
    print("\n" + "="*50)
    print("TJM ANALYSIS")
    print("="*50)
    
    tjm_values = []
    for item in data:
        if item.get('tjm_min'):
            tjm_values.append(item['tjm_min'])
        if item.get('tjm_max'):
            tjm_values.append(item['tjm_max'])
    
    if tjm_values:
        print(f"Total de valeurs TJM: {len(tjm_values)}")
        print(f"TJM minimum: {min(tjm_values)}€")
        print(f"TJM maximum: {max(tjm_values)}€")
        print(f"TJM moyen: {sum(tjm_values)/len(tjm_values):.2f}€")
        
        # Distribution par tranches
        ranges = [
            (0, 300, "Débutant"),
            (300, 500, "Intermédiaire"),
            (500, 700, "Senior"),
            (700, 1000, "Expert"),
            (1000, float('inf'), "Premium")
        ]
        
        print(f"\nDistribution by ranges:")
        for min_val, max_val, label in ranges:
            count = len([v for v in tjm_values if min_val <= v < max_val])
            percentage = count / len(tjm_values) * 100
            print(f"{label} ({min_val}-{max_val if max_val != float('inf') else ''}€): {count} ({percentage:.1f}%)")
    
    else:
        print("ERROR: No TJM data found")


def analyze_technologies(data):
    """Analyse les technologies"""
    print("\n" + "="*50)
    print("TECHNOLOGY ANALYSIS")
    print("="*50)
    
    tech_count = {}
    for item in data:
        technologies = item.get('technologies', [])
        for tech in technologies:
            tech_count[tech] = tech_count.get(tech, 0) + 1
    
    if tech_count:
        sorted_techs = sorted(tech_count.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Technologies uniques: {len(tech_count)}")
        print(f"\nTop 10 technologies:")
        for i, (tech, count) in enumerate(sorted_techs[:10], 1):
            percentage = count / len(data) * 100
            print(f"{i:2d}. {tech}: {count} offers ({percentage:.1f}%)")
    else:
        print("ERROR: No technology data found")


def analyze_locations(data):
    """Analyse les localisations"""
    print("\n" + "="*50)
    print("LOCATION ANALYSIS")
    print("="*50)
    
    location_count = {}
    for item in data:
        city = item.get('city') or item.get('location')
        if city:
            location_count[city] = location_count.get(city, 0) + 1
    
    if location_count:
        sorted_locations = sorted(location_count.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Unique locations: {len(location_count)}")
        print(f"\nTop 10 cities:")
        for i, (city, count) in enumerate(sorted_locations[:10], 1):
            percentage = count / len(data) * 100
            print(f"{i:2d}. {city}: {count} offers ({percentage:.1f}%)")
    else:
        print("ERROR: No location data found")


def analyze_companies(data):
    """Analyse les entreprises"""
    print("\n" + "="*50)
    print("COMPANY ANALYSIS")
    print("="*50)
    
    company_count = {}
    for item in data:
        company = item.get('company')
        if company:
            company_count[company] = company_count.get(company, 0) + 1
    
    if company_count:
        sorted_companies = sorted(company_count.items(), key=lambda x: x[1], reverse=True)
        
        print(f"Unique companies: {len(company_count)}")
        print(f"\nTop 10 companies:")
        for i, (company, count) in enumerate(sorted_companies[:10], 1):
            percentage = count / len(data) * 100
            print(f"{i:2d}. {company}: {count} offers ({percentage:.1f}%)")
    else:
        print("ERROR: No company data found")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Analyseur de données TJM')
    parser.add_argument('file', help='Fichier de données à analyser (.json ou .jsonl)')
    
    args = parser.parse_args()
    
    data_file = Path(args.file)
    
    if not data_file.exists():
        print(f"❌ Fichier non trouvé: {data_file}")
        return 1
    
    analyze_scraped_data(data_file)
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
