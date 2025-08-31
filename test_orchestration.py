#!/usr/bin/env python3
"""
Test de l'orchestration complète AWA
Simule le cycle de vie complet : Scraper -> ETL -> Vérification DB
"""

import requests
import time
import json
from pathlib import Path

def test_scraper_api():
    """Test de l'API Scraper"""
    print("🔍 Test de l'API Scraper...")
    
    try:
        # Health check
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health check OK")
            return True
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connexion échouée: {e}")
        return False

def test_etl_api():
    """Test de l'API ETL"""
    print("🔍 Test de l'API ETL...")
    
    try:
        # Health check
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health check OK")
            return True
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connexion échouée: {e}")
        return False

def trigger_scraper():
    """Déclenche le scraper via API"""
    print("🕷️  Déclenchement du scraper...")
    
    try:
        payload = {"spider": "freework"}
        response = requests.post(
            "http://localhost:8000/api/scrape",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Scraper démarré: {result['message']}")
            print(f"  📄 Fichier de sortie: {result.get('output_file', 'N/A')}")
            return True
        else:
            print(f"  ❌ Échec du scraper: {response.status_code}")
            print(f"  📄 Erreur: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erreur réseau: {e}")
        return False

def trigger_etl():
    """Déclenche l'ETL via API"""
    print("⚙️  Déclenchement de l'ETL...")
    
    try:
        payload = {"file_pattern": "*.jsonl"}
        response = requests.post(
            "http://localhost:8001/api/process",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ ETL terminé: {result['message']}")
            print(f"  📊 Records traités: {result.get('processed_count', 0)}")
            print(f"  📈 Records chargés: {result.get('loaded_count', 0)}")
            print(f"  ⏱️  Durée: {result.get('duration', 0):.2f}s")
            return True
        else:
            print(f"  ❌ Échec de l'ETL: {response.status_code}")
            print(f"  📄 Erreur: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erreur réseau: {e}")
        return False

def check_database():
    """Vérifie les données en base"""
    print("🗄️  Vérification de la base de données...")
    
    try:
        import os
        from dotenv import load_dotenv
        from supabase import create_client
        
        # Charger config
        load_dotenv("../.env.shared")
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("  ❌ Configuration Supabase manquante")
            return False
            
        # Connexion Supabase
        client = create_client(url, key)
        result = client.table('offers').select('*', count='exact').execute()
        
        print(f"  ✅ Total offres en base: {result.count}")
        
        # Afficher les dernières offres
        if result.data and len(result.data) > 0:
            latest = result.data[0]
            print(f"  📋 Dernière offre: {latest.get('title', 'N/A')} - {latest.get('company', 'N/A')}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur base de données: {e}")
        return False

def main():
    """Test complet de l'orchestration"""
    print("🎯 Test de l'orchestration complète AWA")
    print("=" * 50)
    
    # 1. Vérifier les APIs
    scraper_ok = test_scraper_api()
    etl_ok = test_etl_api()
    
    if not scraper_ok:
        print("\n❌ API Scraper non disponible")
        print("   Démarrer avec: cd services/scraper && python -m uvicorn api:app --port 8000")
        return
        
    if not etl_ok:
        print("\n❌ API ETL non disponible")
        print("   Démarrer avec: cd services/etl && python -m uvicorn api:app --port 8001")
        return
    
    print("\n✅ Toutes les APIs sont disponibles!")
    
    # 2. Test du cycle complet
    print("\n🔄 Démarrage du cycle complet...")
    
    # Scraping
    if trigger_scraper():
        print("  ⏳ Attente du scraping (10s)...")
        time.sleep(10)
        
        # ETL
        if trigger_etl():
            print("  ⏳ Attente du traitement (5s)...")
            time.sleep(5)
            
            # Vérification DB
            check_database()
            
            print("\n🎉 Test d'orchestration terminé!")
        else:
            print("\n❌ Échec de l'ETL")
    else:
        print("\n❌ Échec du scraper")

if __name__ == "__main__":
    main()
