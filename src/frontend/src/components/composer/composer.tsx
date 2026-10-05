import { AlertTriangle, ArrowUp, Square } from 'lucide-react';
import { useEffect, useRef, type ChangeEvent, type KeyboardEvent } from 'react';

import { AudioButton } from '@/components/composer/audio-button';
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
 * Ordem dos elementos, de cima para baixo: barra de gravacao (quando ativa) e o
 * campo de texto com o botao de audio a esquerda e o de envio a direita. Os
 * controles de validacao de intencao e proatividade ficam na engrenagem de
 * ajustes do cabecalho (S5-20).
 */
export function Composer({
  value,
  onChange,
  onSubmit,
  onSendAudio,
  conversationId = null,
  onStop,
  isSending,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onSendAudio: (audio: Blob) => Promise<boolean>;
  conversationId?: string | null;
  onStop: () => void;
  isSending: boolean;
}) {
  const recorder = useAudioRecorder();
  const previousConversation = useRef(conversationId);
  const cancelRecording = recorder.cancel;
  useEffect(() => {
    if (previousConversation.current && previousConversation.current !== conversationId)
      cancelRecording();
    previousConversation.current = conversationId;
  }, [conversationId, cancelRecording]);
  const textareaRef = useAutosizeTextarea(value, 1, 200);

  const overLimit = value.length > CHAT_MESSAGE_MAX_LENGTH;
  const canSubmit =
    value.trim().length > 0 &&
    !overLimit &&
    !isSending &&
    recorder.state !== 'recording' &&
    recorder.state !== 'requesting';
  const isRecording = recorder.state === 'recording';

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      if (canSubmit) onSubmit();
    }
  };

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value);
  };

  const handleSendAudio = async () => {
    if (!recorder.recording || isSending) return;
    const sent = await onSendAudio(recorder.recording.blob);
    if (sent) recorder.discard();
  };

  return (
    <div className="border-t border-border bg-surface px-3 py-3 sm:px-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-2.5">
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
            onSend={() => void handleSendAudio()}
            disabled={isSending}
          />
        )}

        {recorder.error && (
          <p className="flex items-start gap-1.5 text-2xs text-danger">
            <AlertTriangle size={12} className="mt-0.5 shrink-0" />
            {recorder.error}
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

        {value.length > CHAT_MESSAGE_MAX_LENGTH * 0.8 && (
          <p
            className={cn(
              'px-1 text-right text-2xs',
              overLimit ? 'text-danger' : 'text-fg-subtle',
            )}
          >
            {formatNumber(value.length)} / {formatNumber(CHAT_MESSAGE_MAX_LENGTH)}
          </p>
        )}
      </div>
    </div>
  );
}
