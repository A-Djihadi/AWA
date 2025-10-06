import { LocationData } from '@/lib/types'
import { useMemo } from 'react'

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

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

interface SummaryCardProps {
  title: string
  location: LocationData | null
  value: number
  unit: string
  icon: React.ReactNode
}

interface WeatherIconProps {
  tjm: number
  minTjm: number
  maxTjm: number
}

interface FranceMapProps {
  locations: LocationData[]
}

interface Position {
  x: number
  y: number
}

// ============================================================================
// CONSTANTS
// ============================================================================

const CITY_POSITIONS: Record<string, Position> = {
  Paris: { x: 165, y: 85 },
  Lyon: { x: 195, y: 145 },
  Marseille: { x: 215, y: 195 },
  Toulouse: { x: 105, y: 190 },
  Bordeaux: { x: 65, y: 155 },
  Nantes: { x: 45, y: 110 },
  Lille: { x: 150, y: 25 },
  Strasbourg: { x: 260, y: 90 },
  Rennes: { x: 30, y: 95 },
  Nice: { x: 245, y: 200 },
  Montpellier: { x: 175, y: 185 },
  Grenoble: { x: 210, y: 155 },
  Dijon: { x: 195, y: 105 },
  'Clermont-Ferrand': { x: 145, y: 145 },
} as const

const FRANCE_MAP_PATH = 
  "M12.369 66.6153C56.9575 69.4202 127.821 25.5431 142.253 1C194.505 29.0493 236.307 57.5995 280.099 57.5994C323.891 57.5994 168.628 150.262 301 210.368C274.625 276.484 192.017 229.902 183.557 216.379C175.097 202.855 107.418 260.423 116.376 260.957C125.333 261.491 2.42838 257.507 45.7109 223.391C128.319 158.276 -43.3666 63.1091 12.369 66.6153Z"

const WEATHER_THRESHOLDS = {
  SUNNY: 0.66,
  CLOUDY: 0.33,
} as const

const SUN_RAY_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315] as const

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

const normalizeCity = (city: string): string => {
  return city
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z]/g, '')
}

const calculateTjmRatio = (tjm: number, minTjm: number, maxTjm: number): number => {
  return maxTjm === minTjm ? 0.5 : (tjm - minTjm) / (maxTjm - minTjm)
}

const getTjmRange = (locations: LocationData[]): { minTjm: number; maxTjm: number } => {
  if (locations.length === 0) return { minTjm: 0, maxTjm: 0 }
  
  const tjmValues = locations.map(loc => loc.averageTjm)
  return {
    minTjm: Math.min(...tjmValues),
    maxTjm: Math.max(...tjmValues),
  }
}

const calculateLocationSummary = (locations: LocationData[]): LocationSummary => {
  const emptyResponse = { highestTjm: null, lowestTjm: null, mostActive: null, leastActive: null }
  
  if (locations.length === 0) return emptyResponse

  const sortedByTjm = [...locations].sort((a, b) => b.averageTjm - a.averageTjm)
  const sortedByActivity = [...locations].sort((a, b) => b.offerCount - a.offerCount)

  return {
    highestTjm: sortedByTjm[0],
    lowestTjm: sortedByTjm[sortedByTjm.length - 1],
    mostActive: sortedByActivity[0],
    leastActive: sortedByActivity[sortedByActivity.length - 1],
  }
}

