/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

import {
  ApiError,
  loginWithPassword,
  type AccessProfile,
  type ProfileKey,
} from '@/lib/api';
import { subscribeToUnauthorized } from '@/lib/api/session-events';

export const PROFILE_LABELS: Record<ProfileKey, string> = {
  pmo: 'PMO',
  lider_subportfolio: 'Líder de subportfólio',
  gerente_projeto: 'Gerente de projeto',
  consulta: 'Consulta',
};

type ValidatedSession = {
  accessToken: string;
  profile: AccessProfile;
  sessionKey: string;
};

type LoginResult = { ok: true } | { ok: false; clearPassword: boolean };

type AccessSessionValue = {
  session: ValidatedSession | null;
  entryMessage: string | null;
  login: (profileKey: ProfileKey, password: string) => Promise<LoginResult>;
  logout: () => void;
};

const AccessSessionContext = createContext<AccessSessionValue | null>(null);

export function AccessSessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<ValidatedSession | null>(null);
  const [entryMessage, setEntryMessage] = useState<string | null>(null);

  const logout = useCallback(() => {
    setSession(null);
    setEntryMessage(null);
  }, []);

  useEffect(
    () =>
      subscribeToUnauthorized(() => {
        setSession(null);
        setEntryMessage('Sua sessão expirou ou não é mais válida.');
      }),
    [],
  );

  const login = useCallback(
    async (profileKey: ProfileKey, password: string): Promise<LoginResult> => {
      setEntryMessage(null);
      try {
        const { access_token: accessToken, profile } = await loginWithPassword(
          profileKey,
          password,
        );
        if (profile.profile_key !== profileKey) {
          setSession(null);
          setEntryMessage(
            `A conta autenticada pertence ao perfil ${PROFILE_LABELS[profile.profile_key]}, mas foi selecionado ${PROFILE_LABELS[profileKey]}.`,
          );
          return { ok: false, clearPassword: true };
        }
        setSession({
          accessToken,
          profile,
          sessionKey: crypto.randomUUID(),
        });
        return { ok: true };
      } catch (error) {
        setSession(null);
        setEntryMessage(
          error instanceof ApiError && error.status === 401
            ? 'Persona ou senha inválida.'
            : 'Não foi possível autenticar. Tente novamente.',
        );
        return { ok: false, clearPassword: true };
      }
    },
    [],
  );

  const value = useMemo(
    () => ({ session, entryMessage, login, logout }),
    [session, entryMessage, login, logout],
  );

  return (
    <AccessSessionContext.Provider value={value}>
      {children}
    </AccessSessionContext.Provider>
  );
}

export function useAccessSession() {
  const value = useContext(AccessSessionContext);
  if (!value) {
    throw new Error(
      'useAccessSession precisa estar dentro de <AccessSessionProvider>.',
    );
  }
  return value;
}
