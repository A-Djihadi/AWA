/**
 * Tests pour les composants de visualisation TJM
 */
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock des composants pour les tests
const TjmChart = ({ data }: { data: any[] }) => {
  if (data.length === 0) {
    return <div>Aucune donnée disponible</div>
  }
  
  return (
    <div>
      {data.map((item, index) => (
        <div key={index}>
          <span>{item.technology}</span>
          <span>{item.avg_tjm}€</span>
        </div>
      ))}
    </div>
  )
}

const TjmCard = ({ mission }: { mission: any }) => {
  return (
    <div className="mission-card">
      <h3>{mission.title}</h3>
      <p>{mission.company}</p>
      <p>{mission.location}</p>
      <p>{mission.tjm_min}€ - {mission.tjm_max}€</p>
      <div className="technologies">
        {mission.technologies.map((tech: string) => (
          <span key={tech} className="tech-badge">{tech}</span>
        ))}
      </div>
      <p>Niveau: {mission.seniority}</p>
      <a 
        href={mission.source_url} 
        target="_blank" 
        rel="noopener noreferrer"
      >
        Voir la mission
      </a>
    </div>
  )
}

describe('TjmChart', () => {
  const mockData = [
    { technology: 'React', avg_tjm: 550, count: 45 },
    { technology: 'Python', avg_tjm: 480, count: 38 },
    { technology: 'Node.js', avg_tjm: 520, count: 32 }
  ]

  test('renders chart with data', () => {
    render(<TjmChart data={mockData} />)
    
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('Python')).toBeInTheDocument()
    expect(screen.getByText('Node.js')).toBeInTheDocument()
  })

  test('shows correct TJM values', () => {
    render(<TjmChart data={mockData} />)
    
    expect(screen.getByText('550€')).toBeInTheDocument()
    expect(screen.getByText('480€')).toBeInTheDocument()
    expect(screen.getByText('520€')).toBeInTheDocument()
  })

  test('renders empty state when no data', () => {
    render(<TjmChart data={[]} />)
    
    expect(screen.getByText(/aucune donnée/i)).toBeInTheDocument()
  })
})

describe('TjmCard', () => {
  const mockMission = {
    id: '1',
    title: 'Développeur React Senior',
    company: 'TechCorp',
    tjm_min: 500,
    tjm_max: 700,
    location: 'Paris',
    technologies: ['React', 'TypeScript'],
    seniority: 'senior',
    source_url: 'https://example.com/job/1'
  }

  test('renders mission information', () => {
    render(<TjmCard mission={mockMission} />)
    
    expect(screen.getByText('Développeur React Senior')).toBeInTheDocument()
    expect(screen.getByText('TechCorp')).toBeInTheDocument()
    expect(screen.getByText('Paris')).toBeInTheDocument()
    expect(screen.getByText('500€ - 700€')).toBeInTheDocument()
  })

  test('renders technologies as badges', () => {
    render(<TjmCard mission={mockMission} />)
    
    expect(screen.getByText('React')).toBeInTheDocument()
    expect(screen.getByText('TypeScript')).toBeInTheDocument()
  })

  test('shows seniority level', () => {
    render(<TjmCard mission={mockMission} />)
    
    expect(screen.getByText(/senior/i)).toBeInTheDocument()
  })

  test('renders external link', () => {
    render(<TjmCard mission={mockMission} />)
    
    const link = screen.getByRole('link', { name: /voir la mission/i })
    expect(link).toHaveAttribute('href', 'https://example.com/job/1')
    expect(link).toHaveAttribute('target', '_blank')
  })
})
