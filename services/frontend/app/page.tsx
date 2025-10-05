'use client'

import { HeroSection } from "@/components/home/HeroSection"
import { LocationStatsSection } from "@/components/home/LocationStatsSection"
import { SearchBar } from "@/components/home/SearchBar"
import { SearchSuggestions } from "@/components/home/SearchSuggestions"
import { SearchResults } from "@/components/home/SearchResults"
import { useSearch, useLocationStats } from "@/lib/hooks"

export default function HomePage() {
  const { 
    searchParams, 
    results, 
    loading: searchLoading, 
    error: searchError, 
    handleSearch 
  } = useSearch()
  
  const { 
    locations, 
    loading: locationLoading, 
    error: locationError 
  } = useLocationStats()

  // Handler pour les suggestions de recherche
  const handleSuggestionClick = (tech?: string, location?: string) => {
    handleSearch({
      technologies: tech || '',
      location: location || ''
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Section Hero */}
      <HeroSection />
      
      {/* Section Statistiques par localisation avec carte de France */}
      <LocationStatsSection 
        locations={locations}
        loading={locationLoading}
        error={locationError}
      />
      
      {/* Barre de recherche horizontale avec 6 sections */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <SearchBar onSearch={handleSearch} isLoading={searchLoading} />
            <SearchSuggestions onSuggestionClick={handleSuggestionClick} />
          </div>
        </div>
      </section>
      
      {/* Section Résultats avec graphique évolution TJM + cartes missions */}
      {(searchParams?.technologies || searchParams?.location) && (
        <SearchResults 
          results={results}
          loading={searchLoading}
          error={searchError}
          searchParams={searchParams}
        />
      )}
    </div>
  )
}
