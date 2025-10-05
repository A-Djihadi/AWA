# 🎯 Modal de Détails d'Offre - Documentation

## ✅ Fonctionnalité Implémentée

Une **modal interactive** s'affiche maintenant quand on clique sur "Voir l'offre" dans une carte de mission.

## 🎨 Composant : `OfferModal`

### Structure de la Modal

```
┌──────────────────────────────────────────────┐
│  [X] Fermer                                  │
│  Titre de la mission                         │
│  Nom de l'entreprise                         │
├──────────────────────────────────────────────┤
│  💰 TJM: 500€ - 600€/jour                   │
├──────────────────────────────────────────────┤
│  📍 Localisation  │  🏠 Remote Policy       │
│  ⭐ Seniority     │  📝 Contract Type       │
├──────────────────────────────────────────────┤
│  📄 Description de la mission                │
│  Lorem ipsum dolor sit amet...               │
├──────────────────────────────────────────────┤
│  💻 Technologies requises                    │
│  [React] [TypeScript] [Node.js]...          │
├──────────────────────────────────────────────┤
│  🔗 Informations sur la source               │
│  Plateforme: freework | Date: 5 oct. 2025   │
├──────────────────────────────────────────────┤
│  [Fermer]    [Voir l'annonce complète →]    │
└──────────────────────────────────────────────┘
```

## 📊 Sections de la Modal

### 1. **Header (Sticky)**
- ✅ Titre de la mission (h2)
- ✅ Nom de l'entreprise
- ✅ Bouton fermer (X) en haut à droite
- ✅ Sticky lors du scroll

### 2. **TJM - Highlight (Vert)**
- ✅ Mise en avant du TJM avec fond vert
- ✅ Format : "500€ - 600€/jour" ou "500€/jour"
- ✅ Emoji 💰
- ✅ Bordure gauche verte (border-l-4)

### 3. **Informations Principales (Grid 2 colonnes)**
- 📍 **Localisation** : Ville, région
- 🏠 **Remote Policy** : Full Remote, Hybrid, etc.
- ⭐ **Seniority Level** : Junior, Senior, etc.
- 📝 **Contract Type** : Freelance, CDI, etc.
- ✅ Affichage conditionnel (seulement si données présentes)

### 4. **Description (Prose)**
- 📄 Titre avec emoji
- ✅ Texte avec `whitespace-pre-wrap` (conserve les sauts de ligne)
- ✅ Classe `prose` pour un bel affichage du texte

### 5. **Technologies (Badges)**
- 💻 Titre avec emoji
- ✅ Badges bleus pour chaque technologie
- ✅ Layout flex-wrap responsive

### 6. **Source Information (Grid 2 colonnes)**
- 🔗 Titre avec emoji
- ✅ Plateforme source (capitalize)
- ✅ Date de publication (format français complet)

### 7. **Footer (Sticky)**
- ✅ Bouton "Fermer" (gris)
- ✅ Bouton "Voir l'annonce complète" (vert) avec icône externe
- ✅ Sticky en bas lors du scroll

## 🎯 Fonctionnalités Interactives

### Fermeture de la Modal
1. **Clic sur le bouton X** (header)
2. **Clic sur le bouton "Fermer"** (footer)
3. **Clic sur l'overlay** (fond noir transparent)
4. **Touche Escape** du clavier
5. **Auto-gestion du scroll** : `overflow: hidden` sur body quand modal ouverte

### Ouverture de la Modal
- **Clic sur "Voir l'offre"** dans une carte de mission
- État géré par `useState<JobOffer | null>`
- Passage de l'offre sélectionnée au composant Modal

## 🔗 URLs des Sources

Fonction `getSourceUrl()` génère l'URL selon la source :

```typescript
switch (offer.source) {
  case 'freework':
    return `https://www.free-work.com/fr/tech-it/mission/${offer.source_id}`
  case 'collective_work':
    return `https://www.collective.work/missions/${offer.source_id}`
  default:
    return '#'
}
```

**TODO :** Ajouter les URLs réelles pour chaque plateforme

## 🎨 Design

### Couleurs
- **Vert** : Highlight TJM, bouton principal (green-400/green-500)
- **Gris** : Background sections (gray-50)
- **Bleu** : Badges technologies (blue-100/blue-800)
- **Blanc** : Background modal
- **Noir transparent** : Overlay (50% opacity)

### Emojis
- 💰 TJM
- 📍 Localisation
- 🏠 Remote
- ⭐ Seniority
- 📝 Contract
- 📄 Description
- 💻 Technologies
- 🔗 Source

### Responsive
- ✅ **Mobile** : Modal pleine largeur, scroll vertical
- ✅ **Desktop** : Max width 3xl, centré
- ✅ **Grid** : 1 colonne mobile → 2 colonnes desktop
- ✅ **Max height** : 90vh avec scroll interne

### Transitions
- ✅ Overlay fade in/out
- ✅ Hover effects sur boutons
- ✅ Smooth scroll

## 💻 Code Intégration

### Dans SearchResults.tsx

```typescript
const [selectedOffer, setSelectedOffer] = useState<JobOffer | null>(null)

