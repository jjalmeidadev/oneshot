import type { ChatMessage } from "@/components/chat/chat-messages";

/**
 * Conversa do chat 1 (primeira seção): a apresentação do assistente e uma
 * consulta simples ao portfólio.
 */
export const INTRO_MESSAGES: ChatMessage[] = [
    {
        id: "intro-1",
        sender: "assistant",
        content:
            "Olá como posso te ajudar? Sou o assistente virtual da MetroSP AI, pronto para responder suas perguntas e fornecer informações sobre nossos serviços.",
    },
    { id: "intro-2", sender: "user", content: "Quero conferir o estado do portfólio." },
    { id: "intro-3", sender: "assistant", content: "Qual portfólio você gostaria de verificar?" },
    { id: "intro-4", sender: "user", content: "Portfólio XPTO." },
    { id: "intro-5", sender: "assistant", content: "Portfólio em andamento." },
    { id: "intro-6", sender: "user", content: "Obrigado!" },
];

/**
 * Conversa do chat 2 (seção espelhada e chat expandido): o foco aqui é a
 * procedência do dado — por isso é a única que traz a pasta de fontes.
 */
export const SOURCE_MESSAGES: ChatMessage[] = [
    {
        id: "source-1",
        sender: "assistant",
        content:
            "Tudo que eu respondo sobre o Portfólio XPTO vem dos documentos oficiais do projeto — posso mostrar de onde saiu cada informação.",
    },
    { id: "source-2", sender: "user", content: "De onde veio o status do cronograma?" },
    {
        id: "source-3",
        sender: "assistant",
        content:
            "Do cronograma físico-financeiro anexado ao TAP, na revisão de agosto. Abra a pasta e escolha o documento para conferir.",
        sources: {
            label: "Fontes do Portfólio XPTO",
            documents: [
                "TAP — Portfólio XPTO.pdf",
                "Cronograma físico-financeiro — rev. ago/2026.xlsx",
                "Nota técnica 12/2026 — acompanhamento.pdf",
            ],
        },
    },
    { id: "source-4", sender: "user", content: "É isso mesmo que eu precisava." },
    {
        id: "source-5",
        sender: "assistant",
        content:
            "Toda resposta vem com a fonte junto: é só abrir a pasta e ir direto ao documento original.",
    },
];
