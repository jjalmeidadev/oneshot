import { AlertTriangle, Check, Trash2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import type { Recording } from '@/hooks/use-audio-recorder';
import { AUDIO_MAX_DURATION_SECONDS, AUDIO_MAX_SIZE_BYTES } from '@/lib/api/constants';
import { formatBytes, formatDuration } from '@/lib/format';
import { cn } from '@/lib/utils';

const BAR_COUNT = 28;

/** Barra exibida enquanto o microfone esta captando. */
export function RecordingBar({
  elapsedSeconds,
  level,
  onCancel,
  onStop,
}: {
  elapsedSeconds: number;
  level: number;
  onCancel: () => void;
  onStop: () => void;
}) {
  const progress = Math.min(1, elapsedSeconds / AUDIO_MAX_DURATION_SECONDS);
  const remaining = Math.max(0, AUDIO_MAX_DURATION_SECONDS - elapsedSeconds);

  return (
    <div className="flex items-center gap-3 rounded-xl border border-danger/40 bg-danger-soft px-3 py-2">
      <span className="flex items-center gap-2 text-xs font-medium text-danger">
        <span className="h-2 w-2 animate-pulse rounded-full bg-danger" aria-hidden />
        {formatDuration(elapsedSeconds)}
      </span>

      <div className="flex h-6 min-w-0 flex-1 items-center gap-[3px]" aria-hidden>
        {Array.from({ length: BAR_COUNT }).map((_, index) => {
          const distance = Math.abs(index - BAR_COUNT / 2) / (BAR_COUNT / 2);
          const height = 12 + level * 100 * (1 - distance * 0.7);
          return (
            <span
              key={index}
              className="w-full rounded-full bg-danger/60 transition-[height] duration-75"
              style={{ height: `${Math.min(24, Math.max(3, height))}px` }}
            />
          );
        })}
      </div>

      <span className="hidden shrink-0 text-2xs text-fg-muted sm:block">
        {formatDuration(remaining)} restantes
      </span>

      <div
        className="hidden h-1 w-16 shrink-0 overflow-hidden rounded-full bg-danger/20 sm:block"
        aria-hidden
      >
        <div
          className="h-full bg-danger transition-[width]"
          style={{ width: `${progress * 100}%` }}
        />
      </div>

      <Button
        variant="ghost"
        size="icon-sm"
        onClick={onCancel}
        aria-label="Descartar gravação"
      >
        <Trash2 size={15} />
      </Button>
      <Button size="icon-sm" onClick={onStop} aria-label="Concluir gravação">
        <Check size={15} />
      </Button>
    </div>
  );
}

/** Revisao da gravacao concluida, antes do envio. */
export function RecordingPreview({
  recording,
  onDiscard,
  onSend,
}: {
  recording: Recording;
  onDiscard: () => void;
  onSend: () => void;
}) {
  const blocked = !recording.containerAccepted || recording.tooLarge;

  return (
    <div
      className={cn(
        'rounded-xl border px-3 py-2',
        blocked ? 'border-warning/40 bg-warning-soft' : 'border-border bg-muted',
      )}
    >
      <div className="flex flex-wrap items-center gap-3">
        <audio
          controls
          src={recording.objectUrl}
          className="h-8 min-w-0 flex-1"
          aria-label="Prévia da gravação"
        />
        <span className="shrink-0 text-2xs text-fg-muted">
          {formatDuration(recording.durationSeconds)} ·{' '}
          {formatBytes(recording.sizeBytes)}
        </span>
        <div className="flex shrink-0 items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onDiscard}
            aria-label="Descartar"
          >
            <Trash2 size={15} />
          </Button>
          <Button size="sm" onClick={onSend} disabled={blocked}>
            Enviar áudio
          </Button>
        </div>
      </div>

      {blocked && (
        <p className="flex items-start gap-1.5 pt-2 text-2xs leading-4 text-warning">
          <AlertTriangle size={12} className="mt-0.5 shrink-0" />
          <span>
            {recording.tooLarge
              ? `A gravação tem ${formatBytes(recording.sizeBytes)} e o endpoint aceita até ${formatBytes(AUDIO_MAX_SIZE_BYTES)}.`
              : `Este navegador gravou em ${recording.mimeType}, e a validação do backend aceita apenas WAV/PCM ou OGG/OPUS. O envio seria recusado com AUDIO_FORMAT_UNSUPPORTED.`}
          </span>
        </p>
      )}
    </div>
  );
}
