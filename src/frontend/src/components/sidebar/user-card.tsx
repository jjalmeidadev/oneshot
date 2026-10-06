import { LogOut } from 'lucide-react';

import { Button } from '@/components/ui/button';
import type { AccessProfile } from '@/lib/api';
import { PROFILE_LABELS, useAccessSession } from '@/state/access-session';

/**
 * Perfil da sessao autenticada, exibido na engrenagem de ajustes (S5-20 com a
 * S5-04). O token nunca aparece na interface: so nome, perfil, escopo e o que
 * o perfil pode fazer, todos resolvidos pelo backend.
 */
export function UserCard() {
  const { session, logout } = useAccessSession();
  if (!session) return null;
  return <ProfileSummary profile={session.profile} onLogout={logout} />;
}

export function ProfileSummary({
  profile,
  onLogout,
}: {
  profile: AccessProfile;
  onLogout: () => void;
}) {
  const name = profile.display_name || profile.email;
  const initials = name
    .replace(/\[.*?\]/g, '')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('');

  return (
    <div className="text-xs">
      <div className="flex items-start gap-2.5">
        <span
          aria-hidden
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-soft text-2xs font-semibold text-primary"
        >
          {initials || '?'}
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold text-fg">{name}</p>
          <p className="truncate text-fg-muted">
            {PROFILE_LABELS[profile.profile_key]} · {profile.scope_label}
          </p>
          <p className="mt-0.5 text-2xs text-fg-subtle">
            {describePermissions(profile)}
          </p>
        </div>
      </div>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="mt-2 w-full justify-start"
        onClick={onLogout}
      >
        <LogOut size={14} aria-hidden />
        Sair
      </Button>
    </div>
  );
}

function describePermissions(profile: AccessProfile): string {
  const actions = [
    profile.can_read && 'consultar',
    profile.can_write && 'alterar',
    profile.can_export && 'exportar',
  ].filter(Boolean) as string[];
  if (actions.length === 0) return 'Sem permissões ativas';
  const last = actions.pop();
  return `Pode ${actions.length ? `${actions.join(', ')} e ${last}` : last}`;
}
