import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { HandwritingText } from '../components/ui/handwriting-text'

gsap.registerPlugin(ScrollTrigger)

function HeroSection() {
    const sectionRef = useRef<HTMLElement>(null)

    useEffect(() => {
        const section = sectionRef.current
        if (!section) return

        const ctx = gsap.context(() => {
            // Título e subtítulo somem conforme a hero é deixada para trás:
            // sobem um pouco, desfocam e apagam, tudo preso ao scroll (scrub),
            // então a saída acompanha o gesto e volta se a página subir.
            const timeline = gsap.timeline({
                scrollTrigger: {
                    trigger: section,
                    start: 'top top',
                    end: 'bottom 55%',
                    scrub: 0.5,
                },
            })

            timeline
                .to(
                    '[data-hero-subtitle]',
                    { opacity: 0, y: -40, filter: 'blur(6px)', ease: 'none', duration: 0.7 },
                    0,
                )
                .to(
                    '[data-hero-title]',
                    { opacity: 0, y: -70, filter: 'blur(8px)', ease: 'none', duration: 1 },
                    0.15,
                )
        }, section)

        return () => ctx.revert()
    }, [])

    return (
        <section
            ref={sectionRef}
            className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center"
        >
            <h1
                data-hero-title
                className="text-4xl font-bold text-white sm:text-5xl lg:text-6xl"
            >
                <HandwritingText
                    text="Bem vindo ao Oneshot"
                    className="text-diamond-300 dark:text-diamond-400"
                    height="2.9em"
                    />
                    {' '} 
            </h1>
            <p
                data-hero-subtitle
                className="max-w-2xl text-lg text-indigo-300 font-medium sm:text-xl"
            >
                Descubra como o OneShot pode transformar sua experiência de trabalho
            </p>
        </section>
    )
}
export default HeroSection
