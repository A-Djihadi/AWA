'use client'

import { JobOffer } from '@/lib/types'
import { useEffect } from 'react'

interface OfferModalProps {
  offer: JobOffer
  isOpen: boolean
  onClose: () => void
}

export const OfferModal = ({ offer, isOpen, onClose }: OfferModalProps) => {
  // Fermer avec la touche Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const formatTjm = () => {
    if (offer.tjm_min && offer.tjm_max) {
      return offer.tjm_min === offer.tjm_max 
        ? `${offer.tjm_min}€/jour` 
        : `${offer.tjm_min}€ - ${offer.tjm_max}€/jour`
    }
    if (offer.tjm_min) return `${offer.tjm_min}€/jour`
    if (offer.tjm_max) return `${offer.tjm_max}€/jour`
    return 'Non spécifié'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // URL de la source (à adapter selon tes besoins)
  const getSourceUrl = () => {
    // TODO: Adapter selon tes sources
    switch (offer.source) {
      case 'freework':
        return `https://www.free-work.com/fr/tech-it/mission/${offer.source_id}`
      case 'collective_work':
        return `https://www.collective.work/missions/${offer.source_id}`
      default:
        return '#'
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div 
          className="relative bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-start z-10">
            <div className="flex-1 pr-4">
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                {offer.title}
              </h2>
              {offer.company && (
                <p className="text-lg text-gray-600">
                  {offer.company}
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-2"
              aria-label="Fermer"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-6 space-y-6">
            {/* TJM - Highlight */}
            <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded-r-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Taux Journalier Moyen</p>
                  <p className="text-3xl font-bold text-green-600">{formatTjm()}</p>
                </div>
                <div className="text-5xl">💰</div>
              </div>
            </div>

            {/* Informations principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Localisation */}
              {offer.location && (
                <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl">📍</div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Localisation</p>
                    <p className="text-gray-800">{offer.location}</p>
                  </div>
                </div>
              )}

              {/* Remote Policy */}
              {offer.remote_policy && (
                <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl">🏠</div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Politique de télétravail</p>
                    <p className="text-gray-800">{offer.remote_policy}</p>
                  </div>
                </div>
              )}

              {/* Seniority Level */}
              {offer.seniority_level && (
                <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl">⭐</div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Niveau d'expérience</p>
                    <p className="text-gray-800">{offer.seniority_level}</p>
                  </div>
                </div>
              )}

              {/* Contract Type */}
              {offer.contract_type && (
                <div className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl">📝</div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Type de contrat</p>
                    <p className="text-gray-800">{offer.contract_type}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Description */}
            {offer.description && (
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-2xl mr-2">📄</span>
                  Description de la mission
                </h3>
                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                    {offer.description}
                  </p>
                </div>
              </div>
            )}

            {/* Technologies */}
            {offer.technologies && offer.technologies.length > 0 && (
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-2xl mr-2">💻</span>
                  Technologies requises
                </h3>
                <div className="flex flex-wrap gap-2">
                  {offer.technologies.map((tech, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1.5 bg-blue-100 text-blue-800 text-sm font-medium rounded-full"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Source Information */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <span className="text-2xl mr-2">🔗</span>
                Informations sur la source
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 font-medium mb-1">Plateforme source</p>
                  <p className="text-gray-800 font-semibold capitalize">{offer.source}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 font-medium mb-1">Date de publication</p>
                  <p className="text-gray-800">{formatDate(offer.scraped_at)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer - Action Buttons */}
          <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-between items-center gap-4">
            <button
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Fermer
            </button>
            <a
              href={getSourceUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-green-400 text-white rounded-lg hover:bg-green-500 transition-colors font-semibold flex items-center gap-2"
            >
              <span>Voir l'annonce complète</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
