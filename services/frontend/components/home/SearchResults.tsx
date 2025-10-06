'use client'

import { useState } from 'react'
import { SearchFormData, JobOffer } from '@/lib/types'
import { OfferModal } from './OfferModal'

interface SearchResultsProps {
  results: JobOffer[]
  loading: boolean
  error: string | null
  searchParams: SearchFormData | null
}

const LoadingGif = () => (
  <div className="flex flex-col items-center justify-center py-16">
    <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
    <p className="text-gray-600">Chargement des résultats...</p>
  </div>
)

const OfferCard = ({ offer, onViewDetails }: { 
  offer: JobOffer
  onViewDetails: () => void
}) => {
  const formatTjm = () => {
    if (offer.tjm_min && offer.tjm_max) {
      return offer.tjm_min === offer.tjm_max 
        ? `${offer.tjm_min}€/j` 
        : `${offer.tjm_min}€ - ${offer.tjm_max}€/j`
    }
    if (offer.tjm_min) return `${offer.tjm_min}€/j`
    if (offer.tjm_max) return `${offer.tjm_max}€/j`
    return 'TJM non spécifié'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border hover:shadow-xl transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-lg font-semibold text-gray-800 line-clamp-2 flex-1">
          {offer.title}
        </h4>
        {(offer.tjm_min || offer.tjm_max) && (
          <span className="text-lg font-bold text-blue-600 whitespace-nowrap ml-4">
            {formatTjm()}
          </span>
        )}
      </div>
      
      {offer.description && (
        <p className="text-gray-600 mb-4 line-clamp-3">
          {offer.description}
        </p>
      )}
      
      <div className="flex flex-wrap gap-2 mb-4">
        {offer.technologies && offer.technologies.length > 0 && (
          <>
            {offer.technologies.slice(0, 5).map((tech: string, index: number) => (
              <span 
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
              >
                {tech}
              </span>
            ))}
            {offer.technologies.length > 5 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded-full">
                +{offer.technologies.length - 5}
              </span>
            )}
          </>
        )}
      </div>
      
      <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
        <div>
          {offer.company && <p className="font-medium text-gray-700">{offer.company}</p>}
          <div className="flex gap-3 mt-1">
            {offer.location && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {offer.location}
              </span>
            )}
            {offer.remote_policy && (
              <span className="px-2 py-0.5 bg-green-100 text-green-800 rounded">
                {offer.remote_policy}
              </span>
            )}
          </div>
        </div>
        
        <div className="text-right">
          {offer.seniority_level && (
            <p className="font-medium text-gray-700">{offer.seniority_level}</p>
          )}
          <p className="text-xs">{formatDate(offer.scraped_at)}</p>
        </div>
      </div>
      
      <div className="flex justify-between items-center pt-4 border-t">
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          Source: {offer.source}
        </span>
        
        <button
          onClick={onViewDetails}
          className="px-4 py-2 bg-green-400 text-white rounded-lg hover:bg-green-500 transition-colors text-sm font-medium"
        >
          Voir l'offre
        </button>
      </div>
    </div>
  )
}

export const SearchResults = ({ 
  results,
  loading,
  error,
  searchParams
}: SearchResultsProps) => {
  const [selectedOffer, setSelectedOffer] = useState<JobOffer | null>(null)

  if (loading) {
    return (
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <LoadingGif />
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <p className="text-red-800">Erreur: {error}</p>
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (!results || !searchParams) {
    return null
  }

  if (results.length === 0) {
    return (
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <h3 className="text-lg font-semibold text-yellow-800 mb-2">
                Aucun résultat trouvé
              </h3>
              <p className="text-yellow-700">
                {searchParams.technologies && searchParams.location 
                  ? `Aucune mission trouvée pour "${searchParams.technologies}" à ${searchParams.location}`
                  : searchParams.technologies
                  ? `Aucune mission trouvée pour "${searchParams.technologies}"`
                  : `Aucune mission trouvée pour ${searchParams.location}`
                }
              </p>
            </div>
          </div>
        </div>
      </section>
    )
  }

  // Calcul des statistiques
  const tjms = results
    .map(offer => offer.tjm_min || offer.tjm_max || 0)
    .filter(tjm => tjm > 0)
  
  const avgTjm = tjms.length > 0 
    ? Math.round(tjms.reduce((a, b) => a + b, 0) / tjms.length)
    : null

  return (
    <section className="py-12 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* En-tête avec statistiques */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Résultats de recherche
            </h2>
            <div className="flex flex-wrap gap-4 text-sm">
              {searchParams.technologies && (
                <span className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg font-medium">
                  🔍 {searchParams.technologies}
                </span>
              )}
              {searchParams.location && (
                <span className="px-4 py-2 bg-green-100 text-green-800 rounded-lg font-medium">
                  📍 {searchParams.location}
                </span>
              )}
              <span className="px-4 py-2 bg-gray-100 text-gray-800 rounded-lg font-medium">
                {results.length} mission{results.length > 1 ? 's' : ''} trouvée{results.length > 1 ? 's' : ''}
              </span>
              {avgTjm && (
                <span className="px-4 py-2 bg-purple-100 text-purple-800 rounded-lg font-medium">
                  💰 TJM moyen: {avgTjm}€/j
                </span>
              )}
            </div>
            {results.length > 0 && (
              <p className="text-sm text-gray-600 mt-3">
              Affichage des {results.length} résultat{results.length > 1 ? 's' : ''} les plus récent{results.length > 1 ? 's' : ''} (limité à 15 max)
              </p>
            )}
          </div>
          
          {/* Grille de missions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((offer) => (
              <OfferCard 
                key={offer.id} 
                offer={offer}
                onViewDetails={() => setSelectedOffer(offer)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Modal */}
      {selectedOffer && (
        <OfferModal
          offer={selectedOffer}
          isOpen={!!selectedOffer}
          onClose={() => setSelectedOffer(null)}
        />
      )}
    </section>
  )
}
