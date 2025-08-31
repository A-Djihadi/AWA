#!/usr/bin/env python3
"""
Test spécialisé pour l'extraction des technologies
Valide la correction du bug des technologies identiques
"""

import sys
import json
import requests
from datetime import datetime
import re

# Import du spider
sys.path.append('.')
from spiders.freework import FreeWorkSpider

class TechnologyExtractionTester:
    def __init__(self):
        self.spider = FreeWorkSpider()
        # URLs avec profils technologiques différents
        self.test_scenarios = [
            {
                'name': 'ERP/Business',
                'url': 'https://www.free-work.com/fr/tech-it/assistant-chef-de-projet/job-mission/chef-de-projet-erp-h-f-328',
                'expected_tech_types': ['erp', 'business', 'management']
            },
            {
                'name': 'DevOps/Cloud',
                'url': 'https://www.free-work.com/fr/tech-it/ingenieur-devops-cloud/job-mission/architecte-technique-it-azure-devops-f-h',
                'expected_tech_types': ['devops', 'cloud', 'infrastructure']
            },
            {
                'name': 'Développement .NET',
                'url': 'https://www.free-work.com/fr/tech-it/developpeur-autre-langage-cobol-perl-vba-ruby-shell/job-mission/developpeur-c-winform-f-h-2',
                'expected_tech_types': ['programming', 'dotnet', 'backend']
            }
        ]
        
    def run_technology_test(self):
        """Exécute le test spécialisé des technologies"""
        print("🔬 TEST SPÉCIALISÉ - EXTRACTION DES TECHNOLOGIES")
        print("=" * 60)
        print("Objectif: Vérifier que chaque offre extrait des technologies contextuelles différentes")
        print()
        
        results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            print(f"🎯 SCÉNARIO {i}/5: {scenario['name']}")
            print(f"URL: {scenario['url']}")
            print("-" * 50)
            
            try:
                # Test de l'extraction
                result = self._test_scenario(scenario)
                results.append(result)
                
                # Affichage immédiat
                self._display_scenario_result(result, i)
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                continue
            
            print()
        
        # Analyse comparative
        self._analyze_technology_diversity(results)
        
    def _test_scenario(self, scenario):
        """Teste un scénario spécifique"""
        result = {
            'scenario': scenario['name'],
            'url': scenario['url'],
            'expected_types': scenario['expected_tech_types'],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Télécharger la page
            response = self._get_response(scenario['url'])
            if not response:
                result['status'] = 'error'
                result['error'] = 'Impossible de télécharger la page'
                return result
            
            # Extraire les technologies
            technologies = self.spider.extract_technologies(response)
            result['technologies'] = technologies
            result['tech_count'] = len(technologies) if technologies else 0
            
            # Analyser la qualité
            result['quality_analysis'] = self._analyze_tech_quality(technologies, scenario['expected_tech_types'])
            result['status'] = 'success'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
    
    def _get_response(self, url):
        """Télécharge et prépare une réponse"""
        try:
            response = requests.get(url, headers={
                'User-Agent': 'AWA-FreeWork-Scraper/1.0'
            }, timeout=15)
            response.raise_for_status()
            
            # Mock response pour Scrapy
            class MockResponse:
                def __init__(self, response):
                    self.url = response.url
                    self.text = response.text
                    
                def css(self, selector):
                    return MockSelector(self.text, selector)
                    
            return MockResponse(response)
        except Exception as e:
            print(f"Erreur de téléchargement: {e}")
            return None
    
    def _analyze_tech_quality(self, technologies, expected_types):
        """Analyse la qualité des technologies extraites"""
        analysis = {
            'is_empty': not technologies,
            'is_too_generic': False,
            'is_contextual': False,
            'matches_expectations': False
        }
        
        if not technologies:
            return analysis
        
        # Vérifier si trop générique (toutes les mêmes technologies)
        generic_indicators = ['laravel', 'java', 'symfony', 'react', 'javascript', 'node', 'angular', 'python', 'php', 'vue']
        if len(technologies) >= 8 and all(tech.lower() in [g.lower() for g in generic_indicators] for tech in technologies):
            analysis['is_too_generic'] = True
        
        # Vérifier la contextualité
        tech_lower = [tech.lower() for tech in technologies]
        
        # Analyser par type attendu
        type_matches = {
            'erp': any(t in tech_lower for t in ['erp', 'sap', 'oracle', 'crm']),
            'business': any(t in tech_lower for t in ['erp', 'crm', 'business', 'management']),
            'devops': any(t in tech_lower for t in ['devops', 'docker', 'kubernetes', 'jenkins', 'ansible']),
            'cloud': any(t in tech_lower for t in ['aws', 'azure', 'gcp', 'cloud']),
            'infrastructure': any(t in tech_lower for t in ['linux', 'docker', 'kubernetes', 'terraform']),
            'programming': any(t in tech_lower for t in ['java', 'python', 'c#', '.net', 'php']),
            'dotnet': any(t in tech_lower for t in ['c#', '.net', 'dotnet', 'asp.net']),
            'backend': any(t in tech_lower for t in ['api', 'sql', 'database', 'server']),
            'frontend': any(t in tech_lower for t in ['react', 'vue', 'angular', 'javascript', 'css']),
            'javascript': any(t in tech_lower for t in ['javascript', 'typescript', 'node', 'react', 'vue']),
            'react': any(t in tech_lower for t in ['react', 'jsx', 'redux']),
            'php': any(t in tech_lower for t in ['php', 'symfony', 'laravel']),
            'fullstack': len([t for t in tech_lower if t in ['react', 'vue', 'angular', 'javascript']]) > 0 and 
                        len([t for t in tech_lower if t in ['php', 'python', 'java', 'api']]) > 0
        }
        
        # Vérifier si correspond aux attentes
        analysis['matches_expectations'] = any(type_matches.get(expected_type, False) for expected_type in expected_types)
        analysis['is_contextual'] = analysis['matches_expectations'] and not analysis['is_too_generic']
        
        return analysis
    
    def _display_scenario_result(self, result, scenario_num):
        """Affiche le résultat d'un scénario"""
        if result['status'] == 'error':
            print(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
            return
        
        technologies = result.get('technologies', [])
        quality = result.get('quality_analysis', {})
        
        print(f"📊 Technologies extraites ({len(technologies)}):")
        if technologies:
            print(f"   {technologies}")
        else:
            print("   Aucune technologie trouvée")
        
        # Analyse qualitative
        print(f"🔍 Analyse qualitative:")
        
        if quality['is_empty']:
            print("   ⚠️ Aucune technologie extraite")
        elif quality['is_too_generic']:
            print("   ❌ Technologies trop génériques (possibles doublons)")
        elif quality['is_contextual']:
            print("   ✅ Technologies contextuelles et pertinentes")
        elif quality['matches_expectations']:
            print("   👍 Technologies correspondent au profil attendu")
        else:
            print("   ⚠️ Technologies ne correspondent pas au contexte")
        
        # Types attendus vs trouvés
        expected = result['expected_types']
        print(f"🎯 Profil attendu: {expected}")
        
        if quality['matches_expectations']:
            print("   ✅ Profil technologique détecté correctement")
        else:
            print("   ⚠️ Profil technologique non détecté")
    
    def _analyze_technology_diversity(self, results):
        """Analyse la diversité des technologies extraites"""
        print("=" * 60)
        print("📈 ANALYSE COMPARATIVE DE LA DIVERSITÉ")
        print("=" * 60)
        
        successful_results = [r for r in results if r['status'] == 'success']
        
        if len(successful_results) < 2:
            print("❌ Pas assez de résultats pour l'analyse comparative")
            return
        
        # Collecter toutes les technologies
        all_tech_sets = []
        tech_by_scenario = {}
        
        for result in successful_results:
            scenario_name = result['scenario']
            technologies = result.get('technologies', [])
            tech_set = set(tech.lower() for tech in technologies)
            all_tech_sets.append(tech_set)
            tech_by_scenario[scenario_name] = technologies
        
        # Calculer la diversité
        print("🔍 TECHNOLOGIES PAR SCÉNARIO:")
        for scenario, techs in tech_by_scenario.items():
            print(f"  {scenario:20}: {techs}")
        
        # Calculer les intersections
        print(f"\n🔄 ANALYSE DES DOUBLONS:")
        
        if len(all_tech_sets) >= 2:
            # Vérifier les paires
            duplicate_pairs = 0
            total_pairs = 0
            
            for i in range(len(all_tech_sets)):
                for j in range(i + 1, len(all_tech_sets)):
                    total_pairs += 1
                    set1, set2 = all_tech_sets[i], all_tech_sets[j]
                    
                    if set1 == set2 and len(set1) > 0:
                        duplicate_pairs += 1
                        scenario1 = list(tech_by_scenario.keys())[i]
                        scenario2 = list(tech_by_scenario.keys())[j]
                        print(f"  ❌ DOUBLON: {scenario1} ≡ {scenario2}")
            
            if duplicate_pairs == 0:
                print("  ✅ Aucun doublon détecté - Extraction contextuelle réussie!")
            else:
                print(f"  ⚠️ {duplicate_pairs}/{total_pairs} paires identiques détectées")
        
        # Statistiques globales
        all_technologies = []
        for result in successful_results:
            all_technologies.extend(result.get('technologies', []))
        
        unique_technologies = list(set(tech.lower() for tech in all_technologies))
        
        print(f"\n📊 STATISTIQUES GLOBALES:")
        print(f"  • Total extractions: {len(all_technologies)}")
        print(f"  • Technologies uniques: {len(unique_technologies)}")
        print(f"  • Ratio diversité: {len(unique_technologies)/len(all_technologies)*100:.1f}%" if all_technologies else "  • Ratio diversité: 0%")
        
        # Score de qualité
        contextual_count = sum(1 for r in successful_results if r.get('quality_analysis', {}).get('is_contextual', False))
        quality_score = (contextual_count / len(successful_results)) * 100 if successful_results else 0
        
        print(f"  • Extractions contextuelles: {contextual_count}/{len(successful_results)} ({quality_score:.1f}%)")
        
        # Verdict final
        print(f"\n🏆 VERDICT FINAL:")
        if duplicate_pairs == 0 and quality_score >= 60:
            print("✅ EXCELLENT - Bug des technologies identiques résolu!")
        elif duplicate_pairs == 0:
            print("👍 BON - Pas de doublons mais qualité contextuelle à améliorer")
        elif quality_score >= 60:
            print("⚠️ MOYEN - Bonne qualité mais quelques doublons persistants")
        else:
            print("❌ FAIBLE - Bug des technologies identiques non résolu")


class MockSelector:
    """Mock pour les sélecteurs CSS de Scrapy"""
    def __init__(self, html_text, selector):
        self.html_text = html_text
        self.selector = selector
        
    def get(self):
        results = self.getall()
        return results[0] if results else None
        
    def getall(self):
        import re
        
        # Pour les scripts JSON-LD
        if 'script[type="application/ld+json"]' in self.selector:
            matches = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', 
                                self.html_text, re.DOTALL)
            return [match.strip() for match in matches]
        
        # Pour les sélecteurs de contenu
        if '[class*="content"]' in self.selector:
            matches = re.findall(r'<[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</[^>]*>', 
                                self.html_text, re.DOTALL)
            if '::text' in self.selector:
                return [re.sub(r'<[^>]+>', '', match).strip() for match in matches]
            return matches
        
        # Pour les meta tags
        if 'meta[name="description"]' in self.selector and '::attr(content)' in self.selector:
            matches = re.findall(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', self.html_text)
            return matches
        
        return []


if __name__ == "__main__":
    tester = TechnologyExtractionTester()
    tester.run_technology_test()
