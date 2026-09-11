import { Sparkles } from 'lucide-react';

import { SUGGESTED_PROMPTS } from '@/data/prompts';

/** Tela inicial de uma conversa vazia. */
export function ChatEmptyState({ onPick }: { onPick: (prompt: string) => void }) {
  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center px-4 py-10 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-soft text-primary">
        <Sparkles size={22} />
      </span>
      <h2 className="pt-4 text-lg font-semibold text-fg">
        Agente de Portfólio do Metrô
      </h2>
      <p className="max-w-md pt-2 text-sm leading-6 text-fg-muted">
        Pergunte em linguagem natural sobre projetos, cronogramas, TAPs e documentos
        normativos. Cada resposta indica os documentos de onde a informação veio.
      </p>

      <div className="grid w-full gap-2 pt-6 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => onPick(prompt)}
            className="rounded-xl border border-border bg-surface px-3.5 py-3 text-left text-xs leading-5 text-fg-muted transition-colors hover:border-primary hover:bg-primary-soft hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
