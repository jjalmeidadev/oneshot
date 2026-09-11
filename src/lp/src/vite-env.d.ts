/// <reference types="vite/client" />

interface ImportMetaEnv {
    /**
     * Endereço do backend de presença ao vivo (`src/rag/backend`).
     * Ex.: `http://localhost:8000`. Vazio (o padrão) mantém a landing page no
     * modo simulado de `?ao-vivo=N`, sem depender de backend nenhum.
     */
    readonly VITE_LIVE_BACKEND_URL?: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
