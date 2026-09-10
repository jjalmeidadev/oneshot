import { act, renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useAudioRecorder } from './use-audio-recorder';
import { normalizeRecording } from '@/lib/audio';

vi.mock('@/lib/audio', () => ({ normalizeRecording: vi.fn() }));

function devices() {
  const stopTrack = vi.fn();
  const stream = { getTracks: () => [{ stop: stopTrack }] };
  const getUserMedia = vi.fn().mockResolvedValue(stream);
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia } });
  class Recorder {
    static isTypeSupported() {
      return true;
    }
    state = 'inactive';
    mimeType = 'audio/ogg';
    onstop: (() => void) | null = null;
    ondataavailable: ((event: { data: Blob }) => void) | null = null;
    start() {
      this.state = 'recording';
    }
    stop() {
      this.state = 'inactive';
      this.ondataavailable?.({ data: new Blob(['samples']) });
      this.onstop?.();
    }
  }
  class Context {
    createAnalyser() {
      return {
        fftSize: 0,
        frequencyBinCount: 16,
        getByteTimeDomainData: (data: Uint8Array) => data.fill(128),
      };
    }
    createMediaStreamSource() {
      return { connect: vi.fn() };
    }
    close() {
      return Promise.resolve();
    }
  }
  vi.stubGlobal('MediaRecorder', Recorder);
  vi.stubGlobal('AudioContext', Context);
  const revoke = vi.fn();
  vi.stubGlobal(
    'URL',
    class extends URL {
      static createObjectURL() {
        return 'blob:recording';
      }
      static revokeObjectURL = revoke;
    },
  );
  vi.mocked(normalizeRecording).mockResolvedValue(
    new Blob([new Uint8Array(32044)], { type: 'audio/wav' }),
  );
  return { getUserMedia, stream, stopTrack, revoke };
}

describe('Ciclo de vida do gravador', () => {
  it('grava, converte para WAV, libera o microfone e revoga a prévia', async () => {
    const { stopTrack, revoke } = devices();
    const { result, unmount } = renderHook(useAudioRecorder);
    await act(async () => {
      await result.current.start();
    });
    expect(result.current.state).toBe('recording');
    act(() => result.current.stop());
    await waitFor(() => expect(result.current.state).toBe('recorded'));
    expect(result.current.recording?.mimeType).toBe('audio/wav');
    expect(result.current.recording?.durationSeconds).toBe(1);
    expect(stopTrack).toHaveBeenCalled();
    unmount();
    expect(revoke).toHaveBeenCalledWith('blob:recording');
  });
  it('cancelamento descarta áudio sem upload nem conversão', async () => {
    devices();
    vi.mocked(normalizeRecording).mockClear();
    const { result } = renderHook(useAudioRecorder);
    await act(async () => {
      await result.current.start();
    });
    act(() => result.current.cancel());
    expect(result.current.state).toBe('idle');
    expect(result.current.recording).toBeNull();
    expect(normalizeRecording).not.toHaveBeenCalled();
  });
  it('libera stream concedida depois da desmontagem', async () => {
    const { getUserMedia, stream, stopTrack } = devices();
    let resolve!: (value: unknown) => void;
    getUserMedia.mockImplementation(
      () =>
        new Promise((r) => {
          resolve = r;
        }),
    );
    const { result, unmount } = renderHook(useAudioRecorder);
    let pending!: Promise<void>;
    act(() => {
      pending = result.current.start();
    });
    unmount();
    await act(async () => {
      resolve(stream);
      await pending;
    });
    expect(stopTrack).toHaveBeenCalledOnce();
  });
  it('comunica permissão negada e falta de suporte', async () => {
    const { getUserMedia } = devices();
    getUserMedia.mockRejectedValue(new DOMException('denied', 'NotAllowedError'));
    const { result } = renderHook(useAudioRecorder);
    await act(async () => {
      await result.current.start();
    });
    expect(result.current.error).toContain('Permissão');
    vi.stubGlobal('MediaRecorder', undefined);
    await act(async () => {
      await result.current.start();
    });
    expect(result.current.state).toBe('unsupported');
  });
  it('erro na conversão permite uma nova tentativa', async () => {
    devices();
    vi.mocked(normalizeRecording).mockRejectedValue(new Error('decode failed'));
    const { result } = renderHook(useAudioRecorder);
    await act(async () => {
      await result.current.start();
    });
    act(() => result.current.stop());
    await waitFor(() => expect(result.current.state).toBe('error'));
    expect(result.current.error).not.toContain('decode failed');
    act(() => result.current.discard());
    expect(result.current.state).toBe('idle');
  });
});
