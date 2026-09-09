import { AlertTriangle, ArrowUp, Square } from 'lucide-react';
import { useState, type ChangeEvent, type KeyboardEvent } from 'react';

import { AudioButton } from '@/components/composer/audio-button';
import { IntentToggle } from '@/components/composer/intent-toggle';
import { RecordingBar, RecordingPreview } from '@/components/composer/recording-bar';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useAudioRecorder } from '@/hooks/use-audio-recorder';
import { useAutosizeTextarea } from '@/hooks/use-autosize-textarea';
import { CHAT_MESSAGE_MAX_LENGTH } from '@/lib/api/constants';
import { formatNumber } from '@/lib/format';
import { cn } from '@/lib/utils';

/**
 * Area de composicao.
 *
 * Ordem dos elementos, de cima para baixo: toggle da camada de intencao,
 * barra de gravacao (quando ativa) e o campo de texto com o botao de audio a
 * esquerda e o de envio a direita.
 */
export function Composer({
  value,
  onChange,
  onSubmit,
  onStop,
  isSending,
  intentLayerEnabled,
  onIntentLayerChange,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onStop: () => void;
  isSending: boolean;
  intentLayerEnabled: boolean;
  onIntentLayerChange: (enabled: boolean) => void;
}) {
  const recorder = useAudioRecorder();
  const [audioNotice, setAudioNotice] = useState<string | null>(null);
  const textareaRef = useAutosizeTextarea(value, 1, 200);

  const overLimit = value.length > CHAT_MESSAGE_MAX_LENGTH;
  const canSubmit = value.trim().length > 0 && !overLimit && !isSending;
  const isRecording = recorder.state === 'recording';

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (canSubmit) onSubmit();
    }
  };

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value);
  };

  /**
   * PONTO DE INTEGRACAO 3: envio do audio.
   *
   * A captura ja entrega `recorder.recording.blob` pronto e conferido contra os
   * limites do endpoint. Falta apenas chamar `uploadAudio` de `lib/api/audio.ts`
   * com o token que o canal entregar, e transformar a resposta em mensagens —
   * a transcricao vira a mensagem do usuario e `answer.text` a do assistente.
   */
  const handleSendAudio = () => {
    setAudioNotice(
      'Captura concluída. O envio para POST /api/audio entra na task de integração — ' +
        'o áudio já está validado contra os limites do endpoint.',
    );
    recorder.discard();
  };

  return (
    <div className="border-t border-border bg-surface px-3 py-3 sm:px-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-2.5">
        <IntentToggle
          enabled={intentLayerEnabled}
          onChange={onIntentLayerChange}
          disabled={isSending}
        />

        {isRecording && (
          <RecordingBar
            elapsedSeconds={recorder.elapsedSeconds}
            level={recorder.level}
            onCancel={recorder.cancel}
            onStop={recorder.stop}
          />
        )}

        {recorder.state === 'recorded' && recorder.recording && (
          <RecordingPreview
            recording={recorder.recording}
            onDiscard={recorder.discard}
            onSend={handleSendAudio}
          />
        )}

        {recorder.error && (
          <p className="flex items-start gap-1.5 text-2xs text-danger">
            <AlertTriangle size={12} className="mt-0.5 shrink-0" />
            {recorder.error}
          </p>
        )}

        {audioNotice && (
          <p className="rounded-lg border border-border bg-muted px-3 py-2 text-2xs leading-4 text-fg-muted">
            {audioNotice}
          </p>
        )}

        <div
          className={cn(
            'flex items-end gap-1.5 rounded-2xl border bg-surface px-2 py-1.5 transition-colors',
            overLimit
              ? 'border-danger'
              : 'border-border focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/10',
          )}
        >
          <AudioButton
            state={recorder.state}
            disabled={isSending || isRecording}
            onStart={() => {
              setAudioNotice(null);
              void recorder.start();
            }}
          />

          <Textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isRecording}
            placeholder="Pergunte sobre projetos, cronogramas, TAPs ou documentos…"
            aria-label="Mensagem para o agente"
            className="max-h-[200px] flex-1 self-center py-1.5"
          />

          {isSending ? (
            <Button
              size="icon"
              variant="outline"
              onClick={onStop}
              aria-label="Interromper resposta"
              className="shrink-0 rounded-full"
            >
              <Square size={14} className="fill-current" />
            </Button>
          ) : (
            <Button
              size="icon"
              onClick={onSubmit}
              disabled={!canSubmit}
              aria-label="Enviar mensagem"
              className="shrink-0 rounded-full"
            >
              <ArrowUp size={17} />
            </Button>
          )}
        </div>

        <div className="flex items-center justify-between gap-3 px-1">
          <p className="text-2xs text-fg-subtle">
            <kbd className="rounded border border-border bg-muted px-1 font-sans">
              Enter
            </kbd>{' '}
            envia ·{' '}
            <kbd className="rounded border border-border bg-muted px-1 font-sans">
              Shift + Enter
            </kbd>{' '}
            quebra linha
          </p>
          {value.length > CHAT_MESSAGE_MAX_LENGTH * 0.8 && (
            <p className={cn('text-2xs', overLimit ? 'text-danger' : 'text-fg-subtle')}>
              {formatNumber(value.length)} / {formatNumber(CHAT_MESSAGE_MAX_LENGTH)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
