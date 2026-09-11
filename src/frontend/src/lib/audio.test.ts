import { describe, it, expect } from 'vitest';
import { encodeWav } from './audio';

describe('WAV enviado ao backend', () => {
  it('produz mono PCM 16 bits a 16 kHz e limita a 60 segundos', async () => {
    const blob = encodeWav(new Float32Array(16_000 * 61));
    const bytes = await new Promise<ArrayBuffer>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as ArrayBuffer);
      reader.onerror = reject;
      reader.readAsArrayBuffer(blob);
    });
    const view = new DataView(bytes);
    expect(view.getUint16(20, true)).toBe(1);
    expect(view.getUint16(22, true)).toBe(1);
    expect(view.getUint32(24, true)).toBe(16000);
    expect(view.getUint16(34, true)).toBe(16);
    expect(blob.size).toBe(44 + 60 * 16000 * 2);
    expect(blob.size).toBeLessThan(2 * 1024 * 1024);
  });
});
