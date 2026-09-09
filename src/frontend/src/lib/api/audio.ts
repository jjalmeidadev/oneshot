/**
 * Rota de audio — `POST /api/audio` (`app/main.py`).
 *
 * Contrato multipart: campo `audio` obrigatorio, `conversation_id` e `language`
 * opcionais, e o cabecalho `Authorization: Bearer <token>` sempre exigido —
 * `resolve_identity` recusa a requisicao sem ele com `401 UNAUTHENTICATED`.
 *
 * A identidade **nao** e emitida por este backend. Ela vem do Microsoft Entra
 * ID (Secao 6.2.4); enquanto o ambiente corporativo nao existe, o backend usa o
 * mapa simulado `AUDIO_SIMULATED_IDENTITIES`. O frontend so repassa o token que
 * receber do canal.
 */

import { requestJson } from './client';
import { AUDIO_DEFAULT_LANGUAGE } from './constants';
import type { AudioUploadResponse } from './schemas';

export type UploadAudioInput = {
  audio: Blob;
  /** Nome do arquivo enviado no multipart; o backend infere o continer do conteudo. */
  filename?: string;
  conversationId?: string | null;
  language?: string;
  /**
   * Token que o canal entrega junto da mensagem. Ainda nao ha fonte de
   * identidade nesta interface — ver README, "Ponto de integracao 3".
   */
  accessToken: string;
  signal?: AbortSignal;
};

export async function uploadAudio(
  input: UploadAudioInput,
): Promise<AudioUploadResponse> {
  const form = new FormData();
  form.append('audio', input.audio, input.filename ?? 'gravacao.ogg');
  if (input.conversationId) {
    form.append('conversation_id', input.conversationId);
  }
  form.append('language', input.language ?? AUDIO_DEFAULT_LANGUAGE);

  // `Content-Type` fica de fora de proposito: o navegador precisa gerar o
  // boundary do multipart, e defini-lo aqui quebraria o parse no FastAPI.
  return requestJson<AudioUploadResponse>('/audio', {
    method: 'POST',
    headers: { Authorization: `Bearer ${input.accessToken}` },
    body: form,
    signal: input.signal,
  });
}
