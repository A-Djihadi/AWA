#!/usr/bin/env python3
"""
Générateur de données réalistes basé sur les vraies offres existantes
Crée des variations réalistes pour peupler la BDD
"""

import os
import sys
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

# Configuration
ETL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ETL_DIR))

# Charger le .env depuis le dossier ETL
env_path = ETL_DIR / '.env'
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"🔧 Configuration:")
print(f"   ETL Dir: {ETL_DIR}")
print(f"   .env: {env_path}")
print(f"   Supabase URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "   ❌ Supabase URL non trouvée")

# Données réalistes françaises
CITIES = [
    'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 
    'Strasbourg', 'Montpellier', 'Bordeaux', 'Lille', 'Rennes',
    'Reims', 'Grenoble', 'Dijon', 'Angers', 'Saint-Étienne',
    'Toulon', 'Le Havre', 'Remote', 'Île-de-France'
]

TECHNOLOGIES = [
    'React', 'Angular', 'Vue.js', 'Node.js', 'Python', 'Django', 'Flask',
    'Java', 'Spring Boot', 'PHP', 'Laravel', 'Symfony', '.NET', 'C#',
    'TypeScript', 'JavaScript', 'PostgreSQL', 'MongoDB', 'MySQL', 'Redis',
    'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'CI/CD',
    'Terraform', 'Ansible', 'Jenkins', 'GraphQL', 'REST API', 'Microservices',
    'React Native', 'Flutter', 'Swift', 'Kotlin', 'Go', 'Rust', 'Scala'
]

COMPANIES = [
    'TechCorp', 'InnovSoft', 'DataFlow', 'CloudNexus', 'DevMasters',
    'CodeFactory', 'Digital Partners', 'IT Solutions', 'WebExperts',
    'SoftwareLab', 'TechHub', 'DevOps Pro', 'Cloud Services', 'DataTech',
    'Innovation Labs', 'Agile Solutions', 'Smart Systems', 'Tech Innovators',
    'Digital Factory', 'IT Consulting', 'Software Partners', 'Tech Advisory'
]

JOB_TITLES = [
    'Développeur Full Stack {tech}',
    'Architecte Solutions {tech}',
    'Lead Developer {tech}',
    'Ingénieur DevOps',
    'Consultant Technique {tech}',
    'Expert {tech} Senior',
    'Tech Lead {tech}',
    'Développeur Backend {tech}',
    'Développeur Frontend {tech}',
    'Ingénieur Cloud {tech}',
    'Data Engineer {tech}',
    'Software Engineer {tech}',
    'Architecte {tech}',
    'Développeur Mobile {tech}',
    'DevOps Engineer',
    'SRE Engineer',
    'Platform Engineer',
    'Solution Architect',
    'Technical Lead {tech}',
    'Senior Developer {tech}'
]

# Valeurs conformes au schéma Supabase
SENIORITY_LEVELS = ['junior', 'senior']  # Valeurs autorisées dans le schéma
REMOTE_POLICIES = ['remote', 'hybrid']  # Valeurs autorisées
CONTRACT_TYPES = ['freelance']  # Seule valeur autorisée

def generate_realistic_offers(base_offers, count=200):
    """Génère des offres réalistes basées sur les vraies offres"""
    print(f"\n📊 Génération de {count} offres réalistes...")
    
    generated_offers = []
    
    for i in range(count):
        # Choisir une vraie offre comme modèle
        if base_offers:
            base_offer = random.choice(base_offers)
            base_techs = base_offer.get('technologies', [])
        else:
            base_techs = []
        
        # Technologies (mélange de réelles et nouvelles)
        num_techs = random.randint(3, 7)
        if base_techs and len(base_techs) >= 2:
            techs = random.sample(base_techs, min(2, len(base_techs)))
            techs.extend(random.sample(TECHNOLOGIES, num_techs - len(techs)))
        else:
            techs = random.sample(TECHNOLOGIES, num_techs)
        
        # Choisir tech principale pour le titre
        main_tech = random.choice(techs)
        
        # Titre
        title_template = random.choice(JOB_TITLES)
        title = title_template.format(tech=main_tech)
        
        # TJM basé sur la séniorité
        seniority = random.choice(SENIORITY_LEVELS)
        if seniority == 'junior':
            tjm_base = random.randint(350, 500)
        else:  # senior
            tjm_base = random.randint(500, 800)
        
        tjm_min = tjm_base
        tjm_max = tjm_base + random.randint(50, 150)
        
        # Ville
        location = random.choice(CITIES)
        
        # Remote policy basé sur la ville
        if location == 'Remote':
            remote_policy = 'remote'
        else:
            remote_policy = random.choice(REMOTE_POLICIES)
        
        # Company
        company = random.choice(COMPANIES)
        
        # Source alternée
        source = random.choice(['freework', 'collective_work'])
        
        # Description
        description = f"Mission {seniority} en {location}. Technologies: {', '.join(techs[:5])}. "
        description += f"Contexte: projet innovant nécessitant une expertise en {main_tech}. "
        description += f"Environnement: {remote_policy.replace('_', ' ')}."
        
        # Date de scraping variée (dernières 2 semaines)
        days_ago = random.randint(0, 14)
        scraped_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        offer = {
            'source': source,
            'source_id': f"{source}_{i+1000}_{random.randint(1000, 9999)}",
            'url': f"https://{source.replace('_', '-')}.com/mission/{i+1000}",
            'title': title,
            'company': company,
            'location': location,
            'tjm_min': tjm_min,
            'tjm_max': tjm_max,
            'tjm_currency': 'EUR',
            'technologies': techs,
            'seniority_level': seniority,
            'remote_policy': remote_policy,
            'contract_type': random.choice(CONTRACT_TYPES),
            'description': description,
            'scraped_at': scraped_at
        }
        
        generated_offers.append(offer)
    
    return generated_offers


def main():
    """Génère et charge des données réalistes"""
    print("\n" + "="*70)
    print("🎲 Générateur de données réalistes AWA")
    print("="*70 + "\n")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Récupérer les vraies offres existantes
        print("📥 Récupération des vraies offres existantes...")
        result = supabase.table('offers').select('*').execute()
        base_offers = result.data
        
        print(f"✅ {len(base_offers)} offres existantes trouvées")
        print(f"   Sources: {set(o['source'] for o in base_offers)}")
        
        # Demander le nombre d'offres à générer
        try:
            count = int(input(f"\n💭 Combien d'offres générer ? [200]: ") or "200")
        except:
            count = 200
        
        # Générer les offres
        generated_offers = generate_realistic_offers(base_offers, count)
        
        # Charger dans Supabase par batch
        print(f"\n📤 Chargement de {len(generated_offers)} offres...")
        
        batch_size = 50
        success_count = 0
        
        for i in range(0, len(generated_offers), batch_size):
            batch = generated_offers[i:i+batch_size]
            
            try:
                supabase.table('offers').insert(batch).execute()
                success_count += len(batch)
                print(f"   ✅ Batch {i//batch_size + 1}: {len(batch)} offres")
            except Exception as e:
                print(f"   ❌ Erreur batch {i//batch_size + 1}: {e}")
        
        # Statistiques finales
        print(f"\n{'='*70}")
        print(f"✅ {success_count}/{len(generated_offers)} offres chargées")
        print(f"{'='*70}\n")
        
        # Vérification
        result = supabase.table('offers').select('source', count='exact').execute()
        total = len(result.data)
        
        sources = {}
        for offer in result.data:
            source = offer.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("📊 Statistiques finales:")
        print(f"   Total: {total} offres")
        print("\n   Par source:")
        for source, count in sorted(sources.items()):
            print(f"      • {source}: {count}")
        
        # Villes
        locations = supabase.table('offers').select('location').execute()
        unique_locations = set(o['location'] for o in locations.data if o.get('location'))
        print(f"\n   Villes: {len(unique_locations)}")
        
        # Technologies
        techs = supabase.table('offers').select('technologies').execute()
        all_techs = set()
        for offer in techs.data:
            if offer.get('technologies'):
                all_techs.update(offer['technologies'])
        print(f"   Technologies: {len(all_techs)}")
        
        # TJM moyen
        tjms = supabase.table('offers').select('tjm_min, tjm_max').execute()
        valid_tjms = [
            (o['tjm_min'] + o['tjm_max']) / 2
            for o in tjms.data
            if o.get('tjm_min') and o.get('tjm_max')
        ]
        
        if valid_tjms:
            avg_tjm = sum(valid_tjms) / len(valid_tjms)
            print(f"   TJM moyen: {avg_tjm:.0f}€/jour")
        
        print(f"\n{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
