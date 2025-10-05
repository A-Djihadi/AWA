import { useState } from 'react'
import { apiService } from '../services/api'
import { JobOffer, SearchFormData } from '../types'

export const useSearch = () => {
  const [searchParams, setSearchParams] = useState<SearchFormData | null>(null)
  const [results, setResults] = useState<JobOffer[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (formData: SearchFormData) => {
    setLoading(true)
    setError(null)
    setSearchParams(formData)
    
    try {
      const offers = await apiService.searchOffers({
        technologies: formData.technologies,
        location: formData.location
      })
      
      setResults(offers)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setResults([])
    setError(null)
    setSearchParams(null)
  }

  return {
    searchParams,
    results,
    loading,
    error,
    handleSearch,
    reset
  }
}
