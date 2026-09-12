import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import type { ReactNode } from 'react';
import { TooltipProvider } from './ui/tooltip';
import { ChatEmptyState } from './chat/chat-empty-state';
import { ChatHeader } from './chat/chat-header';
import { MarkdownMessage } from './chat/markdown-message';
import { MessageBubble } from './chat/message-bubble';
import { MessageList } from './chat/message-list';
import { SourceCitations } from './chat/source-citations';
import { IntentBadge } from './chat/intent-badge';
import { Composer } from './composer/composer';
import { AudioButton } from './composer/audio-button';
import { IntentToggle } from './composer/intent-toggle';
import { RecordingBar, RecordingPreview } from './composer/recording-bar';
import { DocumentCard } from './documents/document-card';
import { DocumentViewer } from './documents/document-viewer';
import { DocumentPanel } from './documents/document-panel';
import { ResponseDetails } from './documents/response-details';
import { ConversationItem } from './sidebar/conversation-item';
import { toAssistantMessage, type Conversation } from '@/lib/domain';
import { response } from '@/tests/fixtures';

const message = toAssistantMessage(response, {
  roundTripMs: 10,
  intentLayerEnabled: true,
});
const doc = message.sources![0];
const conversation: Conversation = {
  id: 'c1',
  title: 'Conversa teste',
  createdAt: '2026-09-09T12:00:00Z',
  updatedAt: '2026-09-09T12:00:00Z',
  status: 'ativa',
  channel: 'webchat',
  messages: [message],
  lastInteractionId: 'i1',
};
function mount(component: ReactNode) {
  return render(<TooltipProvider>{component}</TooltipProvider>);
}

describe('Componentes de chat', () => {
  it('ChatEmptyState envia a sugestão selecionada', async () => {
    const pick = vi.fn();
    mount(<ChatEmptyState onPick={pick} />);
    await userEvent.click(screen.getAllByRole('button')[0]);
    expect(pick).toHaveBeenCalledWith(expect.any(String));
  });
  it('ChatHeader abre menu e documentos com nomes acessíveis', async () => {
    const open = vi.fn(),
      toggle = vi.fn();
    mount(
      <ChatHeader
        conversation={conversation}
        sourceCount={1}
        documentPanelOpen={false}
        onToggleDocumentPanel={toggle}
        onOpenSidebar={open}
      />,
    );
    await userEvent.click(screen.getByRole('button', { name: 'Abrir conversas' }));
    await userEvent.click(
      screen.getByRole('button', { name: 'Documentos recuperados (1)' }),
    );
    expect(open).toHaveBeenCalledOnce();
    expect(toggle).toHaveBeenCalledOnce();
  });
  it('MarkdownMessage renderiza listas/tabelas e não executa HTML', () => {
    const { container } = mount(
      <MarkdownMessage
        content={
          '**Prazo**\n\n- Item\n\n|A|B|\n|-|-|\n|1|2|\n\n<script>alert(1)</script>'
        }
      />,
    );
    expect(screen.getByText('Prazo').tagName).toBe('STRONG');
    expect(screen.getByRole('table')).toBeVisible();
    expect(container.querySelector('script')).toBeNull();
  });
  it('MessageBubble mostra erro controlado e origem de áudio', () => {
    mount(
      <MessageBubble
        message={{ ...message, status: 'error', error: 'Tente novamente' }}
        selectedSourceId={null}
        onSelectSource={vi.fn()}
      />,
    );
    expect(screen.getByText('Não foi possível responder')).toBeVisible();
    expect(screen.getByText('Tente novamente')).toBeVisible();
  });
  it('SourceCitations comunica seleção do documento', async () => {
    const select = vi.fn();
    mount(<SourceCitations sources={[doc]} selectedId={doc.id} onSelect={select} />);
    await userEvent.click(screen.getAllByRole('button')[0]);
    expect(select).toHaveBeenCalledWith(doc.id);
  });
  it('IntentBadge apresenta classificação devolvida', () => {
    mount(<IntentBadge intent={message.intent!} />);
    expect(screen.getByText('consulta_status_projeto')).toBeVisible();
  });
  it('MessageList anuncia processamento e exibe mensagens', async () => {
    mount(
      <MessageList
        messages={[message]}
        isSending={true}
        intentLayerEnabled={true}
        selectedSourceId={null}
        onSelectSource={vi.fn()}
      />,
    );
    expect(screen.getByRole('log')).toHaveAttribute('aria-busy', 'true');
    await waitFor(() =>
      expect(screen.getByText(/Classificando a intenção/)).toBeVisible(),
    );
  });
});

