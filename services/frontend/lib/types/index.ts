export interface Mission {
  id: string
  title: string
  description: string
  tjm_min: number
  tjm_max: number
  company: string
  location: string
  source_url: string
  technologies: string[]
  posted_date: string
  seniority?: string
}

export interface LocationData {
  city: string
  region: string
  averageTjm: number
  offerCount: number
  coordinates: [number, number] // [lat, lng]
}

export interface TjmDataPoint {
  date: string
  tjm: number
}

export interface SearchFormData {
  technologies: string
  location: string
}

export interface SearchResponse {
  missions: Mission[]
  tjmEvolution: TjmDataPoint[]
  totalCount: number
}

export interface LocationStatsResponse {
  locations: LocationData[]
  summary: {
    totalMissions: number
    averageTjm: number
    topCities: string[]
  }
}

export interface JobOffer {
  id: string
  source: string
  source_id: string
  title: string
  company?: string
  tjm_min?: number
  tjm_max?: number
  technologies: string[]
  seniority_level?: string
  location?: string
  remote_policy?: string
  contract_type?: string
  description?: string
  scraped_at: string
}

export interface SearchFilters {
  technologies?: string
  location?: string
}
