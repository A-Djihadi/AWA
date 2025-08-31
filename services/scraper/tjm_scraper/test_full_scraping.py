#!/usr/bin/env python3
"""
Test complet du spider avec une vraie session de scraping
Teste à la fois la découverte d'offres et l'extraction de données
"""

import sys
import json
import requests
from datetime import datetime
import time

# Import du spider
sys.path.append('.')
from spiders.freework import FreeWorkSpider

class FullScrapingTest:
    def __init__(self):
        self.spider = FreeWorkSpider()
        
    def run_full_scraping_test(self):
        """Test complet du processus de scraping"""
        print("🚀 TEST COMPLET DE SCRAPING FREEWORK")
        print("=" * 60)
        print("Test du processus complet: découverte + extraction")
        print()
        
        # 1. Test de la page de listing
        print("📋 ÉTAPE 1: Test de la page de listing")
        print("-" * 40)
        
        listing_url = "https://www.free-work.com/fr/tech-it/jobs?locations=fr~~~&contracts=contractor"
        listing_result = self._test_listing_page(listing_url)
        
        if not listing_result['success']:
            print("❌ Échec du test de listing, arrêt du test")
            return
        
        print(f"✅ Découverte: {listing_result['job_count']} offres trouvées")
        print()
        
        # 2. Test d'extraction sur un échantillon
        print("📊 ÉTAPE 2: Test d'extraction sur échantillon")
        print("-" * 40)
        
        sample_urls = listing_result['job_urls'][:3]  # Prendre 3 exemples
        extraction_results = []
        
        for i, url in enumerate(sample_urls, 1):
            print(f"\n🎯 Test {i}/3: {url}")
            
            result = self._test_job_extraction(url)
            extraction_results.append(result)
            
            # Affichage rapide
            if result['success']:
                tech_count = len(result['data'].get('technologies', []))
                print(f"  ✅ Extraction réussie - {tech_count} technologies")
            else:
                print(f"  ❌ Échec: {result.get('error', 'Erreur inconnue')}")
            
            # Pause pour éviter la surcharge
            time.sleep(2)
        
        # 3. Analyse des résultats
        print("\n" + "=" * 60)
        print("📈 ANALYSE DES RÉSULTATS")
        print("=" * 60)
        
        self._analyze_full_results(listing_result, extraction_results)
    
    def _test_listing_page(self, url):
        """Teste la découverte d'offres sur la page de listing"""
        result = {
            'success': False,
            'job_urls': [],
            'job_count': 0,
            'error': None
        }
        
        try:
            # Télécharger la page
            response = requests.get(url, headers={
                'User-Agent': 'AWA-FreeWork-Scraper/1.0'
            }, timeout=15)
            response.raise_for_status()
            
            # Créer mock response
            mock_response = MockResponse(response.text, url)
            
            # Simuler la méthode parse du spider
            job_links = self._extract_job_links(response.text)
            
            if job_links:
                result['success'] = True
                result['job_urls'] = job_links
                result['job_count'] = len(job_links)
            else:
                result['error'] = "Aucun lien d'offre trouvé"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _extract_job_links(self, html_content):
        """Extrait les liens d'offres depuis une page de listing"""
        import re
        from urllib.parse import urljoin
        
        # Rechercher les liens de missions
        patterns = [
            r'href="([^"]*job-mission[^"]*)"',
            r'href="([^"]*fr/tech-it/[^"]*job[^"]*)"'
        ]
        
        all_links = []
        base_url = "https://www.free-work.com"
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if match.startswith('/'):
                    full_url = base_url + match
                elif match.startswith('http'):
                    full_url = match
                else:
                    full_url = base_url + '/' + match
                
                if 'job-mission' in full_url and full_url not in all_links:
                    all_links.append(full_url)
        
        return all_links[:10]  # Limiter à 10 pour le test
    
    def _test_job_extraction(self, job_url):
        """Teste l'extraction de données d'une offre spécifique"""
        result = {
            'success': False,
            'url': job_url,
            'data': {},
            'error': None
        }
        
        try:
            # Télécharger la page
            response = requests.get(job_url, headers={
                'User-Agent': 'AWA-FreeWork-Scraper/1.0'
            }, timeout=15)
            response.raise_for_status()
            
            # Créer mock response
            mock_response = MockResponse(response.text, job_url)
            
            # Extraire les données avec le spider
            source_id = self.spider.extract_source_id(job_url)
            title = self.spider.extract_title(mock_response)
            tjm_min, tjm_max = self.spider.extract_tjm(mock_response)
            company = self.spider.extract_company(mock_response)
            technologies = self.spider.extract_technologies(mock_response)
            location = self.spider.extract_location(mock_response)
            
            # Construire les données
            job_data = {
                'source': 'freework',
                'source_id': source_id,
                'title': title,
                'company': company,
                'tjm_min': tjm_min,
                'tjm_max': tjm_max,
                'tjm_currency': 'EUR',
                'technologies': technologies,
                'location': location,
                'url': job_url,
                'scraped_at': datetime.now().isoformat()
            }
            
            result['success'] = True
            result['data'] = job_data
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _analyze_full_results(self, listing_result, extraction_results):
        """Analyse les résultats du test complet"""
        
        # Statistiques de découverte
        print(f"🔍 DÉCOUVERTE D'OFFRES:")
        print(f"  • URLs découvertes: {listing_result['job_count']}")
        print(f"  • Statut: {'✅ Succès' if listing_result['success'] else '❌ Échec'}")
        
        if not listing_result['success']:
            print(f"  • Erreur: {listing_result.get('error')}")
            return
        
        # Statistiques d'extraction
        successful_extractions = [r for r in extraction_results if r['success']]
        success_rate = len(successful_extractions) / len(extraction_results) * 100 if extraction_results else 0
        
        print(f"\n📊 EXTRACTION DE DONNÉES:")
        print(f"  • Tests d'extraction: {len(extraction_results)}")
        print(f"  • Réussis: {len(successful_extractions)}")
        print(f"  • Taux de réussite: {success_rate:.1f}%")
        
        if not successful_extractions:
            print("  ❌ Aucune extraction réussie")
            return
        
        # Analyse des champs extraits
        print(f"\n🔧 QUALITÉ DES EXTRACTIONS:")
        
        field_stats = {}
        for result in successful_extractions:
            data = result['data']
            for field, value in data.items():
                if field not in field_stats:
                    field_stats[field] = {'total': 0, 'filled': 0}
                
                field_stats[field]['total'] += 1
                if value is not None and value != '' and value != []:
                    field_stats[field]['filled'] += 1
        
        for field, stats in field_stats.items():
            fill_rate = (stats['filled'] / stats['total']) * 100 if stats['total'] > 0 else 0
            status = "✅" if fill_rate >= 80 else "⚠️" if fill_rate >= 50 else "❌"
            print(f"  {field:15}: {stats['filled']}/{stats['total']} ({fill_rate:.1f}%) {status}")
        
        # Analyse spécifique des technologies
        print(f"\n⚙️ ANALYSE DES TECHNOLOGIES:")
        all_technologies = []
        tech_by_job = []
        
        for result in successful_extractions:
            technologies = result['data'].get('technologies', [])
            all_technologies.extend(technologies)
            tech_by_job.append(technologies)
        
        if all_technologies:
            unique_tech = list(set(all_technologies))
            print(f"  • Technologies trouvées: {len(all_technologies)} total")
            print(f"  • Technologies uniques: {len(unique_tech)}")
            print(f"  • Diversité: {unique_tech}")
            
            # Vérifier les doublons
            duplicate_jobs = 0
            for i in range(len(tech_by_job)):
                for j in range(i + 1, len(tech_by_job)):
                    if tech_by_job[i] == tech_by_job[j] and len(tech_by_job[i]) > 0:
                        duplicate_jobs += 1
            
            if duplicate_jobs == 0:
                print(f"  ✅ Aucun doublon détecté - extraction contextuelle!")
            else:
                print(f"  ⚠️ {duplicate_jobs} paires de doublons détectées")
        else:
            print(f"  ⚠️ Aucune technologie extraite")
        
        # Score global et recommandations
        print(f"\n🏆 ÉVALUATION GLOBALE:")
        
        discovery_score = 100 if listing_result['success'] else 0
        extraction_score = success_rate
        
        # Score de qualité des données
        data_quality_scores = []
        for field, stats in field_stats.items():
            if field not in ['scraped_at', 'source']:  # Exclure les métadonnées
                fill_rate = (stats['filled'] / stats['total']) * 100 if stats['total'] > 0 else 0
                data_quality_scores.append(fill_rate)
        
        avg_data_quality = sum(data_quality_scores) / len(data_quality_scores) if data_quality_scores else 0
        
        global_score = (discovery_score * 0.3 + extraction_score * 0.3 + avg_data_quality * 0.4)
        
        print(f"  • Découverte: {discovery_score:.1f}%")
        print(f"  • Extraction: {extraction_score:.1f}%")
        print(f"  • Qualité données: {avg_data_quality:.1f}%")
        print(f"  • Score global: {global_score:.1f}%")
        
        # Verdict final
        if global_score >= 85:
            print("\n✅ EXCELLENT - Spider prêt pour la production")
        elif global_score >= 70:
            print("\n👍 BON - Spider fonctionnel avec quelques améliorations possibles")
        elif global_score >= 50:
            print("\n⚠️ MOYEN - Spider nécessite des améliorations")
        else:
            print("\n❌ FAIBLE - Spider nécessite des corrections importantes")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        
        if discovery_score < 100:
            print("  • Améliorer la découverte d'offres sur la page de listing")
        
        if extraction_score < 80:
            print("  • Améliorer la robustesse de l'extraction (gestion d'erreurs)")
        
        low_quality_fields = [field for field, stats in field_stats.items() 
                             if (stats['filled'] / stats['total']) * 100 < 70]
        if low_quality_fields:
            print(f"  • Améliorer l'extraction de: {', '.join(low_quality_fields)}")
        
        if len(unique_tech) < 3 and all_technologies:
            print("  • Enrichir l'extraction des technologies")


