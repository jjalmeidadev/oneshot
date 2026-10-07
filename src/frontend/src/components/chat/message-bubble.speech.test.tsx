import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { MessageBubble } from './message-bubble';
import type { ChatMessage } from '@/lib/domain';

const baseMessage: ChatMessage = {
  id: 'answer-1',
  role: 'assistant',
  content: 'Resposta fundamentada.',
  createdAt: '2026-10-05T12:00:00Z',
  origin: 'text',
  status: 'complete',
};

function show(message: ChatMessage) {
  return render(
    <MessageBubble
      message={message}
      selectedSourceId={null}
      onSelectSource={vi.fn()}
      onResolveProactiveSuggestion={vi.fn()}
    />,
  );
}

describe('Áudio da resposta', () => {
  it('reproduz MP3 e libera a URL temporária ao desmontar', () => {
    const createObjectURL = vi.fn().mockReturnValue('blob:answer');
    const revokeObjectURL = vi.fn();
    vi.stubGlobal('URL', { ...URL, createObjectURL, revokeObjectURL });
    const view = show({
      ...baseMessage,
      speech: {
        status: 'available',
        media_type: 'audio/mpeg',
        data_base64: btoa('ID3audio'),
        warning: null,
      },
    });
    expect(screen.getByText('Resposta fundamentada.')).toBeVisible();
    expect(screen.getByLabelText('Resposta em áudio')).toHaveAttribute(
      'src',
      'blob:answer',
    );
    expect(createObjectURL).toHaveBeenCalledOnce();
    view.unmount();
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:answer');
    vi.unstubAllGlobals();
  });

  it('mantém a resposta escrita e mostra aviso quando TTS falha', () => {
    show({
      ...baseMessage,
      speech: {
        status: 'unavailable',
        media_type: null,
        data_base64: null,
        warning: 'Não foi possível gerar o áudio agora.',
      },
    });
    expect(screen.getByText('Resposta fundamentada.')).toBeVisible();
    expect(screen.getByRole('status')).toHaveTextContent(
      'Não foi possível gerar o áudio',
    );
    expect(screen.queryByLabelText('Resposta em áudio')).not.toBeInTheDocument();
  });

  it('preserva o texto e avisa quando o áudio recebido é inválido', () => {
    show({
      ...baseMessage,
      speech: {
        status: 'available',
        media_type: 'audio/mpeg',
        data_base64: 'not-base64!',
        warning: null,
      },
    });
    expect(screen.getByText('Resposta fundamentada.')).toBeVisible();
    expect(screen.getByRole('status')).toHaveTextContent('Não foi possível reproduzir');
  });
});
