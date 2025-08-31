"""
Items definition pour les offres TJM scrappées
"""
import scrapy
from scrapy import Field


class TjmOfferItem(scrapy.Item):
    """Item pour une offre TJM"""
    
    # Identification
    source = Field()           # Source du scraping (ex: 'freelance_informatique')
    source_id = Field()        # ID unique dans la source
    
    # Informations de base
    title = Field()            # Titre de la mission
    company = Field()          # Entreprise
    
    # TJM
    tjm_min = Field()          # TJM minimum
    tjm_max = Field()          # TJM maximum
    tjm_currency = Field()     # Devise (EUR, USD, etc.)
    
    # Compétences
    technologies = Field()     # Liste des technologies requises
    seniority_level = Field()  # Niveau de séniorité
    
    # Localisation
    location = Field()         # Lieu de la mission
    remote_policy = Field()    # Politique télétravail
    
    # Contrat
    contract_type = Field()    # Type de contrat
    description = Field()      # Description complète
    
    # Métadonnées
    url = Field()              # URL de l'offre
    scraped_at = Field()       # Timestamp du scraping


class RawOfferItem(scrapy.Item):
    """Item pour les données brutes avant normalisation"""
    
    source = Field()
    url = Field()
    raw_data = Field()         # Données brutes en JSON
    scraped_at = Field()