const calculateMarketStats = (locations: LocationData[]) => {
  const totalMissions = locations.reduce((sum, loc) => sum + loc.offerCount, 0)
  const averageMarketTjm = locations.length > 0
    ? Math.round(locations.reduce((sum, loc) => sum + loc.averageTjm, 0) / locations.length)
    : 0

  return { totalMissions, averageMarketTjm }
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

const SummaryCard = ({ title, location, value, unit, icon }: SummaryCardProps) => {
  if (!location) return null

  return (
    <div className="bg-white p-4 rounded-lg shadow-md border">
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-semibold text-gray-700">{title}</h4>
        <div className="ml-2">{icon}</div>
      </div>
      <p className="text-lg font-bold text-blue-600">
        {location.city}, {location.region}
      </p>
      <p className="text-sm text-gray-600">
        {value} {unit}
      </p>
    </div>
  )
}

const SunnyWeatherIcon = () => (
  <g className="weather-icon">
    <circle cx="0" cy="0" r="8" fill="#FFD700" />
    {SUN_RAY_ANGLES.map((angle) => (
      <line
        key={angle}
        x1={Math.cos((angle * Math.PI) / 180) * 10}
        y1={Math.sin((angle * Math.PI) / 180) * 10}
        x2={Math.cos((angle * Math.PI) / 180) * 14}
        y2={Math.sin((angle * Math.PI) / 180) * 14}
        stroke="#FFD700"
        strokeWidth="2"
      />
    ))}
  </g>
)

const CloudyWeatherIcon = () => (
  <g className="weather-icon">
    <ellipse cx="-3" cy="0" rx="6" ry="5" fill="#B0C4DE" />
    <ellipse cx="3" cy="2" rx="7" ry="6" fill="#B0C4DE" />
    <ellipse cx="0" cy="-2" rx="5" ry="4" fill="#D3D3D3" />
  </g>
)

const RainyWeatherIcon = () => (
  <g className="weather-icon">
    <ellipse cx="-3" cy="-2" rx="6" ry="5" fill="#778899" />
    <ellipse cx="3" cy="0" rx="7" ry="6" fill="#778899" />
    <ellipse cx="0" cy="-4" rx="5" ry="4" fill="#A9A9A9" />
    {[0, 1, 2].map((i) => (
      <line
        key={i}
        x1={-4 + i * 4}
        y1="6"
        x2={-6 + i * 4}
        y2="12"
        stroke="#4682B4"
        strokeWidth="1.5"
      />
    ))}
  </g>
)

const WeatherIcon = ({ tjm, minTjm, maxTjm }: WeatherIconProps) => {
  const ratio = calculateTjmRatio(tjm, minTjm, maxTjm)

  if (ratio > WEATHER_THRESHOLDS.SUNNY) return <SunnyWeatherIcon />
  if (ratio > WEATHER_THRESHOLDS.CLOUDY) return <CloudyWeatherIcon />
  return <RainyWeatherIcon />
}

const SunnyWeatherIconSVG = () => (
  <svg width="32" height="32" viewBox="-16 -16 32 32" className="inline-block">
    <circle cx="0" cy="0" r="8" fill="#FFD700" />
    {SUN_RAY_ANGLES.map((angle) => (
      <line
        key={angle}
        x1={Math.cos((angle * Math.PI) / 180) * 10}
        y1={Math.sin((angle * Math.PI) / 180) * 10}
        x2={Math.cos((angle * Math.PI) / 180) * 14}
        y2={Math.sin((angle * Math.PI) / 180) * 14}
        stroke="#FFD700"
        strokeWidth="2"
      />
    ))}
  </svg>
)

const CloudyWeatherIconSVG = () => (
  <svg width="32" height="32" viewBox="-16 -16 32 32" className="inline-block">
    <ellipse cx="-3" cy="0" rx="6" ry="5" fill="#B0C4DE" />
    <ellipse cx="3" cy="2" rx="7" ry="6" fill="#B0C4DE" />
    <ellipse cx="0" cy="-2" rx="5" ry="4" fill="#D3D3D3" />
  </svg>
)

const RainyWeatherIconSVG = () => (
  <svg width="32" height="32" viewBox="-16 -16 32 32" className="inline-block">
    <ellipse cx="-3" cy="-2" rx="6" ry="5" fill="#778899" />
    <ellipse cx="3" cy="0" rx="7" ry="6" fill="#778899" />
    <ellipse cx="0" cy="-4" rx="5" ry="4" fill="#A9A9A9" />
    {[0, 1, 2].map((i) => (
      <line
        key={i}
        x1={-4 + i * 4}
        y1="6"
        x2={-6 + i * 4}
        y2="12"
        stroke="#4682B4"
        strokeWidth="1.5"
      />
    ))}
  </svg>
)

const getWeatherIconSVG = (tjm: number, minTjm: number, maxTjm: number): React.ReactNode => {
  const ratio = calculateTjmRatio(tjm, minTjm, maxTjm)

  if (ratio > WEATHER_THRESHOLDS.SUNNY) return <SunnyWeatherIconSVG />
  if (ratio > WEATHER_THRESHOLDS.CLOUDY) return <CloudyWeatherIconSVG />
  return <RainyWeatherIconSVG />
}

const FranceMap = ({ locations }: FranceMapProps) => {
  const { minTjm, maxTjm } = useMemo(() => getTjmRange(locations), [locations])

  const locationMap = useMemo(() => {
    const map = new Map<string, LocationData>()
    locations.forEach((loc) => {
      const normalized = normalizeCity(loc.city)
      map.set(normalized, loc)
    })
    return map
  }, [locations])

  return (
    <svg viewBox="0 0 320 280" className="w-full h-full">
      <path
        d={FRANCE_MAP_PATH}
        fill="#E8F5E9"
        stroke="#4CAF50"
        strokeWidth="2"
      />

      {Object.entries(CITY_POSITIONS).map(([cityName, pos]) => {
        const location = locationMap.get(normalizeCity(cityName))
        if (!location) return null

        return (
          <g key={cityName} transform={`translate(${pos.x}, ${pos.y})`}>
            <WeatherIcon tjm={location.averageTjm} minTjm={minTjm} maxTjm={maxTjm} />
            <circle cx="0" cy="0" r="2" fill="#333" opacity="0.3" />
          </g>
        )
      })}
    </svg>
  )
}

const MarketStatsCards = ({ 
  totalMissions, 
  averageMarketTjm, 
  cityCount 
}: { 
  totalMissions: number
  averageMarketTjm: number
  cityCount: number
}) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
    <div className="text-center p-4 bg-green-50 rounded-lg">
      <div className="text-3xl font-bold text-green-600">{totalMissions}</div>
      <div className="text-sm text-gray-600 mt-1">Missions disponibles</div>
    </div>
    <div className="text-center p-4 bg-blue-50 rounded-lg">
      <div className="text-3xl font-bold text-blue-600">{averageMarketTjm}€</div>
      <div className="text-sm text-gray-600 mt-1">TJM moyen du marché</div>
    </div>
    <div className="text-center p-4 bg-purple-50 rounded-lg">
      <div className="text-3xl font-bold text-purple-600">{cityCount}</div>
      <div className="text-sm text-gray-600 mt-1">Villes couvertes</div>
    </div>
  </div>
)

