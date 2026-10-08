import type { ResponseBlock } from '@/lib/api/schemas';

/** Exemplo sintético no formato 1.2.0 da #270; não representa dados reais. */
export const responseBlocks: ResponseBlock[] = [
  {
    type: 'table',
    columns: ['Informação', 'Valor'],
    rows: [
      { cells: ['Avanço', '42,5%'], citation_ids: ['Fonte 1'] },
      { cells: ['Status', 'Em andamento'], citation_ids: ['Fonte 1'] },
    ],
  },
  {
    type: 'indicator',
    label: 'Avanço',
    value: 42.5,
    unit: '%',
    citation_ids: ['Fonte 1'],
  },
  { type: 'highlight', text: 'Status: Em andamento', citation_ids: ['Fonte 1'] },
];
