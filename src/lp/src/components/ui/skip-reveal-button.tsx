import { FastForward } from "lucide-react";
import { cn } from "@/lib/utils";
import { GLASS, GLASS_INTERACTIVE } from "@/lib/styles";

export interface SkipRevealButtonProps {
    onSkip: () => void;
}

/**
 * Aparece só enquanto uma seção de chat está segurando a página, e conclui a
 * conversa na hora para quem não quiser rolar mensagem por mensagem.
 */
export default function SkipRevealButton({ onSkip }: SkipRevealButtonProps) {
    return (
        <button
            type="button"
            onClick={onSkip}
            className={cn(
                "fixed bottom-8 left-1/2 z-40 flex -translate-x-1/2 cursor-pointer items-center gap-2 px-5 py-3 text-sm font-medium text-white/70 hover:text-white",
                GLASS,
                GLASS_INTERACTIVE,
            )}
        >
            <FastForward className="size-4" />
            Pular animação
        </button>
    );
}
