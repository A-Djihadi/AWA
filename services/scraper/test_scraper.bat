@echo off
REM Script de test rapide pour Windows

echo "=== Test du scraper AWA ==="

REM Vérification Python
python --version
if %errorlevel% neq 0 (
    echo "Erreur: Python non installé"
    exit /b 1
)

REM Installation des dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

REM Création des dossiers
if not exist "data" mkdir data
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
if not exist "logs" mkdir logs

REM Test de configuration
echo "Test de la configuration Scrapy..."
python -m scrapy list

REM Test du spider de base
echo "Test du spider de test..."
python -m scrapy crawl test -L INFO

echo "Test terminé! Vérifiez les fichiers dans data/raw/"
pause
