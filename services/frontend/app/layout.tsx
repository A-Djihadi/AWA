import Navbar from '../components/Navbar'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <head>
        <title>TJM Analytics - Freelance IT</title>
        <meta name="description" content="Analysez les taux journaliers moyens et trouvez les meilleures missions freelance IT en France" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="bg-gray-50 min-h-screen">
        <Navbar />
      
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
        
        <footer className="bg-gray-800 text-white py-8">
          <div className="container mx-auto px-4 text-center">
            <p>&copy; 2024 TJM Analytics. Analyse des missions freelance IT en France.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