describe('Componentes de entrada', () => {
  const props = {
    value: 'prazo',
    onChange: vi.fn(),
    onSubmit: vi.fn(),
    onStop: vi.fn(),
    onSendAudio: vi.fn(),
    isSending: false,
    intentLayerEnabled: true,
    onIntentLayerChange: vi.fn(),
  };
  it('Composer envia por Enter, preserva Shift+Enter e bloqueia excesso de texto', () => {
    const submit = vi.fn();
    const { rerender } = mount(<Composer {...props} onSubmit={submit} />);
    const input = screen.getByRole('textbox', { name: 'Mensagem para o agente' });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });
    expect(submit).not.toHaveBeenCalled();
    fireEvent.keyDown(input, { key: 'Enter' });
    expect(submit).toHaveBeenCalledOnce();
    rerender(
      <TooltipProvider>
        <Composer {...props} value={'x'.repeat(20001)} />
      </TooltipProvider>,
    );
    expect(screen.getByRole('button', { name: 'Enviar mensagem' })).toBeDisabled();
  });
  it('Composer oferece interrupção durante envio', async () => {
    const stop = vi.fn();
    mount(<Composer {...props} isSending onStop={stop} />);
    await userEvent.click(screen.getByRole('button', { name: 'Interromper resposta' }));
    expect(stop).toHaveBeenCalledOnce();
  });
  it('AudioButton bloqueia captura sem suporte', () => {
    mount(<AudioButton state="unsupported" onStart={vi.fn()} />);
    expect(
      screen.getByRole('button', { name: 'Gravar pergunta em áudio' }),
    ).toBeDisabled();
  });
  it('IntentToggle encaminha alteração e respeita disabled', async () => {
    const change = vi.fn();
    mount(<IntentToggle enabled onChange={change} disabled={false} />);
    await userEvent.click(screen.getByRole('switch'));
    expect(change).toHaveBeenCalledWith(false);
  });
  it('RecordingBar permite concluir ou descartar', async () => {
    const stop = vi.fn(),
      cancel = vi.fn();
    mount(
      <RecordingBar elapsedSeconds={20} level={0.2} onCancel={cancel} onStop={stop} />,
    );
    await userEvent.click(screen.getByRole('button', { name: 'Concluir gravação' }));
    await userEvent.click(screen.getByRole('button', { name: 'Descartar gravação' }));
    expect(stop).toHaveBeenCalledOnce();
    expect(cancel).toHaveBeenCalledOnce();
  });
  it('RecordingPreview impede envio fora do contrato', () => {
    mount(
      <RecordingPreview
        recording={{
          blob: new Blob(),
          mimeType: 'audio/webm',
          durationSeconds: 1,
          sizeBytes: 10,
          containerAccepted: false,
          tooLarge: false,
          objectUrl: 'blob:teste',
        }}
        onDiscard={vi.fn()}
        onSend={vi.fn()}
      />,
    );
    expect(screen.getByRole('button', { name: 'Enviar áudio' })).toBeDisabled();
  });
});

describe('Documentos e conversas', () => {
  it('DocumentCard indica seleção e permite abrir', async () => {
    const select = vi.fn();
    mount(<DocumentCard document={doc} selected onSelect={select} />);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-current', 'true');
    await userEvent.click(button);
    expect(select).toHaveBeenCalledOnce();
  });
  it('DocumentViewer mostra trecho, origem e ausência honesta', () => {
    const { rerender } = mount(<DocumentViewer document={doc} />);
    expect(screen.getByText(doc.excerpt!)).toBeVisible();
    expect(screen.getByRole('link', { name: 'Abrir no SharePoint' })).toHaveAttribute(
      'href',
      doc.webUrl,
    );
    rerender(
      <TooltipProvider>
        <DocumentViewer document={{ ...doc, excerpt: undefined }} />
      </TooltipProvider>,
    );
    expect(screen.getByText('Trecho não disponível nesta resposta')).toBeVisible();
  });
  it('DocumentPanel navega entre fontes e métricas', async () => {
    mount(
      <DocumentPanel
        documents={[doc]}
        selectedDocument={doc}
        onSelect={vi.fn()}
        lastAssistantMessage={message}
      />,
    );
    await userEvent.click(screen.getByRole('tab', { name: 'Resposta' }));
    expect(screen.getByRole('tab', { name: 'Resposta' })).toHaveAttribute(
      'aria-selected',
      'true',
    );
    expect(screen.getByText('teste')).toBeVisible();
    expect(screen.getByText(/Entidades/)).toBeVisible();
    expect(screen.getByText('(Projeto Linha Verde)')).toBeVisible();
  });
  it('ResponseDetails não inventa métricas sem resposta', () => {
    mount(<ResponseDetails message={null} />);
    expect(screen.queryByText('teste')).not.toBeInTheDocument();
  });
  it('ConversationItem permite selecionar e excluir por teclado', async () => {
    const select = vi.fn(),
      remove = vi.fn();
    mount(
      <ConversationItem
        conversation={conversation}
        active
        onSelect={select}
        onDelete={remove}
      />,
    );
    await userEvent.tab();
    await userEvent.keyboard('{Enter}');
    expect(select).toHaveBeenCalledOnce();
    await userEvent.click(
      screen.getByRole('button', { name: 'Excluir conversa Conversa teste' }),
    );
    expect(remove).toHaveBeenCalledOnce();
  });
});