class MockResponse:
    """Mock pour simuler une réponse Scrapy"""
    def __init__(self, html_content, url):
        self.text = html_content
        self.url = url
        
    def css(self, selector):
        return MockSelector(self.text, selector)


class MockSelector:
    """Mock pour les sélecteurs CSS"""
    def __init__(self, html_text, selector):
        self.html_text = html_text
        self.selector = selector
        
    def get(self):
        results = self.getall()
        return results[0] if results else None
        
    def getall(self):
        import re
        
        # Titre h1
        if self.selector == 'h1::text':
            matches = re.findall(r'<h1[^>]*>(.*?)</h1>', self.html_text, re.DOTALL)
            return [re.sub(r'<[^>]+>', '', match).strip() for match in matches]
        
        # Meta OG title
        if 'meta[property="og:title"]' in self.selector and '::attr(content)' in self.selector:
            matches = re.findall(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', self.html_text)
            return matches
        
        # Meta description
        if 'meta[name="description"]' in self.selector and '::attr(content)' in self.selector:
            matches = re.findall(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', self.html_text)
            return matches
        
        # Scripts JSON-LD
        if 'script[type="application/ld+json"]' in self.selector:
            matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', 
                                self.html_text, re.DOTALL)
            return [match.strip() for match in matches]
        
        # Contenu par classe
        if '[class*="content"]' in self.selector:
            matches = re.findall(r'<[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</[^>]*>', 
                                self.html_text, re.DOTALL)
            if '::text' in self.selector:
                return [re.sub(r'<[^>]+>', '', match).strip() for match in matches]
            return matches
        
        return []


if __name__ == "__main__":
    tester = FullScrapingTest()
    tester.run_full_scraping_test()
