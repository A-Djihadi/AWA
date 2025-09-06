import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-helpers'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    
    // Get all offers
    const { data: offers, error } = await supabase
      .from('offers')
      .select('tjm_min, tjm_max, technologies')
      .not('tjm_min', 'is', null)
      .not('tjm_max', 'is', null)

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    // Calculate TJM statistics
    const tjmValues = offers.flatMap(offer => [offer.tjm_min, offer.tjm_max].filter(Boolean))
    
    const tjmStats = {
      count: tjmValues.length,
      min: Math.min(...tjmValues),
      max: Math.max(...tjmValues),
      avg: Math.round(tjmValues.reduce((a, b) => a + b, 0) / tjmValues.length),
      median: calculateMedian(tjmValues)
    }

    // Calculate technology distribution
    const techCount: Record<string, number> = {}
    offers.forEach(offer => {
      if (Array.isArray(offer.technologies)) {
        offer.technologies.forEach((tech: string) => {
          techCount[tech] = (techCount[tech] || 0) + 1
        })
      }
    })

    const topTech = Object.entries(techCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .map(([tech, count]) => ({ tech, count }))

    // Get total offers count
    const { count: totalOffers } = await supabase
      .from('offers')
      .select('*', { count: 'exact', head: true })

    return NextResponse.json({
      tjm: tjmStats,
      technologies: topTech,
      totalOffers: totalOffers || 0,
      status: "success"
    })

  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

function calculateMedian(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0
    ? Math.round((sorted[mid - 1] + sorted[mid]) / 2)
    : sorted[mid]
}
