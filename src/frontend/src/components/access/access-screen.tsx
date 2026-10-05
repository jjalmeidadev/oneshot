import { Eye, EyeOff, LogIn } from 'lucide-react';
import { useRef, useState, type FormEvent } from 'react';

import { Button } from '@/components/ui/button';
import type { ProfileKey } from '@/lib/api';
import { PROFILE_LABELS, useAccessSession } from '@/state/access-session';

const PROFILE_KEYS = Object.keys(PROFILE_LABELS) as ProfileKey[];

export function AccessScreen() {
  const { entryMessage, login } = useAccessSession();
  const [profileKey, setProfileKey] = useState<ProfileKey | ''>('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const profileRef = useRef<HTMLSelectElement>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setValidationMessage(null);
    if (!profileKey || !password) {
      setValidationMessage('Selecione uma persona e informe a senha.');
      profileRef.current?.focus();
      return;
    }
    setLoading(true);
    const result = await login(profileKey, password);
    setLoading(false);
    if (!result.ok) {
      if (result.clearPassword) setPassword('');
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
            <h1 className="text-xl font-semibold text-fg">ONESHOT</h1>
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
            <label htmlFor="access-password" className="text-sm font-medium text-fg">
              Senha
            </label>
            <div className="relative mt-1.5">
              <input
                id="access-password"
                required
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                spellCheck={false}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="h-11 w-full rounded-lg border border-border bg-surface px-3 pr-12 text-sm text-fg outline-none focus:border-primary focus:ring-2 focus:ring-ring"
              />
              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                className="absolute inset-y-0 right-0 flex w-11 items-center justify-center text-fg-muted hover:text-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
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
            {loading ? 'Entrando...' : 'Entrar'}
          </Button>
        </form>
      </section>
    </main>
  );
}
