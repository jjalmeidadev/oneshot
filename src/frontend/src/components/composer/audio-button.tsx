import { Mic, MicOff } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { RecorderState } from '@/hooks/use-audio-recorder';
import { AUDIO_MAX_DURATION_SECONDS, AUDIO_MAX_SIZE_BYTES } from '@/lib/api/constants';
import { formatBytes } from '@/lib/format';

/**
 * Botao de gravacao de audio.
 *
 * Os limites citados no tooltip nao sao escolha da interface: vem da validacao
 * local de `app/audio/validation.py`, que roda antes de qualquer chamada ao
 * provedor de transcricao.
 */
export function AudioButton({
  state,
  disabled,
  onStart,
}: {
  state: RecorderState;
  disabled?: boolean;
  onStart: () => void;
}) {
  const unsupported = state === 'unsupported';

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={onStart}
          disabled={disabled || unsupported || state === 'requesting'}
          aria-label="Gravar pergunta em áudio"
          className="shrink-0 rounded-full"
        >
          {unsupported ? <MicOff size={17} /> : <Mic size={17} />}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="top">
        {unsupported ? (
          'Este navegador não permite gravar áudio.'
        ) : (
          <>
            <p className="font-medium">Gravar pergunta em áudio</p>
            <p className="mt-1 text-fg-muted">
              Até {AUDIO_MAX_DURATION_SECONDS} segundos e{' '}
              {formatBytes(AUDIO_MAX_SIZE_BYTES)}, em WAV/PCM ou OGG/OPUS mono. A
              gravação para sozinha no limite.
            </p>
          </>
        )}
      </TooltipContent>
    </Tooltip>
  );
}
