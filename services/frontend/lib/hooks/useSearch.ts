import { useState } from 'react'
import { SearchFormData, SearchResponse, TjmDataPoint, Mission } from '../types'
import { apiService } from '../services/api'

interface UseSearchState {
  searchParams: SearchFormData | null
  loading: boolean
  error: string | null
  results: {
    position: string
    location: string
    tjmEvolution: TjmDataPoint[]
    recentMissions: Mission[]
  } | null
}

export const useSearch = () => {
  const [state, setState] = useState<UseSearchState>({
    searchParams: null,
    loading: false,
    error: null,
    results: null
  })

  const handleSearch = async (searchData: SearchFormData) => {
    setState(prev => ({ 
      ...prev, 
      searchParams: searchData,
      loading: true, 
      error: null 
    }))

    try {
      // Recherche des missions
      const searchResponse = await apiService.searchMissions(searchData)
      
      // Récupération de l'évolution du TJM
      const tjmEvolution = await apiService.getTjmEvolution(
        searchData.position, 
        searchData.location
      )

      setState(prev => ({
        ...prev,
        loading: false,
        error: null,
        results: {
          position: searchData.position,
          location: searchData.location,
          tjmEvolution: tjmEvolution.data || [],
          recentMissions: searchResponse.missions || []
        }
      }))
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Erreur de recherche'
      }))
    }
  }

  const clearResults = () => {
    setState({
      searchParams: null,
      loading: false,
      error: null,
      results: null
    })
  }

  return {
    searchParams: state.searchParams,
    results: state.results,
    loading: state.loading,
    error: state.error,
    handleSearch,
    clearResults
  }
}
