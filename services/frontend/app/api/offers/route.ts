import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase-helpers'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    
    const { searchParams } = new URL(request.url)
    const limit = parseInt(searchParams.get('limit') || '50')
    const tech = searchParams.get('tech')
    const location = searchParams.get('location')

    let query = supabase
      .from('offers')
      .select('*')
      .order('scraped_at', { ascending: false })
      .limit(limit)

    // Apply filters
    if (tech) {
      query = query.contains('technologies', [tech])
    }

    if (location) {
      query = query.ilike('location', `%${location}%`)
    }

    const { data, error } = await query

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ 
      offers: data || [],
      count: data?.length || 0,
      filters: { tech, location, limit },
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
