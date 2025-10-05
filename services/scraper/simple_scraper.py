#!/usr/bin/env python3
"""
Scraper alternatif utilisant requests et BeautifulSoup
Compatible Python 3.13
"""

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

# Paths
SCRAPER_DIR = Path(__file__).parent
DATA_DIR = SCRAPER_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def scrape_freework(num_pages=15):
    """Scrape FreeWork missions"""
    print(f"\n{'='*70}")
    print(f"🕷️  Scraping FreeWork ({num_pages} pages)")
    print(f"{'='*70}\n")
    
    all_offers = []
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    
    for page in range(1, num_pages + 1):
        print(f"📄 Page {page}/{num_pages}...", end=' ')
        
        url = f'https://www.free-work.com/fr/tech-it/jobs?page={page}&locations=fr~~~&contracts=contractor'
        
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver les liens de missions
            mission_links = soup.find_all('a', href=re.compile(r'/fr/tech-it/job-mission/'))
            
            print(f"Trouvé {len(mission_links)} liens", end=' ')
            
            for link in mission_links[:20]:  # Max 20 par page
                mission_url = urljoin(url, link.get('href'))
                
                # Extraire l'offre
                offer = scrape_freework_mission(session, mission_url)
                if offer:
                    all_offers.append(offer)
            
            print(f"✅ ({len(all_offers)} total)")
            time.sleep(2)  # Respecter le rate limiting
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            continue
    
    return all_offers


def scrape_freework_mission(session, url):
    """Scrape une mission FreeWork spécifique"""
    try:
        response = session.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraire les informations
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else None
        
        if not title:
            return None
        
        # Extraire l'ID
        source_id = url.split('/')[-1].split('?')[0]
        
        # Extraire le TJM
        text_content = soup.get_text()
        tjm_min, tjm_max = extract_tjm(text_content)
        
        # Extraire company, location, etc.
        company = extract_text(soup, ['company', 'employer'])
        location = extract_text(soup, ['location', 'city', 'lieu'])
        
        # Technologies
        tech_tags = soup.find_all(class_=re.compile(r'skill|tech|tag'))
        technologies = [tag.text.strip() for tag in tech_tags[:10] if tag.text.strip()]
        
        # Description
        desc_tag = soup.find(class_=re.compile(r'description|content'))
        description = desc_tag.text.strip()[:500] if desc_tag else ""
        
        return {
            'source': 'freework',
            'source_id': source_id,
            'url': url,
            'title': title,
            'company': company or 'N/A',
            'location': location or 'Remote',
            'tjm_min': tjm_min,
            'tjm_max': tjm_max,
            'tjm_currency': 'EUR',
            'technologies': technologies,
            'description': description,
            'scraped_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"\n   ⚠️  Erreur mission: {e}")
        return None


def scrape_collective_work(num_pages=15):
    """Scrape Collective.work missions"""
    print(f"\n{'='*70}")
    print(f"🕷️  Scraping Collective.work ({num_pages} pages)")
    print(f"{'='*70}\n")
    
    all_offers = []
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    
    for page in range(1, num_pages + 1):
        print(f"📄 Page {page}/{num_pages}...", end=' ')
        
        url = f'https://www.collective.work/job?page={page}'
        
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver les cards de job
            job_cards = soup.find_all(class_=re.compile(r'job|card|offer'))
            
            print(f"Trouvé {len(job_cards)} cards", end=' ')
            
            for card in job_cards[:30]:
                offer = extract_collective_job(card, url)
                if offer and offer.get('tjm_min'):
                    all_offers.append(offer)
            
            print(f"✅ ({len(all_offers)} total)")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            continue
    
    return all_offers


def extract_collective_job(card, base_url):
    """Extraire les infos d'une card Collective.work"""
    try:
        # Titre
        title_tag = card.find(['h2', 'h3'])
        title = title_tag.text.strip() if title_tag else None
        
        if not title:
            return None
        
        # TJM
        text = card.get_text()
        tjm_min, tjm_max = extract_tjm(text)
        
        if not tjm_min:
            return None
        
        # URL
        link = card.find('a')
        job_url = urljoin(base_url, link.get('href')) if link else base_url
        source_id = job_url.split('/')[-1] if '/' in job_url else str(hash(title))
        
        # Company & Location
        company = extract_text(card, ['company', 'employer']) or 'N/A'
        location = extract_text(card, ['location', 'city']) or 'Remote'
        
        # Technologies
        tech_tags = card.find_all(class_=re.compile(r'skill|tech|tag'))
        technologies = [tag.text.strip() for tag in tech_tags[:10] if tag.text.strip()]
        
        return {
            'source': 'collective_work',
            'source_id': source_id,
            'url': job_url,
            'title': title,
            'company': company,
            'location': location,
            'tjm_min': tjm_min,
            'tjm_max': tjm_max,
            'tjm_currency': 'EUR',
            'technologies': technologies,
            'description': text[:300],
            'scraped_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        return None


def extract_tjm(text):
    """Extraire le TJM depuis du texte"""
    patterns = [
        r'(\d{3,4})\s*[-–]\s*(\d{3,4})\s*€',
        r'(\d{3,4})\s*€\s*[-–]\s*(\d{3,4})\s*€',
        r'tjm[:\s]*(\d{3,4})(?:\s*[-–]\s*(\d{3,4}))?\s*€?',
        r'(\d{3,4})\s*€\s*(?:par\s*jour|\/j)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 2 and groups[1]:
                return int(groups[0]), int(groups[1])
            else:
                tjm = int(groups[0])
                return tjm, tjm
    
    return None, None


def extract_text(soup, class_hints):
    """Extraire du texte avec des hints de classe"""
    for hint in class_hints:
        tag = soup.find(class_=re.compile(hint, re.I))
        if tag:
            return tag.text.strip()
    return None


def main():
    """Main scraping function"""
    print("\n" + "="*70)
    print("🚀 AWA Scraper Alternative (requests + BeautifulSoup)")
    print("="*70)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_offers = []
    
    # Scrape FreeWork
    freework_offers = scrape_freework(num_pages=15)
    all_offers.extend(freework_offers)
    print(f"\n✅ FreeWork: {len(freework_offers)} offres")
    
    # Scrape Collective.work
    collective_offers = scrape_collective_work(num_pages=15)
    all_offers.extend(collective_offers)
    print(f"✅ Collective.work: {len(collective_offers)} offres")
    
    # Sauvegarder
    if all_offers:
        output_file = DATA_DIR / 'scraped_offers.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_offers, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*70}")
        print(f"✅ Total: {len(all_offers)} offres sauvegardées")
        print(f"📁 Fichier: {output_file}")
        print(f"={'='*70}\n")
    else:
        print("\n❌ Aucune offre scrapée")
    
    return len(all_offers) > 0


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
