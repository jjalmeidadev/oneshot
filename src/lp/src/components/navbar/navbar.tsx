interface AnimatedNavLinkProps {
    label: string;
}

function AnimatedNavLink({ label }: AnimatedNavLinkProps) {
    return (
        <a
            href="#"
            className="group relative cursor-pointer text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
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