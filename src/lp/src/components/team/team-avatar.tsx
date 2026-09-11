import { teamInitials, type TeamMember } from "@/lib/team";
import { cn } from "@/lib/utils";

export interface TeamAvatarProps {
    member: TeamMember;
    /** Baixa a saturação e o brilho — usado no rodapé, onde a cor cheia
     *  competiria com o resto do conteúdo. */
    muted?: boolean;
    className?: string;
    children?: React.ReactNode;
}

/**
 * Avatar de um integrante: a foto, quando existir, ou as iniciais sobre a
 * cor de destaque da pessoa.
 */
export default function TeamAvatar({ member, muted, className, children }: TeamAvatarProps) {
    // O círculo recorta o que passa dele (`overflow-hidden`), então o rótulo
    // fica fora dele: dentro, ficaria cortado e não apareceria no hover.
    return (
        <span className="relative inline-flex">
            <span
                className={cn(
                    "flex size-10 items-center justify-center overflow-hidden rounded-full border-2 text-sm font-medium",
                    muted
                        ? "border-white/10 text-neutral-900/70"
                        : "border-white/20 text-neutral-900",
                    className,
                )}
                style={{
                    backgroundColor: member.color,
                    filter: muted ? "saturate(0.55) brightness(0.82)" : undefined,
                }}
            >
                {member.imageSrc ? (
                    <img
                        src={member.imageSrc}
                        alt={member.name}
                        className="size-full object-cover"
                    />
                ) : (
                    teamInitials(member.name)
                )}
            </span>
            {children}
        </span>
    );
}
