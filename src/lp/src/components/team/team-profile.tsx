import { AnimatePresence, motion } from "motion/react";
import { ArrowUpRight, X } from "lucide-react";
import { teamInitials, type TeamMember } from "@/lib/team";
import { GLASS } from "@/lib/styles";
import { cn } from "@/lib/utils";

export interface TeamProfileProps {
    member: TeamMember | null;
    onClose: () => void;
}

/**
 * Mini-perfil de um integrante. Usa o mesmo gesto do painel de
 * acompanhamento ao vivo — abre por cima, fecha no X ou no fundo — para o
 * site ter um vocabulário só de "abrir detalhe".
 */
export default function TeamProfile({ member, onClose }: TeamProfileProps) {
    return (
        <AnimatePresence>
            {member && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    onClick={onClose}
                    className="fixed inset-0 z-40 flex items-center justify-center bg-neutral-950/85 p-6 backdrop-blur-md"
                >
                    <motion.article
                        initial={{ scale: 0.94, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                        exit={{ scale: 0.94, y: 20 }}
                        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                        onClick={(event) => event.stopPropagation()}
                        className={cn(GLASS, "relative w-full max-w-md overflow-hidden p-8")}
                    >
                        <button
                            type="button"
                            onClick={onClose}
                            aria-label="Fechar perfil"
                            className="absolute top-4 right-4 flex size-9 cursor-pointer items-center justify-center rounded-full border border-white/10 bg-white/5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
                        >
                            <X className="size-4" />
                        </button>

                        <div className="flex flex-col items-center gap-4 text-center">
                            <span
                                className="flex size-24 items-center justify-center overflow-hidden rounded-full border-4 border-white/10 text-2xl font-medium text-neutral-900"
                                style={{ backgroundColor: member.color }}
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

                            <div className="flex flex-col gap-1">
                                <h3 className="text-xl font-medium text-white">{member.name}</h3>
                                <p className="text-sm font-normal text-indigo-300">
                                    {member.designation}
                                </p>
                            </div>

                            {member.bio && (
                                <p className="text-sm font-normal leading-relaxed text-white/60">
                                    {member.bio}
                                </p>
                            )}

                            {/* As marcas entram como imagem, e não como
                                máscara: são logos coloridas, e achatá-las numa
                                cor só descaracterizaria as duas. */}
                            <div className="mt-2 flex w-full flex-col gap-2">
                                {member.instagram && (
                                    <a
                                        href={member.instagram}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="group/link flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-normal text-white/70 transition-colors hover:border-white/25 hover:bg-white/10 hover:text-white"
                                    >
                                        <img
                                            src="/instagram.svg"
                                            alt=""
                                            className="size-5 shrink-0 transition-transform duration-300 group-hover/link:scale-110"
                                        />
                                        Instagram
                                        <ArrowUpRight className="ml-auto size-4 opacity-50 transition-opacity group-hover/link:opacity-100" />
                                    </a>
                                )}
                                {member.linkedin && (
                                    <a
                                        href={member.linkedin}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="group/link flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-normal text-white/70 transition-colors hover:border-white/25 hover:bg-white/10 hover:text-white"
                                    >
                                        <img
                                            src="/linkedin-logo.png"
                                            alt=""
                                            className="size-5 shrink-0 object-contain transition-transform duration-300 group-hover/link:scale-110"
                                        />
                                        LinkedIn
                                        <ArrowUpRight className="ml-auto size-4 opacity-50 transition-opacity group-hover/link:opacity-100" />
                                    </a>
                                )}
                            </div>
                        </div>
                    </motion.article>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
