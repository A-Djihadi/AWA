'use client'

import { HeroSection } from "@/components/home/HeroSection"
import { LocationStatsSection } from "@/components/home/LocationStatsSection"
import { SearchBar } from "@/components/home/SearchBar"
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
            <h2 className="text-3xl font-bold text-center mb-8 text-gray-900">
              Rechercher des missions
            </h2>
            <SearchBar onSearch={handleSearch} />
          </div>
        </div>
      </section>
      
      {/* Section Résultats avec graphique évolution TJM + cartes missions */}
      {(searchParams?.position || searchParams?.location) && (
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
