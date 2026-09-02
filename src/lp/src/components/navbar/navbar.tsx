interface AnimatedNavLinkProps {
    label: string;
    href: string;
    onSelect?: (event: React.MouseEvent<HTMLAnchorElement>) => void;
}

function AnimatedNavLink({ label, href, onSelect }: AnimatedNavLinkProps) {
    return (
        <a
            href={href}
            onClick={onSelect}
            className="group relative cursor-pointer text-sm font-medium text-white/60 transition-colors hover:text-white"
        >
            {label}

            <span
                className="
                    absolute
                    -bottom-1
                    left-0
                    h-[1px]
                    w-full
                    origin-left
                    scale-x-0
                    bg-current
                    transition-transform
                    duration-300
                    ease-out
                    group-hover:scale-x-100
                "
            />
        </a>
    );
}

export default AnimatedNavLink;
