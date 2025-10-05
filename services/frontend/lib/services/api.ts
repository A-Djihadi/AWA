import { JobOffer, SearchFilters, LocationData } from '../types'

const API_BASE_URL = '/api'

export const apiService = {
  async searchOffers(filters: SearchFilters): Promise<JobOffer[]> {
    const params = new URLSearchParams()
    
    if (filters.technologies) {
      params.append('tech', filters.technologies)
    }
    
    if (filters.location) {
      params.append('location', filters.location)
    }
    
    const url = `${API_BASE_URL}/offers${params.toString() ? `?${params.toString()}` : ''}`
    
    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    return response.json()
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/stats`)
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    return response.json()
  },

  async getLocationStats(): Promise<{ locations: LocationData[], summary: { totalMissions: number, averageTjm: number, topCities: string[] } }> {
    const response = await fetch(`${API_BASE_URL}/location-stats`)
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    return response.json()
  }
}