const LoadingSkeleton = () => (
  <section className="py-16 bg-gray-50">
    <div className="container mx-auto px-4">
      <div className="animate-pulse">
        <div className="h-8 bg-gray-300 rounded w-1/3 mx-auto mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="h-96 bg-gray-300 rounded" />
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-300 rounded" />
            ))}
          </div>
        </div>
      </div>
    </div>
  </section>
)

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const LocationStatsSection = ({ locations, loading = false }: LocationStatsProps) => {
  const summary = useMemo(() => calculateLocationSummary(locations), [locations])
  const { minTjm, maxTjm } = useMemo(() => getTjmRange(locations), [locations])
  const { totalMissions, averageMarketTjm } = useMemo(
    () => calculateMarketStats(locations),
    [locations]
  )

  if (loading) return <LoadingSkeleton />

  return (
    <section className="py-16 bg-gradient-to-b from-green-100 to-white">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-4 text-gray-800">
          Récapitulatif du Marché Freelance
        </h2>

        {/* Introduction Section */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-gray-700 text-lg leading-relaxed mb-4">
              Bienvenue sur <span className="font-bold text-green-600">AWA</span>, votre plateforme
              de référence pour trouver des missions freelance en France. Découvrez en temps réel
              les opportunités disponibles et les tendances du marché.
            </p>
            <MarketStatsCards
              totalMissions={totalMissions}
              averageMarketTjm={averageMarketTjm}
              cityCount={locations.length}
            />
          </div>
        </div>

        <h3 className="text-2xl font-semibold text-center mb-8 text-gray-700">
          Répartition Géographique des Missions
        </h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* France Map */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h3 className="text-xl font-semibold mb-4 text-gray-700">
              🗺️ Carte des TJM par Ville
            </h3>
            <div className="aspect-square w-full">
              <FranceMap locations={locations} />
            </div>
          </div>

          {/* Summary Cards */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-6 text-gray-700"> Synthèse des Données</h3>

            <SummaryCard
              title="TJM le plus élevé"
              location={summary.highestTjm}
              value={summary.highestTjm?.averageTjm || 0}
              unit="€/jour"
              icon={getWeatherIconSVG(summary.highestTjm?.averageTjm || maxTjm, minTjm, maxTjm)}
            />

            <SummaryCard
              title="TJM le plus bas"
              location={summary.lowestTjm}
              value={summary.lowestTjm?.averageTjm || 0}
              unit="€/jour"
              icon={getWeatherIconSVG(summary.lowestTjm?.averageTjm || minTjm, minTjm, maxTjm)}
            />

            <SummaryCard
              title="Zone la plus active"
              location={summary.mostActive}
              value={summary.mostActive?.offerCount || 0}
              unit="missions"
              icon={getWeatherIconSVG(summary.mostActive?.averageTjm || 0, minTjm, maxTjm)}
            />

            <SummaryCard
              title="Zone la moins active"
              location={summary.leastActive}
              value={summary.leastActive?.offerCount || 0}
              unit="missions"
              icon={getWeatherIconSVG(summary.leastActive?.averageTjm || 0, minTjm, maxTjm)}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
