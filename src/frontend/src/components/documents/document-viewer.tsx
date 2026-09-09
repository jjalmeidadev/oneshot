import { ExternalLink, FileSearch, Hash, Info, Layers, Timer } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { formatDateTime } from '@/lib/format';
import type { RetrievedDocument } from '@/lib/domain';

/**
 * Visualizacao do documento de onde a resposta saiu.
 *
 * Os metadados exibidos sao exatamente os campos de `GeminiSource`: titulo,
 * lista de origem, `webUrl`, `lastModifiedDateTime` e o score do recuperador.
 *
 * O trecho do documento e o unico campo que a API ainda nao entrega. O texto
 * existe no backend, em `RetrievedDocument.document.content`, mas e descartado
 * ao montar `GeminiSource` em `app/gemini/client.py`. Enquanto o campo nao vier,
 * esta area mostra o aviso abaixo em vez de inventar conteudo — ver README,
 * "Lacuna 1".
 */
export function DocumentViewer({ document }: { document: RetrievedDocument }) {
  return (
    <article className="flex h-full flex-col">
      <header className="px-3 pb-3 pt-1">
        <div className="flex items-start gap-2">
          <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded bg-primary font-mono text-[11px] font-semibold text-primary-fg">
            {document.citationOrder}
          </span>
          <h3 className="min-w-0 flex-1 text-sm font-semibold leading-5 text-fg">
            {document.title}
          </h3>
        </div>

        <dl className="grid gap-1.5 pt-3 text-2xs">
          <MetaRow icon={Layers} label="Lista de origem" value={document.listName} />
          <MetaRow
            icon={Timer}
            label="Atualizado em"
            value={formatDateTime(document.lastModified)}
          />
          <MetaRow icon={Hash} label="Identificador" value={document.id} mono />
          <div className="flex items-center gap-1.5">
            <FileSearch size={12} className="shrink-0 text-fg-subtle" />
            <dt className="text-fg-subtle">Score do recuperador</dt>
            <dd className="ml-auto flex items-center gap-1.5">
              <Badge tone="primary">{document.score.toFixed(3)}</Badge>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    aria-label="Como o score é calculado"
                    className="rounded-full text-fg-subtle hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <Info size={12} />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="left" className="w-72">
                  Soma dos termos da pergunta encontrados no documento, com peso dobrado
                  para os que aparecem no título, mais a cobertura da consulta. Não é
                  uma probabilidade e não tem teto em 1.
                </TooltipContent>
              </Tooltip>
            </dd>
          </div>
        </dl>
      </header>

      <Separator />

      <div className="min-h-0 flex-1 overflow-y-auto scrollbar-slim px-3 py-3">
        {document.excerpt ? (
          <blockquote className="border-l-2 border-primary/40 pl-3 text-xs leading-6 text-fg-muted">
            {document.excerpt}
          </blockquote>
        ) : (
          <div className="rounded-lg border border-dashed border-border-strong bg-muted px-3 py-3">
            <p className="text-2xs font-medium text-fg">
              Trecho não disponível nesta resposta
            </p>
            <p className="pt-1 text-2xs leading-4 text-fg-muted">
              O conteúdo do documento é usado pelo backend ao montar o contexto, mas não
              acompanha a resposta da API. Abrir o documento na origem mostra o texto
              completo.
            </p>
          </div>
        )}
      </div>

      <div className="border-t border-border p-3">
        <Button asChild variant="outline" size="sm" className="w-full">
          <a href={document.webUrl} target="_blank" rel="noreferrer">
            <ExternalLink size={13} />
            Abrir no SharePoint
          </a>
        </Button>
        <p className="pt-2 text-center text-2xs text-fg-subtle">
          Lista simulada do MVP · dados fictícios
        </p>
      </div>
    </article>
  );
}

function MetaRow({
  icon: Icon,
  label,
  value,
  mono = false,
}: {
  icon: typeof Layers;
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <Icon size={12} className="shrink-0 text-fg-subtle" />
      <dt className="shrink-0 text-fg-subtle">{label}</dt>
      <dd
        className={
          mono
            ? 'ml-auto truncate font-mono text-fg-muted'
            : 'ml-auto truncate text-fg-muted'
        }
        title={value}
      >
        {value}
      </dd>
    </div>
  );
}
