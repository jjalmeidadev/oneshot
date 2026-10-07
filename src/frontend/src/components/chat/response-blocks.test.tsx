import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ResponseBlocks } from './response-blocks';
import { MessageBubble } from './message-bubble';
import { TooltipProvider } from '@/components/ui/tooltip';
import { toAssistantMessage } from '@/lib/domain';
import type { ResponseBlock } from '@/lib/api/schemas';
import { response } from '@/tests/fixtures';
import { responseBlocks } from '@/tests/response-blocks-fixture';

const message = toAssistantMessage(
  { ...response, blocks: responseBlocks },
  { roundTripMs: 1, intentLayerEnabled: false },
);

function mount(blocks = responseBlocks, select = vi.fn()) {
  return render(
    <ResponseBlocks
      blocks={blocks}
      sources={message.sources!}
      onSelectSource={select}
    />,
  );
}

describe('Blocos de resposta da #271', () => {
  it('expõe tabela com legenda, cabeçalhos, células e referências por linha', () => {
    mount();
    const table = screen.getByRole('table', { name: 'Tabela da resposta' });
    expect(within(table).getAllByRole('columnheader')).toHaveLength(3);
    expect(within(table).getAllByRole('row')).toHaveLength(3);
    expect(within(table).getByRole('cell', { name: '42,5%' })).toBeVisible();
    expect(screen.getByRole('region', { name: /Tabela da resposta/ })).toHaveAttribute(
      'tabindex',
      '0',
    );
  });
  it('associa nome e valor do indicador sem alterar percentuais ou zero', () => {
    mount([
      responseBlocks[1],
      {
        type: 'indicator',
        label: 'Saldo',
        value: 0,
        unit: null,
        citation_ids: ['Fonte 1'],
      },
      {
        type: 'indicator',
        label: 'Variação',
        value: -1.25,
        unit: null,
        citation_ids: ['Fonte 1'],
      },
    ]);
    const region = screen.getByRole('region', { name: 'Indicador: Avanço' });
    expect(within(region).getByRole('term')).toHaveTextContent('Avanço');
    expect(within(region).getByRole('definition')).toHaveTextContent('42,5%');
    expect(screen.getByRole('region', { name: 'Indicador: Saldo' })).toHaveTextContent(
      '0',
    );
    expect(
      screen.getByRole('region', { name: 'Indicador: Variação' }),
    ).toHaveTextContent('-1,25');
  });
  it('identifica destaque por texto e semântica e escapa HTML', () => {
    const text = '<img src=x onerror=alert(1)> Atenção';
    const { container } = mount([
      { type: 'highlight', text, citation_ids: ['Fonte 1'] },
    ]);
    expect(
      screen.getByRole('complementary', { name: 'Destaque da resposta' }),
    ).toHaveTextContent(text);
    expect(screen.getByText('Destaque')).toBeVisible();
    expect(container.querySelector('img')).toBeNull();
  });
  it('abre a fonte correta com teclado usando citation_id explícito', async () => {
    const select = vi.fn();
    render(
      <ResponseBlocks
        blocks={[responseBlocks[1]]}
        sources={[
          {
            ...message.sources![0],
            id: 'extract-2',
            citationId: 'Fonte 1',
            citationOrder: 7,
          },
        ]}
        onSelectSource={select}
      />,
    );
    await userEvent.tab();
    expect(screen.getByRole('button', { name: /Consultar Fonte 1/ })).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    expect(select).toHaveBeenCalledWith('extract-2');
  });
  it('mantém referência ausente como texto sem botão enganoso', () => {
    render(
      <ResponseBlocks
        blocks={[responseBlocks[1]]}
        sources={[]}
        onSelectSource={vi.fn()}
      />,
    );
    expect(screen.getByText('Fonte 1')).toBeVisible();
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });
  it('ignora blocos inválidos e futuros sem quebrar os válidos', () => {
    const invalid = [
      null,
      { type: 'future' },
      { type: 'indicator', label: 'NaN', value: NaN },
      { type: 'table', columns: ['A'], rows: [{ cells: [], citation_ids: [] }] },
      { type: 'highlight', text: '', citation_ids: [] },
    ];
    mount([...invalid, responseBlocks[2]] as ResponseBlock[]);
    expect(screen.getByRole('complementary')).toHaveTextContent('Status: Em andamento');
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });
  it('renderiza os três blocos dentro da mensagem e preserva texto legado', () => {
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
    expect(screen.getByRole('table')).toBeVisible();
    expect(screen.getByRole('region', { name: 'Indicador: Avanço' })).toBeVisible();
    expect(screen.getByRole('complementary')).toBeVisible();
    expect(screen.getByText(/O projeto está em andamento/)).toBeVisible();
  });
  it.each(['insufficient', 'error'] as const)(
    'não exibe fatos estruturados quando a resposta está %s',
    (status) => {
      render(
        <TooltipProvider>
          <MessageBubble
            message={{
              ...message,
              ...(status === 'error'
                ? { status, error: 'Falha' }
                : { evidenceStatus: status }),
            }}
            selectedSourceId={null}
            onSelectSource={vi.fn()}
            onResolveProactiveSuggestion={vi.fn()}
          />
        </TooltipProvider>,
      );
      expect(screen.queryByRole('table')).not.toBeInTheDocument();
    },
  );
  it('não acrescenta elementos para blocos ausentes', () => {
    const { container } = mount([]);
    expect(container).toBeEmptyDOMElement();
    expect(
      toAssistantMessage(response, { roundTripMs: 1, intentLayerEnabled: false })
        .blocks,
    ).toEqual([]);
  });
});
