'use client'

/**
 * Composant de suggestions de recherche
 * Affiche des exemples cliquables pour faciliter la recherche
 */

interface SearchSuggestion {
  label: string
  tech?: string
  location?: string
  description: string
}

interface SearchSuggestionsProps {
  onSuggestionClick: (tech?: string, location?: string) => void
}

const suggestions: SearchSuggestion[] = [
  {
    label: "🔥 React à Paris",
    tech: "React",
    location: "Paris",
    description: "Missions React dans la capitale"
  },
  {
    label: "🐍 Python Remote",
    tech: "Python",
    location: "Remote",
    description: "Missions Python en télétravail"
  },
  {
    label: "☁️ AWS",
    tech: "AWS",
    description: "Toutes les missions AWS"
  },
  {
    label: "📍 Lyon",
    location: "Lyon",
    description: "Toutes les missions à Lyon"
  },
  {
    label: "⚛️ React",
    tech: "React",
    description: "Toutes les missions React"
  },
  {
    label: "🏙️ Paris",
    location: "Paris",
    description: "Toutes les missions à Paris"
  }
]

export const SearchSuggestions = ({ onSuggestionClick }: SearchSuggestionsProps) => {
  return (
    <div className="mt-6 mb-8">
      <p className="text-sm text-gray-600 mb-3 text-center">
        Suggestions de recherche populaires :
      </p>
      
      <div className="flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSuggestionClick(suggestion.tech, suggestion.location)}
            className="group px-4 py-2 bg-white border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all shadow-sm hover:shadow-md"
            title={suggestion.description}
          >
            <span className="text-sm font-medium text-gray-700 group-hover:text-blue-700">
              {suggestion.label}
            </span>
          </button>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          💡 Astuce : Cliquez sur une suggestion ou saisissez vos propres critères
        </p>
      </div>
    </div>
  )
}
