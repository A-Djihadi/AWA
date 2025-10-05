# 🔍 Guide de Recherche AWA

## Fonctionnalités de Recherche

L'application AWA supporte plusieurs types de recherches pour trouver des missions freelance.

### 1. Recherche par Technologie

Recherchez des missions nécessitant une technologie spécifique :

**Exemples :**
- `React`
- `Python`
- `AWS`
- `TypeScript`
- `Docker`

**Comment ça marche :**
- La recherche est **exacte** (sensible à la casse)
- Cherche dans le tableau `technologies` de chaque offre
- Exemple : "React" trouvera toutes les offres contenant "React" dans leurs technologies

**Données disponibles :**
Technologies présentes dans la base (exemples) :
- .NET, ABAP, AWS, Agile, Android, Angular, Apex
- Azure DevOps, C#, Confluence, Django, Docker
- Firebase, Go, Java, JavaScript, Kotlin, Laravel
- Node.js, PHP, Python, React, Spring Boot, Vue.js
- Et bien d'autres...

### 2. Recherche par Localisation

Recherchez des missions dans une ville ou région spécifique :

**Exemples :**
- `Paris`
- `Lyon`
- `Remote`
- `Île-de-France`
- `Marseille`

**Comment ça marche :**
- La recherche est **partielle** et **insensible à la casse**
- Cherche dans le champ `location` de chaque offre
- Exemple : "paris" trouvera "Paris", "Paris, France", "Paris, Île-de-France"

### 3. Recherche Combinée

Combinez technologie ET localisation pour affiner votre recherche :

**Exemples :**
- `React` + `Paris` → Missions React à Paris
- `Python` + `Remote` → Missions Python en télétravail
- `AWS` + `Lyon` → Missions AWS à Lyon

**Comment ça marche :**
- Les deux filtres sont appliqués simultanément (AND)
- Seules les offres correspondant aux DEUX critères sont retournées

## Interface Utilisateur

### Barre de Recherche

La barre de recherche est composée de 5 sections :

```
┌────────┬─────────────────────┬──────┬──────────────────────┬──────────────┐
│ 🔍     │ Technologie...      │ 📍   │ Localisation...      │ Rechercher   │
└────────┴─────────────────────┴──────┴──────────────────────┴──────────────┘
```

1. **Icône de recherche** (🔍) - Indicateur visuel
2. **Champ Technologie** - Saisissez une technologie (ex: React, Python, AWS)
3. **Icône de localisation** (📍) - Indicateur visuel
4. **Champ Localisation** - Saisissez une ville (ex: Paris, Lyon, Remote)
5. **Bouton Rechercher** - Lance la recherche

### Validation

- Le bouton "Rechercher" est **désactivé** si aucun critère n'est saisi
- Vous devez saisir au moins UNE technologie OU UNE localisation
- Pendant la recherche, le bouton affiche "Recherche..."

## Résultats

### Affichage des Résultats

Les résultats sont affichés sous forme de cartes avec :

#### En-tête
- **Statistiques** : Nombre de missions trouvées, TJM moyen
- **Critères de recherche** : Technologies et localisation recherchées

#### Cartes de Mission
Chaque carte affiche :
- **Titre** de la mission
- **TJM** (Taux Journalier Moyen) : min - max ou valeur unique
- **Description** (3 lignes max)
- **Technologies** (5 premières + compteur si plus)
- **Entreprise**
- **Localisation** avec icône 📍
- **Remote policy** (badge vert si applicable)
- **Seniority level** (Junior, Senior, etc.)
- **Date de scraping**
- **Source** de l'offre
- **Bouton "Voir l'offre"** pour accéder aux détails

### États

#### Chargement
- Spinner animé avec message "Chargement des résultats..."

#### Aucun résultat
- Message personnalisé selon les critères :
  - "Aucune mission trouvée pour 'React'"
  - "Aucune mission trouvée pour 'React' à Paris"
  - "Aucune mission trouvée pour Paris"

#### Erreur
- Message d'erreur en rouge avec détails

## API Endpoints

### GET `/api/offers`

Récupère les offres filtrées par technologie et/ou localisation.

**Paramètres Query :**
- `tech` (optionnel) : Technologie à rechercher (ex: "React")
- `location` (optionnel) : Localisation à rechercher (ex: "Paris")

**Exemples de requêtes :**

```bash
# Toutes les offres (triées par date)
GET /api/offers

# Offres React
GET /api/offers?tech=React

# Offres à Paris
GET /api/offers?location=Paris

# Offres React à Paris
GET /api/offers?tech=React&location=Paris
```

**Réponse :**

```json
[
  {
    "id": "uuid",
    "source": "freework",
    "source_id": "12345",
    "title": "Développeur React Senior",
    "company": "TechCorp",
    "tjm_min": 500,
    "tjm_max": 600,
    "technologies": ["React", "TypeScript", "Node.js"],
    "seniority_level": "Senior",
    "location": "Paris",
    "remote_policy": "Hybrid",
    "contract_type": "Freelance",
    "description": "Mission de développement...",
    "scraped_at": "2025-10-05T10:00:00Z"
  }
]
```

## Cas d'Usage

### Freelance React cherchant mission à Paris

1. Saisir "React" dans le champ Technologie
2. Saisir "Paris" dans le champ Localisation
3. Cliquer sur "Rechercher"
4. Voir les 1+ missions React à Paris
5. Consulter les TJM, descriptions, et postuler

### Freelance Python cherchant mission Remote

1. Saisir "Python" dans le champ Technologie
2. Saisir "Remote" dans le champ Localisation
3. Cliquer sur "Rechercher"
4. Voir toutes les missions Python en télétravail

### Découvrir les missions à Lyon

1. Laisser le champ Technologie vide
2. Saisir "Lyon" dans le champ Localisation
3. Cliquer sur "Rechercher"
4. Voir toutes les missions disponibles à Lyon

## Base de Données

### Statistiques Actuelles

- **103 offres** au total
- Sources : `generated_data`, `collective_work`, `freework`, `test_deduplication`
- Technologies : 50+ (React, Python, Java, AWS, Docker, etc.)
- Localisations : Paris, Lyon, Marseille, Remote, Toulouse, Nantes, etc.

### Déduplication

Le système évite les doublons grâce à :
- Contrainte unique sur `(source, source_id)`
- Upsert lors de l'insertion (mise à jour si existe déjà)

## Améliorations Futures

### Recherche Avancée
- [ ] Recherche partielle dans les technologies (ex: "Reac" trouve "React")
- [ ] Recherche par range de TJM (ex: 400-600€/j)
- [ ] Recherche par seniority level
- [ ] Recherche par remote policy
- [ ] Filtres multiples (plusieurs technologies)

### UX
- [ ] Suggestions automatiques (autocomplete)
- [ ] Historique de recherche
- [ ] Sauvegarder des recherches favorites
- [ ] Alertes email pour nouvelles missions

### Affichage
- [ ] Graphique d'évolution du TJM par technologie
- [ ] Carte interactive des localisations
- [ ] Export des résultats (CSV, PDF)
- [ ] Comparaison de missions

---

**Date de mise à jour :** 5 octobre 2025
**Version :** 1.0.0