// Dans le map des offres
<OfferCard 
  offer={offer}
  onViewDetails={() => setSelectedOffer(offer)}
/>

// En fin de composant
{selectedOffer && (
  <OfferModal
    offer={selectedOffer}
    isOpen={!!selectedOffer}
    onClose={() => setSelectedOffer(null)}
  />
)}
```

### Props du Composant

```typescript
interface OfferModalProps {
  offer: JobOffer          // L'offre à afficher
  isOpen: boolean          // État d'ouverture
  onClose: () => void      // Callback de fermeture
}
```

## 🚀 Utilisation

### Scénario Utilisateur

1. **Recherche** une mission (ex: "React" à "Paris")
2. **Voit** les cartes de résultats
3. **Clique** sur "Voir l'offre" sur une carte
4. **Modal s'ouvre** avec tous les détails
5. **Consulte** les informations complètes :
   - TJM détaillé
   - Description complète
   - Technologies requises
   - Informations de localisation
   - Source et date
6. **Clique** sur "Voir l'annonce complète" → Redirigé vers la plateforme source
7. **Ferme** la modal (X, Escape, overlay, ou bouton Fermer)

## ✨ Améliorations UX

### Gestion du Scroll
```typescript
useEffect(() => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'  // Désactive scroll body
  }
  return () => {
    document.body.style.overflow = 'unset'   // Réactive scroll body
  }
}, [isOpen])
```

### Gestion Keyboard
```typescript
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') onClose()
  }
  if (isOpen) {
    document.addEventListener('keydown', handleEscape)
  }
  return () => {
    document.removeEventListener('keydown', handleEscape)
  }
}, [isOpen, onClose])
```

### Click Outside
```typescript
<div 
  className="fixed inset-0"
  onClick={onClose}  // Ferme sur clic overlay
/>
<div 
  onClick={(e) => e.stopPropagation()}  // Empêche fermeture sur clic modal
>
  {/* Contenu modal */}
</div>
```

## 🎯 Champs Affichés

### Toujours Affichés
- ✅ Titre (`offer.title`)
- ✅ Source (`offer.source`)
- ✅ Date (`offer.scraped_at`)

### Conditionnels (si présents)
- 💼 Entreprise (`offer.company`)
- 💰 TJM (`offer.tjm_min`, `offer.tjm_max`)
- 📍 Localisation (`offer.location`)
- 🏠 Remote policy (`offer.remote_policy`)
- ⭐ Seniority (`offer.seniority_level`)
- 📝 Type de contrat (`offer.contract_type`)
- 📄 Description (`offer.description`)
- 💻 Technologies (`offer.technologies[]`)

## 🔧 Configuration

### URLs des Plateformes

**Actuellement configuré :**
- Freework : `https://www.free-work.com/fr/tech-it/mission/{source_id}`
- Collective Work : `https://www.collective.work/missions/{source_id}`

**À ajouter :**
- [ ] Comet
- [ ] Malt
- [ ] Crème de la Crème
- [ ] Autres plateformes

### Format de Date
```typescript
formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',      // "octobre" au lieu de "10"
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
// Exemple : "5 octobre 2025, 14:30"
```

## ✅ Checklist

- [x] Composant OfferModal créé
- [x] Intégration dans SearchResults
- [x] État selectedOffer avec useState
- [x] Gestion ouverture/fermeture
- [x] Fermeture par Escape
- [x] Fermeture par clic overlay
- [x] Gestion du scroll body
- [x] Design responsive
- [x] Sections header/footer sticky
- [x] Bouton vers annonce source
- [x] Affichage conditionnel des champs
- [x] Emojis et couleurs cohérentes
- [x] Transitions smooth
- [ ] URLs réelles des plateformes
- [ ] Tests sur mobile
- [ ] Accessibilité (ARIA labels)

## 🎯 Améliorations Futures

1. **Partage**
   - Bouton partage (LinkedIn, Twitter, Email)
   - Copy link to clipboard
   - QR code

2. **Favoris**
   - Bouton "Ajouter aux favoris"
   - Sauvegarde dans localStorage
   - Liste des favoris

3. **Comparaison**
   - Sélection de plusieurs offres
   - Vue comparative côte à côte
   - Export CSV

4. **Candidature**
   - Formulaire de candidature intégré
   - Upload CV
   - Lettre de motivation

5. **Historique**
   - Offres déjà consultées
   - Badge "Déjà vu"
   - Nettoyage automatique

---

**Date :** 5 octobre 2025
**Version :** 1.0.0
**Status :** ✅ Fonctionnel
