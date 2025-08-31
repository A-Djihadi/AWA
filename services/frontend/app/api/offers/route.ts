import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '../../../lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    
    // Get query parameters
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
      return NextResponse.json({ error: error.message }, { status: 500 })
    }
    
    return NextResponse.json({ 
      data,
      count: data?.length || 0,
      filters: { tech, location, limit }
    })
    
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const supabase = createServerClient()
    
    const { data, error } = await supabase
      .from('offers')
      .insert(body)
      .select()
    
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 400 })
    }
    
    return NextResponse.json({ data }, { status: 201 })
    
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
