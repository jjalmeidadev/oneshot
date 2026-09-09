import { cn } from '@/lib/utils';

/**
 * Barra de confianca do classificador.
 *
 * O marcador do limiar existe porque o numero sozinho nao diz nada: e a posicao
 * dele em relacao ao limiar que decide se a solicitacao aciona um handler, cai
 * no fluxo generico da macrointencao ou recebe a resposta de limitacao.
 */
export function Meter({
  value,
  threshold,
  tone = 'primary',
  className,
  label,
}: {
  /** Valor entre 0 e 1. */
  value: number;
  /** Limiar entre 0 e 1; desenhado como marca vertical. */
  threshold?: number;
  tone?: 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
  label?: string;
}) {
  const percent = Math.max(0, Math.min(1, value)) * 100;
  const tones = {
    primary: 'bg-primary',
    success: 'bg-success',
    warning: 'bg-warning',
    danger: 'bg-danger',
  } as const;

  return (
    <div
      className={cn(
        'relative h-1.5 w-full overflow-hidden rounded-full bg-subtle',
        className,
      )}
      role="meter"
      aria-valuenow={Number(percent.toFixed(1))}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
    >
      <div
        className={cn('h-full rounded-full transition-[width]', tones[tone])}
        style={{ width: `${percent}%` }}
      />
      {threshold !== undefined && (
        <span
          className="absolute inset-y-0 w-px bg-fg/50"
          style={{ left: `${Math.max(0, Math.min(1, threshold)) * 100}%` }}
          aria-hidden
        />
      )}
    </div>
  );
}
