import { describe, expect, it } from 'vitest';
import { toAssistantMessage } from './domain';
import { response } from '@/tests/fixtures';
import type { ChatResponse } from './api/schemas';

describe('referências preservadas na interface', () => {
  it('preserva evidencias, periodos e correlacao ao converter a resposta', () => {
    const source = {
      ...response.sources[0],
      citation_id: 'Fonte 1',
      artifact_id: 'artifact-17',
      extract_id: 'extract-17',
      project_id: 'project-17',
      source_locator: 'Planilha!B17',
      registration_period: { start: '2026-09-01', end: '2026-09-24' },
      validity: { start: '2026-09-01', end: null },
      attributes: { Status: 'Em andamento' },
    };
    const payload: ChatResponse = {
      ...response,
      contract_version: '1.1.0',
      trace_id: 'trace-17',
      evidence_status: 'referenced',
      claims: [
        {
          text: source.excerpt!,
          citation_ids: ['Fonte 1'],
          evidence: [
            {
              citation_id: 'Fonte 1',
              field: 'excerpt',
              attribute: null,
              quote: source.excerpt!,
            },
          ],
        },
      ],
      sources: [
        source,
        { ...source, citation_id: 'Fonte 2', extract_id: 'extract-18' },
      ],
    };
    const message = toAssistantMessage(payload, {
      roundTripMs: 10,
      intentLayerEnabled: true,
    });
    expect(message.traceId).toBe('trace-17');
    expect(message.contractVersion).toBe('1.1.0');
    expect(message.claims).toEqual(payload.claims);
    expect(message.evidenceStatus).toBe('referenced');
    expect(message.sources?.[0]).toMatchObject({
      sourceId: source.id,
      artifactId: 'artifact-17',
      extractId: 'extract-17',
      projectId: 'project-17',
      sourceLocator: 'Planilha!B17',
      registrationPeriod: source.registration_period,
      validity: source.validity,
      attributes: source.attributes,
    });
    expect(message.sources?.[0].id).not.toBe(message.sources?.[1].id);
  });

  it('mantem abstencao sem criar afirmacoes ou metadados ausentes', () => {
    const message = toAssistantMessage(
      {
        ...response,
        evidence_status: 'insufficient',
        text: 'Não há evidência recuperada suficiente.',
        claims: [],
      },
      { roundTripMs: 10, intentLayerEnabled: false },
    );
    expect(message.evidenceStatus).toBe('insufficient');
    expect(message.claims).toEqual([]);
    expect(message.sources?.[0].registrationPeriod).toBeUndefined();
    expect(message.sources?.[0].id).toBe(response.sources[0].id);
  });
});
