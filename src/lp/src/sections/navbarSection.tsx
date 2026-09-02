import { useCallback, useEffect, useRef, useState } from "react";
import AnimatedNavLink from "@/components/navbar/navbar";
import { cn } from "@/lib/utils";

/** `target: null` = topo da página; senão, o seletor da seção de destino. */
const LINKS = [
    { label: "Home", href: "#topo", target: null },
    { label: "Modelo", href: "#modelo", target: "#modelo" },
    { label: "Integração", href: "#integracao", target: "#integracao" },
];

/** Ignore scroll jitter below this many pixels. */
const DIRECTION_THRESHOLD = 6;
/** Near the top of the page the navbar is always available. */
const TOP_ZONE = 80;

function NavbarSection() {
    const [visible, setVisible] = useState(true);
    const [overTakeover, setOverTakeover] = useState(false);
    const lastYRef = useRef(0);

    // Only shows up when the page is scrolled back up (or when the visitor is
    // at the very top) — scrolling down tucks it away.
    useEffect(() => {
        lastYRef.current = window.scrollY;

        const onScroll = () => {
            const y = window.scrollY;
            const delta = y - lastYRef.current;
            if (Math.abs(delta) < DIRECTION_THRESHOLD) return;
            lastYRef.current = y;
            setVisible(y <= TOP_ZONE || delta < 0);
        };

        window.addEventListener("scroll", onScroll, { passive: true });
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    // The "Converse com o OneShot" section takes the whole screen, so the
    // navbar stays out of the way there whichever way the page is moving.
    useEffect(() => {
        const target = document.querySelector("[data-try-section]");
        if (!target) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                setOverTakeover(entry.isIntersecting && entry.intersectionRatio >= 0.35);
            },
            { threshold: [0, 0.2, 0.35, 0.6, 1] },
        );
        observer.observe(target);
        return () => observer.disconnect();
    }, []);

    // Navegação por JS em vez do salto nativo da âncora: assim o percurso é
    // suave sem precisar de `scroll-behavior: smooth` global, que tornaria
    // suaves também as correções instantâneas de scroll das seções de chat.
    const goTo = useCallback(
        (selector: string | null) => (event: React.MouseEvent<HTMLAnchorElement>) => {
            event.preventDefault();
            if (!selector) {
                window.scrollTo({ top: 0, behavior: "smooth" });
                return;
            }
            const destination = document.querySelector<HTMLElement>(selector);
            if (!destination) return;
            window.scrollTo({
                top: window.scrollY + destination.getBoundingClientRect().top,
                behavior: "smooth",
            });
        },
        [],
    );

    const hidden = overTakeover || !visible;
    const shell =
        "flex items-center rounded-2xl border border-white/10 bg-white/5 shadow-lg backdrop-blur-xl";

    return (
        <div
            className={cn(
                "fixed inset-x-0 top-4 z-50 grid grid-cols-[1fr_auto_1fr] items-center gap-3 px-4 transition-[opacity,transform] duration-500 ease-out md:px-8",
                hidden && "pointer-events-none -translate-y-24 opacity-0",
            )}
            aria-hidden={hidden}
        >
            {/* Logo do Inteli e wordmark do OneShot ficam soltos nas pontas,
                sem casca de vidro — só a marca, na mesma altura visual (28px). */}
            <a
                href="#topo"
                onClick={goTo(null)}
                aria-label="Inteli — topo da página"
                className="justify-self-start"
            >
                <img
                    src="/inteli-logo.png"
                    alt="Inteli"
                    className="h-7 w-auto brightness-0 invert"
                />
            </a>

            <nav className={cn(shell, "justify-self-center gap-8 px-8 py-4")}>
                {LINKS.map((link) => (
                    <AnimatedNavLink
                        key={link.label}
                        label={link.label}
                        href={link.href}
                        onSelect={goTo(link.target)}
                    />
                ))}
            </nav>

            <a
                href="#topo"
                onClick={goTo(null)}
                className="justify-self-end text-2xl leading-7 font-medium tracking-tight text-white transition-opacity duration-300 hover:opacity-70"
            >
                OneShot
            </a>
        </div>
    );
}

export default NavbarSection;
