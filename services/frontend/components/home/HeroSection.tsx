interface HeroSectionProps {
  title?: string
  description?: string
}

export const HeroSection = ({ 
  title = "TJM Analytics - Freelance IT", 
  description = "Analysez les taux journaliers moyens et trouvez les meilleures missions freelance IT en France"
}: HeroSectionProps) => {
  return (
    <section className="bg-gradient-to-r from-blue-600 to-purple-700 text-white py-20">
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
