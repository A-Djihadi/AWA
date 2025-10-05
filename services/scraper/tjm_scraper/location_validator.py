"""
Validateur de localisations pour les villes françaises

Ce module contient une liste exhaustive des villes françaises
et des méthodes de validation/normalisation des localisations.
"""

# Liste exhaustive des villes françaises (top 200 + variations)
FRENCH_CITIES = {
    # Villes majeures
    'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg',
    'montpellier', 'bordeaux', 'lille', 'rennes', 'reims', 'le havre', 
    'saint-étienne', 'toulon', 'grenoble', 'dijon', 'angers', 'nîmes', 
    'villeurbanne', 'clermont-ferrand', 'aix-en-provence', 'brest', 'limoges',
    'tours', 'amiens', 'perpignan', 'metz', 'besançon', 'orléans', 'rouen',
    'mulhouse', 'caen', 'nancy', 'argenteuil', 'saint-denis', 'roubaix',
    'tourcoing', 'nanterre', 'avignon', 'créteil', 'poitiers', 'versailles',
    'courbevoie', 'vitry-sur-seine', 'pau', 'la rochelle', 'aubervilliers',
    'champigny-sur-marne', 'boulogne-billancourt', 'neuilly-sur-seine',
    'issy-les-moulineaux', 'puteaux', 'levallois-perret',
    
    # Villes moyennes
    'antibes', 'cannes', 'dunkerque', 'montreuil', 'aulnay-sous-bois',
    'asnières-sur-seine', 'colombes', 'saint-maur-des-fossés', 'drancy',
    'rueil-malmaison', 'ajaccio', 'bourges', 'la seyne-sur-mer', 'calais',
    'saint-quentin', 'valence', 'mérignac', 'cholet', 'vannes', 'troyes',
    'lorient', 'chambéry', 'beziers', 'sète', 'beauvais', 'châteauroux',
    'épinay-sur-seine', 'meaux', 'fréjus', 'annecy', 'laval', 'quimper',
    'pessac', 'charleville-mézières', 'arles', 'niort', 'saint-brieuc',
    'bayonne', 'salon-de-provence', 'hyères', 'brive-la-gaillarde',
    'cergy', 'carcassonne', 'la roche-sur-yon', 'albi', 'évreux',
    'tarbes', 'montauban', 'angoulême', 'belfort', 'châtellerault',
    
    # Régions et départements
    'ile-de-france', 'idf', 'région parisienne', 'grand paris', 'petite couronne',
    'grande couronne', 'hauts-de-france', 'nouvelle-aquitaine', 'occitanie',
    'auvergne-rhône-alpes', 'provence-alpes-côte d\'azur', 'paca', 'bretagne',
    'pays de la loire', 'centre-val de loire', 'grand est', 'bourgogne-franche-comté',
    'normandie', 'corse',
    
    # Quartiers d'affaires
    'la défense', 'defense', 'bercy', 'montparnasse', 'saint-lazare',
    'gare de lyon', 'part-dieu', 'euralille',
    
    # Termes génériques
    'remote', 'télétravail', 'full remote', 'hybride', 'france', 'national',
    'distanciel', '100% remote', 'partout en france', 'toute la france'
}

# Variations courantes (mapping vers nom normalisé)
CITY_VARIATIONS = {
    'paris 75': 'Paris',
    'lyon 69': 'Lyon',
    'marseille 13': 'Marseille',
    'île-de-france': 'Île-de-France',
    'idf': 'Île-de-France',
    'paca': 'Provence-Alpes-Côte d\'Azur',
    'defense': 'La Défense',
    'la defense': 'La Défense',
    '100% remote': 'Remote',
    'full remote': 'Remote',
    'télétravail': 'Remote',
    'distanciel': 'Remote',
    'teletravail': 'Remote',
    'partout en france': 'France',
    'toute la france': 'France',
}


def normalize_location(location: str) -> str | None:
    """
    Normalise et valide une localisation
    
    Args:
        location: La localisation brute extraite
        
    Returns:
        La localisation normalisée si valide, None sinon
    """
    if not location or not isinstance(location, str):
        return None
    
    # Nettoyer
    location_clean = location.strip().lower()
    
    # Supprimer les codes postaux
    location_clean = ''.join(c for c in location_clean if not c.isdigit() or c.isspace())
    location_clean = location_clean.strip()
    
    # Vérifier les variations connues
    if location_clean in CITY_VARIATIONS:
        return CITY_VARIATIONS[location_clean]
    
    # Vérification directe
    if location_clean in FRENCH_CITIES:
        return location.title()
    
    # Vérification partielle (contient une ville française)
    for city in FRENCH_CITIES:
        if city in location_clean or location_clean in city:
            # Retourner la ville normalisée
            return city.title()
    
    # Détection de patterns Remote/Télétravail
    remote_patterns = ['remote', 'télétravail', 'full remote', 'hybride', 
                      'distance', '100%', 'distanciel']
    for pattern in remote_patterns:
        if pattern in location_clean:
            return 'Remote'
    
    # Détection France générique
    if 'france' in location_clean:
        return 'France'
    
    # Si aucune correspondance, retourner None (sera filtré)
    return None


def is_valid_french_location(location: str) -> bool:
    """
    Vérifie si une localisation est valide (ville française)
    
    Args:
        location: La localisation à vérifier
        
    Returns:
        True si valide, False sinon
    """
    normalized = normalize_location(location)
    return normalized is not None


def extract_city_from_text(text: str) -> str | None:
    """
    Extrait une ville française depuis un texte
    
    Args:
        text: Le texte contenant potentiellement une ville
        
    Returns:
        La ville normalisée si trouvée, None sinon
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Chercher chaque ville connue dans le texte
    # Trier par longueur décroissante pour matcher les villes composées en premier
    sorted_cities = sorted(FRENCH_CITIES, key=len, reverse=True)
    
    for city in sorted_cities:
        if city in text_lower:
            return city.title()
    
    return None


if __name__ == "__main__":
    # Tests
    test_locations = [
        "Paris",
        "Paris 75008",
        "Celad",  # Entreprise - devrait retourner None
        "Île-de-France",
        "Remote",
        "Full Remote",
        "Lyon, France",
        "Hexagone Digitale",  # Entreprise - devrait retourner None
        "La Défense",
        "Marseille 13",
        "Télétravail complet",
    ]
    
    print("🧪 Tests de validation de localisation:\n")
    for loc in test_locations:
        normalized = normalize_location(loc)
        valid = is_valid_french_location(loc)
        norm_str = normalized if normalized else "None"
        print(f"   {loc:30} → {norm_str:20} (valide: {valid})")
