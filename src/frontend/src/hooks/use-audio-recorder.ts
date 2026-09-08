import { useCallback, useEffect, useRef, useState } from 'react';

import {
  AUDIO_ACCEPTED_MIME_TYPES,
  AUDIO_MAX_DURATION_SECONDS,
  AUDIO_MAX_SIZE_BYTES,
} from '@/lib/api/constants';

/**
 * Captura de audio no navegador.
 *
 * A captura e responsabilidade do frontend; o envio para `POST /api/audio` e a
 * task de integracao. O hook para no ponto exato dessa fronteira: entrega um
 * `Blob` pronto, com duracao, tamanho e continer ja conferidos contra os
 * limites da Secao 8.7.3, e nao faz nenhuma chamada de rede.
 *
 * O continer importa. A validacao do backend aceita WAV/PCM e OGG/OPUS; o
 * `MediaRecorder` do Chrome grava `audio/webm;codecs=opus`, que seria recusado
 * com `AUDIO_FORMAT_UNSUPPORTED`. Por isso o hook negocia o tipo e expoe
 * `containerAccepted`, para a interface avisar antes de gastar uma requisicao.
 */

export type RecorderState =
  'idle' | 'requesting' | 'recording' | 'recorded' | 'error' | 'unsupported';

export type Recording = {
  blob: Blob;
  mimeType: string;
  durationSeconds: number;
  sizeBytes: number;
  /** `false` quando o navegador so soube gravar um continer que o backend recusa. */
  containerAccepted: boolean;
  /** Acima do teto de 2 MB do endpoint. */
  tooLarge: boolean;
  objectUrl: string;
};

function pickMimeType(): { mimeType: string; accepted: boolean } {
  if (typeof MediaRecorder === 'undefined') {
    return { mimeType: '', accepted: false };
  }

  for (const candidate of AUDIO_ACCEPTED_MIME_TYPES) {
    if (MediaRecorder.isTypeSupported(candidate)) {
      return { mimeType: candidate, accepted: true };
    }
  }

  // Ultimo recurso: grava no que o navegador oferecer, sinalizando que o
  // backend recusaria o arquivo. O Chrome cai aqui, com webm/opus.
  for (const fallback of ['audio/webm;codecs=opus', 'audio/webm']) {
    if (MediaRecorder.isTypeSupported(fallback)) {
      return { mimeType: fallback, accepted: false };
    }
  }

  return { mimeType: '', accepted: false };
}

export function useAudioRecorder() {
  const [state, setState] = useState<RecorderState>('idle');
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [level, setLevel] = useState(0);
  const [recording, setRecording] = useState<Recording | null>(null);
  const [error, setError] = useState<string | null>(null);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const frameRef = useRef<number | null>(null);
  const startedAtRef = useRef(0);
  const timerRef = useRef<number | null>(null);

  const cleanup = useCallback(() => {
    if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    if (timerRef.current !== null) window.clearInterval(timerRef.current);
    frameRef.current = null;
    timerRef.current = null;

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    void audioContextRef.current?.close().catch(() => undefined);
    audioContextRef.current = null;
    recorderRef.current = null;
  }, []);

  useEffect(
    () => () => {
      cleanup();
      if (recording) URL.revokeObjectURL(recording.objectUrl);
    },
    // A limpeza roda apenas na desmontagem; incluir `recording` reiniciaria o
    // efeito a cada gravacao e revogaria a URL ainda em uso pelo player.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const stop = useCallback(() => {
    if (recorderRef.current?.state === 'recording') {
      recorderRef.current.stop();
    }
  }, []);

  const start = useCallback(async () => {
    setError(null);

    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setState('unsupported');
      setError('Este navegador não permite gravar áudio.');
      return;
    }

    setState('requesting');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      const { mimeType, accepted } = pickMimeType();
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };

      recorder.onstop = () => {
        const type = recorder.mimeType || mimeType || 'audio/webm';
        const blob = new Blob(chunksRef.current, { type });
        const durationSeconds = (performance.now() - startedAtRef.current) / 1000;

        setRecording((previous) => {
          if (previous) URL.revokeObjectURL(previous.objectUrl);
          return {
            blob,
            mimeType: type,
            durationSeconds,
            sizeBytes: blob.size,
            containerAccepted: accepted,
            tooLarge: blob.size > AUDIO_MAX_SIZE_BYTES,
            objectUrl: URL.createObjectURL(blob),
          };
        });
        setState('recorded');
        setLevel(0);
        cleanup();
      };

      // Medidor de nivel: so alimenta a animacao da barra de gravacao.
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      audioContext.createMediaStreamSource(stream).connect(analyser);
      const buffer = new Uint8Array(analyser.frequencyBinCount);

      const readLevel = () => {
        analyser.getByteTimeDomainData(buffer);
        let peak = 0;
        for (const sample of buffer) {
          peak = Math.max(peak, Math.abs(sample - 128) / 128);
        }
        setLevel(peak);
        frameRef.current = requestAnimationFrame(readLevel);
      };
      frameRef.current = requestAnimationFrame(readLevel);

      startedAtRef.current = performance.now();
      setElapsedSeconds(0);
      timerRef.current = window.setInterval(() => {
        const elapsed = (performance.now() - startedAtRef.current) / 1000;
        setElapsedSeconds(elapsed);
        // A gravacao para sozinha no limite do endpoint, em vez de deixar o
        // usuario gravar um arquivo que ja seria recusado com AUDIO_TOO_LONG.
        if (elapsed >= AUDIO_MAX_DURATION_SECONDS) {
          recorderRef.current?.stop();
        }
      }, 100);

      recorder.start(250);
      setState('recording');
    } catch (cause) {
      cleanup();
      setState('error');
      setError(
        cause instanceof DOMException && cause.name === 'NotAllowedError'
          ? 'Permissão de microfone negada pelo navegador.'
          : 'Não foi possível acessar o microfone.',
      );
    }
  }, [cleanup]);

  const discard = useCallback(() => {
    setRecording((previous) => {
      if (previous) URL.revokeObjectURL(previous.objectUrl);
      return null;
    });
    setElapsedSeconds(0);
    setLevel(0);
    setError(null);
    setState('idle');
  }, []);

  const cancel = useCallback(() => {
    if (recorderRef.current?.state === 'recording') {
      recorderRef.current.onstop = null;
      recorderRef.current.stop();
    }
    cleanup();
    discard();
  }, [cleanup, discard]);

  return {
    state,
    elapsedSeconds,
    /** Pico do sinal entre 0 e 1, para a animacao da barra. */
    level,
    recording,
    error,
    maxDurationSeconds: AUDIO_MAX_DURATION_SECONDS,
    start,
    stop,
    cancel,
    discard,
  };
}
