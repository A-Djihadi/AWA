import { SearchFormData, Mission, TjmDataPoint } from '@/lib/types'

interface SearchResultsProps {
  results: {
    position: string
    location: string
    tjmEvolution: TjmDataPoint[]
    recentMissions: Mission[]
  } | null
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

const TjmEvolutionChart = ({ data, position }: { 
  data: TjmDataPoint[]
  position: string 
}) => {
  if (data.length === 0) {
    return (
      <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">Aucune donnée d'évolution disponible</p>
      </div>
    )
  }

  const maxTjm = Math.max(...data.map(d => d.tjm))
  const minTjm = Math.min(...data.map(d => d.tjm))

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        Évolution du TJM - {position}
      </h3>
      
      {/* Graphique simplifié - placeholder */}
      <div className="h-64 bg-gradient-to-t from-blue-50 to-blue-100 rounded-lg p-4 relative">
        <div className="absolute top-2 right-2 text-sm text-gray-600">
          Max: {maxTjm}€ | Min: {minTjm}€
        </div>
        
        <div className="h-full flex items-end justify-between space-x-1">
          {data.map((point, index) => {
            const height = ((point.tjm - minTjm) / (maxTjm - minTjm)) * 80 + 20
            return (
              <div key={index} className="flex flex-col items-center">
                <div 
                  className="bg-blue-600 rounded-t"
                  style={{ 
                    width: `${Math.max(100 / data.length - 2, 10)}%`,
                    height: `${height}%` 
                  }}
                />
                <span className="text-xs text-gray-600 mt-1">
                  {new Date(point.date).toLocaleDateString('fr-FR', { 
                    month: 'short' 
                  })}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

const MissionCard = ({ mission }: { mission: Mission }) => {
  const formatTjm = (min: number, max: number) => {
    return min === max ? `${min}€` : `${min}€ - ${max}€`
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border hover:shadow-xl transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-lg font-semibold text-gray-800 line-clamp-2">
          {mission.title}
        </h4>
        <span className="text-lg font-bold text-blue-600 whitespace-nowrap ml-4">
          {formatTjm(mission.tjm_min, mission.tjm_max)}
        </span>
      </div>
      
      <p className="text-gray-600 mb-4 line-clamp-3">
        {mission.description}
      </p>
      
      <div className="flex flex-wrap gap-2 mb-4">
        {mission.technologies.slice(0, 3).map((tech, index) => (
          <span 
            key={index}
            className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
          >
            {tech}
          </span>
        ))}
        {mission.technologies.length > 3 && (
          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded-full">
            +{mission.technologies.length - 3}
          </span>
        )}
      </div>
      
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-500">
          <p>{mission.company}</p>
          <p>{mission.location}</p>
        </div>
        
        <a
          href={mission.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Postuler
        </a>
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

  const { position, location, tjmEvolution, recentMissions } = results

  if (tjmEvolution.length === 0 && recentMissions.length === 0) {
    return (
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <p className="text-yellow-800">Aucun résultat trouvé pour cette recherche.</p>
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="py-12 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Résultats pour "{position}" à {location}
        </h2>
        
        {/* Graphique d'évolution du TJM */}
        <div className="mb-12">
          <TjmEvolutionChart data={tjmEvolution} position={position} />
        </div>
        
        {/* Missions récentes */}
        {recentMissions.length > 0 && (
          <div>
            <h3 className="text-2xl font-semibold mb-6 text-gray-800">
              Missions Récentes ({recentMissions.length})
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentMissions.slice(0, 3).map((mission) => (
                <MissionCard key={mission.id} mission={mission} />
              ))}
            </div>
            
            {recentMissions.length > 3 && (
              <div className="text-center mt-8">
                <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Voir plus de missions ({recentMissions.length - 3})
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
