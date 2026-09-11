import * as React from "react";
import { motion, type Transition } from "motion/react";
import { cn } from "@/lib/utils";

/**
 * Grupo de avatares sobrepostos, com o avatar subindo no hover e um rótulo
 * aparecendo acima dele.
 *
 * Adaptado do componente da comunidade: a versão original depende do tooltip
 * do shadcn (e, por baixo, do Radix), que não faz parte deste projeto. Aqui o
 * rótulo é um elemento próprio, controlado por CSS no hover do item — mesma
 * API, sem dependência nova.
 */
type AvatarGroupProps = Omit<React.ComponentProps<"div">, "translate"> & {
    children: React.ReactElement[];
    transition?: Transition;
    invertOverlap?: boolean;
    translate?: string | number;
};

function AvatarGroup({
    children,
    className,
    transition = { type: "spring", stiffness: 300, damping: 17 },
    invertOverlap = false,
    translate = "-30%",
    ...props
}: AvatarGroupProps) {
    const count = React.Children.count(children);

    return (
        <div
            data-slot="avatar-group"
            className={cn("flex h-10 flex-row items-center -space-x-2", className)}
            {...props}
        >
            {children?.map((child, index) => (
                <motion.div
                    key={index}
                    data-slot="avatar-container"
                    initial="initial"
                    whileHover="hover"
                    whileTap="hover"
                    className="group/avatar relative"
                    style={{ zIndex: invertOverlap ? count - index : index }}
                >
                    <motion.div
                        variants={{ initial: { y: 0 }, hover: { y: translate } }}
                        transition={transition}
                    >
                        {child}
                    </motion.div>
                </motion.div>
            ))}
        </div>
    );
}

function AvatarGroupTooltip({
    children,
    className,
}: {
    children: React.ReactNode;
    className?: string;
}) {
    return (
        <span
            className={cn(
                "pointer-events-none absolute -top-10 left-1/2 -translate-x-1/2 translate-y-1 whitespace-nowrap rounded-lg border border-white/10 bg-neutral-900/95 px-3 py-1.5 text-xs font-normal text-white opacity-0 shadow-lg backdrop-blur-sm transition-all duration-200 group-hover/avatar:translate-y-0 group-hover/avatar:opacity-100",
                className,
            )}
            role="tooltip"
        >
            {children}
        </span>
    );
}

export { AvatarGroup, AvatarGroupTooltip };
export default AvatarGroup;
