#!/usr/bin/env node
/**
 * Test de connexion Supabase pour AWA
 * Usage: node test-supabase.js
 */

require('dotenv').config({ path: './services/frontend/.env.local' })
const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

console.log('🔗 Test de connexion Supabase pour AWA...\n')

// Vérifier les variables d'environnement
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Variables d\'environnement manquantes!')
  console.error('Assurez-vous que services/frontend/.env.local contient:')
  console.error('- NEXT_PUBLIC_SUPABASE_URL')
  console.error('- NEXT_PUBLIC_SUPABASE_ANON_KEY')
  process.exit(1)
}

console.log('📋 Configuration:')
console.log(`URL: ${supabaseUrl}`)
console.log(`Anon Key: ${supabaseAnonKey.substring(0, 20)}...`)
console.log(`Service Key: ${supabaseServiceKey ? '✅ Configuré' : '❌ Manquant'}\n`)

async function testConnection() {
  // Test avec clé anonyme (lecture)
  console.log('🔍 Test connexion avec clé anonyme...')
  const supabaseAnon = createClient(supabaseUrl, supabaseAnonKey)
  
  try {
    // Test lecture des tables
    const { data: offers, error: offersError } = await supabaseAnon
      .from('offers')
      .select('count(*)')
      .limit(1)
    
    if (offersError) {
      console.error('❌ Erreur lecture offers:', offersError.message)
    } else {
      console.log('✅ Lecture offers: OK')
    }

    const { data: techMapping, error: techError } = await supabaseAnon
      .from('tech_mapping')
      .select('count(*)')
      .limit(1)
    
    if (techError) {
      console.error('❌ Erreur lecture tech_mapping:', techError.message)
    } else {
      console.log('✅ Lecture tech_mapping: OK')
    }

    // Test données réelles
    const { data: sampleOffers, error: sampleError } = await supabaseAnon
      .from('offers')
      .select('id, title, company, tjm_min, tjm_max, technologies')
      .limit(5)
    
    if (sampleError) {
      console.error('❌ Erreur échantillon offers:', sampleError.message)
    } else {
      console.log(`✅ Trouvé ${sampleOffers.length} offers`)
      sampleOffers.forEach(offer => {
        console.log(`  - ${offer.title} (${offer.company}) - ${offer.tjm_min}-${offer.tjm_max}€`)
      })
    }

  } catch (error) {
    console.error('❌ Erreur de connexion:', error.message)
  }

  // Test avec service role (écriture) si disponible
  if (supabaseServiceKey) {
    console.log('\n🔐 Test connexion avec service role...')
    const supabaseService = createClient(supabaseUrl, supabaseServiceKey)
    
    try {
      // Test d'insertion
      const testOffer = {
        source: 'test',
        source_id: `test-${Date.now()}`,
        title: 'Test Developer',
        company: 'Test Company',
        tjm_min: 400,
        tjm_max: 500,
        technologies: ['JavaScript', 'React'],
        scraped_at: new Date().toISOString()
      }

      const { data: insertData, error: insertError } = await supabaseService
        .from('offers')
        .insert(testOffer)
        .select()
      
      if (insertError) {
        console.error('❌ Erreur insertion:', insertError.message)
      } else {
        console.log('✅ Insertion test: OK')
        
        // Supprimer l'offre test
        await supabaseService
          .from('offers')
          .delete()
          .eq('id', insertData[0].id)
        
        console.log('✅ Nettoyage test: OK')
      }

    } catch (error) {
      console.error('❌ Erreur service role:', error.message)
    }
  }

  console.log('\n🎉 Tests terminés!')
}

testConnection()
