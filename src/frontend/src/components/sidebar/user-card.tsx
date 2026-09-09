import { ShieldCheck } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { MOCK_USER } from '@/data/mock';

const ROLE_LABELS: Record<string, string> = {
  diretoria: 'Diretoria',
  pmo: 'PMO',
  lider_subportfolio: 'Líder de subportfólio',
  equipe_projeto: 'Equipe de projeto',
  gti: 'GTI',
  admin: 'Administrador',
};

/**
 * Identificacao do usuario.
 *
 * A autenticacao nao e feita por este frontend nem pelo backend: a identidade
 * vem do Microsoft Entra ID atraves do canal (Secao 6.2.4). Os dados abaixo
 * saem de `data/mock.ts` e devem ser trocados pelo perfil que o canal entregar
 * — ver README, "Ponto de integracao 3".
 */
export function UserCard() {
  const initials = MOCK_USER.displayName
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-left">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-2xs font-semibold text-primary-fg">
            {initials}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-xs font-medium text-fg">
              {MOCK_USER.displayName}
            </span>
            <span className="block truncate text-2xs text-fg-subtle">
              {MOCK_USER.department}
            </span>
          </span>
          <Badge tone="outline" className="shrink-0">
            {ROLE_LABELS[MOCK_USER.roleName] ?? MOCK_USER.roleName}
          </Badge>
        </div>
      </TooltipTrigger>
      <TooltipContent side="top" align="start">
        <p className="flex items-center gap-1.5 font-medium">
          <ShieldCheck size={13} /> Identidade simulada
        </p>
        <p className="mt-1 text-fg-muted">
          O perfil viria do Microsoft Entra ID pelo canal. O escopo do que cada perfil
          enxerga do portfólio depende de <code>access_rules</code>, que ainda não está
          implementado.
        </p>
      </TooltipContent>
    </Tooltip>
  );
}
