import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-helpers'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    const searchParams = request.nextUrl.searchParams
    
    // Récupération des paramètres de recherche
    const tech = searchParams.get('tech')
    const location = searchParams.get('location')
    
    console.log('🔍 Recherche:', { tech, location })
    
    // Construction de la requête Supabase
    let query = supabase
      .from('offers')
      .select('*')
      .order('scraped_at', { ascending: false })
    
    // Filtre par technologie si présent
    // Utilise contains pour rechercher une technologie spécifique dans le tableau
    if (tech) {
      const techTrimmed = tech.trim()
      query = query.contains('technologies', [techTrimmed])
    }
    
    // Filtre par localisation si présent
    // Utilise ilike pour une recherche insensible à la casse
    if (location) {
      const locationTrimmed = location.trim()
      query = query.ilike('location', `%${locationTrimmed}%`)
    }
    
    const { data, error } = await query
    
    if (error) {
      console.error('❌ Supabase error:', error)
      return NextResponse.json(
        { error: 'Erreur lors de la récupération des offres' },
        { status: 500 }
      )
    }
    
    console.log(`✅ ${data?.length || 0} offres trouvées`)
    
    return NextResponse.json(data || [])
  } catch (error) {
    console.error('❌ API error:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}
