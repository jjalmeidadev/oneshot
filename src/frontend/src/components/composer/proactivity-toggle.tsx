import { Sparkles } from 'lucide-react';

import { Switch } from '@/components/ui/switch';
import { cn } from '@/lib/utils';

export function ProactivityToggle({
  enabled,
  onChange,
  disabled,
}: {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-full border px-2.5 py-1 transition-colors',
        enabled ? 'border-primary/40 bg-primary-soft' : 'border-border bg-muted',
        disabled && 'opacity-60',
      )}
    >
      <Sparkles
        size={13}
        className={cn('shrink-0', enabled ? 'text-primary' : 'text-fg-subtle')}
      />
      <label
        htmlFor="proactivity-mode"
        className={cn(
          'cursor-pointer select-none text-2xs font-medium',
          enabled ? 'text-primary' : 'text-fg-muted',
        )}
      >
        Modo proatividade
      </label>
      <Switch
        id="proactivity-mode"
        checked={enabled}
        onCheckedChange={onChange}
        disabled={disabled}
        aria-label="Ativar sugestões proativas depois da resposta principal"
      />
    </div>
  );
}
