'use client'

import { useState } from 'react'
import { SearchFormData } from '@/lib/types'
import { useAnalytics } from '@/components/Analytics'

interface SearchBarProps {
  onSearch: (formData: SearchFormData) => void
  isLoading?: boolean
}

export const SearchBar = ({ onSearch, isLoading = false }: SearchBarProps) => {
  const { trackEvent } = useAnalytics()
  const [formData, setFormData] = useState<SearchFormData>({
    technologies: '',
    location: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Tracker l'événement de recherche
    trackEvent('search', {
      search_term: formData.technologies || 'any',
      location: formData.location || 'any',
      has_tech: !!formData.technologies,
      has_location: !!formData.location
    })
    
    onSearch(formData)
  }

  return (
    <section id="search">
      <form onSubmit={handleSubmit} className="max-w-5xl mx-auto">
        {/* Barre de recherche horizontale avec 5 sections */}
        <div className="flex items-center bg-gray-100 rounded-lg shadow-lg overflow-hidden">
            {/* Section 1: Icône de recherche */}
            <div className="flex items-center justify-center px-4 py-4 bg-green-400 text-white">
              <svg 
                className="w-6 h-6" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
                />
              </svg>
            </div>

            {/* Section 2: Saisie technologie */}
            <div className="flex-1 px-4">
              <input
                type="text"
                placeholder="Technologie (ex: React, Python, AWS...)"
                value={formData.technologies}
                onChange={(e) => setFormData({ ...formData, technologies: e.target.value })}
                className="w-full py-4 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
              />
            </div>

            {/* Section 3: Icône de localisation */}
            <div className="flex items-center justify-center px-4 py-4 bg-green-400 text-white border-l border-gray-300">
              <svg 
                className="w-6 h-6" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" 
                />
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" 
                />
              </svg>
            </div>

            {/* Section 4: Saisie localisation */}
            <div className="flex-1 px-4 border-l border-gray-300">
              <input
                type="text"
                placeholder="Localisation (ex: Paris, Lyon, Remote...)"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full py-4 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
              />
            </div>

            {/* Section 5: Bouton de recherche */}
            <button
              type="submit"
              disabled={isLoading || (!formData.technologies && !formData.location)}
              className="px-8 py-4 bg-green-400 text-white font-semibold hover:bg-green-500 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Recherche...' : 'Rechercher'}
            </button>
          </div>

          {/* Message d'aide */}
          <p className="text-center text-gray-500 text-sm mt-4">
            Recherchez des missions freelance par technologie et localisation
          </p>
        </form>
      </section>
  )
}
