import { Info, Layers, Zap } from 'lucide-react';

import { Switch } from '@/components/ui/switch';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import {
  INTENT_CATALOG_SIZE,
  INTENT_MACRO_THRESHOLD,
  INTENT_SPECIFIC_THRESHOLD,
} from '@/lib/api/constants';
import { cn } from '@/lib/utils';

/**
 * Toggle da camada validadora de intencao, acima do campo de texto.
 *
 * Ligado, a solicitacao passa primeiro pelo classificador hierarquico de
 * `app/nlp/inference.py`: ele preve a macrointencao e a intencao especifica e
 * aplica os limiares antes de qualquer chamada ao modelo de linguagem. Abaixo
 * do limiar da macro, o agente devolve a resposta controlada do RF08 sem
 * chamar o LLM.
 *
 * Desligado, a pergunta vai direto para `POST /api/chat`, que so faz a
 * recuperacao no RAG e chama o Gemini.
 *
 * O estado viaja como `use_intent_classifier` nas rotas de texto e audio.
 * Desligar o controle e um opt-out explicito do pipeline de PLN.
 */
export function IntentToggle({
  enabled,
  onChange,
  disabled,
}: {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <div
        className={cn(
          'flex items-center gap-2 rounded-full border px-2.5 py-1 transition-colors',
          enabled ? 'border-primary/40 bg-primary-soft' : 'border-border bg-muted',
        )}
      >
        {enabled ? (
          <Layers size={13} className="shrink-0 text-primary" />
        ) : (
          <Zap size={13} className="shrink-0 text-fg-subtle" />
        )}

        <label
          htmlFor="intent-layer"
          className={cn(
            'cursor-pointer select-none text-2xs font-medium',
            enabled ? 'text-primary' : 'text-fg-muted',
          )}
        >
          Validação de intenção
        </label>

        <Switch
          id="intent-layer"
          checked={enabled}
          onCheckedChange={onChange}
          disabled={disabled}
          aria-label="Ativar a camada validadora de intenção antes do modelo de linguagem"
        />
      </div>

      <span className="text-2xs text-fg-subtle">
        {enabled
          ? 'Classificador de intenções antes do LLM'
          : 'Pergunta direto para o LLM com RAG'}
      </span>

      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            aria-label="Como funciona a validação de intenção"
            className="rounded-full p-0.5 text-fg-subtle transition-colors hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <Info size={13} />
          </button>
        </TooltipTrigger>
        <TooltipContent side="top" align="start" className="w-80">
          <p className="font-medium">Camada validadora de intenção</p>
          <p className="mt-1 text-fg-muted">
            Ligada, a solicitação passa antes pelo classificador hierárquico: ele prevê
            a macrointenção entre CONSULTA, TRANSAÇÃO, ALERTA e FORA_DE_ESCOPO e, em
            seguida, uma das {INTENT_CATALOG_SIZE} intenções do catálogo.
          </p>
          <p className="mt-2 text-fg-muted">
            Abaixo de {INTENT_MACRO_THRESHOLD} na macrointenção, o agente responde com a
            mensagem de limitação sem chamar o modelo de linguagem. Acima disso, mas
            abaixo de {INTENT_SPECIFIC_THRESHOLD} na intenção, segue pelo fluxo genérico
            da macro em vez de acionar um handler incerto.
          </p>
          <p className="mt-2 text-fg-muted">
            Desligada, a pergunta vai direto ao LLM com a recuperação do RAG — mais
            rápido, sem a barreira que evita acionar o handler errado.
          </p>
        </TooltipContent>
      </Tooltip>
    </div>
  );
}
