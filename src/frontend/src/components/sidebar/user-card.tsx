import { LogOut } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { PROFILE_LABELS, useAccessSession } from '@/state/access-session';

export function UserCard() {
  const { session, logout } = useAccessSession();
  if (!session) return null;
  const { profile } = session;

  return (
    <div className="rounded-lg bg-muted p-2 text-xs">
      <p className="truncate font-semibold text-fg">
        {profile.display_name || profile.email}
      </p>
      <p className="mt-0.5 text-fg-muted">{PROFILE_LABELS[profile.profile_key]}</p>
      <p className="truncate text-fg-subtle">{profile.scope_label}</p>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="mt-2 w-full justify-start"
        onClick={logout}
      >
        <LogOut size={14} />
        Sair
      </Button>
    </div>
  );
}
