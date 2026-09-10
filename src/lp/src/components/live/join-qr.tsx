import { useEffect, useState } from "react";
import QRCode from "qrcode";
import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import { GLASS } from "@/lib/styles";

/** Lado do PNG gerado. Grande de propósito: a tela da apresentação é projetada. */
const QR_PIXELS = 640;

/**
 * O convite para entrar na sala pelo celular.
 *
 * O código é gerado a partir de `window.location.origin` — a URL em que a
 * página está de fato publicada. Isso é o ponto: o mesmo componente funciona
 * em `localhost`, no preview da Vercel e em produção, sem ninguém precisar
 * lembrar de atualizar um link.
 *
 * Aparece só em telas grandes. Num celular, um QR para a página que a pessoa
 * já está vendo não serviria para nada — quem precisa dele é a tela projetada,
 * para o visitante apontar a câmera e entrar pela rede dele, sem depender do
 * Wi-Fi do local.
 */
export default function JoinQr({ className }: { className?: string }) {
    const [image, setImage] = useState<string | null>(null);
    // A origem não muda enquanto a página vive, então é estado inicial e não
    // efeito — ler durante a renderização evita um segundo render à toa.
    const [url] = useState(() =>
        typeof window === "undefined" ? "" : window.location.origin,
    );

    useEffect(() => {
        if (!url) return;

        let cancelled = false;
        QRCode.toDataURL(url, {
            width: QR_PIXELS,
            margin: 1,
            errorCorrectionLevel: "M",
            // Módulos escuros sobre branco: é o contraste que as câmeras leem
            // melhor, mesmo projetado. A moldura clara é proposital.
            color: { dark: "#0a0a0b", light: "#ffffff" },
        })
            .then((dataUrl) => {
                if (!cancelled) setImage(dataUrl);
            })
            .catch(() => {
                // Sem o código, o endereço em texto ainda permite entrar.
                if (!cancelled) setImage(null);
            });

        return () => {
            cancelled = true;
        };
    }, [url]);

    if (!url) return null;

    return (
        <motion.aside
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className={cn(GLASS, "flex shrink-0 flex-col items-center gap-3 p-4", className)}
        >
            <span className="text-xs font-medium uppercase tracking-widest text-indigo-300">
                Entre pelo celular
            </span>

            {image ? (
                <img
                    src={image}
                    alt={`QR code para abrir ${url}`}
                    width={QR_PIXELS}
                    height={QR_PIXELS}
                    className="h-40 w-40 rounded-xl bg-white p-2 lg:h-48 lg:w-48"
                />
            ) : (
                <div className="flex h-40 w-40 items-center justify-center rounded-xl border border-white/10 lg:h-48 lg:w-48">
                    <span className="px-3 text-center text-xs font-normal text-white/40">
                        Não foi possível gerar o código
                    </span>
                </div>
            )}

            <p className="text-center text-xs font-normal leading-relaxed text-white/50">
                Aponte a câmera. Abre na rede do seu aparelho — não precisa
                estar no Wi-Fi daqui.
            </p>

            <span className="max-w-full truncate text-[11px] font-normal text-white/30">
                {url.replace(/^https?:\/\//, "")}
            </span>
        </motion.aside>
    );
}
