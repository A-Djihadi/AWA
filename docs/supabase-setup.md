# Configuration Supabase pour AWA

## 🚀 Guide de configuration étape par étape

### 1. Créer le projet Supabase

1. **Aller sur [supabase.com](https://supabase.com)**
2. **Se connecter/créer un compte**
3. **Créer un nouveau projet** :
   - Project Name: `awa-tjm-analytics`
   - Database Password: (choisir un mot de passe fort)
   - Region: `Europe (eu-west-1)` ou proche de vous

### 2. Récupérer les credentials

Dans votre dashboard Supabase, aller dans **Settings > API** :

- **Project URL** : `https://xxxxx.supabase.co`
- **anon public** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **service_role** : `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 3. Configuration des variables d'environnement

Créer le fichier `.env.local` dans `services/frontend/` :

```bash
# Copier l'example
cd services/frontend
cp .env.example .env.local

# Éditer avec vos vraies valeurs
NEXT_PUBLIC_SUPABASE_URL=https://votre-projet.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=votre_anon_key
SUPABASE_SERVICE_ROLE_KEY=votre_service_role_key
```

### 4. Créer le schéma de base de données

Dans Supabase Dashboard > **SQL Editor** :

1. **Copier le contenu** du fichier `infra/migrations/001_initial_schema.sql`
2. **Coller dans l'éditeur SQL**
3. **Exécuter** (bouton RUN)

### 5. Configurer Row Level Security (RLS)

Exécuter ce SQL supplémentaire :

```sql
-- Enable RLS
ALTER TABLE offers ENABLE ROW LEVEL SECURITY;
ALTER TABLE snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE tech_mapping ENABLE ROW LEVEL SECURITY;

-- Politique pour lecture publique des offers
CREATE POLICY "Allow public read access" ON offers
    FOR SELECT USING (true);

-- Politique pour lecture publique des snapshots  
CREATE POLICY "Allow public read access" ON snapshots
    FOR SELECT USING (true);

-- Politique pour lecture publique des tech_mapping
CREATE POLICY "Allow public read access" ON tech_mapping
    FOR SELECT USING (true);
```

### 6. Insérer des données de test (optionnel)

```sql
-- Quelques technologies de base
INSERT INTO tech_mapping (raw_tech, normalized_tech, category) VALUES
('react', 'React', 'frontend'),
('javascript', 'JavaScript', 'frontend'),
('python', 'Python', 'backend'),
('nodejs', 'Node.js', 'backend'),
('docker', 'Docker', 'devops');

-- Une offre de test
INSERT INTO offers (source, source_id, title, company, tjm_min, tjm_max, technologies, location) VALUES
('freework', 'test-001', 'Développeur React Senior', 'TechCorp', 500, 650, 
 ARRAY['React', 'JavaScript', 'TypeScript'], 'Paris');
```

## 🔧 Vérification de la configuration

### Test de connexion

Créer un fichier `test-supabase.js` temporaire :

```javascript
const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = 'YOUR_SUPABASE_URL'
const supabaseKey = 'YOUR_ANON_KEY'

const supabase = createClient(supabaseUrl, supabaseKey)

async function testConnection() {
  try {
    const { data, error } = await supabase
      .from('offers')
      .select('count(*)')
    
    if (error) {
      console.error('❌ Erreur:', error.message)
    } else {
      console.log('✅ Connexion réussie!', data)
    }
  } catch (err) {
    console.error('❌ Erreur de connexion:', err.message)
  }
}

testConnection()
```

### Test du frontend

```bash
cd services/frontend
npm run dev
```

Aller sur `http://localhost:3000` - le dashboard devrait se charger.

## 📊 Tables créées

- **`offers`** : Offres scrappées avec TJM, technologies, etc.
- **`snapshots`** : Agrégations périodiques pour analytics
- **`tech_mapping`** : Normalisation des noms de technologies
- **`raw_offers`** : Archive des données brutes (optionnel)
- **`scraping_sources`** : Configuration des sources

## 🔒 Sécurité

- **RLS activé** sur toutes les tables
- **Lecture publique** autorisée pour le dashboard
- **Service role** pour insertion/update via ETL
- **Anon key** pour lecture frontend

## 🆘 Troubleshooting

### Erreur "Cannot find module '@supabase/supabase-js'"
```bash
cd services/frontend
npm install @supabase/supabase-js
```

### Erreur de connexion
- Vérifier l'URL du projet
- Vérifier les clés dans `.env.local`
- Vérifier que RLS est bien configuré

### Pas de données
- Insérer des données de test
- Vérifier les politiques RLS
- Tester avec l'éditeur SQL Supabase
