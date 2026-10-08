import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { TooltipProvider } from '../ui/tooltip';
import { DocumentViewer } from './document-viewer';
import { SourceCitations } from '../chat/source-citations';
import { ResponseDetails } from './response-details';
import { toAssistantMessage, toRetrievedDocument } from '@/lib/domain';
import { response } from '@/tests/fixtures';

it('exibe identificadores e periodos disponiveis da fonte', () => {
  const source = toRetrievedDocument(
    {
      ...response.sources[0],
      artifact_id: 'artifact-17',
      extract_id: 'extract-17',
      project_id: 'project-17',
      source_locator: 'Planilha!B17',
      registration_period: { start: '2026-09-01', end: '2026-09-24' },
      validity: { start: '2026-09-01', end: null },
      attributes: { Status: 'Em andamento' },
    },
    0,
  );
  render(
    <TooltipProvider>
      <DocumentViewer document={source} />
    </TooltipProvider>,
  );
  for (const value of [
    'artifact-17',
    'extract-17',
    'project-17',
    'Planilha!B17',
    'Período de registro',
    'Vigência',
    'Em andamento',
    '01 de set. de 2026 — 24 de set. de 2026',
    '01 de set. de 2026 — Fim não informado',
  ]) {
    expect(screen.getByText(value)).toBeVisible();
  }
});

it('exibe o identificador que permite localizar a auditoria', () => {
  const message = toAssistantMessage(
    { ...response, trace_id: 'trace-17' },
    { roundTripMs: 10, intentLayerEnabled: false },
  );
  render(<ResponseDetails message={message} />);
  expect(screen.getByText('trace-17')).toBeVisible();
});

it('sinaliza fontes consultadas que nao sustentam uma resposta insuficiente', () => {
  const sources = [toRetrievedDocument(response.sources[0], 0)];
  const { rerender } = render(
    <SourceCitations sources={sources} selectedId={null} onSelect={() => {}} />,
  );
  expect(screen.getByText('Fontes (1)')).toBeVisible();
  rerender(
    <SourceCitations sources={sources} selectedId={null} onSelect={() => {}} unused />,
  );
  expect(
    screen.getByText('Fontes consultadas, sem evidência para esta resposta'),
  ).toBeVisible();
});
