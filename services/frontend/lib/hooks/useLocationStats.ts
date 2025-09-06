import { useState, useEffect } from 'react'
import { LocationData } from '../types'
import { apiService } from '../services/api'

interface UseLocationStatsState {
  locations: LocationData[]
  loading: boolean
  error: string | null
}

export const useLocationStats = () => {
  const [state, setState] = useState<UseLocationStatsState>({
    locations: [],
    loading: true,
    error: null
  })

  useEffect(() => {
    const fetchLocationStats = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }))
        
        const response = await apiService.getLocationStats()
        
        setState({
          locations: response.locations || [],
          loading: false,
          error: null
        })
      } catch (error) {
        setState({
          locations: [],
          loading: false,
          error: error instanceof Error ? error.message : 'Erreur de chargement'
        })
      }
    }

    fetchLocationStats()
  }, [])

  return state
}
