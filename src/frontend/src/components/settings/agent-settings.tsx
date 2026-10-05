import { Code2, Layers, Settings, Sparkles, type LucideIcon } from 'lucide-react';
import { useId, type ReactNode } from 'react';

import { UserCard } from '@/components/sidebar/user-card';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';

/**
 * Engrenagem de ajustes do agente, no canto superior direito do chat (S5-20).
 *
 * Centraliza o que antes ficava espalhado pela tela: os controles que estendem
 * a capacidade do modelo (validacao de intencao e sugestoes proativas), o modo
 * tecnico e o token da sessao. A proatividade continua controlavel tambem no
 * proprio card da sugestao, que e onde o usuario a percebe (ocorrencia O8).
 */
export function AgentSettings({
  intentLayerEnabled,
  onIntentLayerChange,
  proactivityEnabled,
  onProactivityChange,
  showTechnicalDetails,
  onShowTechnicalDetailsChange,
  accessToken,
  onAccessTokenChange,
  disabled = false,
}: {
  intentLayerEnabled: boolean;
  onIntentLayerChange: (enabled: boolean) => void;
  proactivityEnabled: boolean;
  onProactivityChange: (enabled: boolean) => void;
  showTechnicalDetails: boolean;
  onShowTechnicalDetailsChange: (enabled: boolean) => void;
  accessToken: string;
  onAccessTokenChange: (token: string) => void;
  /** Bloqueia as trocas de modo enquanto uma resposta esta em andamento. */
  disabled?: boolean;
}) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon-sm" aria-label="Ajustes do agente">
          <Settings size={16} />
        </Button>
      </PopoverTrigger>
      <PopoverContent aria-label="Ajustes do agente">
        <p className="px-1 pb-2 text-xs font-semibold text-fg">Ajustes do agente</p>

        <div className="space-y-1">
          <SettingRow
            icon={Layers}
            label="Validação de intenção"
            description="Classifica a pergunta antes de chamar o modelo de linguagem."
            checked={intentLayerEnabled}
            onCheckedChange={onIntentLayerChange}
            disabled={disabled}
          />
          <SettingRow
            nested
            icon={Sparkles}
            label="Sugestões proativas"
            description={
              intentLayerEnabled
                ? 'Depois da resposta, o agente pode oferecer uma ação extra. Nada é executado sem a sua confirmação.'
                : 'Requer a validação de intenção ligada.'
            }
            checked={proactivityEnabled}
            onCheckedChange={onProactivityChange}
            disabled={disabled || !intentLayerEnabled}
          />
          <SettingRow
            icon={Code2}
            label="Mostrar detalhes técnicos"
            description="Exibe a intenção classificada, o modelo, a latência e os tokens de cada resposta."
            checked={showTechnicalDetails}
            onCheckedChange={onShowTechnicalDetailsChange}
          />
        </div>

        <Separator className="my-3" />

        <div className="px-1 pb-1">
          <UserCard
            accessToken={accessToken}
            onAccessTokenChange={onAccessTokenChange}
          />
        </div>
      </PopoverContent>
    </Popover>
  );
}

function SettingRow({
  icon: Icon,
  label,
  description,
  checked,
  onCheckedChange,
  disabled = false,
  nested = false,
}: {
  icon: LucideIcon;
  label: string;
  description: ReactNode;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  nested?: boolean;
}) {
  const id = useId();
  return (
    <div
      className={cn(
        'flex items-start gap-2.5 rounded-lg px-1 py-2',
        nested && 'ml-4 border-l border-border pl-3',
        disabled && 'opacity-60',
      )}
    >
      <Icon
        size={14}
        className={cn('mt-0.5 shrink-0', checked ? 'text-primary' : 'text-fg-subtle')}
      />
      <div className="min-w-0 flex-1">
        <label
          htmlFor={id}
          className={cn(
            'block select-none text-xs font-medium text-fg',
            disabled ? 'cursor-not-allowed' : 'cursor-pointer',
          )}
        >
          {label}
        </label>
        <p id={`${id}-description`} className="mt-0.5 text-2xs leading-4 text-fg-muted">
          {description}
        </p>
      </div>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        disabled={disabled}
        aria-describedby={`${id}-description`}
      />
    </div>
  );
}
