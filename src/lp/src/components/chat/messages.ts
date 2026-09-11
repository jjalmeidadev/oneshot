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
            "Olá como posso te ajudar? Sou o OneShot, pronto para responder suas perguntas e fornecer informações sobre nossos serviços.",
    },
    { id: "intro-2", sender: "user", content: "Quero conferir o estado de um portfólio." },
    { id: "intro-3", sender: "assistant", content: "Qual portfólio você gostaria de verificar?" },
    { id: "intro-4", sender: "user", content: "Portfólio XPTO." },
    { id: "intro-5", sender: "assistant", content: "Portfólio em andamento." },
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
            "Tudo que eu respondo sobre o Portfólio XPTO vem dos documentos oficiais do projeto. Posso mostrar de onde saiu cada informação.",
    },
    { id: "source-2", sender: "user", content: "De onde veio o status do cronograma?" },
    {
        id: "source-3",
        sender: "assistant",
        content:
            "Do cronograma físico-financeiro anexado ao TAP, na revisão de agosto. Abra a pasta e escolha o documento para conferir.",
        sources: {
            label: "Fontes do Portfólio XPTO",
            // Conversa roteirizada: nomes sem link, porque não há arquivo
            // por trás. As respostas reais do RAG trazem `url` e o item da
            // pasta vira download.
            documents: [
                { name: "TAP — Portfólio XPTO.pdf" },
                { name: "Cronograma físico-financeiro — rev. ago/2026.xlsx" },
                { name: "Nota técnica 12/2026 — acompanhamento.pdf" },
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

/**
 * Conversa do celular: uma única mensagem, convidando à pergunta.
 *
 * No telefone a seção de teste é a única de chat que existe, e ela serve para
 * o visitante perguntar — não para assistir a um diálogo pronto. A conversa
 * roteirizada acima faz sentido no desktop, onde ela é revelada pela rolagem
 * como parte da apresentação; aqui ela só ocuparia a tela e empurraria o
 * campo para fora.
 */
export const MOBILE_INTRO_MESSAGES: ChatMessage[] = [
    {
        id: "mobile-intro",
        sender: "assistant",
        content:
            "Faça uma pergunta sobre o projeto. Eu respondo a partir da documentação do OneShot e mostro de onde veio cada informação.",
    },
];
