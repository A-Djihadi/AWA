import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-helpers'
import { LocationData } from '@/lib/types'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    
    console.log('🔍 Fetching location statistics...')
    
    // Récupérer toutes les offres avec leurs informations de localisation et TJM
    const { data: offers, error } = await supabase
      .from('offers')
      .select('location, tjm_min, tjm_max')
      .not('location', 'is', null)

    if (error) {
      console.error('❌ Supabase error:', error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    console.log(`✅ Retrieved ${offers?.length || 0} offers`)

    // Grouper par localisation et calculer les statistiques
    const locationMap = new Map<string, {
      count: number
      tjms: number[]
      city: string
      region: string
    }>()

    offers?.forEach(offer => {
      if (!offer.location) return

      // Extraire ville et région de la localisation
      const parts = offer.location.split(',').map((p: string) => p.trim())
      const city = parts[0] || offer.location
      const region = parts[1] || parts[0] || 'France'

      const key = city.toLowerCase()
      
      if (!locationMap.has(key)) {
        locationMap.set(key, {
          count: 0,
          tjms: [],
          city,
          region
        })
      }

      const loc = locationMap.get(key)!
      loc.count++

      // Ajouter les TJM valides
      if (offer.tjm_min && offer.tjm_min > 0) loc.tjms.push(offer.tjm_min)
      if (offer.tjm_max && offer.tjm_max > 0) loc.tjms.push(offer.tjm_max)
    })

    // Convertir en tableau LocationData avec coordonnées fictives
    const locations: LocationData[] = Array.from(locationMap.entries()).map(([key, data]) => {
      const avgTjm = data.tjms.length > 0
        ? Math.round(data.tjms.reduce((a, b) => a + b, 0) / data.tjms.length)
        : 0

      // Coordonnées fictives (à remplacer par vraies coordonnées plus tard)
      const coordinates: [number, number] = getCoordinates(data.city)

      return {
        city: data.city,
        region: data.region,
        averageTjm: avgTjm,
        offerCount: data.count,
        coordinates
      }
    })

    // Trier par nombre d'offres (décroissant)
    locations.sort((a, b) => b.offerCount - a.offerCount)

    // Calculer le résumé
    const totalMissions = locations.reduce((sum, loc) => sum + loc.offerCount, 0)
    const avgTjm = locations.length > 0
      ? Math.round(locations.reduce((sum, loc) => sum + loc.averageTjm, 0) / locations.length)
      : 0

    console.log(`✅ Processed ${locations.length} unique locations`)
    console.log(`📊 Total missions: ${totalMissions}, Avg TJM: ${avgTjm}€`)

    return NextResponse.json({
      locations,
      summary: {
        totalMissions,
        averageTjm: avgTjm,
        topCities: locations.slice(0, 5).map(loc => loc.city)
      }
    })

  } catch (error) {
    console.error('❌ API Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Fonction helper pour obtenir des coordonnées approximatives
// TODO: Remplacer par une vraie API de géocodage
function getCoordinates(city: string): [number, number] {
  const coordinates: Record<string, [number, number]> = {
    'paris': [48.8566, 2.3522],
    'lyon': [45.7640, 4.8357],
    'marseille': [43.2965, 5.3698],
    'toulouse': [43.6047, 1.4442],
    'nice': [43.7102, 7.2620],
    'nantes': [47.2184, -1.5536],
    'strasbourg': [48.5734, 7.7521],
    'montpellier': [43.6108, 3.8767],
    'bordeaux': [44.8378, -0.5792],
    'lille': [50.6292, 3.0573],
    'rennes': [48.1173, -1.6778],
    'reims': [49.2583, 4.0317],
    'le havre': [49.4944, 0.1079],
    'grenoble': [45.1885, 5.7245],
    'dijon': [47.3220, 5.0415],
    'remote': [46.6034, 1.8883] // Centre de la France
  }

  const cityLower = city.toLowerCase()
  return coordinates[cityLower] || [46.6034, 1.8883] // Par défaut: centre France
}
