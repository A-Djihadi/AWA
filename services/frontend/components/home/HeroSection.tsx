interface HeroSectionProps {
  title?: string
  description?: string
}

export const HeroSection = ({ 
  title = "Another Weather Application", 
  description = " Another Weather Application - AWA est une application de météo qui vous permet d'analyser les taux journaliers moyens (TJM) des missions freelance en fonction de divers critères tels que la localisation et la technologie. Cela permet de comprendre les tendances du marché et de se positionner au mieux."

}: HeroSectionProps) => {
  return (
    <section className="bg-gradient-to-b from-blue-600 to-purple-700 text-white py-20">
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          {title}
        </h1>
        <p className="text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed">
          {description}
        </p>
      </div>
    </section>
  )
}
