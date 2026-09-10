import { AUDIO_MAX_DURATION_SECONDS, AUDIO_MAX_SIZE_BYTES } from './api/constants';

/** Codifica PCM mono de 16 bits; o corte por amostras respeita o teto de 60 s. */
export function encodeWav(samples: Float32Array, sampleRate = 16_000): Blob {
  const count = Math.min(samples.length, sampleRate * AUDIO_MAX_DURATION_SECONDS);
  const buffer = new ArrayBuffer(44 + count * 2);
  const view = new DataView(buffer);
  const text = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i++)
      view.setUint8(offset + i, value.charCodeAt(i));
  };
  text(0, 'RIFF');
  view.setUint32(4, 36 + count * 2, true);
  text(8, 'WAVE');
  text(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  text(36, 'data');
  view.setUint32(40, count * 2, true);
  for (let i = 0; i < count; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(44 + i * 2, Math.round(sample * (sample < 0 ? 32768 : 32767)), true);
  }
  return new Blob([buffer], { type: 'audio/wav' });
}

/** Decodifica o contêiner do navegador e reamostra antes do upload. */
export async function normalizeRecording(blob: Blob): Promise<Blob> {
  const decoder = new AudioContext();
  try {
    const decoded = await decoder.decodeAudioData(await blob.arrayBuffer());
    const frames = Math.min(Math.floor(decoded.duration * 16_000), 60 * 16_000);
    if (frames < 1) throw new Error('Áudio vazio');
    const renderer = new OfflineAudioContext(1, frames, 16_000);
    const source = renderer.createBufferSource();
    source.buffer = decoded;
    source.connect(renderer.destination);
    source.start();
    const rendered = await renderer.startRendering();
    const result = encodeWav(rendered.getChannelData(0));
    if (result.size > AUDIO_MAX_SIZE_BYTES) throw new Error('Áudio muito grande');
    return result;
  } finally {
    await decoder.close();
  }
}
