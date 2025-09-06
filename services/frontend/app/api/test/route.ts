import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // Test endpoint simple sans Supabase
    return NextResponse.json({ 
      message: "API est fonctionnelle",
      timestamp: new Date().toISOString(),
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
