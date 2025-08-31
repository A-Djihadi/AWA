import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '../../../../lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    
    // TJM Statistics
    const { data: tjmStats, error: tjmError } = await supabase
      .from('offers')
      .select('tjm_min, tjm_max')
      .not('tjm_min', 'is', null)
      .not('tjm_max', 'is', null)
    
    if (tjmError) {
      return NextResponse.json({ error: tjmError.message }, { status: 500 })
    }
    
    // Calculate statistics
    const tjmValues = tjmStats.flatMap(offer => [offer.tjm_min, offer.tjm_max].filter(Boolean))
    
    const stats = {
      count: tjmValues.length,
      min: Math.min(...tjmValues),
      max: Math.max(...tjmValues),
      avg: tjmValues.reduce((a, b) => a + b, 0) / tjmValues.length,
      median: calculateMedian(tjmValues)
    }
    
    // Technology distribution
    const { data: techData, error: techError } = await supabase
      .from('offers')
      .select('technologies')
      .not('technologies', 'is', null)
    
    if (techError) {
      return NextResponse.json({ error: techError.message }, { status: 500 })
    }
    
    const techCount: Record<string, number> = {}
    techData.forEach(offer => {
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
    
    return NextResponse.json({
      tjm: stats,
      technologies: topTech,
      totalOffers: tjmStats.length
    })
    
  } catch (error) {
    console.error('Stats API Error:', error)
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
    ? (sorted[mid - 1] + sorted[mid]) / 2
    : sorted[mid]
}
