import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { MarkdownMessage } from './markdown-message';
import { MessageBubble } from './message-bubble';
import { SourceCitations } from './source-citations';
import { TooltipProvider } from '@/components/ui/tooltip';
import type { ChatMessage } from '@/lib/domain';

describe('Renderização de mensagens', () => {
  it('MarkdownMessage preserva semântica de citações, código, ênfase, listas e links', () => {
    const { container } = render(
      <MarkdownMessage
        content={
          '*ênfase*\n\n1. Primeiro\n\n> Citação\n\n`inline`\n\n```txt\nbloco\n```\n\n[Documento](https://example.com/documento)'
        }
      />,
    );
    expect(screen.getByText('ênfase').tagName).toBe('EM');
    expect(screen.getByRole('list').tagName).toBe('OL');
    expect(container.querySelector('blockquote')).toHaveTextContent('Citação');
    expect(screen.getByText('inline').tagName).toBe('CODE');
    expect(container.querySelector('pre')).toHaveTextContent('bloco');
    expect(screen.getByRole('link', { name: 'Documento' })).toHaveAttribute(
      'href',
      'https://example.com/documento',
    );
    expect(screen.getByRole('link')).toHaveAttribute('rel', 'noreferrer');
  });

  it('MessageBubble diferencia pergunta transcrita de resposta do agente', () => {
    const message: ChatMessage = {
      id: 'audio-1',
      role: 'user',
      content: 'Pergunta transcrita',
      createdAt: '2026-10-05T12:00:00Z',
      origin: 'audio',
      status: 'complete',
      transcription: { durationSeconds: 10, confidence: 0.9 },
    };
    render(
      <TooltipProvider>
        <MessageBubble
          message={message}
          selectedSourceId={null}
          onSelectSource={vi.fn()}
          onResolveProactiveSuggestion={vi.fn()}
        />
      </TooltipProvider>,
    );
    expect(screen.getByText('Pergunta transcrita')).toBeVisible();
    expect(screen.getByRole('button', { name: 'Transcrito' })).toBeVisible();
    expect(screen.queryByText('Fontes consultadas')).not.toBeInTheDocument();
  });

  it('SourceCitations não mostra uma seção sem fontes', () => {
    const { container } = render(
      <SourceCitations sources={[]} selectedId={null} onSelect={vi.fn()} />,
    );
    expect(container).toBeEmptyDOMElement();
  });
});
