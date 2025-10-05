import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-helpers'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    
    // Récupérer toutes les technologies uniques
    const { data, error } = await supabase
      .from('offers')
      .select('technologies')
    
    if (error) {
      console.error('❌ Supabase error:', error)
      return NextResponse.json(
        { error: 'Erreur lors de la récupération des technologies' },
        { status: 500 }
      )
    }
    
    // Extraire et dédupliquer les technologies
    const techSet = new Set<string>()
    data?.forEach(offer => {
      if (offer.technologies && Array.isArray(offer.technologies)) {
        offer.technologies.forEach((tech: string) => {
          techSet.add(tech)
        })
      }
    })
    
    const technologies = Array.from(techSet).sort()
    
    console.log(`✅ ${technologies.length} technologies trouvées`)
    
    return NextResponse.json({
      technologies,
      count: technologies.length
    })
  } catch (error) {
    console.error('❌ API error:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}
