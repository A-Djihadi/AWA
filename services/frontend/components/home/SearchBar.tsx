import { useState } from 'react'

interface SearchFormData {
  position: string
  location: string
}

interface SearchBarProps {
  onSearch: (data: SearchFormData) => void
  loading?: boolean
}

export const SearchBar = ({ onSearch, loading = false }: SearchBarProps) => {
  const [formData, setFormData] = useState<SearchFormData>({
    position: '',
    location: ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.position.trim() && formData.location.trim()) {
      onSearch(formData)
    }
  }

  const handleInputChange = (field: keyof SearchFormData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }))
  }

  const isFormValid = formData.position.trim() && formData.location.trim()

  return (
    <section className="py-12 bg-white">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Rechercher des Missions
        </h2>
        
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex items-center bg-gray-100 rounded-full p-2 shadow-lg">
            {/* Icône de recherche */}
            <div className="flex items-center justify-center w-12 h-12 text-gray-500">
              <svg 
                className="w-5 h-5" 
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

            {/* Zone de saisie poste */}
            <div className="flex-1 px-4">
              <input
                type="text"
                placeholder="Poste recherché (ex: Développeur React)"
                value={formData.position}
                onChange={handleInputChange('position')}
                className="w-full p-3 bg-transparent border-none outline-none text-gray-700 placeholder-gray-500"
                disabled={loading}
              />
            </div>

            {/* Séparateur */}
            <div className="w-px h-8 bg-gray-300" />

            {/* Icône de localisation */}
            <div className="flex items-center justify-center w-12 h-12 text-gray-500">
              <svg 
                className="w-5 h-5" 
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

            {/* Zone de saisie localisation */}
            <div className="flex-1 px-4">
              <input
                type="text"
                placeholder="Localisation (ex: Paris, Lyon, Remote)"
                value={formData.location}
                onChange={handleInputChange('location')}
                className="w-full p-3 bg-transparent border-none outline-none text-gray-700 placeholder-gray-500"
                disabled={loading}
              />
            </div>

            {/* Bouton de recherche */}
            <button
              type="submit"
              disabled={!isFormValid || loading}
              className={`
                px-8 py-3 rounded-full font-semibold transition-all duration-200
                ${isFormValid && !loading
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg' 
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                  <span>Recherche...</span>
                </div>
              ) : (
                'Rechercher'
              )}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}
