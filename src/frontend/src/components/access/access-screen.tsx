import { Eye, EyeOff, LogIn } from 'lucide-react';
import { useRef, useState, type FormEvent } from 'react';

import { Button } from '@/components/ui/button';
import type { ProfileKey } from '@/lib/api';
import { PROFILE_LABELS, useAccessSession } from '@/state/access-session';

const PROFILE_KEYS = Object.keys(PROFILE_LABELS) as ProfileKey[];

export function AccessScreen() {
  const { entryMessage, login } = useAccessSession();
  const [profileKey, setProfileKey] = useState<ProfileKey | ''>('');
  const [accessToken, setAccessToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const profileRef = useRef<HTMLSelectElement>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setValidationMessage(null);
    if (!profileKey || !accessToken.trim()) {
      setValidationMessage('Selecione uma persona e informe o token de acesso.');
      profileRef.current?.focus();
      return;
    }
    setLoading(true);
    const result = await login(profileKey, accessToken.trim());
    setLoading(false);
    if (!result.ok) {
      if (result.clearToken) setAccessToken('');
      profileRef.current?.focus();
    }
  };

  const message = validationMessage ?? entryMessage;

  return (
    <main className="flex min-h-screen items-center justify-center bg-app p-4 sm:p-8">
      <section className="w-full max-w-lg rounded-2xl border border-border bg-surface p-6 shadow-panel sm:p-8">
        <div className="mb-6 flex items-center gap-3">
          <img
            src="/logo-metro-sp.png"
            alt="Metrô de São Paulo"
            className="h-10 w-auto rounded"
          />
          <div>
            <h1 className="text-xl font-semibold text-fg">Agente de Portfólio</h1>
            <p className="text-sm text-fg-muted">
              O acesso e o escopo são confirmados pelo perfil vinculado ao token.
            </p>
          </div>
        </div>

        <form className="space-y-5" onSubmit={submit} noValidate>
          <div>
            <label htmlFor="access-persona" className="text-sm font-medium text-fg">
              Persona
            </label>
            <select
              ref={profileRef}
              id="access-persona"
              autoFocus
              required
              value={profileKey}
              onChange={(event) => setProfileKey(event.target.value as ProfileKey | '')}
              className="mt-1.5 h-11 w-full rounded-lg border border-border bg-surface px-3 text-sm text-fg outline-none focus:border-primary focus:ring-2 focus:ring-ring"
            >
              <option value="">Selecione uma persona</option>
              {PROFILE_KEYS.map((key) => (
                <option key={key} value={key}>
                  {PROFILE_LABELS[key]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="access-token" className="text-sm font-medium text-fg">
              Access token JWT
            </label>
            <div className="relative mt-1.5">
              <input
                id="access-token"
                required
                type={showToken ? 'text' : 'password'}
                autoComplete="off"
                spellCheck={false}
                value={accessToken}
                onChange={(event) => setAccessToken(event.target.value)}
                className="h-11 w-full rounded-lg border border-border bg-surface px-3 pr-12 font-mono text-sm text-fg outline-none focus:border-primary focus:ring-2 focus:ring-ring"
              />
              <button
                type="button"
                onClick={() => setShowToken((value) => !value)}
                className="absolute inset-y-0 right-0 flex w-11 items-center justify-center text-fg-muted hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label={showToken ? 'Ocultar token' : 'Mostrar token'}
              >
                {showToken ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            <p className="mt-1 text-xs text-fg-muted">
              O token fica somente na memória e será descartado ao sair ou recarregar.
            </p>
          </div>

          {message && (
            <p
              role="alert"
              className="rounded-lg bg-danger-soft p-3 text-sm text-danger"
            >
              {message}
            </p>
          )}

          <Button type="submit" size="lg" className="w-full" disabled={loading}>
            <LogIn size={18} />
            {loading ? 'Validando acesso...' : 'Entrar'}
          </Button>
        </form>
      </section>
    </main>
  );
}
