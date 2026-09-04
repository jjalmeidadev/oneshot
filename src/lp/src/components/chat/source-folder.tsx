import { useEffect, useState } from "react";
import { Check, FileText } from "lucide-react";
import { Folder } from "@/components/ui/folder";
import { SOURCE_FOCUS_EVENT } from "@/components/ui/ghost-documents";
import { cn } from "@/lib/utils";

export interface SourceFolderProps {
    label: string;
    documents: string[];
}

/**
 * A pasta de fontes que aparece nas respostas do chat 2: passar o mouse abre
 * a pasta, clicar lista os documentos que sustentam a resposta para o
 * visitante escolher de qual deles veio o dado.
 */
export default function SourceFolder({ label, documents }: SourceFolderProps) {
    const [open, setOpen] = useState(false);
    const [selected, setSelected] = useState<string | null>(null);

    // Avisa o fundo da seção: o documento fantasma correspondente acende
    // quando a pasta entra em cena e a cada vez que ela é aberta.
    useEffect(() => {
        window.dispatchEvent(new CustomEvent(SOURCE_FOCUS_EVENT));
    }, [open]);

    return (
        // `pointer-events-auto`: enquanto o chat 2 ainda está preso na seção
        // (a janela só libera eventos depois de expandir), a pasta é a única
        // parte que continua clicável — ela já nasce interativa.
        <div className="pointer-events-auto mt-3 flex flex-col gap-2 border-t border-white/10 pt-3">
            <span className="text-[10px] font-normal uppercase tracking-widest text-white/40">
                {label}
            </span>

            <button
                type="button"
                onClick={() => setOpen((value) => !value)}
                aria-expanded={open}
                aria-label={open ? "Fechar lista de documentos" : "Abrir lista de documentos"}
                className="w-fit rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-amber-400/60"
            >
                {/* A pasta tem 240x160 por construção; meia escala encaixa no balão. */}
                <span className="block h-[80px] w-[120px] overflow-hidden">
                    <Folder className="origin-top-left scale-50" />
                </span>
            </button>

            <span className="text-[11px] font-normal text-white/40">
                {open ? "Escolha o documento" : "Clique na pasta para ver os documentos"}
            </span>

            {open && (
                <ul className="flex flex-col gap-1">
                    {documents.map((document) => {
                        const isSelected = selected === document;
                        return (
                            <li key={document}>
                                <button
                                    type="button"
                                    onClick={() => setSelected(document)}
                                    className={cn(
                                        "flex w-full items-start gap-2 rounded-lg px-2 py-1.5 text-left text-xs font-normal transition-colors",
                                        isSelected
                                            ? "bg-amber-400/15 text-amber-100"
                                            : "text-white/60 hover:bg-white/10 hover:text-white",
                                    )}
                                >
                                    {isSelected ? (
                                        <Check className="mt-0.5 size-3.5 shrink-0" />
                                    ) : (
                                        <FileText className="mt-0.5 size-3.5 shrink-0" />
                                    )}
                                    <span className="min-w-0 break-words">{document}</span>
                                </button>
                            </li>
                        );
                    })}
                </ul>
            )}
        </div>
    );
}
