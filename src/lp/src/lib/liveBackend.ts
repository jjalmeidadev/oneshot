/**
 * Endereço do backend de presença ao vivo (`src/rag/backend`).
 *
 * Um lugar só para essa configuração, porque dois arquivos precisam dela — o
 * hook que observa a sala e o que entra nela — e duas cópias da mesma
 * normalização de URL divergiriam mais cedo ou mais tarde.
 *
 * `VITE_LIVE_BACKEND_URL` aceita `http://192.168.0.10:8000` (o caso do teste
 * em rede local, em que o celular precisa do IP da máquina e não de
 * `localhost`) ou `/` quando o backend for servido na mesma origem. Vazio — o
 * padrão — deixa a landing page no modo simulado de `?ao-vivo=N`.
 */

const RAW_BACKEND_URL = (import.meta.env.VITE_LIVE_BACKEND_URL ?? "").trim();

/** Há backend configurado? Se não, a página se comporta como sempre se comportou. */
export const HAS_LIVE_BACKEND = RAW_BACKEND_URL !== "";

/** Sem a barra final, para concatenar os caminhos sem duplicá-la. */
const BACKEND_URL = RAW_BACKEND_URL.replace(/\/+$/, "");

/** Rota de leitura da sala inteira (o mesmo corpo que o WebSocket empurra). */
export const LIVE_SESSIONS_PATH = "/api/live/sessions";

export function liveApiUrl(path: string): string {
    return `${BACKEND_URL}${path}`;
}

/** Endereço do canal de observação, derivado do mesmo endereço base. */
export function liveWebsocketUrl(): string {
    const absolute = /^https?:/.test(BACKEND_URL)
        ? BACKEND_URL
        : `${window.location.origin}${BACKEND_URL}`;
    return `${absolute.replace(/^http/, "ws")}/ws/live`;
}
