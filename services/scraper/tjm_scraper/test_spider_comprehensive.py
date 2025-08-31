#!/usr/bin/env python3
"""
Test complet et approfondi du spider FreeWork corrigé
Valide toutes les fonctionnalités d'extraction de données
"""

import sys
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
import re

# Import du spider
sys.path.append('.')
from spiders.freework import FreeWorkSpider

class FreeWorkTester:
    def __init__(self):
        self.spider = FreeWorkSpider()
        self.test_urls = [
            # URLs de test fonctionnelles
            'https://www.free-work.com/fr/tech-it/assistant-chef-de-projet/job-mission/chef-de-projet-erp-h-f-328',
            'https://www.free-work.com/fr/tech-it/ingenieur-devops-cloud/job-mission/architecte-technique-it-azure-devops-f-h',
            'https://www.free-work.com/fr/tech-it/developpeur-autre-langage-cobol-perl-vba-ruby-shell/job-mission/developpeur-c-winform-f-h-2'
        ]
        
    def run_comprehensive_test(self):
        """Exécute un test complet du spider"""
        print("🧪 DÉBUT DU TEST COMPLET DU SPIDER FREEWORK")
        print("=" * 60)
        
        results = []
        
        for i, url in enumerate(self.test_urls, 1):
            print(f"\n📋 TEST {i}/3: {url}")
            print("-" * 50)
            
            try:
                # Télécharger la page
                response = self._get_response(url)
                if not response:
                    print("❌ Impossible de télécharger la page")
                    continue
                
                # Tester toutes les méthodes d'extraction
                result = self._test_all_extractions(response, url)
                results.append(result)
                
                # Afficher les résultats
                self._display_result(result, i)
                
            except Exception as e:
                print(f"❌ Erreur lors du test: {e}")
                continue
        
        # Résumé final
        self._display_summary(results)
        
    def _get_response(self, url):
        """Simule une réponse Scrapy"""
        try:
            response = requests.get(url, headers={
                'User-Agent': 'AWA-FreeWork-Scraper/1.0'
            }, timeout=10)
            response.raise_for_status()
            
            # Créer un objet mock response pour Scrapy
            class MockResponse:
                def __init__(self, response):
                    self.url = response.url
                    self.text = response.text
                    self._response = response
                    
                def css(self, selector):
                    return MockSelector(self.text, selector)
                    
            return MockResponse(response)
        except Exception as e:
            print(f"Erreur de téléchargement: {e}")
            return None
    
    def _test_all_extractions(self, response, url):
        """Teste toutes les méthodes d'extraction"""
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'extractions': {}
        }
        
        # Test de chaque méthode d'extraction
        extraction_methods = [
            ('source_id', self.spider.extract_source_id, url),
            ('title', self.spider.extract_title, response),
            ('tjm', self.spider.extract_tjm, response),
            ('company', self.spider.extract_company, response),
            ('technologies', self.spider.extract_technologies, response),
            ('location', self.spider.extract_location, response),
            ('seniority', self.spider.extract_seniority, response),
            ('remote_policy', self.spider.extract_remote_policy, response),
            ('contract_type', self.spider.extract_contract_type, response),
            ('description', self.spider.extract_description, response)
        ]
        
        for method_name, method, arg in extraction_methods:
            try:
                if method_name == 'tjm':
                    tjm_min, tjm_max = method(arg)
                    result['extractions'][method_name] = {
                        'min': tjm_min,
                        'max': tjm_max,
                        'status': '✅' if tjm_min or tjm_max else '⚠️'
                    }
                else:
                    value = method(arg)
                    result['extractions'][method_name] = {
                        'value': value,
                        'status': '✅' if value else '⚠️'
                    }
            except Exception as e:
                result['extractions'][method_name] = {
                    'value': None,
                    'status': '❌',
                    'error': str(e)
                }
        
        return result
    
    def _display_result(self, result, test_num):
        """Affiche les résultats d'un test"""
        print(f"\n📊 RÉSULTATS DU TEST {test_num}:")
        
        extractions = result['extractions']
        
        # Source ID
        source_id = extractions.get('source_id', {})
        print(f"🆔 Source ID: {source_id.get('status', '❌')} {source_id.get('value', 'N/A')}")
        
        # Titre
        title = extractions.get('title', {})
        print(f"📝 Titre: {title.get('status', '❌')} {title.get('value', 'N/A')}")
        
        # TJM
        tjm = extractions.get('tjm', {})
        tjm_min = tjm.get('min')
        tjm_max = tjm.get('max')
        if tjm_min and tjm_max:
            if tjm_min == tjm_max:
                print(f"💰 TJM: {tjm.get('status', '❌')} {tjm_min}€")
            else:
                print(f"💰 TJM: {tjm.get('status', '❌')} {tjm_min}€ - {tjm_max}€")
        else:
            print(f"💰 TJM: {tjm.get('status', '❌')} Non trouvé")
        
        # Entreprise
        company = extractions.get('company', {})
        print(f"🏢 Entreprise: {company.get('status', '❌')} {company.get('value', 'N/A')}")
        
        # Technologies
        technologies = extractions.get('technologies', {})
        tech_list = technologies.get('value', [])
        print(f"⚙️ Technologies: {technologies.get('status', '❌')} {tech_list} ({len(tech_list)} trouvées)")
        
        # Localisation
        location = extractions.get('location', {})
        print(f"📍 Localisation: {location.get('status', '❌')} {location.get('value', 'N/A')}")
        
        # Séniorité
        seniority = extractions.get('seniority', {})
        print(f"👔 Séniorité: {seniority.get('status', '❌')} {seniority.get('value', 'N/A')}")
        
        # Télétravail
        remote = extractions.get('remote_policy', {})
        print(f"🏠 Télétravail: {remote.get('status', '❌')} {remote.get('value', 'N/A')}")
        
        # Type contrat
        contract = extractions.get('contract_type', {})
        print(f"📄 Contrat: {contract.get('status', '❌')} {contract.get('value', 'N/A')}")
        
        # Description
        description = extractions.get('description', {})
        desc_value = description.get('value', '')
        desc_preview = (desc_value[:100] + '...') if desc_value and len(desc_value) > 100 else desc_value
        print(f"📃 Description: {description.get('status', '❌')} {desc_preview or 'N/A'}")
        
        # Erreurs
        errors = []
        for field, data in extractions.items():
            if data.get('status') == '❌' and 'error' in data:
                errors.append(f"{field}: {data['error']}")
        
        if errors:
            print(f"\n❌ ERREURS:")
            for error in errors:
                print(f"   • {error}")
    
    def _display_summary(self, results):
        """Affiche un résumé des tests"""
        print("\n" + "=" * 60)
        print("📈 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        if not results:
            print("❌ Aucun test réussi")
            return
        
        # Statistiques par champ
        field_stats = {}
        total_tests = len(results)
        
        for result in results:
            for field, data in result['extractions'].items():
                if field not in field_stats:
                    field_stats[field] = {'success': 0, 'warning': 0, 'error': 0}
                
                status = data.get('status', '❌')
                if status == '✅':
                    field_stats[field]['success'] += 1
                elif status == '⚠️':
                    field_stats[field]['warning'] += 1
                else:
                    field_stats[field]['error'] += 1
        
        print(f"\n📊 TAUX DE RÉUSSITE ({total_tests} tests):")
        for field, stats in field_stats.items():
            success_rate = (stats['success'] / total_tests) * 100
            print(f"  {field:15}: {stats['success']}/{total_tests} ({success_rate:.1f}%) ✅{stats['success']} ⚠️{stats['warning']} ❌{stats['error']}")
        
        # Analyse des technologies
        print(f"\n⚙️ ANALYSE DES TECHNOLOGIES:")
        all_technologies = []
        for result in results:
            tech_data = result['extractions'].get('technologies', {})
            tech_list = tech_data.get('value', [])
            if tech_list:
                all_technologies.extend(tech_list)
        
        if all_technologies:
            unique_tech = list(set(all_technologies))
            print(f"  • Technologies trouvées: {len(all_technologies)} total, {len(unique_tech)} uniques")
            print(f"  • Technologies uniques: {sorted(unique_tech)}")
            
            # Vérifier s'il y a encore des doublons suspects
            tech_counts = {}
            for result in results:
                tech_list = result['extractions'].get('technologies', {}).get('value', [])
                tech_key = tuple(sorted(tech_list))
                tech_counts[tech_key] = tech_counts.get(tech_key, 0) + 1
            
            duplicates = [(tech, count) for tech, count in tech_counts.items() if count > 1]
            if duplicates:
                print(f"  ⚠️ ATTENTION: Technologies identiques détectées:")
                for tech_tuple, count in duplicates:
                    print(f"     {list(tech_tuple)} → {count} fois")
            else:
                print(f"  ✅ Pas de doublons détectés - extraction contextuelle réussie!")
        else:
            print(f"  ⚠️ Aucune technologie extraite")
        
        # Score global
        total_extractions = sum(len(result['extractions']) for result in results)
        successful_extractions = sum(
            1 for result in results 
            for data in result['extractions'].values() 
            if data.get('status') == '✅'
        )
        
        global_score = (successful_extractions / total_extractions) * 100 if total_extractions > 0 else 0
        
        print(f"\n🏆 SCORE GLOBAL: {successful_extractions}/{total_extractions} ({global_score:.1f}%)")
        
        if global_score >= 80:
            print("✅ EXCELLENT - Spider très performant")
        elif global_score >= 60:
            print("👍 BON - Spider performant avec quelques améliorations possibles")
        elif global_score >= 40:
            print("⚠️ MOYEN - Spider nécessite des améliorations")
        else:
            print("❌ FAIBLE - Spider nécessite des corrections importantes")


class MockSelector:
    """Mock pour les sélecteurs CSS de Scrapy"""
    def __init__(self, html_text, selector):
        self.html_text = html_text
        self.selector = selector
        
    def get(self):
        """Retourne le premier élément trouvé"""
        results = self.getall()
        return results[0] if results else None
        
    def getall(self):
        """Retourne tous les éléments trouvés (simulation basique)"""
        # Simulation basique - dans un vrai test, on utiliserait BeautifulSoup ou lxml
        import re
        
        # Pour les sélecteurs de texte simples
        if '::text' in self.selector:
            base_selector = self.selector.replace('::text', '')
            # Recherche basique pour les titres h1
            if base_selector == 'h1':
                matches = re.findall(r'<h1[^>]*>(.*?)</h1>', self.html_text, re.DOTALL)
                return [re.sub(r'<[^>]+>', '', match).strip() for match in matches]
        
        # Pour les attributs
        if '::attr(' in self.selector:
            # Exemple: meta[property="og:title"]::attr(content)
            attr_match = re.search(r'::attr\(([^)]+)\)', self.selector)
            if attr_match:
                attr_name = attr_match.group(1)
                base_selector = self.selector.split('::attr')[0]
                
                if 'meta[property="og:title"]' in base_selector:
                    matches = re.findall(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', self.html_text)
                    return matches
        
        # Pour les scripts JSON-LD
        if 'script[type="application/ld+json"]' in self.selector:
            matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', 
                                self.html_text, re.DOTALL)
            return [match.strip() for match in matches]
        
        return []


if __name__ == "__main__":
    tester = FreeWorkTester()
    tester.run_comprehensive_test()
