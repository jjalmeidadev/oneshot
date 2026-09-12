import { AnimatePresence, motion } from 'framer-motion';
import { FileStack, Gauge, Library } from 'lucide-react';

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
 * A aba "Resposta" reune latencia, tokens e o resultado do classificador.
 */
export function DocumentPanel({
  documents,
  selectedDocument,
  onSelect,
  lastAssistantMessage,
}: {
  documents: RetrievedDocument[];
  selectedDocument: RetrievedDocument | null;
  onSelect: (id: string) => void;
  lastAssistantMessage: ChatMessage | null;
}) {
  return (
    <Tabs defaultValue="sources" className="flex h-full flex-col bg-surface">
      <div className="px-3 pb-2 pt-3">
        <TabsList className="w-full">
          <TabsTrigger value="sources" className="flex-1">
            <Library size={13} />
            Documentos
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
        {documents.length === 0 ? (
          <EmptyState
            icon={FileStack}
            title="Nenhum documento recuperado"
            description="Quando a pergunta casar com alguma lista indexada, os documentos usados na resposta aparecem aqui."
          />
        ) : (
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
        )}
      </TabsContent>

      <TabsContent value="details" className="min-h-0 flex-1">
        <ScrollArea className="h-full">
          <ResponseDetails message={lastAssistantMessage} />
        </ScrollArea>
      </TabsContent>
    </Tabs>
  );
}
