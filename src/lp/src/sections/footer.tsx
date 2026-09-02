import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { Mail } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

const WORDMARK = "OneShot";

const LINK_GROUPS = [
    {
        title: "Produto",
        links: [
            { label: "Home", href: "#" },
            { label: "Modelo", href: "#" },
            { label: "Integração", href: "#" },
        ],
    },
    {
        title: "Projeto",
        links: [
            { label: "Documentação", href: "#" },
            { label: "Repositório", href: "#" },
        ],
    },
];

// Os SVGs de marca entram como máscara CSS em vez de <img>: assim o ícone
// herda a cor do texto (`bg-current`) e acompanha o hover, o que um <img>
// com `fill="currentColor"` não faz.
const SOCIALS = [
    { label: "GitHub", href: "#", mask: "/github.svg" },
    { label: "LinkedIn", href: "#", mask: "/linkedin.svg" },
    { label: "E-mail", href: "mailto:contato@oneshot.dev", mask: null },
];

export default function FooterSection() {
    const sectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const section = sectionRef.current;
        if (!section) return;

        const ctx = gsap.context(() => {
            const timeline = gsap.timeline({
                scrollTrigger: {
                    trigger: section,
                    start: "top 85%",
                    toggleActions: "play none none reverse",
                },
            });

            // The rule draws itself across the top, then the wordmark rises
            // letter by letter and the columns follow.
            timeline
                .fromTo(
                    "[data-footer-rule]",
                    { scaleX: 0 },
                    { scaleX: 1, duration: 1, ease: "power3.out" },
                )
                .fromTo(
                    "[data-footer-letter]",
                    { yPercent: 110, opacity: 0 },
                    {
                        yPercent: 0,
                        opacity: 1,
                        duration: 0.9,
                        ease: "power4.out",
                        stagger: 0.05,
                    },
                    "-=0.6",
                )
                .fromTo(
                    "[data-footer-col]",
                    { y: 24, opacity: 0 },
                    { y: 0, opacity: 1, duration: 0.7, ease: "power3.out", stagger: 0.1 },
                    "-=0.6",
                )
                .fromTo(
                    "[data-footer-bottom]",
                    { opacity: 0 },
                    { opacity: 1, duration: 0.6, ease: "none" },
                    "-=0.3",
                );
        }, section);

        return () => ctx.revert();
    }, []);

    return (
        <footer
            ref={sectionRef}
            className="relative mx-auto flex w-full max-w-6xl flex-col gap-12 px-6 pt-20 pb-10 md:px-16"
        >
            <div
                data-footer-rule
                className="h-px w-full origin-left bg-gradient-to-r from-white/30 via-white/10 to-transparent"
            />

            <div className="flex flex-col gap-12 md:flex-row md:items-end md:justify-between">
                {/* Wordmark: cada letra sobe de dentro de uma máscara. */}
                <h2
                    aria-label={WORDMARK}
                    className="flex overflow-hidden text-6xl font-bold leading-none text-white lg:text-8xl"
                >
                    {WORDMARK.split("").map((letter, index) => (
                        <span
                            key={`${letter}-${index}`}
                            data-footer-letter
                            aria-hidden
                            className="inline-block"
                        >
                            {letter}
                        </span>
                    ))}
                </h2>

                <div className="flex flex-wrap gap-12">
                    {LINK_GROUPS.map((group) => (
                        <nav key={group.title} data-footer-col className="flex flex-col gap-3">
                            <span className="text-xs uppercase tracking-widest text-indigo-300">
                                {group.title}
                            </span>
                            {group.links.map((link) => (
                                <a
                                    key={link.label}
                                    href={link.href}
                                    className="group relative w-fit text-sm text-white/60 transition-colors hover:text-white"
                                >
                                    {link.label}
                                    <span className="absolute -bottom-1 left-0 h-px w-full origin-left scale-x-0 bg-current transition-transform duration-300 ease-out group-hover:scale-x-100" />
                                </a>
                            ))}
                        </nav>
                    ))}

                    <div data-footer-col className="flex flex-col gap-3">
                        <span className="text-xs uppercase tracking-widest text-indigo-300">
                            Contato
                        </span>
                        <div className="flex gap-3">
                            {SOCIALS.map(({ label, href, mask }) => (
                                <a
                                    key={label}
                                    href={href}
                                    aria-label={label}
                                    className="flex size-10 items-center justify-center rounded-full border border-white/10 bg-white/5 text-white/60 transition-all duration-300 hover:-translate-y-1 hover:border-white/25 hover:bg-white/10 hover:text-white"
                                >
                                    {mask ? (
                                        <span
                                            aria-hidden
                                            className="size-4 bg-current [mask-position:center] [mask-repeat:no-repeat] [mask-size:contain]"
                                            style={{ maskImage: `url(${mask})`, WebkitMaskImage: `url(${mask})` }}
                                        />
                                    ) : (
                                        <Mail className="size-4" />
                                    )}
                                </a>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div
                data-footer-bottom
                className="flex flex-col gap-2 border-t border-white/10 pt-6 text-xs text-white/40 md:flex-row md:items-center md:justify-between"
            >
                <span className="flex items-center gap-3">
                    <img
                        src="/inteli-logo.png"
                        alt="Inteli"
                        className="h-5 w-auto opacity-60"
                    />
                    ES07 · Grupo 05
                </span>
                <span>© {new Date().getFullYear()} OneShot</span>
            </div>
        </footer>
    );
}
