import { HeroHighlight } from '../components/ui/hero-highlight'

function HeroSection() {
    return (
        <HeroHighlight containerClassName="h-screen">
            <div className="flex flex-col items-center justify-center gap-4 text-center">
                <h1 className="text-4xl font-bold text-black dark:text-white sm:text-5xl lg:text-6xl">
                    Bem-vindo ao OneShot
                </h1>
                <p className="max-w-2xl text-lg text-gray-600 dark:text-gray-300 sm:text-xl">
                    Esse é o subtitulo da Hero section
                </p>
            </div>
        </HeroHighlight>
    )
}
export default HeroSection