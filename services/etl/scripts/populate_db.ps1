# AWA - Script PowerShell pour peupler la base de données
# Lance le scraping de 15 pages sur FreeWork et Collective.work

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🚀 AWA - Pipeline de peuplement BDD" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$startTime = Get-Date

# Chemins
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$etlDir = Split-Path -Parent $scriptPath
$servicesDir = Split-Path -Parent $etlDir
$scraperDir = Join-Path $servicesDir "scraper"
$dataDir = Join-Path $scraperDir "data"

Write-Host "📁 Dossiers:" -ForegroundColor Yellow
Write-Host "   ETL: $etlDir"
Write-Host "   Scraper: $scraperDir"
Write-Host "   Data: $dataDir`n"

# Étape 1: Nettoyer la BDD
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🗑️  ÉTAPE 1: Nettoyage BDD" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location $etlDir
python -c @"
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

result = supabase.table('offers').select('id', count='exact').execute()
count = len(result.data)
print(f'📊 Offres actuelles: {count}')

if count > 0:
    for source in ['freework', 'collective_work', 'generated_data', 'test', 'test_deduplication']:
        try:
            supabase.table('offers').delete().eq('source', source).execute()
            print(f'   ✅ Supprimé: {source}')
        except:
            pass
    print('✅ BDD nettoyée')
else:
    print('ℹ️  BDD déjà vide')
"@

# Étape 2: Nettoyer les anciens fichiers
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🧹 ÉTAPE 2: Nettoyage fichiers" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (Test-Path $dataDir) {
    Get-ChildItem $dataDir -Filter "*.json" | ForEach-Object {
        Remove-Item $_.FullName -Force
        Write-Host "   Supprimé: $($_.Name)" -ForegroundColor Green
    }
}

# Étape 3: Lancer les scrapers
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🕷️  ÉTAPE 3: Scraping (15 pages x 2)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location $scraperDir

# FreeWork
Write-Host "🚀 Scraping FreeWork..." -ForegroundColor Yellow
Write-Host "   Pages: 1-15" -ForegroundColor Gray
Write-Host "   Début: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Gray

scrapy crawl freework -O "data/freework.json" --loglevel=INFO

if (Test-Path "data/freework.json") {
    $freeworkData = Get-Content "data/freework.json" -Raw | ConvertFrom-Json
    $freeworkCount = if ($freeworkData -is [Array]) { $freeworkData.Count } else { 1 }
    Write-Host "   ✅ FreeWork: $freeworkCount offres`n" -ForegroundColor Green
} else {
    Write-Host "   ❌ FreeWork: Échec`n" -ForegroundColor Red
    $freeworkCount = 0
}

# Collective.work
Write-Host "🚀 Scraping Collective.work..." -ForegroundColor Yellow
Write-Host "   Pages: 1-15" -ForegroundColor Gray
Write-Host "   Début: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Gray

scrapy crawl collective_work -O "data/collective_work.json" --loglevel=INFO

if (Test-Path "data/collective_work.json") {
    $collectiveData = Get-Content "data/collective_work.json" -Raw | ConvertFrom-Json
    $collectiveCount = if ($collectiveData -is [Array]) { $collectiveData.Count } else { 1 }
    Write-Host "   ✅ Collective.work: $collectiveCount offres`n" -ForegroundColor Green
} else {
    Write-Host "   ❌ Collective.work: Échec`n" -ForegroundColor Red
    $collectiveCount = 0
}

$totalScraped = $freeworkCount + $collectiveCount
Write-Host "📊 Total scrapé: $totalScraped offres`n" -ForegroundColor Cyan

# Étape 4: Charger dans Supabase
if ($totalScraped -gt 0) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "📤 ÉTAPE 4: Chargement Supabase" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Set-Location $etlDir
    python run_full_pipeline.py
    
    # Étape 5: Vérification
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ ÉTAPE 5: Vérification" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    python -c @"
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

result = supabase.table('offers').select('source', count='exact').execute()
total = len(result.data)

print(f'📊 Total en BDD: {total} offres\n')

sources = {}
for offer in result.data:
    source = offer.get('source', 'unknown')
    sources[source] = sources.get(source, 0) + 1

print('📋 Par source:')
for source, count in sorted(sources.items()):
    print(f'   • {source}: {count}')

locations = supabase.table('offers').select('location').execute()
unique_locations = set(o['location'] for o in locations.data if o.get('location'))
print(f'\n🏙️  Villes: {len(unique_locations)}')

techs = supabase.table('offers').select('technologies').execute()
all_techs = set()
for offer in techs.data:
    if offer.get('technologies'):
        all_techs.update(offer['technologies'])
print(f'💻 Technologies: {len(all_techs)}')

tjms = supabase.table('offers').select('tjm_min, tjm_max').execute()
valid_tjms = [(o['tjm_min'] + o['tjm_max']) / 2 for o in tjms.data if o.get('tjm_min') and o.get('tjm_max')]
if valid_tjms:
    print(f'💰 TJM moyen: {sum(valid_tjms) / len(valid_tjms):.0f}€/jour')
"@
} else {
    Write-Host "❌ Aucune donnée scrapée. Abandon.`n" -ForegroundColor Red
}

# Résumé
$duration = (Get-Date) - $startTime
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ PIPELINE TERMINÉ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "⏱️  Durée: $([math]::Round($duration.TotalSeconds, 1))s ($([math]::Round($duration.TotalMinutes, 1)) min)" -ForegroundColor Yellow
Write-Host "📅 Fin: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "========================================`n" -ForegroundColor Cyan
