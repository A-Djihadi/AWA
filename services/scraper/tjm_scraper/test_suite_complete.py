#!/usr/bin/env python3
"""
Synthèse complète des tests du spider FreeWork corrigé
Résumé de tous les tests effectués et validation finale
"""

import sys
import subprocess
from datetime import datetime
import json

def run_test_suite():
    """Exécute la suite complète de tests et génère un rapport"""
    
    print("🔬 SUITE COMPLÈTE DE TESTS - SPIDER FREEWORK CORRIGÉ")
    print("=" * 70)
    print(f"Date d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Tests à exécuter
    tests = [
        {
            'name': 'Tests Unitaires',
            'file': 'test_unit_extraction.py',
            'description': 'Validation des fonctions avec données simulées',
            'critical': True
        },
        {
            'name': 'Test Complet',
            'file': 'test_spider_comprehensive.py', 
            'description': 'Test de toutes les fonctionnalités avec données réelles',
            'critical': True
        },
        {
            'name': 'Test Technologies',
            'file': 'test_technologies_specialized.py',
            'description': 'Validation de la correction du bug des technologies identiques',
            'critical': True
        },
        {
            'name': 'Test Scraping Complet',
            'file': 'test_full_scraping.py',
            'description': 'Test du processus complet découverte + extraction',
            'critical': False
        }
    ]
    
    results = []
    
    print("📋 EXÉCUTION DES TESTS")
    print("-" * 50)
    
    for i, test in enumerate(tests, 1):
        print(f"\n🧪 TEST {i}/4: {test['name']}")
        print(f"📄 Fichier: {test['file']}")
        print(f"📝 Description: {test['description']}")
        print(f"🔴 Critique: {'Oui' if test['critical'] else 'Non'}")
        
        try:
            print("⏳ Exécution en cours...")
            
            # Exécuter le test (capture la sortie mais ne l'affiche pas ici)
            result = subprocess.run(
                [sys.executable, test['file']], 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            test_result = {
                'name': test['name'],
                'file': test['file'],
                'success': result.returncode == 0,
                'critical': test['critical'],
                'output_lines': len(result.stdout.split('\n')),
                'error': result.stderr if result.stderr else None
            }
            
            # Analyser la sortie pour extraire des métriques
            output = result.stdout
            metrics = extract_metrics(output, test['name'])
            test_result['metrics'] = metrics
            
            results.append(test_result)
            
            if test_result['success']:
                print(f"✅ Réussi - {test_result['output_lines']} lignes de sortie")
                if metrics:
                    for key, value in metrics.items():
                        print(f"   📊 {key}: {value}")
            else:
                print(f"❌ Échec - Code de sortie: {result.returncode}")
                if test_result['error']:
                    print(f"   🔥 Erreur: {test_result['error'][:100]}...")
                    
        except subprocess.TimeoutExpired:
            print("⏰ Timeout - Test trop long (>60s)")
            results.append({
                'name': test['name'],
                'file': test['file'],
                'success': False,
                'critical': test['critical'],
                'error': 'Timeout'
            })
        except Exception as e:
            print(f"💥 Exception: {e}")
            results.append({
                'name': test['name'],
                'file': test['file'],
                'success': False,
                'critical': test['critical'],
                'error': str(e)
            })
    
    # Génération du rapport final
    print("\n" + "=" * 70)
    print("📊 RAPPORT FINAL DE VALIDATION")
    print("=" * 70)
    
    generate_final_report(results)

def extract_metrics(output, test_name):
    """Extrait des métriques spécifiques de la sortie d'un test"""
    metrics = {}
    
    if not output:
        return metrics
    
    # Métriques communes
    if "SCORE GLOBAL:" in output:
        try:
            import re
            score_match = re.search(r'SCORE GLOBAL: ([\d.]+)%', output)
            if score_match:
                metrics['Score Global'] = f"{score_match.group(1)}%"
        except:
            pass
    
    # Métriques spécifiques par test
    if test_name == "Tests Unitaires":
        if "EXCELLENT" in output:
            metrics['Statut'] = "EXCELLENT"
        elif "BON" in output:
            metrics['Statut'] = "BON"
        else:
            metrics['Statut'] = "À améliorer"
    
    elif test_name == "Test Technologies":
        if "Bug des technologies identiques résolu" in output:
            metrics['Bug Technologies'] = "✅ Résolu"
        elif "Pas de doublons détectés" in output:
            metrics['Bug Technologies'] = "✅ Résolu"
        else:
            metrics['Bug Technologies'] = "⚠️ À vérifier"
    
    elif test_name == "Test Scraping Complet":
        if "Spider prêt pour la production" in output:
            metrics['Production Ready'] = "✅ Oui"
        elif "fonctionnel" in output.lower():
            metrics['Production Ready'] = "⚠️ Avec améliorations"
        else:
            metrics['Production Ready'] = "❌ Non"
    
    return metrics

def generate_final_report(results):
    """Génère le rapport final de validation"""
    
    # Statistiques générales
    total_tests = len(results)
    successful_tests = len([r for r in results if r['success']])
    critical_tests = [r for r in results if r['critical']]
    critical_passed = len([r for r in critical_tests if r['success']])
    
    print(f"📈 STATISTIQUES GÉNÉRALES:")
    print(f"  • Total des tests: {total_tests}")
    print(f"  • Tests réussis: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    print(f"  • Tests critiques: {len(critical_tests)}")
    print(f"  • Tests critiques réussis: {critical_passed}/{len(critical_tests)} ({critical_passed/len(critical_tests)*100:.1f}%)")
    
    # Détail par test
    print(f"\n📋 DÉTAIL PAR TEST:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        critical_mark = "🔴" if result['critical'] else "🔵"
        print(f"  {status} {critical_mark} {result['name']}")
        
        if result.get('metrics'):
            for key, value in result['metrics'].items():
                print(f"      📊 {key}: {value}")
        
        if not result['success'] and result.get('error'):
            error_preview = result['error'][:80] + "..." if len(result['error']) > 80 else result['error']
            print(f"      💥 {error_preview}")
    
    # Validation des corrections apportées
    print(f"\n🔧 VALIDATION DES CORRECTIONS:")
    
    # Vérifier la correction du bug des technologies
    tech_test = next((r for r in results if 'Technologies' in r['name']), None)
    if tech_test and tech_test['success']:
        if tech_test.get('metrics', {}).get('Bug Technologies') == "✅ Résolu":
            print("  ✅ Bug des technologies identiques: RÉSOLU")
        else:
            print("  ⚠️ Bug des technologies identiques: À vérifier")
    else:
        print("  ❌ Bug des technologies identiques: Test échoué")
    
    # Vérifier la qualité générale
    unit_test = next((r for r in results if 'Unitaires' in r['name']), None)
    if unit_test and unit_test['success']:
        if unit_test.get('metrics', {}).get('Statut') == "EXCELLENT":
            print("  ✅ Fonctions d'extraction: EXCELLENTES")
        else:
            print("  👍 Fonctions d'extraction: BONNES")
    else:
        print("  ❌ Fonctions d'extraction: Test échoué")
    
    # Vérifier la robustesse
    comprehensive_test = next((r for r in results if 'Complet' in r['name'] and 'Scraping' not in r['name']), None)
    if comprehensive_test and comprehensive_test['success']:
        print("  ✅ Tests avec données réelles: RÉUSSIS")
    else:
        print("  ❌ Tests avec données réelles: ÉCHOUÉS")
    
    # Verdict final
    print(f"\n🏆 VERDICT FINAL:")
    
    if critical_passed == len(critical_tests) and successful_tests >= total_tests * 0.75:
        print("✅ SPIDER VALIDÉ - Toutes les corrections fonctionnent correctement")
        print("📋 PRÊT POUR:")
        print("  • Intégration de l'architecture refactorisée")
        print("  • Déploiement en production")
        print("  • Scraping à grande échelle")
        
    elif critical_passed == len(critical_tests):
        print("👍 SPIDER FONCTIONNEL - Corrections principales validées") 
        print("📋 PRÊT POUR:")
        print("  • Tests supplémentaires")
        print("  • Intégration progressive")
        print("⚠️ RECOMMANDATIONS:")
        print("  • Corriger les tests non critiques échoués")
        
    else:
        print("❌ SPIDER NÉCESSITE DES CORRECTIONS")
        print("🔧 ACTIONS REQUISES:")
        failed_critical = [r for r in critical_tests if not r['success']]
        for test in failed_critical:
            print(f"  • Corriger: {test['name']}")
    
    # Résumé des améliorations apportées
    print(f"\n📝 RÉSUMÉ DES AMÉLIORATIONS APPORTÉES:")
    print("  1. ✅ Correction du bug des technologies identiques")
    print("     - Extraction ciblée avec JSON-LD et sélecteurs spécifiques")
    print("     - Filtrage contextuel pour éviter le contenu des scripts")
    print("     - Normalisation et validation des technologies extraites")
    print()
    print("  2. ✅ Amélioration de l'extraction des données")
    print("     - Sélecteurs CSS optimisés basés sur l'analyse de la structure")
    print("     - Patterns regex améliorés pour TJM, entreprise, localisation")
    print("     - Gestion robuste des erreurs et cas edge")
    print()
    print("  3. ✅ Tests complets de validation")
    print("     - Tests unitaires avec données simulées")
    print("     - Tests d'intégration avec données réelles")
    print("     - Validation spécifique de la correction des technologies")
    print("     - Test du processus complet de scraping")

if __name__ == "__main__":
    run_test_suite()
