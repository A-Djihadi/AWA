/**
 * Tests pour les utilitaires et fonctions helper
 */
import '@testing-library/jest-dom'

// Fonctions utilitaires à tester
const formatTjm = (min: number, max: number): string => {
  if (min === max) {
    return `${min}€`
  }
  return `${min}€ - ${max}€`
}

const normalizeTechnology = (tech: string): string => {
  const techMap: Record<string, string> = {
    'javascript': 'Javascript',
    'js': 'Javascript',
    'react': 'React',
    'reactjs': 'React',
    'vue': 'Vue.js',
    'vuejs': 'Vue.js',
    'angular': 'Angular',
    'nodejs': 'Node.js',
    'node': 'Node.js',
    'typescript': 'Typescript',
    'ts': 'Typescript'
  }
  
  return techMap[tech.toLowerCase()] || tech
}

const calculateAverageTjm = (missions: Array<{tjm_min: number, tjm_max: number}>): number => {
  if (missions.length === 0) return 0
  
  const total = missions.reduce((sum, mission) => {
    const avg = (mission.tjm_min + mission.tjm_max) / 2
    return sum + avg
  }, 0)
  
  return Math.round(total / missions.length)
}

const filterMissionsBySeniority = (
  missions: Array<{seniority: string}>, 
  seniority: string
): Array<{seniority: string}> => {
  return missions.filter(mission => mission.seniority === seniority)
}

describe('TJM Utilities', () => {
  describe('formatTjm', () => {
    test('formats single TJM value', () => {
      expect(formatTjm(500, 500)).toBe('500€')
    })

    test('formats TJM range', () => {
      expect(formatTjm(400, 600)).toBe('400€ - 600€')
    })

    test('handles edge cases', () => {
      expect(formatTjm(0, 0)).toBe('0€')
      expect(formatTjm(1000, 1500)).toBe('1000€ - 1500€')
    })
  })

  describe('normalizeTechnology', () => {
    test('normalizes JavaScript variants', () => {
      expect(normalizeTechnology('javascript')).toBe('Javascript')
      expect(normalizeTechnology('JS')).toBe('Javascript')
      expect(normalizeTechnology('js')).toBe('Javascript')
    })

    test('normalizes React variants', () => {
      expect(normalizeTechnology('react')).toBe('React')
      expect(normalizeTechnology('reactjs')).toBe('React')
      expect(normalizeTechnology('REACT')).toBe('React')
    })

    test('normalizes Vue variants', () => {
      expect(normalizeTechnology('vue')).toBe('Vue.js')
      expect(normalizeTechnology('vuejs')).toBe('Vue.js')
      expect(normalizeTechnology('VueJS')).toBe('Vue.js')
    })

    test('normalizes Node.js variants', () => {
      expect(normalizeTechnology('nodejs')).toBe('Node.js')
      expect(normalizeTechnology('node')).toBe('Node.js')
      expect(normalizeTechnology('NODE')).toBe('Node.js')
    })

    test('preserves unknown technologies', () => {
      expect(normalizeTechnology('Python')).toBe('Python')
      expect(normalizeTechnology('Java')).toBe('Java')
      expect(normalizeTechnology('Go')).toBe('Go')
    })
  })

  describe('calculateAverageTjm', () => {
    test('calculates average for multiple missions', () => {
      const missions = [
        { tjm_min: 400, tjm_max: 600 }, // avg: 500
        { tjm_min: 500, tjm_max: 700 }, // avg: 600
        { tjm_min: 300, tjm_max: 500 }  // avg: 400
      ]
      // Overall average: (500 + 600 + 400) / 3 = 500
      expect(calculateAverageTjm(missions)).toBe(500)
    })

    test('handles single mission', () => {
      const missions = [{ tjm_min: 500, tjm_max: 700 }]
      expect(calculateAverageTjm(missions)).toBe(600)
    })

    test('returns 0 for empty array', () => {
      expect(calculateAverageTjm([])).toBe(0)
    })

    test('rounds to nearest integer', () => {
      const missions = [
        { tjm_min: 500, tjm_max: 501 }, // avg: 500.5
        { tjm_min: 600, tjm_max: 601 }  // avg: 600.5
      ]
      // Overall average: (500.5 + 600.5) / 2 = 550.5 → 551
      expect(calculateAverageTjm(missions)).toBe(551)
    })
  })

  describe('filterMissionsBySeniority', () => {
    const missions = [
      { seniority: 'junior' },
      { seniority: 'senior' },
      { seniority: 'junior' },
      { seniority: 'medior' },
      { seniority: 'senior' }
    ]

    test('filters junior missions', () => {
      const juniorMissions = filterMissionsBySeniority(missions, 'junior')
      expect(juniorMissions).toHaveLength(2)
      expect(juniorMissions.every(m => m.seniority === 'junior')).toBe(true)
    })

    test('filters senior missions', () => {
      const seniorMissions = filterMissionsBySeniority(missions, 'senior')
      expect(seniorMissions).toHaveLength(2)
      expect(seniorMissions.every(m => m.seniority === 'senior')).toBe(true)
    })

    test('filters medior missions', () => {
      const mediorMissions = filterMissionsBySeniority(missions, 'medior')
      expect(mediorMissions).toHaveLength(1)
      expect(mediorMissions[0].seniority).toBe('medior')
    })

    test('returns empty array for non-existent seniority', () => {
      const expertMissions = filterMissionsBySeniority(missions, 'expert')
      expect(expertMissions).toHaveLength(0)
    })
  })
})

describe('Data Validation', () => {
  const isValidTjmRange = (min: number, max: number): boolean => {
    return min > 0 && max > 0 && min <= max
  }

  const isValidTechnology = (tech: string): boolean => {
    return tech.length > 0 && tech.length <= 50
  }

  const isValidSeniority = (seniority: string): boolean => {
    const validLevels = ['junior', 'medior', 'senior', 'lead', 'expert']
    return validLevels.includes(seniority.toLowerCase())
  }

  describe('isValidTjmRange', () => {
    test('validates correct TJM ranges', () => {
      expect(isValidTjmRange(400, 600)).toBe(true)
      expect(isValidTjmRange(500, 500)).toBe(true)
      expect(isValidTjmRange(1, 1000)).toBe(true)
    })

    test('rejects invalid TJM ranges', () => {
      expect(isValidTjmRange(600, 400)).toBe(false) // min > max
      expect(isValidTjmRange(0, 500)).toBe(false)   // min = 0
      expect(isValidTjmRange(500, 0)).toBe(false)   // max = 0
      expect(isValidTjmRange(-100, 500)).toBe(false) // negative
    })
  })

  describe('isValidTechnology', () => {
    test('validates technology names', () => {
      expect(isValidTechnology('React')).toBe(true)
      expect(isValidTechnology('JavaScript')).toBe(true)
      expect(isValidTechnology('A')).toBe(true)
    })

    test('rejects invalid technology names', () => {
      expect(isValidTechnology('')).toBe(false)
      expect(isValidTechnology('A'.repeat(51))).toBe(false)
    })
  })

  describe('isValidSeniority', () => {
    test('validates seniority levels', () => {
      expect(isValidSeniority('junior')).toBe(true)
      expect(isValidSeniority('SENIOR')).toBe(true)
      expect(isValidSeniority('Medior')).toBe(true)
    })

    test('rejects invalid seniority levels', () => {
      expect(isValidSeniority('beginner')).toBe(false)
      expect(isValidSeniority('master')).toBe(false)
      expect(isValidSeniority('')).toBe(false)
    })
  })
})
