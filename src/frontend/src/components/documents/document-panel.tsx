import { AnimatePresence, motion } from 'framer-motion';
import { BookOpen, FileStack, Gauge, Library } from 'lucide-react';

import { DocumentCard } from '@/components/documents/document-card';
import { DocumentViewer } from '@/components/documents/document-viewer';
import { ResponseDetails } from '@/components/documents/response-details';
import { EmptyState } from '@/components/ui/empty-state';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { ChatMessage, RetrievedDocument } from '@/lib/domain';

/**
 * Painel da direita: o que o RAG recuperou para a ultima resposta.
 *
 * A lista mostra os documentos na mesma ordem das citacoes `[Fonte N]`; o
 * documento selecionado abre logo abaixo, com os metadados que a API entrega.
 * A aba "Resposta", com latencia, tokens e o resultado do classificador, so
 * existe no modo tecnico (S5-20); fora dele o painel mostra apenas as fontes.
 *
 * O painel nao declara landmark proprio: quem o envolve decide (o `aside` no
 * layout de tres colunas ou o dialogo nos paineis deslizantes).
 */
export function DocumentPanel({
  documents,
  selectedDocument,
  onSelect,
  lastAssistantMessage,
  showResponseDetails = false,
  showHeading = true,
}: {
  documents: RetrievedDocument[];
  selectedDocument: RetrievedDocument | null;
  onSelect: (id: string) => void;
  lastAssistantMessage: ChatMessage | null;
  showResponseDetails?: boolean;
  /**
   * Falso quando quem envolve o painel ja tem o titulo (o `DialogTitle` do
   * painel deslizante), para nao haver dois titulos "Fontes da resposta".
   */
  showHeading?: boolean;
}) {
  const sources = (
    <SourceList
      documents={documents}
      selectedDocument={selectedDocument}
      onSelect={onSelect}
    />
  );

  if (!showResponseDetails) {
    return (
      <div className="flex h-full flex-col bg-surface">
        {showHeading && (
          <h2 className="flex items-center gap-1.5 px-4 pb-2 pt-3.5 text-xs font-semibold text-fg">
            <BookOpen size={14} className="text-primary" aria-hidden />
            Fontes da resposta
            {documents.length > 0 && (
              <span className="rounded bg-muted px-1 font-mono text-[10px] text-fg-muted">
                {documents.length}
              </span>
            )}
          </h2>
        )}
        <div className="flex min-h-0 flex-1 flex-col">{sources}</div>
      </div>
    );
  }

  return (
    <Tabs defaultValue="sources" className="flex h-full flex-col bg-surface">
      {/* Mantem a hierarquia de titulos: as secoes da aba Resposta sao h3. */}
      {showHeading && <h2 className="sr-only">Fontes da resposta</h2>}
      <div className="px-3 pb-2 pt-3">
        <TabsList className="w-full">
          <TabsTrigger value="sources" className="flex-1">
            <Library size={13} />
            Fontes
            {documents.length > 0 && (
              <span className="rounded bg-border px-1 font-mono text-[10px]">
                {documents.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="details" className="flex-1">
            <Gauge size={13} />
            Resposta
          </TabsTrigger>
        </TabsList>
      </div>

      <TabsContent value="sources" className="flex min-h-0 flex-1 flex-col">
        {sources}
      </TabsContent>

      <TabsContent value="details" className="min-h-0 flex-1">
        <ScrollArea className="h-full">
          <ResponseDetails message={lastAssistantMessage} />
        </ScrollArea>
      </TabsContent>
    </Tabs>
  );
}

function SourceList({
  documents,
  selectedDocument,
  onSelect,
}: {
  documents: RetrievedDocument[];
  selectedDocument: RetrievedDocument | null;
  onSelect: (id: string) => void;
}) {
  if (documents.length === 0) {
    return (
      <EmptyState
        icon={FileStack}
        title="Nenhuma fonte nesta resposta"
        description="Quando a pergunta casar com alguma lista indexada, os documentos usados na resposta aparecem aqui."
      />
    );
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <ScrollArea className="max-h-56 shrink-0">
        <div className="space-y-1.5 px-3 pb-3">
          {documents.map((document) => (
            <DocumentCard
              key={document.id}
              document={document}
              selected={document.id === selectedDocument?.id}
              onSelect={() => onSelect(document.id)}
            />
          ))}
        </div>
      </ScrollArea>

      <Separator />

      <div className="min-h-0 flex-1">
        <AnimatePresence mode="wait">
          {selectedDocument && (
            <motion.div
              key={selectedDocument.id}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              className="h-full"
            >
              <DocumentViewer document={selectedDocument} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
