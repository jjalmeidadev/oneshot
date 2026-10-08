import { createRef } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { Search } from 'lucide-react';

import { Badge } from './badge';
import { Button } from './button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from './dialog';
import { EmptyState } from './empty-state';
import { Meter } from './meter';
import { ScrollArea, ScrollBar } from './scroll-area';
import { Separator } from './separator';
import { Skeleton } from './skeleton';
import { Switch } from './switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs';
import { Textarea } from './textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './tooltip';

describe('Primitivos da interface', () => {
  it('Button encaminha clique e ref, bloqueia disabled e permite link asChild', async () => {
    const click = vi.fn();
    const ref = createRef<HTMLButtonElement>();
    const { rerender } = render(
      <Button ref={ref} onClick={click}>
        Enviar
      </Button>,
    );
    expect(ref.current).toBe(screen.getByRole('button'));
    await userEvent.click(screen.getByRole('button'));
    expect(click).toHaveBeenCalledOnce();
    rerender(
      <Button disabled onClick={click}>
        Enviar
      </Button>,
    );
    await userEvent.click(screen.getByRole('button'));
    expect(click).toHaveBeenCalledOnce();
    rerender(
      <Button asChild>
        <a href="/docs">Documentação</a>
      </Button>,
    );
    expect(screen.getByRole('link')).toHaveAttribute('href', '/docs');
    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('Badge preserva conteúdo, tom e atributos do consumidor', () => {
    render(
      <Badge tone="warning" aria-label="Situação">
        Atenção
      </Badge>,
    );
    expect(screen.getByLabelText('Situação')).toHaveTextContent('Atenção');
    expect(screen.getByLabelText('Situação')).toHaveClass('text-warning');
  });

  it('Textarea encaminha edição e ref e respeita disabled', async () => {
    const ref = createRef<HTMLTextAreaElement>();
    const change = vi.fn();
    const { rerender } = render(
      <Textarea ref={ref} aria-label="Pergunta" onChange={change} />,
    );
    await userEvent.type(screen.getByRole('textbox'), 'Prazo?');
    expect(ref.current).toHaveValue('Prazo?');
    expect(change).toHaveBeenCalled();
    rerender(<Textarea aria-label="Pergunta" disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('Switch alterna por teclado e não altera quando desabilitado', async () => {
    const change = vi.fn();
    const { rerender } = render(
      <Switch aria-label="Sugestões" onCheckedChange={change} />,
    );
    await userEvent.tab();
    await userEvent.keyboard(' ');
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true');
    expect(change).toHaveBeenCalledWith(true);
    rerender(<Switch aria-label="Sugestões" disabled onCheckedChange={change} />);
    await userEvent.click(screen.getByRole('switch'));
    expect(change).toHaveBeenCalledOnce();
  });

  it('Tabs associa conteúdo à seleção e permite navegação por setas', async () => {
    render(
      <Tabs defaultValue="sources">
        <TabsList aria-label="Detalhes">
          <TabsTrigger value="sources">Fontes</TabsTrigger>
          <TabsTrigger value="answer">Resposta</TabsTrigger>
        </TabsList>
        <TabsContent value="sources">Documentos</TabsContent>
        <TabsContent value="answer">Métricas</TabsContent>
      </Tabs>,
    );
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Documentos');
    await userEvent.tab();
    await userEvent.keyboard('{ArrowRight}');
    await waitFor(() =>
      expect(screen.getByRole('tab', { name: 'Resposta' })).toHaveAttribute(
        'aria-selected',
        'true',
      ),
    );
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Métricas');
  });

  it.each(['center', 'left', 'right'] as const)(
    'Dialog %s abre com descrição e fecha por Escape',
    async (side) => {
      render(
        <Dialog>
          <DialogTrigger asChild>
            <Button>Abrir</Button>
          </DialogTrigger>
          <DialogContent side={side}>
            <DialogTitle>Documentos</DialogTitle>
            <DialogDescription>Fontes da resposta</DialogDescription>
            <DialogClose asChild>
              <Button>Concluir</Button>
            </DialogClose>
          </DialogContent>
        </Dialog>,
      );
      await userEvent.click(screen.getByRole('button', { name: 'Abrir' }));
      const dialog = screen.getByRole('dialog', { name: 'Documentos' });
      expect(dialog).toHaveAccessibleDescription('Fontes da resposta');
      expect(screen.getByRole('button', { name: 'Fechar' })).toBeVisible();
      await userEvent.click(screen.getByRole('button', { name: 'Concluir' }));
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      await userEvent.click(screen.getByRole('button', { name: 'Abrir' }));
      await userEvent.keyboard('{Escape}');
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Abrir' })).toHaveFocus();
    },
  );

  it('Dialog permite omitir o botão de fechar', () => {
    render(
      <Dialog open>
        <DialogContent showClose={false}>
          <DialogTitle>Conversas</DialogTitle>
          <DialogDescription>Histórico</DialogDescription>
        </DialogContent>
      </Dialog>,
    );
    expect(screen.getByRole('dialog')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Fechar' })).not.toBeInTheDocument();
  });

  it('Tooltip exibe a ajuda ao focar o controle', async () => {
    render(
      <TooltipProvider delayDuration={0}>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button>Fontes</Button>
          </TooltipTrigger>
          <TooltipContent>Consultar documentos</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    await userEvent.tab();
    expect(await screen.findByRole('tooltip')).toHaveTextContent(
      'Consultar documentos',
    );
    expect(screen.getByRole('button')).toHaveAccessibleDescription(
      'Consultar documentos',
    );
  });

  it('EmptyState apresenta descrição e ação e permite versão compacta', async () => {
    const action = vi.fn();
    const { rerender } = render(
      <EmptyState
        icon={Search}
        title="Nada encontrado"
        description="Ajuste a busca"
        action={<Button onClick={action}>Limpar</Button>}
      />,
    );
    expect(screen.getByText('Ajuste a busca')).toBeVisible();
    await userEvent.click(screen.getByRole('button'));
    expect(action).toHaveBeenCalledOnce();
    rerender(<EmptyState compact icon={Search} title="Sem documentos" />);
    expect(screen.getByText('Sem documentos')).toBeVisible();
    expect(screen.queryByText('Ajuste a busca')).not.toBeInTheDocument();
  });

  it.each([
    [-1, 0],
    [0.754, 75.4],
    [2, 100],
  ])('Meter limita %s e anuncia %s por cento', (value, percent) => {
    render(<Meter label="Confiança" value={value} threshold={2} />);
    expect(screen.getByRole('meter', { name: 'Confiança' })).toHaveAttribute(
      'aria-valuenow',
      String(percent),
    );
    expect(screen.getByRole('meter')).toHaveAttribute('aria-valuemin', '0');
    expect(screen.getByRole('meter')).toHaveAttribute('aria-valuemax', '100');
    expect(screen.getByRole('meter').lastElementChild).toHaveStyle({ left: '100%' });
  });

  it('Meter omite marcador quando não há limiar', () => {
    render(<Meter value={0.5} />);
    expect(screen.getByRole('meter').children).toHaveLength(1);
  });

  it('ScrollArea encaminha refs e renderiza ScrollBar nas duas orientações', () => {
    const ref = createRef<HTMLDivElement>();
    const viewport = createRef<HTMLDivElement>();
    render(
      <ScrollArea ref={ref} viewportRef={viewport} type="always" aria-label="Histórico">
        Conversas
        <ScrollBar orientation="horizontal" forceMount data-testid="horizontal" />
      </ScrollArea>,
    );
    expect(ref.current).toBe(screen.getByLabelText('Histórico'));
    expect(viewport.current).toHaveTextContent('Conversas');
    expect(screen.getByTestId('horizontal')).toHaveAttribute(
      'data-orientation',
      'horizontal',
    );
  });

  it('Separator diferencia decoração de separador acessível', () => {
    const { rerender } = render(<Separator data-testid="separator" />);
    expect(screen.getByTestId('separator')).toHaveAttribute('role', 'none');
    rerender(<Separator decorative={false} orientation="vertical" />);
    expect(screen.getByRole('separator')).toHaveAttribute(
      'aria-orientation',
      'vertical',
    );
  });

  it('Skeleton é decorativo e preserva atributos e classes', () => {
    render(<Skeleton data-testid="loading" className="h-8" />);
    expect(screen.getByTestId('loading')).toHaveAttribute('aria-hidden', 'true');
    expect(screen.getByTestId('loading')).toHaveClass('animate-pulse', 'h-8');
  });
});
