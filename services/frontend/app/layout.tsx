export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <head>
        <title>AWA - TJM Analytics</title>
        <meta name="description" content="Analytics platform for freelance daily rates" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="bg-gray-50 min-h-screen">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">AWA</h1>
                <span className="ml-2 text-sm text-gray-500">TJM Analytics</span>
              </div>
              <div className="flex space-x-4">
                <a href="/" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Dashboard
                </a>
                <a href="/offers" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Offers
                </a>
                <a href="/stats" className="text-gray-700 hover:text-gray-900 px-3 py-2">
                  Statistics
                </a>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {children}
        </main>
      </body>
    </html>
  )
}
