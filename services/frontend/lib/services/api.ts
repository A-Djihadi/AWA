import { SearchFormData, SearchResponse, LocationStatsResponse } from '../types'

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = '/api'
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    return response.json()
  }

  async searchMissions(searchData: SearchFormData): Promise<SearchResponse> {
    const params = new URLSearchParams({
      position: searchData.position,
      location: searchData.location
    })

    const response = await fetch(`${this.baseUrl}/offers?${params}`)
    return this.handleResponse<SearchResponse>(response)
  }

  async getLocationStats(): Promise<LocationStatsResponse> {
    const response = await fetch(`${this.baseUrl}/stats/locations`)
    return this.handleResponse<LocationStatsResponse>(response)
  }

  async getTjmEvolution(position: string, location: string): Promise<any> {
    const params = new URLSearchParams({ position, location })
    const response = await fetch(`${this.baseUrl}/stats/tjm-evolution?${params}`)
    return this.handleResponse(response)
  }
}

export const apiService = new ApiService()
