import Image from 'next/image'
import HeroFontSvg from '@/assets/hero_font.svg'

interface HeroSectionProps {
  title?: string
  description?: string
}

export const HeroSection = ({ 
  title = "Another Weather Application", 
  description = "Another Weather Application - AWA est une application de météo qui vous permet d'analyser les taux journaliers moyens (TJM) des missions freelance en fonction de divers critères tels que la localisation et la technologie. Cela permet de comprendre les tendances du marché et de se positionner au mieux."
}: HeroSectionProps) => {
  return (
    <section className="relative bg-gradient-to-b from-green-200 to-green-100 text-green-950 py-20">
      <div className="container mx-auto px-4">
        <div className="relative p-9">
          <div className="absolute inset-0 opacity-50">
            <Image
              src={HeroFontSvg}
              alt="Background pattern"
              fill
              className="object-contain"
              priority
            />
          </div>
          
          <div className="relative z-10 text-center px-4 py-8">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 drop-shadow-lg">
              {title}
            </h1>
            <p className="text-xl md:text-2xl max-w-3xl mx-auto leading-relaxed drop-shadow-md">
              {description}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
