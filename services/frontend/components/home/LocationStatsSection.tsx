import { LocationData } from '@/lib/types'

interface LocationStatsProps {
  locations: LocationData[]
  loading: boolean
  error?: string | null
}

interface LocationSummary {
  highestTjm: LocationData | null
  lowestTjm: LocationData | null
  mostActive: LocationData | null
  leastActive: LocationData | null
}

const calculateLocationSummary = (locations: LocationData[]): LocationSummary => {
  if (locations.length === 0) {
    return { highestTjm: null, lowestTjm: null, mostActive: null, leastActive: null }
  }

  const sortedByTjm = [...locations].sort((a, b) => b.averageTjm - a.averageTjm)
  const sortedByActivity = [...locations].sort((a, b) => b.offerCount - a.offerCount)

  return {
    highestTjm: sortedByTjm[0],
    lowestTjm: sortedByTjm[sortedByTjm.length - 1],
    mostActive: sortedByActivity[0],
    leastActive: sortedByActivity[sortedByActivity.length - 1]
  }
}

const SummaryCard = ({ title, location, value, unit }: {
  title: string
  location: LocationData | null
  value: number
  unit: string
}) => {
  if (!location) return null

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border">
      <h4 className="font-semibold text-gray-700 mb-2">{title}</h4>
      <p className="text-lg font-bold text-blue-600">
        {location.city}, {location.region}
      </p>
      <p className="text-sm text-gray-600">
        {value} {unit}
      </p>
    </div>
  )
}

export const LocationStatsSection = ({ locations, loading = false }: LocationStatsProps) => {
  const summary = calculateLocationSummary(locations)

  if (loading) {
    return (
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/3 mx-auto mb-8"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="h-96 bg-gray-300 rounded"></div>
              <div className="space-y-4">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-24 bg-gray-300 rounded"></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
          Répartition Géographique des Missions
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Carte de France - Placeholder */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-4 text-gray-700">
              Localisation des Missions
            </h3>
            <div className="h-80 bg-gradient-to-br from-blue-100 to-green-100 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">🗺️</div>
                <p className="text-gray-600">Carte de France interactive</p>
                <p className="text-sm text-gray-500 mt-2">
                  {locations.length} localisations détectées
                </p>
              </div>
            </div>
          </div>

          {/* Synthèse des données */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-6 text-gray-700">
              Synthèse des Données
            </h3>
            
            <SummaryCard
              title="TJM le plus élevé"
              location={summary.highestTjm}
              value={summary.highestTjm?.averageTjm || 0}
              unit="€/jour"
            />
            
            <SummaryCard
              title="TJM le plus bas"
              location={summary.lowestTjm}
              value={summary.lowestTjm?.averageTjm || 0}
              unit="€/jour"
            />
            
            <SummaryCard
              title="Zone la plus active"
              location={summary.mostActive}
              value={summary.mostActive?.offerCount || 0}
              unit="missions"
            />
            
            <SummaryCard
              title="Zone la moins active"
              location={summary.leastActive}
              value={summary.leastActive?.offerCount || 0}
              unit="missions"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
