import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { HandwritingText } from '../components/ui/handwriting-text'

gsap.registerPlugin(ScrollTrigger)

const SUBTITLE = 'Descubra como o OneShot pode transformar sua experiência de trabalho'

/**
 * Por palavra: `speed` é o quanto ela sobe (camadas em velocidades
 * diferentes) e `lag` é o atraso com que ela persegue o scroll — no
 * ScrollTrigger isso é o próprio valor de `scrub`, que já é uma perseguição
 * suavizada. É a combinação dos dois que dá o efeito de camadas se
 * desmontando, cada uma no seu tempo.
 */
const WORD_SPEED = [1, 1.45, 0.75, 1.2, 0.9, 1.6, 1.05]
const WORD_LAG = [0.5, 1.1, 0.75, 1.5, 0.9, 1.25, 0.65]

function HeroSection() {
    const sectionRef = useRef<HTMLElement>(null)

    useEffect(() => {
        const section = sectionRef.current
        if (!section) return

        const ctx = gsap.context(() => {
            // O título sai como um bloco só, com pouco atraso: é a camada
            // "próxima" da câmera.
            gsap.to('[data-hero-title]', {
                yPercent: -55,
                opacity: 0,
                filter: 'blur(8px)',
                ease: 'none',
                scrollTrigger: {
                    trigger: section,
                    start: 'top top',
                    end: 'bottom 45%',
                    scrub: 0.4,
                },
            })

            // Cada palavra do subtítulo é a sua própria camada.
            gsap.utils.toArray<HTMLElement>('[data-hero-word]').forEach((word, index) => {
                const speed = WORD_SPEED[index % WORD_SPEED.length]
                const lag = WORD_LAG[index % WORD_LAG.length]

                gsap.to(word, {
                    y: -150 * speed,
                    x: index % 2 === 0 ? -18 * speed : 22 * speed,
                    opacity: 0,
                    filter: 'blur(6px)',
                    ease: 'none',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top top',
                        end: 'bottom 45%',
                        scrub: lag,
                    },
                })
            })
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
                className="flex max-w-2xl flex-wrap justify-center gap-x-[0.3em] text-lg text-gray-200 sm:text-2xl"
            >
                {SUBTITLE.split(' ').map((word, index) => (
                    <span
                        key={`${word}-${index}`}
                        data-hero-word
                        className="inline-block will-change-transform"
                    >
                        {word}
                    </span>
                ))}
            </p>
        </section>
    )
}
export default HeroSection
