import Navbar from '../components/Navbar'
import { Analytics } from '../components/Analytics'
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AWA - Analyse du Marché Freelance IT',
  description: 'Découvrez les meilleures missions freelance en France. Analysez les TJM, explorez les opportunités par ville et technologie.',
  keywords: ['freelance', 'IT', 'TJM', 'missions', 'France', 'développeur', 'consultant'],
  authors: [{ name: 'AWA Team' }],
  openGraph: {
    title: 'AWA - Analyse du Marché Freelance IT',
    description: 'Trouvez les meilleures missions freelance en France',
    type: 'website',
    locale: 'fr_FR',
  },
  icons: {
    icon: '/icon.svg',
    apple: '/icon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className="bg-gray-50 min-h-screen">
        {/* Google Analytics */}
        <Analytics gaId={process.env.NEXT_PUBLIC_GA_ID} />
        
        <Navbar />
      
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
        
        <footer className="bg-gray-800 text-white py-8">
          <div className="container mx-auto px-4 text-center">
            <p>&copy; 2024 AWA. Analyse des missions freelance IT en France.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
