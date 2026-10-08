import { Info } from 'lucide-react';

import type { ResponseBlock } from '@/lib/api/schemas';
import type { RetrievedDocument } from '@/lib/domain';

type ReferencesProps = {
  sources: RetrievedDocument[];
  onSelectSource: (id: string) => void;
};

function References({
  ids,
  sources,
  onSelectSource,
}: ReferencesProps & { ids: string[] }) {
  return (
    <span className="mt-2 flex flex-wrap gap-2 text-xs">
      {ids.map((id) => {
        const source = sources.find(
          (item) => (item.citationId ?? `Fonte ${item.citationOrder}`) === id,
        );
        return source ? (
          <button
            key={id}
            type="button"
            className="rounded px-1 text-primary underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label={`Consultar ${id}: ${source.title}`}
            onClick={() => onSelectSource(source.id)}
          >
            {id}
          </button>
        ) : (
          <span key={id}>{id}</span>
        );
      })}
    </span>
  );
}

export function ResponseTable({
  block,
  ...references
}: ReferencesProps & { block: Extract<ResponseBlock, { type: 'table' }> }) {
  return (
    <div
      role="region"
      aria-label="Tabela da resposta, role horizontalmente para ver todas as colunas"
      tabIndex={0}
      className="max-w-full overflow-x-auto rounded-xl border border-border bg-surface text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <table className="w-full border-collapse text-left text-sm">
        <caption className="p-3 text-left font-semibold">Tabela da resposta</caption>
        <thead className="bg-muted">
          <tr>
            {block.columns.map((column, index) => (
              <th key={index} scope="col" className="px-3 py-2 font-semibold">
                {column}
              </th>
            ))}
            <th scope="col" className="px-3 py-2 font-semibold">
              Fontes
            </th>
          </tr>
        </thead>
        <tbody>
          {block.rows.map((row, index) => (
            <tr key={index} className="border-t border-border">
              {row.cells.map((cell, column) => (
                <td key={column} className="min-w-32 break-words px-3 py-2 align-top">
                  {cell}
                </td>
              ))}
              <td className="min-w-32 px-3 py-2 align-top">
                <References ids={row.citation_ids} {...references} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const numberFormat = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 });

export function ResponseIndicator({
  block,
  ...references
}: ReferencesProps & { block: Extract<ResponseBlock, { type: 'indicator' }> }) {
  return (
    <section
      aria-label={`Indicador: ${block.label}`}
      className="rounded-xl border border-border bg-primary-soft p-3 text-fg"
    >
      <dl>
        <dt className="text-sm font-semibold">{block.label}</dt>
        <dd className="mt-1 break-words text-2xl font-bold tabular-nums text-primary">
          {numberFormat.format(block.value)}
          {block.unit ?? ''}
        </dd>
      </dl>
      <References ids={block.citation_ids} {...references} />
    </section>
  );
}

export function ResponseHighlight({
  block,
  ...references
}: ReferencesProps & { block: Extract<ResponseBlock, { type: 'highlight' }> }) {
  return (
    <aside
      aria-label="Destaque da resposta"
      className="rounded-xl border-l-4 border-warning bg-warning-soft p-3 text-fg"
    >
      <p className="flex items-center gap-2 text-sm font-semibold text-warning">
        <Info size={16} aria-hidden="true" />
        Destaque
      </p>
      <p className="mt-1 whitespace-pre-wrap break-words text-sm leading-6">
        {block.text}
      </p>
      <References ids={block.citation_ids} {...references} />
    </aside>
  );
}

// A API pode evoluir ou devolver dados incompletos: preserve o texto da mensagem.
function isRenderable(block: ResponseBlock): boolean {
  if (!block || typeof block !== 'object') return false;
  const refs = (ids: string[]) =>
    Array.isArray(ids) &&
    ids.length > 0 &&
    ids.every((id) => typeof id === 'string' && id.trim().length > 0);
  switch (block.type) {
    case 'table':
      return (
        Array.isArray(block.columns) &&
        block.columns.length > 0 &&
        block.columns.every((column) => typeof column === 'string') &&
        Array.isArray(block.rows) &&
        block.rows.length > 0 &&
        block.rows.every(
          (row) =>
            row &&
            Array.isArray(row.cells) &&
            row.cells.length === block.columns.length &&
            row.cells.every((cell) => typeof cell === 'string') &&
            refs(row.citation_ids),
        )
      );
    case 'indicator':
      return (
        typeof block.label === 'string' &&
        block.label.trim().length > 0 &&
        typeof block.value === 'number' &&
        Number.isFinite(block.value) &&
        (block.unit == null || block.unit === '%') &&
        refs(block.citation_ids)
      );
    case 'highlight':
      return (
        typeof block.text === 'string' &&
        block.text.trim().length > 0 &&
        refs(block.citation_ids)
      );
    default:
      return false;
  }
}

export function ResponseBlocks({
  blocks,
  ...references
}: ReferencesProps & { blocks: ResponseBlock[] }) {
  const valid = Array.isArray(blocks) ? blocks.filter(isRenderable) : [];
  if (valid.length === 0) return null;
  return (
    <div aria-label="Dados em destaque da resposta" className="mt-3 space-y-3">
      {valid.map((block, index) => {
        switch (block.type) {
          case 'table':
            return <ResponseTable key={index} block={block} {...references} />;
          case 'indicator':
            return <ResponseIndicator key={index} block={block} {...references} />;
          case 'highlight':
            return <ResponseHighlight key={index} block={block} {...references} />;
        }
      })}
    </div>
  );
}
