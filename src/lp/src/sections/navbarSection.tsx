import AnimatedNavLink from "@/components/navbar/navbar";

const links = ["Home", "Modelo", "Integração"];

function NavbarSection() {
    return (
        <div className="fixed top-4 left-1/2 z-50 -translate-x-1/2">
            <nav className="flex items-center gap-8 rounded-2xl border border-white/10 bg-white/5 px-8 py-4 shadow-lg backdrop-blur-xl">
                {links.map((link) => (
                    <AnimatedNavLink
                        key={link}
                        label={link}
                    />
                ))}
            </nav>
        </div>
    );
}

export default NavbarSection;