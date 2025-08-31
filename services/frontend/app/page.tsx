'use client'

import { useEffect, useState } from 'react'

interface TJMStats {
  count: number
  min: number
  max: number
  avg: number
  median: number
}

interface TechStat {
  tech: string
  count: number
}

interface StatsData {
  tjm: TJMStats
  technologies: TechStat[]
  totalOffers: number
}

export default function HomePage() {
  const [stats, setStats] = useState<StatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setError(data.error)
        } else {
          setStats(data)
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading data: {error}</p>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">No data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">TJM Analytics Dashboard</h2>
        
        {/* TJM Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-600">Total Offers</h3>
            <p className="text-2xl font-bold text-blue-900">{stats.totalOffers}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-green-600">Average TJM</h3>
            <p className="text-2xl font-bold text-green-900">{Math.round(stats.tjm.avg)}€</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-purple-600">Median TJM</h3>
            <p className="text-2xl font-bold text-purple-900">{Math.round(stats.tjm.median)}€</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-red-600">Min TJM</h3>
            <p className="text-2xl font-bold text-red-900">{stats.tjm.min}€</p>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-orange-600">Max TJM</h3>
            <p className="text-2xl font-bold text-orange-900">{stats.tjm.max}€</p>
          </div>
        </div>

        {/* Top Technologies */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Technologies</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {stats.technologies.map((tech, index) => (
              <div key={tech.tech} className="text-center">
                <div className="bg-white rounded-lg p-3 shadow-sm">
                  <p className="font-medium text-gray-900">{tech.tech}</p>
                  <p className="text-sm text-gray-600">{tech.count} offers</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
