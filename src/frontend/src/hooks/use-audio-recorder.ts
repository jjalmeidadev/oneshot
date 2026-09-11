import { normalizeRecording } from '@/lib/audio';
import { useCallback, useEffect, useRef, useState } from 'react';

import {
  AUDIO_ACCEPTED_MIME_TYPES,
  AUDIO_MAX_DURATION_SECONDS,
  AUDIO_MAX_SIZE_BYTES,
} from '@/lib/api/constants';

/** Captura no contêiner do navegador e converte para WAV PCM mono de 16 kHz. */

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

  // O Chrome usa WebM; normalizeRecording converte antes do upload.
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

  const generation = useRef(0);
  const objectUrlRef = useRef<string | null>(null);
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
      generation.current++;
      if (recorderRef.current) recorderRef.current.onstop = null;
      if (recorderRef.current?.state === 'recording') recorderRef.current.stop();
      cleanup();
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    },
    [cleanup],
  );

  const stop = useCallback(() => {
    if (recorderRef.current?.state === 'recording') {
      recorderRef.current.stop();
    }
  }, []);

  const start = useCallback(async () => {
    const current = ++generation.current;
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
      if (generation.current !== current) {
        stream.getTracks().forEach((track) => track.stop());
        return;
      }
      streamRef.current = stream;

      const { mimeType } = pickMimeType();
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };

      recorder.onstop = async () => {
        const raw = new Blob(chunksRef.current, {
          type: recorder.mimeType || mimeType,
        });
        cleanup();
        setLevel(0);
        setState('requesting');
        try {
          const blob = await normalizeRecording(raw);
          if (generation.current !== current) return;
          if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
          const objectUrl = URL.createObjectURL(blob);
          objectUrlRef.current = objectUrl;
          setRecording({
            blob,
            mimeType: 'audio/wav',
            durationSeconds: (blob.size - 44) / 32000,
            sizeBytes: blob.size,
            containerAccepted: true,
            tooLarge: blob.size > AUDIO_MAX_SIZE_BYTES,
            objectUrl,
          });
          setState('recorded');
        } catch {
          if (generation.current !== current) return;
          setError(
            'Não foi possível preparar a gravação. Grave novamente ou envie texto.',
          );
          setState('error');
        }
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
        if (
          elapsed >= AUDIO_MAX_DURATION_SECONDS &&
          recorderRef.current?.state === 'recording'
        ) {
          recorderRef.current.stop();
        }
      }, 100);

      recorder.start(250);
      setState('recording');
    } catch (cause) {
      if (generation.current !== current) return;
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
    generation.current++;
    objectUrlRef.current = null;
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
    generation.current++;
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
